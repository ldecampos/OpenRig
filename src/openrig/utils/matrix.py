"""Matrix utility functions for the OpenRig coordinate system.

Provides helpers for building and inverting 4×4 row-major identity matrices
based on the axis configuration defined in ``constants.Axis``.
"""

from openrig.constants import Axis, Vector


def _get_vector_from_axis(axis: Axis) -> tuple[float, ...]:
    """Converts an Axis enum member to a direction vector tuple.

    Args:
        axis: The axis to convert (e.g. ``Axis.X``, ``Axis.Y_NEGATIVE``).

    Returns:
        A 3-element tuple with the unit vector, sign-flipped for negative axes.
    """
    base_axis_map = {
        Axis.X: Vector.X,
        Axis.Y: Vector.Y,
        Axis.Z: Vector.Z,
    }
    # Get the positive axis (e.g., from '-X' get 'X')
    positive_axis = Axis(axis.value.strip("-"))
    base_vector = base_axis_map[positive_axis]

    multiplier = -1.0 if axis.is_negative else 1.0
    return tuple(multiplier * v for v in base_vector)


def get_identity(aim_axis: Axis, up_axis: Axis, side_axis: Axis) -> tuple[float, ...]:
    """Builds a 4x4 identity matrix for a specific coordinate system.

    Args:
        aim_axis: The axis that represents the forward/aim direction (new X).
        up_axis: The axis that represents the up direction (new Y).
        side_axis: The axis that represents the side direction (new Z).

    Returns:
        A 16-element tuple representing the row-major identity matrix.
    """
    aim_vec = _get_vector_from_axis(aim_axis)
    up_vec = _get_vector_from_axis(up_axis)
    side_vec = _get_vector_from_axis(side_axis)

    return (
        aim_vec[0],
        aim_vec[1],
        aim_vec[2],
        0.0,
        up_vec[0],
        up_vec[1],
        up_vec[2],
        0.0,
        side_vec[0],
        side_vec[1],
        side_vec[2],
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
    )


def get_default_identity() -> tuple[float, ...]:
    """Gets the default identity matrix based on the axis order from the Axis class.

    Returns:
        A 16-element tuple for the default identity matrix.
    """
    return get_identity(Axis.AIM, Axis.UP, Axis.SIDE)


def get_inverse(matrix: tuple[float, ...]) -> tuple[float, ...]:
    """Calculates the inverse of a 4x4 orthonormal rotation matrix.

    The calculation is performed by transposing the matrix.

    Args:
        matrix: A 16-element tuple representing the row-major matrix.

    Returns:
        A 16-element tuple for the inverted (transposed) matrix.
    """
    return (
        matrix[0],
        matrix[4],
        matrix[8],
        matrix[12],
        matrix[1],
        matrix[5],
        matrix[9],
        matrix[13],
        matrix[2],
        matrix[6],
        matrix[10],
        matrix[14],
        matrix[3],
        matrix[7],
        matrix[11],
        matrix[15],
    )


def get_default_inverse() -> tuple[float, ...]:
    """Gets the inverse of the default identity matrix.

    Returns:
        A 16-element tuple for the inverted default identity matrix.
    """
    default_identity = get_default_identity()
    return get_inverse(default_identity)
