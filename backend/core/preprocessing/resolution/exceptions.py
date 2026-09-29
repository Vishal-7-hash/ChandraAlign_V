class ResolutionError(Exception):
    pass


class ResolutionXMLParseError(ResolutionError):
    pass


class ResolutionExtractionError(ResolutionError):
    pass


class ResolutionResamplingError(ResolutionError):
    pass