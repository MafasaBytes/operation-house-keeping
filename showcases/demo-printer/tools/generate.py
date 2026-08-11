"""One-time generator for the frozen SN-001 showcase STEP source.

Run manually with the CAD extra installed:

    .venv/bin/python showcases/demo-printer/tools/generate.py

Synthetic showcase evidence; represents no real machine. The frozen file
in `../sources/` is canonical: STEP embeds a FILE_NAME timestamp, so
regenerated output is byte-different and must never silently replace it.
The golden expectations are hand-authored in
tests/structural_evidence/golden_showcase.py from ../SOURCES.md — never
from this script (independent-oracle rule). This script is never imported
by a test.

Design intent encoded here (mirrored by SOURCES.md):

    printer-assembly (root assembly)
      extruder-1    -> extruder-unit   box 40 x 30 x 45 mm at (120, 40, 20)
      gantry-left   -> gantry-sub      subassembly          at (0, 0, 200)
      gantry-right  -> gantry-sub      subassembly          at (300, 0, 200)
        idler-front -> idler-wheel     cyl r8 x 6 mm        at (10, 5, 0)
        idler-rear  -> idler-wheel     cyl r8 x 6 mm        at (90, 5, 0)
      fan-1         -> hotend-fan      box 30 x 30 x 10 mm  at (125, 35, 70)

gantry-sub is used TWICE deliberately, so the idler usages have a parent
definition with two uses (derived-path ambiguity). No view metadata is
written anywhere. Units: millimetres, AP214IS.
"""

from pathlib import Path

from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Trsf, gp_Vec
from OCP.IFSelect import IFSelect_ReturnStatus
from OCP.Interface import Interface_Static
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_StepModelType
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDocStd import TDocStd_Document
from OCP.TopLoc import TopLoc_Location
from OCP.XCAFDoc import XCAFDoc_DocumentTool

SOURCES_DIR = Path(__file__).resolve().parent.parent / "sources"


def set_name(label, name: str) -> None:
    TDataStd_Name.Set_s(label, TCollection_ExtendedString(name))


def at(x: float, y: float, z: float) -> TopLoc_Location:
    trsf = gp_Trsf()
    trsf.SetTranslationPart(gp_Vec(x, y, z))
    return TopLoc_Location(trsf)


def generate(path: Path) -> None:
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    shapes = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())

    l_extruder = shapes.AddShape(
        BRepPrimAPI_MakeBox(40.0, 30.0, 45.0).Shape(), False)
    set_name(l_extruder, "extruder-unit")
    l_idler = shapes.AddShape(
        BRepPrimAPI_MakeCylinder(8.0, 6.0).Shape(), False)
    set_name(l_idler, "idler-wheel")
    l_fan = shapes.AddShape(
        BRepPrimAPI_MakeBox(30.0, 30.0, 10.0).Shape(), False)
    set_name(l_fan, "hotend-fan")

    gantry = shapes.NewShape()
    set_name(gantry, "gantry-sub")
    set_name(shapes.AddComponent(gantry, l_idler, at(10, 5, 0)),
             "idler-front")
    set_name(shapes.AddComponent(gantry, l_idler, at(90, 5, 0)),
             "idler-rear")

    root = shapes.NewShape()
    set_name(root, "printer-assembly")
    set_name(shapes.AddComponent(root, l_extruder, at(120, 40, 20)),
             "extruder-1")
    set_name(shapes.AddComponent(root, gantry, at(0, 0, 200)),
             "gantry-left")
    set_name(shapes.AddComponent(root, gantry, at(300, 0, 200)),
             "gantry-right")
    set_name(shapes.AddComponent(root, l_fan, at(125, 35, 70)), "fan-1")

    shapes.UpdateAssemblies()
    Interface_Static.SetCVal_s("write.step.schema", "AP214IS")
    writer = STEPCAFControl_Writer()
    writer.Transfer(doc, STEPControl_StepModelType.STEPControl_AsIs)
    status = writer.Write(str(path))
    assert status == IFSelect_ReturnStatus.IFSelect_RetDone, status
    print(f"wrote {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    generate(SOURCES_DIR / "printer_assembly.step")
