import re
import xml.etree.ElementTree as ET
from pathlib import Path

from .exceptions import (
    ResolutionExtractionError,
    ResolutionXMLParseError,
)
from .models import ResolutionInfo


class ResolutionParser:

    def parse(
        self,
        xml_path: str | Path,
    ) -> ResolutionInfo:

        path = Path(xml_path)

        if not path.exists():
            raise ResolutionXMLParseError(
                f"XML file not found: {path}"
            )

        try:
            root = ET.parse(path).getroot()
        except Exception as exc:
            raise ResolutionXMLParseError(
                f"Failed to parse XML: {exc}"
            ) from exc

        instrument = self._detect_instrument(root)

        if instrument == "OHRC":
            resolution = self._extract_ohrc_resolution(root)

        elif instrument == "NAC":
            resolution = self._extract_nac_resolution(root)

        else:
            raise ResolutionExtractionError(
                "Unsupported or unknown instrument."
            )

        return ResolutionInfo(
            meters_per_pixel=resolution,
            instrument=instrument,
            metadata={
                "xml_path": str(path),
            },
        )

    def _detect_instrument(
        self,
        root: ET.Element,
    ) -> str | None:

        text = " ".join(
            element.text.strip()
            for element in root.iter()
            if element.text and element.text.strip()
        ).upper()

        if "OHRC" in text or "ORBiter HIGH RESOLUTION CAMERA".upper() in text:
            return "OHRC"

        if "LROC" in text and "NAC" in text:
            return "NAC"

        return None

    def _extract_ohrc_resolution(
        self,
        root: ET.Element,
    ) -> float:

        for element in root.iter():

            if self._local_name(element.tag) != "pixel_resolution":
                continue

            unit = element.attrib.get("unit", "").strip().lower()

            if unit != "m/pixel":
                continue

            try:
                value = float(
                    element.text.strip()
                )
            except (AttributeError, ValueError) as exc:
                raise ResolutionExtractionError(
                    "Invalid OHRC pixel_resolution value."
                ) from exc

            if value <= 0:
                raise ResolutionExtractionError(
                    "OHRC pixel resolution must be greater than zero."
                )

            return value

        raise ResolutionExtractionError(
            "OHRC pixel_resolution field was not found."
        )

    def _extract_nac_resolution(
        self,
        root: ET.Element,
    ) -> float:

        descriptions = []

        for element in root.iter():

            if self._local_name(element.tag) != "description":
                continue

            if element.text:
                descriptions.append(
                    " ".join(
                        element.text.split()
                    )
                )

        text = " ".join(descriptions)

        match = re.search(
            r"NACs?.{0,250}?\(\s*"
            r"([0-9]+(?:\.[0-9]+)?)"
            r"\s*m/pixel\s*\)",
            text,
            flags=re.IGNORECASE,
        )

        if match is None:
            match = re.search(
                r"NACs?.{0,250}?"
                r"([0-9]+(?:\.[0-9]+)?)"
                r"\s*m/pixel",
                text,
                flags=re.IGNORECASE,
            )

        if match is None:
            raise ResolutionExtractionError(
                "NAC pixel resolution could not be extracted."
            )

        resolution = float(
            match.group(1)
        )

        if resolution <= 0:
            raise ResolutionExtractionError(
                "NAC pixel resolution must be greater than zero."
            )

        return resolution

    @staticmethod
    def _local_name(
        tag: str,
    ) -> str:

        return tag.rsplit(
            "}",
            1,
        )[-1]