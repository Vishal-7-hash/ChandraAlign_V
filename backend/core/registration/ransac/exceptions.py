class RANSACError(Exception):
    pass


class InsufficientMatchesError(RANSACError):
    pass


class HomographyEstimationError(RANSACError):
    pass