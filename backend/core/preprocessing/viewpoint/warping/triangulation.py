from dataclasses import dataclass

import numpy as np
from scipy.spatial import Delaunay


@dataclass(frozen=True)
class Triangulation:
    reference_points: np.ndarray
    source_points: np.ndarray
    triangles: np.ndarray


def create_triangulation(
    reference_points: np.ndarray,
    source_points: np.ndarray,
) -> Triangulation | None:

    try:
        reference_points = np.asarray(
            reference_points,
            dtype=np.float32,
        )

        source_points = np.asarray(
            source_points,
            dtype=np.float32,
        )
    except Exception:
        return None

    if reference_points.ndim != 2 or reference_points.shape[1] != 2:
        return None

    if source_points.ndim != 2 or source_points.shape[1] != 2:
        return None

    if len(reference_points) != len(source_points):
        return None

    if len(reference_points) < 3:
        return None

    valid = (
        np.isfinite(reference_points).all(axis=1)
        & np.isfinite(source_points).all(axis=1)
    )

    reference_points = reference_points[valid]
    source_points = source_points[valid]

    if len(reference_points) < 3:
        return None

    _, reference_indices = np.unique(
        reference_points,
        axis=0,
        return_index=True,
    )

    reference_indices = np.sort(reference_indices)

    reference_points = reference_points[reference_indices]
    source_points = source_points[reference_indices]

    _, source_indices = np.unique(
        source_points,
        axis=0,
        return_index=True,
    )

    source_indices = np.sort(source_indices)

    reference_points = reference_points[source_indices]
    source_points = source_points[source_indices]

    if len(reference_points) < 3:
        return None

    try:
        delaunay = Delaunay(reference_points)
    except Exception as exc:
        print(f"TIN: triangulation failed: {exc}")
        return None

    simplices = np.asarray(
        delaunay.simplices,
        dtype=np.int32,
    )

    if simplices.ndim != 2 or simplices.shape[1] != 3:
        return None

    valid_triangles = []

    for triangle in simplices:

        ref_triangle = reference_points[triangle]
        src_triangle = source_points[triangle]

        ref_edge0 = ref_triangle[1] - ref_triangle[0]
        ref_edge1 = ref_triangle[2] - ref_triangle[0]
        ref_area = abs(
            ref_edge0[0] * ref_edge1[1]
            - ref_edge0[1] * ref_edge1[0]
        )

        src_edge0 = src_triangle[1] - src_triangle[0]
        src_edge1 = src_triangle[2] - src_triangle[0]
        src_area = abs(
            src_edge0[0] * src_edge1[1]
            - src_edge0[1] * src_edge1[0]
        )

        if ref_area <= 1e-6:
            continue

        if src_area <= 1e-6:
            continue

        valid_triangles.append(triangle)

    if not valid_triangles:
        print("TIN: no valid non-degenerate triangles.")
        return None

    return Triangulation(
        reference_points=reference_points,
        source_points=source_points,
        triangles=np.asarray(
            valid_triangles,
            dtype=np.int32,
        ),
    )