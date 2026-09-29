import numpy as np

from .models import ControlPoints


def filter_control_points(
    control_points: ControlPoints,
) -> ControlPoints:

    reference = np.asarray(
        control_points.reference_points,
        dtype=np.float32,
    )

    source = np.asarray(
        control_points.source_points,
        dtype=np.float32,
    )

    indices = np.arange(control_points.count)

    valid = (
        np.isfinite(reference).all(axis=1)
        & np.isfinite(source).all(axis=1)
    )

    reference = reference[valid]
    source = source[valid]
    indices = indices[valid]

    if len(reference) == 0:
        return ControlPoints(
            reference_points=np.empty((0, 2), dtype=np.float32),
            source_points=np.empty((0, 2), dtype=np.float32),
            confidence=None,
            metadata={
                **control_points.metadata,
                "original_count": control_points.count,
                "filtered_count": 0,
            },
        )

    pairs = np.hstack((reference, source))

    _, unique_indices = np.unique(
        pairs,
        axis=0,
        return_index=True,
    )

    unique_indices = np.sort(unique_indices)

    reference = reference[unique_indices]
    source = source[unique_indices]
    indices = indices[unique_indices]

    _, unique_indices = np.unique(
        reference,
        axis=0,
        return_index=True,
    )

    unique_indices = np.sort(unique_indices)

    reference = reference[unique_indices]
    source = source[unique_indices]
    indices = indices[unique_indices]

    _, unique_indices = np.unique(
        source,
        axis=0,
        return_index=True,
    )

    unique_indices = np.sort(unique_indices)

    reference = reference[unique_indices]
    source = source[unique_indices]
    indices = indices[unique_indices]

    confidence = None

    if control_points.confidence is not None:
        confidence = np.asarray(
            control_points.confidence,
            dtype=np.float32,
        )[indices]

    metadata = dict(control_points.metadata)
    metadata["original_count"] = control_points.count
    metadata["filtered_count"] = len(reference)

    return ControlPoints(
        reference_points=reference,
        source_points=source,
        confidence=confidence,
        metadata=metadata,
    )