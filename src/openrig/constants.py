"""Module that defines a set of constants used throughout the project.

Include common values for rigging-related properties to ensure consistency.
"""

from enum import Enum, IntEnum


class Tokens(str, Enum):
    """Defines the core components for the procedural naming system.

    These tokens represent the fundamental parts of a name
    assembled by the naming manager. The order and usage of these tokens
    will define the final naming convention across the project.
    """

    DESCRIPTOR = "descriptor"
    SIDE = "side"
    USAGE = "usage"


class Side(str, Enum):
    """Common side tokens for naming conventions."""

    LEFT = "l"
    RIGHT = "r"
    CENTER = "c"
    MIDDLE = "m"

    LEFT_LONG = "left"
    RIGHT_LONG = "right"
    CENTER_LONG = "center"
    MIDDLE_LONG = "middle"

    DEFAULT = CENTER

    def mirror(self) -> "Side":
        """Gets the mirrored side token.

        Returns:
            The mirrored side token (e.g., LEFT becomes RIGHT).
        """
        mapping = {
            Side.LEFT: Side.RIGHT,
            Side.RIGHT: Side.LEFT,
            Side.LEFT_LONG: Side.RIGHT_LONG,
            Side.RIGHT_LONG: Side.LEFT_LONG,
        }
        # For center/middle or any other unmapped side, return itself.
        return mapping.get(self, self)

    def is_left(self) -> bool:
        """Checks if the side is 'left'.

        Returns:
            True if the side is LEFT or LEFT_LONG, False otherwise.
        """
        return self in (Side.LEFT, Side.LEFT_LONG)

    def is_right(self) -> bool:
        """Checks if the side is 'right'.

        Returns:
            True if the side is RIGHT or RIGHT_LONG, False otherwise.
        """
        return self in (Side.RIGHT, Side.RIGHT_LONG)

    def is_center(self) -> bool:
        """Checks if the side is 'center'.

        Returns:
            True if the side is CENTER or CENTER_LONG, False otherwise.
        """
        return self in (Side.CENTER, Side.CENTER_LONG)


class Position(str, Enum):
    """Common position tokens for naming conventions."""

    FRONT = "front"
    BACK = "back"
    UP = "up"
    DOWN = "down"
    MIDDLE = "middle"
    INTERNAL = "internal"
    EXTERNAL = "external"

    def mirror(self) -> "Position":
        """Gets the mirrored position token.

        Returns:
            The mirrored position token (e.g., FRONT becomes BACK).
        """
        mapping = {
            Position.FRONT: Position.BACK,
            Position.BACK: Position.FRONT,
            Position.UP: Position.DOWN,
            Position.DOWN: Position.UP,
            Position.INTERNAL: Position.EXTERNAL,
            Position.EXTERNAL: Position.INTERNAL,
        }
        # For 'middle' or any other unmapped position, return itself.
        return mapping.get(self, self)


class Usage(str, Enum):
    """Defines common usage tokens."""

    # --- General Organization ---
    GUIDES = "guides"
    COMPONENT = "cmp"
    IN = "in"
    CONTROLS = "controls"
    LOGIC = "logic"
    DEFORM = "deform"
    SETTINGS = "settings"
    LOCAL = "local"
    OUT = "out"


class Extension(str, Enum):
    """Common file extensions for export and import operations."""

    # Scene files
    MAYA_ASCII = "ma"
    MAYA_BINARY = "mb"

    # Geometry/Cache files
    OBJ = "obj"
    FBX = "fbx"
    ABC = "abc"

    # Data files
    JSON = "json"
    XML = "xml"

    # Script files
    PYTHON = "py"
    MEL = "mel"

    # Image files
    PNG = "png"
    JPG = "jpg"
    EXR = "exr"
    TIFF = "tif"

    @classmethod
    def get_scene_formats(cls) -> tuple["Extension", ...]:
        """Gets a tuple of all Maya scene file extensions."""
        return (cls.MAYA_ASCII, cls.MAYA_BINARY)

    @classmethod
    def get_geometry_formats(cls) -> tuple["Extension", ...]:
        """Gets a tuple of all common geometry cache/export extensions."""
        return (cls.OBJ, cls.FBX, cls.ABC)

    @classmethod
    def get_image_formats(cls) -> tuple["Extension", ...]:
        """Gets a tuple of all common image file extensions."""
        return (cls.PNG, cls.JPG, cls.EXR, cls.TIFF)

    @classmethod
    def get_data_formats(cls) -> tuple["Extension", ...]:
        """Gets a tuple of all common data file extensions."""
        return (cls.JSON, cls.XML)

    @classmethod
    def get_script_formats(cls) -> tuple["Extension", ...]:
        """Gets a tuple of all common script file extensions."""
        return (cls.PYTHON, cls.MEL)


class AttributeType(str, Enum):
    """Common attribute types for Maya nodes."""

    # --- Single Value Numeric Types ---
    BOOL = "bool"
    LONG = "long"  # Default integer type in Maya's addAttr
    DOUBLE = "double"  # Default float type in Maya's addAttr
    FLOAT = "float"
    TIME = "time"
    ANGLE = "angle"

    # --- Compound Numeric Types ---
    DOUBLE2 = "double2"
    DOUBLE3 = "double3"
    FLOAT2 = "float2"
    FLOAT3 = "float3"

    # --- Alias Types ---
    VECTOR = "vector"  # Alias for double3
    COLOR = "color"  # Alias for float3

    # --- Other Data Types ---
    ENUM = "enum"
    STRING = "string"
    MESSAGE = "message"
    MATRIX = "matrix"
    COMPOUND = "compound"  # Generic compound for custom structures

    @classmethod
    def get_numeric_types(cls) -> tuple["AttributeType", ...]:
        """Gets a tuple of all single-value numeric attribute types."""
        return (cls.BOOL, cls.LONG, cls.DOUBLE, cls.FLOAT, cls.TIME, cls.ANGLE)

    @classmethod
    def get_compound_numeric_types(cls) -> tuple["AttributeType", ...]:
        """Gets a tuple of all compound numeric attribute types, including aliases."""
        return (
            cls.DOUBLE2,
            cls.DOUBLE3,
            cls.FLOAT2,
            cls.FLOAT3,
            cls.VECTOR,
            cls.COLOR,
        )


class RotateOrder(Enum):
    """Represents a Maya rotate order, holding both its string and index value.

    This provides a single source of truth for rotate orders, preventing
    discrepancies between string and integer representations.

    The default rotate order for the project can be set by changing the
    `DEFAULT` class attribute.
    """

    XYZ = ("xyz", 0)
    YZX = ("yzx", 1)
    ZXY = ("zxy", 2)
    XZY = ("xzy", 3)
    YXZ = ("yxz", 4)
    ZYX = ("zyx", 5)

    def __init__(self, string_value: str, index_value: int):
        """Initializes the RotateOrder enum member.

        Args:
            string_value (str): The string representation of the rotate order.
            index_value (int): The integer index of the rotate order.
        """
        self._string_value = string_value
        self._index_value = index_value

    @property
    def as_string(self) -> str:
        """The string representation of the rotate order (e.g., 'xyz')."""
        return self._string_value

    @property
    def as_index(self) -> int:
        """The integer index of the rotate order (e.g., 0)."""
        return self._index_value

    # This line defines the default rotate order for the project.
    # To change it, simply point to a different member (e.g., DEFAULT = XYZ).
    DEFAULT = XYZ


class VectorIndex(IntEnum):
    """Low-level integer indices for accessing components of vector attributes.

    This enum is intentionally a simple `IntEnum` to be used directly for
    indexing lists or tuples returned by Maya commands (e.g., `vector[VectorIndex.Y]`).

    For a higher-level, more descriptive representation of axes, see the `Axis` class.
    """

    X = 0
    Y = 1
    Z = 2
    W = 3

    DEFAULT = X


class ColorIndex(IntEnum):
    """Maya Index Colors for Drawing Overrides."""

    DEFAULT = 0
    BLACK = 1
    DARK_GREY = 2
    LIGHT_GREY = 3
    BURGUNDY = 4
    NAVY_BLUE = 5
    BLUE = 6
    DARK_GREEN = 7
    DARK_PURPLE = 8
    MAGENTA = 9
    BROWN = 10
    DARK_BROWN = 11
    DULL_RED = 12
    RED = 13
    GREEN = 14
    BLUE_SKY = 15
    WHITE = 16
    YELLOW = 17
    CYAN = 18
    LIGHT_GREEN = 19
    PINK = 20
    PEACH = 21
    LIGHT_YELLOW = 22
    SEA_GREEN = 23
    LIGHT_BROWN = 24
    OLIVE = 25
    LIME_GREEN = 26
    TEAL_GREEN = 27
    LIGHT_BLUE = 28
    DARK_BLUE = 29
    PURPLE = 30
    DARK_MAGENTA = 31


class ColorRGB(tuple[float, float, float], Enum):
    """Standard RGB Float Colors."""

    WHITE = (1.0, 1.0, 1.0)
    BLACK = (0.0, 0.0, 0.0)
    RED = (1.0, 0.0, 0.0)
    GREEN = (0.0, 1.0, 0.0)
    BLUE = (0.0, 0.0, 1.0)
    YELLOW = (1.0, 1.0, 0.0)
    CYAN = (0.0, 1.0, 1.0)
    MAGENTA = (1.0, 0.0, 1.0)
    ORANGE = (1.0, 0.5, 0.0)
    PURPLE = (0.5, 0.0, 0.5)
    BROWN = (0.5, 0.25, 0.0)
    PINK = (1.0, 0.75, 0.8)
    GREY = (0.5, 0.5, 0.5)
    DARK_GREY = (0.25, 0.25, 0.25)
    LIGHT_GREY = (0.75, 0.75, 0.75)
    LIGHT_RED = (1.0, 0.5, 0.5)
    LIGHT_GREEN = (0.5, 1.0, 0.5)
    LIGHT_BLUE = (0.5, 0.5, 1.0)
    LIGHT_YELLOW = (1.0, 1.0, 0.5)
    DARK_RED = (0.5, 0.0, 0.0)
    DARK_GREEN = (0.0, 0.5, 0.0)
    DARK_BLUE = (0.0, 0.0, 0.5)
    DARK_YELLOW = (0.5, 0.5, 0.0)
    DARK_CYAN = (0.0, 0.5, 0.5)
    DARK_MAGENTA = (0.5, 0.0, 0.5)
    DARK_ORANGE = (0.5, 0.25, 0.0)
    DARK_PURPLE = (0.25, 0.0, 0.25)
    DARK_BROWN = (0.25, 0.125, 0.0)
    DARK_PINK = (0.5, 0.25, 0.5)

    CHANNELS = ("R", "G", "B")


class Axis(str, Enum):
    """Common axis tokens for naming conventions and vector operations."""

    X = "X"
    Y = "Y"
    Z = "Z"
    X_NEGATIVE = "-X"
    Y_NEGATIVE = "-Y"
    Z_NEGATIVE = "-Z"

    # This tuple unpacking defines the default axis system for the project.
    # To change the default (e.g., to a Y-up system), modify this line.
    AIM, UP, SIDE = (X, Y, Z)

    DEFAULT = AIM

    @property
    def is_negative(self) -> bool:
        """Checks if the axis is negative (e.g., '-X')."""
        return self.value.startswith("-")

    @property
    def is_positive(self) -> bool:
        """Checks if the axis is positive (e.g., 'X')."""
        return not self.is_negative

    @property
    def as_index(self) -> int:
        """Gets the corresponding integer index for axis (0 for X, 1 for Y, 2 for Z).

        Note:
            This method ignores the sign of the axis (e.g., both 'X' and '-X' return 0).

        Returns:
            The integer index (0, 1, or 2).

        Raises:
            ValueError: If the axis does not have a corresponding index.
        """
        positive_self = Axis(self.value.strip("-"))
        mapping = {
            Axis.X: VectorIndex.X,
            Axis.Y: VectorIndex.Y,
            Axis.Z: VectorIndex.Z,
        }
        try:
            return mapping[positive_self]
        except KeyError:
            raise ValueError(
                f"Axis '{self.value}' does not have a corresponding vector index."
            ) from None

    def mirror(self) -> "Axis":
        """Gets the mirrored axis.

        For example, 'X' becomes '-X' and '-Y' becomes 'Y'.

        Returns:
            The mirrored Axis member.
        """
        if self.is_negative:
            return Axis(self.value[1:])
        return Axis(f"-{self.value}")

    @classmethod
    def get_default_order(cls) -> tuple["Axis", "Axis", "Axis"]:
        """Gets the default axis order tuple defined by (AIM, UP, SIDE).

        Returns:
            A tuple containing the default aim, up, and side axes.
        """
        return (cls.AIM, cls.UP, cls.SIDE)

    @classmethod
    def get_axis_orders(cls) -> dict[str, tuple["Axis", ...]]:
        """Gets a dictionary of all supported axis orders.

        Returns:
            A dictionary mapping rotate order strings to tuples of Axis members.
        """
        return {
            "xyz": (cls.X, cls.Y, cls.Z),
            "yzx": (cls.Y, cls.Z, cls.X),
            "zxy": (cls.Z, cls.X, cls.Y),
            "xzy": (cls.X, cls.Z, cls.Y),
            "yxz": (cls.Y, cls.X, cls.Z),
            "zyx": (cls.Z, cls.Y, cls.X),
        }


class Vector(tuple[int, int, int], Enum):
    """Constants related to vector definitions. Inherits from tuple."""

    X = (1, 0, 0)
    Y = (0, 1, 0)
    Z = (0, 0, 1)

    # This tuple unpacking defines the default vectors for the project.
    AIM, UP, SIDE = (X, Y, Z)

    @classmethod
    def get_default_order(cls) -> tuple["Vector", "Vector", "Vector"]:
        """Gets the default vector tuple defined by (AIM, UP, SIDE).

        Returns:
            A tuple containing the default aim, up, and side vectors.
        """
        return (cls.AIM, cls.UP, cls.SIDE)


class Attribute(str, Enum):
    """Common attribute names for rigging elements."""

    # --- General Node Attributes ---
    MESSAGE = "message"
    NODE_STATE = "nodeState"

    # --- Transform Attributes ---
    TRANSLATE = "translate"
    ROTATE = "rotate"
    SCALE = "scale"
    SHEAR = "shear"
    ROTATE_ORDER = "rotateOrder"
    ROTATE_PIVOT = "rotatePivot"
    SCALE_PIVOT = "scalePivot"

    # --- Joint Specific Attributes ---
    JOINT_ORIENT = "jointOrient"
    ROTATE_AXIS = "rotateAxis"

    # --- Matrix Attributes ---
    MATRIX = "matrix"
    WORLD_MATRIX = "worldMatrix"
    WORLD_INVERSE_MATRIX = "worldInverseMatrix"
    PARENT_MATRIX = "parentMatrix"
    PARENT_INVERSE_MATRIX = "parentInverseMatrix"
    OFFSET_PARENT_MATRIX = "offsetParentMatrix"

    # --- Dag Node Attributes ---
    VISIBILITY = "visibility"
    INTERMEDIATE_OBJECT = "intermediateObject"
    TEMPLATE = "template"
    LOD_VISIBILITY = "lodVisibility"

    # --- Drawing Overrides ---
    OVERRIDE_ENABLED = "overrideEnabled"
    OVERRIDE_DISPLAY_TYPE = "overrideDisplayType"
    OVERRIDE_LOD = "overrideLevelOfDetail"
    OVERRIDE_COLOR = "overrideColor"
    OVERRIDE_COLOR_RGB = "overrideColorRGB"


class Matrix:
    """Constants and factory methods related to matrix definitions."""

    IDENTITY_XYZ: tuple[float, ...] = (
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
        0.0,
        0.0,
        0.0,
        0.0,
        1.0,
    )

    ZERO: tuple[float, ...] = (
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
        0.0,
    )

    @staticmethod
    def _get_vector_from_axis(axis: Axis) -> tuple[float, ...]:
        """Helper to convert an Axis enum member to a vector tuple."""
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

    @classmethod
    def get_identity(
        cls, aim_axis: Axis, up_axis: Axis, side_axis: Axis
    ) -> tuple[float, ...]:
        """Builds a 4x4 identity matrix for a specific coordinate system.

        Args:
            aim_axis: The axis that represents the forward/aim direction (new X).
            up_axis: The axis that represents the up direction (new Y).
            side_axis: The axis that represents the side direction (new Z).

        Returns:
            A 16-element tuple representing the row-major identity matrix.
        """
        aim_vec = cls._get_vector_from_axis(aim_axis)
        up_vec = cls._get_vector_from_axis(up_axis)
        side_vec = cls._get_vector_from_axis(side_axis)

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

    @classmethod
    def get_default(cls) -> tuple[float, ...]:
        """Gets the default identity matrix based on the axis order from the Axis class.

        Returns:
            A 16-element tuple for the default identity matrix.
        """
        return cls.get_identity(Axis.AIM, Axis.UP, Axis.SIDE)

    @classmethod
    def get_inverse(cls, matrix: tuple[float, ...]) -> tuple[float, ...]:
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

    @classmethod
    def get_default_inverse(cls) -> tuple[float, ...]:
        """Gets the inverse of the default identity matrix.

        Returns:
            A 16-element tuple for the inverted default identity matrix.
        """
        default_identity = cls.get_default()
        return cls.get_inverse(default_identity)
