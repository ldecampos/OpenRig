"""Module that defines a set of constants used throughout the project.

Include common values for rigging-related properties to ensure consistency.
"""

from enum import Enum, IntEnum
from typing import ClassVar

from openrig.config import SETTINGS


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

    DEFAULT: ClassVar["Side"]


# Set default side from configuration
Side.DEFAULT = Side(SETTINGS.get("side_default", "c"))


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
    """Defines core rigging usage tokens (Structure, Hierarchy, Mechanics)."""

    # --- Core ---
    CONTROL = "ctr"
    OFFSET = "offset"
    GROUP = "grp"
    PIVOT = "pivot"
    ROOT = "root"
    SETTINGS = "settings"
    SNAP = "snap"
    TRIGGER = "trg"
    AUTO = "auto"
    ZERO = "zero"
    SPLINE = "spl"
    RIG_TYPE = "rigType"

    # --- Organizers ---
    COMPONENT = "cmp"
    MODULE = "module"
    INPUTS = "inputs"
    OUTPUTS = "outputs"
    CONTROLS = "controls"
    JOINTS = "joints"
    SKELETON = "skeleton"
    LOGIC = "logic"
    RIG = "rig"
    LOCAL = "local"
    LOCALS = "locals"
    IN = "in"
    OUT = "out"
    END = "end"

    # --- Geometry ---
    GEOMETRY = "geo"
    MESH = "mesh"
    CURVE = "crv"
    NURBS = "nurbs"
    LATTICE = "lat"
    LATTICE_BASE = "latBase"
    VERTEX = "vtx"
    CV = "cv"

    # --- Joint ---
    JOINT = "jnt"
    GEO_SKIN_JOINT = "skn"
    CURVE_SKIN_JOINT = "cskn"
    NURBS_SKIN_JOINT = "nskn"
    LATTICE_SKIN_JOINT = "lskn"
    PREBIND = "prebind"
    SKIN_SET = "skinSet"

    # --- Mechanics ---
    IK_HANDLE = "ikh"
    EFFECTOR = "effector"
    IK_SPLINE = "iks"

    POLE_VECTOR = "pv"
    DRIVER = "drv"
    DRIVERS = "drivers"
    GUIDE = "guide"
    GUIDES = "guides"
    REFERENCE = "ref"
    LOCATOR = "loc"
    ANCHOR = "anchor"

    # --- Miscellaneous ---
    ANIMATION_CURVE = "acrv"
    SET_DRIVEN_KEY = "sdk"
    TEST = "test"
    TEMP = "temp"
    RBF = "rbf"
    ZIP = "zip"
    PUSH = "push"
    PULL = "pull"
    MACRO = "macro"
    MICRO = "micro"


class UsageComponent(str, Enum):
    """Defines semantic component types."""

    BODY = "boy"
    FACE = "face"
    EXTRA = "extra"
    CUSTOM = "custom"
    GENERIC = "generic"
    HAIR = "hair"
    CLOTH = "cloth"
    UTILS = "utils"
    PROP = "prop"
    ELEMENT = "elem"


class UsageDeformer(str, Enum):
    """Defines deformer types."""

    SKIN_CLUSTER = "skin"
    BLEND_SHAPE = "bs"
    SQUASH = "squash"
    BEND = "bend"
    TWIST = "twist"
    WRAP = "wrap"
    WAVE = "wave"
    CORRECTIVE = "crr"
    DELTA_MUSH = "dm"
    FFD = "ffd"


class UsageConstraint(str, Enum):
    """Defines constraint types."""

    PARENT_CONSTRAINT = "pasns"
    POINT_CONSTRAINT = "posns"
    ORIENT_CONSTRAINT = "orsns"
    SCALE_CONSTRAINT = "scsns"
    AIM_CONSTRAINT = "aimsns"
    POLE_VECTOR_CONSTRAINT = "pvsns"
    MATRIX_CONSTRAINT = "matcns"
    COMPONENT_MATCH = "componentMatch"


class UsageUtility(str, Enum):
    """Defines utility node types (Math, Matrix, Vector, etc)."""

    # --- Math & Logic ---
    ADD = "add"
    SUBTRACT = "sub"
    PRODUCT = "prod"
    MULTIPLY = "mult"
    DIVIDE = "div"
    POWER = "pow"
    REVERSE = "rev"
    CONDITION = "cond"
    CLAMP = "clamp"
    REMAP = "remap"
    PLUS_MINUS_AVERAGE = "pma"
    BLEND = "blend"
    DISTANCE = "dist"
    MAX = "max"
    MIN = "min"
    NORMALIZE = "norm"
    ANGLE_BETWEEN = "ab"
    SQUARE_ROOT = "sqrt"
    ABSOLUTE = "abs"

    # --- Matrix ---
    COMPOSE_MATRIX = "cmat"
    DECOMPOSE_MATRIX = "dmat"
    MULTIPLY_MATRIX = "multmat"
    INVERSE_MATRIX = "invmat"
    BLEND_MATRIX = "blendmat"
    PICK_MATRIX = "pickmat"
    FOUR_BY_FOUR_MATRIX = "fbfmat"
    AIM_MATRIX = "aimmat"
    POINT_MATRIX_MULT = "pmatmult"
    PROXIMITY_PIN = "pin"
    UV_PIN = "uvPin"

    # --- Vector & Quaternion ---
    VECTOR_PRODUCT = "vecp"
    EULER_TO_QUAT = "e2q"
    QUAT_TO_EULER = "q2e"
    QUAT_SLERP = "qslerp"
    QUAT_INVERT = "qinv"
    QUAT_PRODUCT = "qprod"

    # --- Curve & Surface ---
    CURVE_INFO = "cinfo"
    POINT_ON_CURVE_INFO = "pocinfo"
    NEAREST_POINT_ON_CURVE = "npoc"
    SURFACE_INFO = "sinfo"
    CLOSEST_POINT_ON_SURFACE = "cpos"
    CLOSEST_POINT_ON_MESH = "cpom"


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

    DEFAULT: ClassVar["RotateOrder"]


# Set default rotate order from configuration
RotateOrder.DEFAULT = RotateOrder[SETTINGS.get("rotate_order_default", "xyz").upper()]


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

    AIM: ClassVar["Axis"]
    UP: ClassVar["Axis"]
    SIDE: ClassVar["Axis"]
    DEFAULT: ClassVar["Axis"]


# Set default axis system from configuration
Axis.AIM = Axis(SETTINGS.get("axis_aim", "X"))
Axis.UP = Axis(SETTINGS.get("axis_up", "Y"))
Axis.SIDE = Axis(SETTINGS.get("axis_side", "Z"))
Axis.DEFAULT = Axis.AIM


class Vector(tuple[int, int, int], Enum):
    """Constants related to vector definitions. Inherits from tuple."""

    X = (1, 0, 0)
    Y = (0, 1, 0)
    Z = (0, 0, 1)


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
    """Constants related to matrix definitions."""

    IDENTITY: tuple[float, ...] = (
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


class ShapeType(str, Enum):
    """Common shape types for control curves."""

    LOCATOR = "locator"
    CIRCLE = "circle"
    SQUARE = "square"
    TRIANGLE = "triangle"
    SPHERE = "sphere"
    CUBE = "cube"
    LINE = "line"
    LOLLIPOP = "lollipop"
    INFO = "info"
    UMBRELLA = "umbrella"
    DUMBBELL = "dumbbell"
    ARROW = "arrow"
    DOUBLEARROW = "doubleArrow"
    TUBE = "tube"
    FK = "fk"
    OCTAGON = "octagon"
    MAIN = "main"
    ROOT = "root"
    WINGS = "wings"
    CHEST = "chest"
    HIPS = "hips"
    PELVIS = "pelvis"
    FOOT = "foot"
    NECK = "neck"
    HEAD = "head"

    DEFAULT: ClassVar["ShapeType"]


# Set default shape type from configuration
ShapeType.DEFAULT = ShapeType(SETTINGS.get("shape_type_default", "circle"))
