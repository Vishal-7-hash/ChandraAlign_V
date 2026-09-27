from __future__ import annotations

import time
from typing import Any

import numpy as np
import torch
from kornia.feature import LoFTR

from .config import LoFTRConfig
from .exceptions import (
    ImageShapeError,
    InvalidImageError,
    MatchingError,
    ModelInitializationError,
)
from .result import LoFTRResult


class LoFTRMatcher:
    """
    Production-oriented LoFTR matching engine.

    Responsibilities:
        - Load LoFTR
        - Manage device
        - Validate input tensors
        - Run LoFTR inference
        - Extract correspondences
        - Return a clean LoFTRResult

    This class intentionally does NOT:
        - load images from disk
        - resize images
        - denoise images
        - normalize image intensities
        - perform lunar preprocessing
        - perform registration
        - estimate a homography
        - perform RANSAC
        - modify the input images
    """

    def __init__(self, config: LoFTRConfig | None = None) -> None:

        self.config = config or LoFTRConfig()

        self.config.validate()

        self.device = self.config.resolve_device()

        self._model: LoFTR | None = None

        self._initialize_model()

    # ------------------------------------------------------------------
    # MODEL
    # ------------------------------------------------------------------

    def _initialize_model(self) -> None:
        """Initialize the pretrained LoFTR model."""

        try:
            model = LoFTR(
                pretrained=self.config.pretrained
            )

            model = model.to(self.device)
            model.eval()

            self._model = model

        except Exception as exc:
            raise ModelInitializationError(
                "Failed to initialize LoFTR. "
                f"Model='{self.config.pretrained}', "
                f"device='{self.device}'."
            ) from exc

    @property
    def model(self) -> LoFTR:
        """Return the initialized LoFTR model."""

        if self._model is None:
            raise ModelInitializationError(
                "LoFTR model has not been initialized."
            )

        return self._model

    # ------------------------------------------------------------------
    # INPUT VALIDATION
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_image(
        image: torch.Tensor | np.ndarray,
        name: str,
    ) -> None:
        """
        Validate an image before passing it to LoFTR.

        Accepted logical formats:

            H x W
            1 x H x W
            1 x 1 x H x W

        The tensor passed to LoFTR will always be:

            1 x 1 x H x W
        """

        if isinstance(image, np.ndarray):

            if image.ndim not in (2, 3, 4):
                raise InvalidImageError(
                    f"{name} must have 2, 3, or 4 dimensions. "
                    f"Received shape={image.shape}."
                )

        elif isinstance(image, torch.Tensor):

            if image.ndim not in (2, 3, 4):
                raise InvalidImageError(
                    f"{name} must have 2, 3, or 4 dimensions. "
                    f"Received shape={tuple(image.shape)}."
                )

        else:

            raise InvalidImageError(
                f"{name} must be a numpy.ndarray or torch.Tensor. "
                f"Received {type(image).__name__}."
            )

    @staticmethod
    def _to_tensor(
        image: torch.Tensor | np.ndarray,
        name: str,
    ) -> torch.Tensor:
        """
        Convert an image into LoFTR's required tensor shape:

            [1, 1, H, W]

        For integer images such as uint8:

            0-255 -> 0.0-1.0

        No spatial preprocessing is performed here.

        This method does NOT:
            - resize
            - denoise
            - enhance
            - geometrically transform
        """

        LoFTRMatcher._validate_image(image, name)

        # --------------------------------------------------------------
        # NumPy -> Torch
        # --------------------------------------------------------------

        if isinstance(image, np.ndarray):

            if not np.issubdtype(image.dtype, np.number):
                raise InvalidImageError(
                    f"{name} must contain numeric values."
                )

            tensor = torch.from_numpy(
                np.ascontiguousarray(image)
            )

        else:

            tensor = image

        # --------------------------------------------------------------
        # Convert layouts to [1, 1, H, W]
        #
        # Supported:
        #     H x W
        #     1 x H x W
        #     1 x 1 x H x W
        # --------------------------------------------------------------

        if tensor.ndim == 2:

            tensor = tensor.unsqueeze(0).unsqueeze(0)

        elif tensor.ndim == 3:

            if tensor.shape[0] != 1:
                raise InvalidImageError(
                    f"{name} is 3D but its first dimension is "
                    f"{tensor.shape[0]}. "
                    "LoFTR expects a single grayscale channel."
                )

            tensor = tensor.unsqueeze(0)

        elif tensor.ndim == 4:

            if tensor.shape[0] != 1:
                raise InvalidImageError(
                    f"{name} batch size must be 1. "
                    f"Received batch size={tensor.shape[0]}."
                )

            if tensor.shape[1] != 1:
                raise InvalidImageError(
                    f"{name} must contain exactly one channel. "
                    f"Received channels={tensor.shape[1]}."
                )

        # --------------------------------------------------------------
        # DEBUG: before conversion
        # --------------------------------------------------------------

        tensor = tensor.contiguous()

        print(
            f"\n[{name}] BEFORE CONVERSION"
        )
        print("  shape:", tuple(tensor.shape))
        print("  dtype:", tensor.dtype)
        print("  min:", tensor.min().item())
        print("  max:", tensor.max().item())

        # --------------------------------------------------------------
        # Convert to float32
        # --------------------------------------------------------------

        if tensor.is_floating_point():

            tensor = tensor.float()

        else:

            tensor = tensor.float() / 255.0

        # --------------------------------------------------------------
        # DEBUG: after conversion
        # --------------------------------------------------------------

        print(
            f"[{name}] AFTER CONVERSION"
        )
        print("  shape:", tuple(tensor.shape))
        print("  dtype:", tensor.dtype)
        print("  min:", tensor.min().item())
        print("  max:", tensor.max().item())

        return tensor

    # ------------------------------------------------------------------
    # DIMENSION VALIDATION
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_dimensions(
        image0: torch.Tensor,
        image1: torch.Tensor,
    ) -> None:
        """
        Validate spatial dimensions.

        We do NOT resize or pad here.
        """

        h0, w0 = image0.shape[-2:]
        h1, w1 = image1.shape[-2:]

        if h0 < 8 or w0 < 8:
            raise ImageShapeError(
                f"image0 is too small: {(h0, w0)}."
            )

        if h1 < 8 or w1 < 8:
            raise ImageShapeError(
                f"image1 is too small: {(h1, w1)}."
            )

    # ------------------------------------------------------------------
    # MATCHING
    # ------------------------------------------------------------------

    def match(
        self,
        image0: torch.Tensor | np.ndarray,
        image1: torch.Tensor | np.ndarray,
    ) -> LoFTRResult:
        """
        Match two already-prepared grayscale images.

        Parameters
        ----------
        image0:
            Reference/fixed image.

        image1:
            Moving/source image.

        Returns
        -------
        LoFTRResult
            Final LoFTR correspondences and confidence values.
        """

        tensor0 = self._to_tensor(
            image0,
            "image0",
        )

        tensor1 = self._to_tensor(
            image1,
            "image1",
        )

        self._validate_dimensions(
            tensor0,
            tensor1,
        )

        tensor0 = tensor0.to(
            device=self.device,
            non_blocking=True,
        )

        tensor1 = tensor1.to(
            device=self.device,
            non_blocking=True,
        )

        input_dict: dict[str, torch.Tensor] = {
            "image0": tensor0,
            "image1": tensor1,
        }

        try:

            if self.device.type == "cuda":
                torch.cuda.synchronize()

            start_time = time.perf_counter()

            with torch.inference_mode():

                if self.config.use_amp:

                    with torch.autocast(
                        device_type="cuda",
                        dtype=torch.float16,
                    ):
                        output = self.model(input_dict)

                else:

                    output = self.model(input_dict)

            if self.device.type == "cuda":
                torch.cuda.synchronize()

            elapsed_ms = (
                time.perf_counter() - start_time
            ) * 1000.0

        except Exception as exc:

            raise MatchingError(
                "LoFTR inference failed."
            ) from exc

        return self._build_result(
            output=output,
            image0_shape=tuple(
                tensor0.shape[-2:]
            ),
            image1_shape=tuple(
                tensor1.shape[-2:]
            ),
            inference_time_ms=elapsed_ms,
        )

    # ------------------------------------------------------------------
    # OUTPUT
    # ------------------------------------------------------------------

    def _build_result(
        self,
        output: dict[str, Any],
        image0_shape: tuple[int, int],
        image1_shape: tuple[int, int],
        inference_time_ms: float,
    ) -> LoFTRResult:
        """
        Convert LoFTR output into our stable result object.
        """

        required_keys = (
            "keypoints0",
            "keypoints1",
            "confidence",
        )

        missing = [
            key
            for key in required_keys
            if key not in output
        ]

        if missing:

            raise MatchingError(
                "LoFTR returned an unexpected output structure. "
                f"Missing keys: {missing}. "
                f"Available keys: {list(output.keys())}"
            )

        keypoints0 = (
            output["keypoints0"]
            .detach()
            .cpu()
            .numpy()
        )

        keypoints1 = (
            output["keypoints1"]
            .detach()
            .cpu()
            .numpy()
        )

        confidence = (
            output["confidence"]
            .detach()
            .cpu()
            .numpy()
        )

        keypoints0 = np.asarray(
            keypoints0,
            dtype=np.float32,
        )

        keypoints1 = np.asarray(
            keypoints1,
            dtype=np.float32,
        )

        confidence = np.asarray(
            confidence,
            dtype=np.float32,
        )

        if (
            keypoints0.ndim != 2
            or keypoints0.shape[1] != 2
        ):
            raise MatchingError(
                "Unexpected keypoints0 shape: "
                f"{keypoints0.shape}"
            )

        if (
            keypoints1.ndim != 2
            or keypoints1.shape[1] != 2
        ):
            raise MatchingError(
                "Unexpected keypoints1 shape: "
                f"{keypoints1.shape}"
            )

        if len(keypoints0) != len(keypoints1):

            raise MatchingError(
                "keypoints0 and keypoints1 contain "
                "different numbers of matches."
            )

        if len(confidence) != len(keypoints0):

            raise MatchingError(
                "confidence count does not match "
                "the number of correspondences."
            )

        result = LoFTRResult(
            keypoints0=keypoints0,
            keypoints1=keypoints1,
            confidence=confidence,
            image0_shape=image0_shape,
            image1_shape=image1_shape,
            inference_time_ms=inference_time_ms,
            metadata={
                "backend": "kornia",
                "model": self.config.pretrained,
                "device": str(self.device),
                "raw_output_keys": tuple(
                    output.keys()
                ),
            },
        )

        if self.config.confidence_threshold is not None:

            result = result.filter_by_confidence(
                self.config.confidence_threshold
            )

        return result