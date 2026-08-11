"""Hand-authored golden expectations for the SN-001 showcase.

Structure and counts are authored from `showcases/demo-printer/SOURCES.md`
(the designed-structure prose) — never from the generator and never from
the implementation (independent-oracle rule). The upstream hex ids are a
different kind of golden: they are extractor-LOCAL identifiers derived
once by the accepted `derive_entity_id` at freeze time and pinned here as
literals so a toolchain shift fails loudly (A11); they are never
canonical anchors.
"""

BOM_SOURCE_ID = "showcase-printer-bom"
STEP_SOURCE_ID = "showcase-printer-cad"

# ---- from SOURCES.md (design intent) --------------------------------------
EXPECTED_BOM_ROW_COUNT = 6
EXPECTED_BOM_CONTAINMENT = {2: 1, 3: 1, 4: 1, 5: 1, 6: 2}
EXPECTED_DUPLICATE_LABEL_ROWS = (4, 5)          # BRK-400 / BRK-401
EXPECTED_QUANTITY_LEXEMES = {"1", "4", "2"}     # verbatim, never parsed

EXPECTED_STEP_DEFINITION_COUNT = 5
EXPECTED_STEP_USAGE_COUNT = 6                   # + 1 synthesized root = 7
EXPECTED_ASSEMBLY_DEFINITIONS = {"printer-assembly", "gantry-sub"}
EXPECTED_TWICE_USED_DEFINITION = "gantry-sub"   # gantry-left + gantry-right
EXPECTED_AMBIGUOUS_PATH_USAGES = ("idler-front", "idler-rear")
EXPECTED_AMBIGUOUS_PATH_COUNT = 2

# ---- pinned at freeze time (A11: an OCCT shift fails loudly) --------------
STEP_RAW_RECORD_ID = "bf4c84d44f569cd712d9281aa2f8d428"
BOM_RAW_RECORD_ID = "acc5f289912d91be96e52ad8d44580b7"

UPSTREAM_DEFINITION_IDS = {
    "0:1:1:1": "c55e1eaa2228a8538ffd61f7f507f12c",  # printer-assembly
    "0:1:1:2": "27a4c0360d2d01758c50dbb1b486e2db",  # extruder-unit
    "0:1:1:3": "6da1f6ae4f8247897538317014224d13",  # gantry-sub
    "0:1:1:4": "39ad12f8c64e94f64947fb1e737d2c5a",  # idler-wheel
    "0:1:1:5": "59b103c35df6bb2be2c43e0be79d8e0e",  # hotend-fan
}
UPSTREAM_USAGE_IDS = {
    "0:1:1:1:1": "cc9888c62685d48953adfef514339088",  # extruder-1
    "0:1:1:1:2": "d01511cdc9156efeee9e36f0b9a34000",  # gantry-left
    "0:1:1:1:3": "11b95c69789fed35415b544302607dfd",  # gantry-right
    "0:1:1:1:4": "92dacc75188147a88f0006adc1876046",  # fan-1
    "0:1:1:3:1": "83a372955b827e4d6699cf466b9a2bf3",  # idler-front
    "0:1:1:3:2": "382122f9c80ecbd8a3e2359d00dc34c3",  # idler-rear
}
