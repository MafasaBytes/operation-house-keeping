"""One-time generator for the frozen STEP fixtures.

Run manually with the CAD extra installed:

    .venv/bin/python backend/data_sources/testing/fixtures/generators/generate_step_fixtures.py

The frozen files in the parent directory are the canonical fixtures; this
script is documentation of their origin (see FIXTURES.md). Re-running it
produces semantically identical but byte-different files (STEP embeds a
FILE_NAME timestamp), so regenerated output must never silently replace the
frozen fixtures. The golden test expectations are hand-authored in
tests/data_sources/golden_step_assembly.py and are deliberately NOT
produced by this script (independent-oracle rule).

Design intent encoded here (and mirrored by the hand-authored oracle):

    demo-unit (root assembly)
      base-1      -> base-plate     box 80 x 60 x 6 mm      at (0, 0, 0)
      bracket-A   -> bracket-sub    subassembly              at (20, 15, 6),
                                    rotated +30 deg about Z
        plate-1     -> bracket-plate box 30 x 20 x 4 mm     at (0, 0, 0)
        bolt-front  -> bolt-m6      cylinder r3 x 12 mm     at (5, 5, 4)
        bolt-rear   -> bolt-m6      cylinder r3 x 12 mm     at (25, 15, 4)

Units: millimetres, written explicitly by the AP214IS writer.
"""

import math
from pathlib import Path

from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.gp import gp_Ax1, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from OCP.IFSelect import IFSelect_ReturnStatus
from OCP.Interface import Interface_Static
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_StepModelType
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
from OCP.TDocStd import TDocStd_Document
from OCP.TopLoc import TopLoc_Location
from OCP.XCAFDoc import XCAFDoc_DocumentTool

FIXTURES_DIR = Path(__file__).resolve().parent.parent


def set_name(label, name: str) -> None:
    TDataStd_Name.Set_s(label, TCollection_ExtendedString(name))


def location(x: float, y: float, z: float, rot_z_deg: float = 0.0) -> TopLoc_Location:
    trsf = gp_Trsf()
    if rot_z_deg:
        trsf.SetRotation(
            gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.radians(rot_z_deg)
        )
    trsf.SetTranslationPart(gp_Vec(x, y, z))
    return TopLoc_Location(trsf)


def write_step(doc, path: Path) -> None:
    Interface_Static.SetCVal_s("write.step.schema", "AP214IS")
    writer = STEPCAFControl_Writer()
    writer.Transfer(doc, STEPControl_StepModelType.STEPControl_AsIs)
    status = writer.Write(str(path))
    assert status == IFSelect_ReturnStatus.IFSelect_RetDone, status
    print(f"wrote {path} ({path.stat().st_size} bytes)")


def generate_assembly(path: Path) -> None:
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    shapes = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())

    l_base = shapes.AddShape(BRepPrimAPI_MakeBox(80.0, 60.0, 6.0).Shape(), False)
    set_name(l_base, "base-plate")
    l_plate = shapes.AddShape(BRepPrimAPI_MakeBox(30.0, 20.0, 4.0).Shape(), False)
    set_name(l_plate, "bracket-plate")
    l_bolt = shapes.AddShape(BRepPrimAPI_MakeCylinder(3.0, 12.0).Shape(), False)
    set_name(l_bolt, "bolt-m6")

    sub = shapes.NewShape()
    set_name(sub, "bracket-sub")
    set_name(shapes.AddComponent(sub, l_plate, location(0, 0, 0)), "plate-1")
    set_name(shapes.AddComponent(sub, l_bolt, location(5, 5, 4)), "bolt-front")
    set_name(shapes.AddComponent(sub, l_bolt, location(25, 15, 4)), "bolt-rear")

    root = shapes.NewShape()
    set_name(root, "demo-unit")
    set_name(shapes.AddComponent(root, l_base, location(0, 0, 0)), "base-1")
    set_name(
        shapes.AddComponent(root, sub, location(20, 15, 6, rot_z_deg=30.0)),
        "bracket-A",
    )

    shapes.UpdateAssemblies()
    write_step(doc, path)


def generate_part_only(path: Path) -> None:
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    shapes = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    label = shapes.AddShape(BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape(), False)
    set_name(label, "lone-cube")
    shapes.UpdateAssemblies()
    write_step(doc, path)


def generate_corrupted(source: Path, path: Path) -> None:
    data = source.read_bytes()
    cut = int(len(data) * 0.6)
    path.write_bytes(data[:cut])  # valid header, DATA section truncated mid-entity
    print(f"wrote {path} ({path.stat().st_size} bytes, truncated at {cut})")


def generate_masquerade(path: Path) -> None:
    ole_magic = bytes.fromhex("d0cf11e0a1b11ae1")
    path.write_bytes(ole_magic + b"\x00" * 504)
    print(f"wrote {path} (fake OLE container under a .step name)")


if __name__ == "__main__":
    assembly = FIXTURES_DIR / "step_assembly.step"
    generate_assembly(assembly)
    generate_part_only(FIXTURES_DIR / "step_part_only.step")
    generate_corrupted(assembly, FIXTURES_DIR / "step_corrupted.step")
    generate_masquerade(FIXTURES_DIR / "native_cad_masquerade.step")
