class LoFTRError(Exception):
    """Base exception for the LoFTR matching module."""


class InvalidImageError(LoFTRError):
    """Raised when an input image has an invalid format or shape."""


class ImageShapeError(LoFTRError):
    """Raised when image dimensions are incompatible."""


class MatchingError(LoFTRError):
    """Raised when LoFTR inference fails."""


class ModelInitializationError(LoFTRError):
    """Raised when the LoFTR model cannot be initialized."""