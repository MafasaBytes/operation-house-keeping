"""Hand-authored golden expectations for step_assembly.step.

Independent oracle: these values are written from the intended assembly
design (see FIXTURES.md) and the manual Part 21 inspection of the frozen
file. They are NOT produced by the fixture generator or the extractor.
"""

import math

COS30 = math.cos(math.radians(30.0))
SIN30 = math.sin(math.radians(30.0))

EXPECTED_SCHEMAS = ["AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }"]

# definition name -> is_assembly
EXPECTED_DEFINITIONS = {
    "demo-unit": True,
    "bracket-sub": True,
    "base-plate": False,
    "bracket-plate": False,
    "bolt-m6": False,
}

# occurrence name -> (definition name, parent definition name, translation xyz)
EXPECTED_OCCURRENCES = {
    "base-1": ("base-plate", "demo-unit", (0.0, 0.0, 0.0)),
    "bracket-A": ("bracket-sub", "demo-unit", (20.0, 15.0, 6.0)),
    "plate-1": ("bracket-plate", "bracket-sub", (0.0, 0.0, 0.0)),
    "bolt-front": ("bolt-m6", "bracket-sub", (5.0, 5.0, 4.0)),
    "bolt-rear": ("bolt-m6", "bracket-sub", (25.0, 15.0, 4.0)),
}

# bracket-A carries a +30 degree rotation about Z: rows 0 and 1 of the
# rotation block are (cos -sin 0) and (sin cos 0).
EXPECTED_BRACKET_A_ROTATION = {
    (0, 0): COS30,
    (0, 1): -SIN30,
    (1, 0): SIN30,
    (1, 1): COS30,
    (2, 2): 1.0,
}

EXPECTED_LENGTH_UNIT = "millimetre"
EXPECTED_ROOT_DEFINITION = "demo-unit"
EXPECTED_INSTANCE_COUNT = 6  # 5 occurrences + 1 synthesized root
EXPECTED_MESH_NODE_COUNT = 4  # base-1, plate-1, bolt-front, bolt-rear
