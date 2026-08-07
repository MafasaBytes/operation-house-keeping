"""One-time generator for the frozen PDF fixtures.

Run manually with the PDF extra installed (pypdf is needed only for the
encrypted and active-content fixtures):

    .venv/bin/python backend/data_sources/testing/fixtures/generators/generate_pdf_fixtures.py

The frozen files are canonical; this script documents their origin. The
golden expectations live in tests/data_sources/golden_pdf_fixtures.py and
are hand-authored from the DESIGNED coordinates below — deliberately not
produced by any extractor (independent-oracle rule).

How xref offsets are produced: `build_pdf` serializes objects 1..N in
order, records the byte offset of each `N 0 obj` header, then emits a
classic xref table with those offsets and a trailer pointing at the xref
position. Everything is fixed content, so output bytes are deterministic
(except the pypdf-encrypted fixture, which is frozen precisely because
AES salts make regeneration byte-different).

Designed content (the oracle source of truth):

  manual_multipage.pdf  3 pages 612x792, labels i / 1 / 2
    p0: "OPERATION MANUAL" Helv 14 at baseline (72, 720)
        "Revision 2"       Helv 10 at (72, 700)
    p1: "TORQUE SPEC 45 Nm" Helv 12 at (72, 720)
        "BOLT M6"           Helv 10 at (200, 400)
        line (72,100) -> (300,100)
    p2: "SERVICE PROCEDURE"      Helv 12 at (72, 720)
        "Step 1: remove bracket" Helv 10 at (72, 690)

  table_page.pdf  ruled 3x3 grid: verticals x = 72,222,372,522;
    horizontals y = 510,540,570,600; header baseline y=580, rows 550/520;
    column text x = 77/227/377; cells:
      ITEM NO | QTY | UNIT
      100-002 |  8  | piece
      100-003 |  8  | piece

  drawing_callouts.pdf  rect (100,500)+200x100; leader line
    (300,550)->(380,600); callouts Helv 8 "BRACKET-A" at (385,600),
    "SEE DETAIL B" at (385,585)

  scanned_only.pdf   64x64 RGB gradient image drawn at (100,300) size
    400x400; zero text objects
  mixed_text_image.pdf  same image at (150,400) size 300x300 plus
    "FIGURE 3-1 Hydraulic pump" Helv 12 at (72, 720)
  rotated_page.pdf   /Rotate 90, "ROTATED DRAWING" Helv 12 at (72, 720)
  malformed.pdf      manual_multipage truncated to 60%
  encrypted.pdf      manual_multipage encrypted AES-256, user password
                     "fixture-password-2026" (published test vector, not a
                     credential)
  active_content.pdf one page "ACTIVE CONTENT TEST" plus a JavaScript
                     name-tree entry, an /A /URI link annotation to
                     http://example.invalid/manual, and an embedded file
                     notes.txt — declarations only, never executed
"""

import zlib
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent.parent


def build_pdf(objects: list[bytes], header: bytes = b"%PDF-1.4\n") -> bytes:
    out = bytearray(header)
    offsets = []
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode() + body + b"\nendobj\n"
    xref_pos = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode()
    return bytes(out)


def stream_obj(dict_body: bytes, stream: bytes) -> bytes:
    return (
        b"<< " + dict_body + b" /Length " + str(len(stream)).encode() + b" >>\n"
        b"stream\n" + stream + b"\nendstream"
    )


def content_obj(content: bytes) -> bytes:
    return stream_obj(b"", content)


HELVETICA = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"


def text(x: float, y: float, size: float, string: str) -> bytes:
    escaped = string.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")
    return f"BT /F1 {size:g} Tf {x:g} {y:g} Td ({escaped}) Tj ET\n".encode()


def gradient_image_obj() -> bytes:
    raw = bytearray()
    for y in range(64):
        for x in range(64):
            raw += bytes(((x * 4) % 256, (y * 4) % 256, 128))
    data = zlib.compress(bytes(raw), 9)
    return stream_obj(
        b"/Type /XObject /Subtype /Image /Width 64 /Height 64 "
        b"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode",
        data,
    )


def generate_manual() -> bytes:
    contents = [
        text(72, 720, 14, "OPERATION MANUAL") + text(72, 700, 10, "Revision 2"),
        text(72, 720, 12, "TORQUE SPEC 45 Nm")
        + text(200, 400, 10, "BOLT M6")
        + b"72 100 m 300 100 l S\n",
        text(72, 720, 12, "SERVICE PROCEDURE")
        + text(72, 690, 10, "Step 1: remove bracket"),
    ]
    page_refs = b"[3 0 R 4 0 R 5 0 R]"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R /PageLabels << /Nums "
        b"[0 << /S /r >> 1 << /S /D /St 1 >>] >> >>",
        b"<< /Type /Pages /Kids " + page_refs + b" /Count 3 >>",
    ]
    for i in range(3):
        objects.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 6 0 R >> >> /Contents "
            + str(7 + i).encode() + b" 0 R >>"
        )
    objects.append(HELVETICA)
    objects.extend(content_obj(c) for c in contents)
    return build_pdf(objects)


def one_page_pdf(content: bytes, page_extra: bytes = b"", resources: bytes | None = None,
                 extra_objects: list[bytes] | None = None) -> bytes:
    resources = resources if resources is not None else b"<< /Font << /F1 4 0 R >> >>"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources "
        + resources + b" /Contents 5 0 R " + page_extra + b">>",
        HELVETICA,
        content_obj(content),
    ]
    objects.extend(extra_objects or [])
    return build_pdf(objects)


def generate_table() -> bytes:
    content = bytearray()
    for x in (72, 222, 372, 522):
        content += f"{x} 510 m {x} 600 l S\n".encode()
    for y in (510, 540, 570, 600):
        content += f"72 {y} m 522 {y} l S\n".encode()
    rows = [
        (580, ["ITEM NO", "QTY", "UNIT"]),
        (550, ["100-002", "8", "piece"]),
        (520, ["100-003", "8", "piece"]),
    ]
    for y, cells in rows:
        for x, value in zip((77, 227, 377), cells):
            content += text(x, y, 10, value)
    return one_page_pdf(bytes(content))


def generate_drawing() -> bytes:
    content = (
        b"100 500 200 100 re S\n"
        b"300 550 m 380 600 l S\n"
        + text(385, 600, 8, "BRACKET-A")
        + text(385, 585, 8, "SEE DETAIL B")
    )
    return one_page_pdf(content)


def generate_scanned_only() -> bytes:
    content = b"q 400 0 0 400 100 300 cm /Im1 Do Q\n"
    return one_page_pdf(
        content,
        resources=b"<< /XObject << /Im1 6 0 R >> >>",
        extra_objects=[gradient_image_obj()],
    )


def generate_mixed() -> bytes:
    content = (
        text(72, 720, 12, "FIGURE 3-1 Hydraulic pump")
        + b"q 300 0 0 300 150 400 cm /Im1 Do Q\n"
    )
    return one_page_pdf(
        content,
        resources=b"<< /Font << /F1 4 0 R >> /XObject << /Im1 6 0 R >> >>",
        extra_objects=[gradient_image_obj()],
    )


def generate_rotated() -> bytes:
    return one_page_pdf(text(72, 720, 12, "ROTATED DRAWING"), page_extra=b"/Rotate 90 ")


def generate_rotated_cropbox() -> bytes:
    """Rotation combined with an offset CropBox, plus a link annotation.

    Designed raw (unrotated user-space) content:
      MediaBox [0 0 612 792], CropBox [50 40 562 742], /Rotate 90
      text "CROPPED ROTATED" Helv 12 at raw baseline (72, 700)
      Link annotation /Rect [100 600 200 640] -> http://example.invalid/detail
    Expected canonical (CropBox-relative, displayed): page 702 x 512;
      x' = y_raw - 40, y' = x_raw - 50 for /Rotate 90.
    """
    return build_pdf([
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/CropBox [50 40 562 742] /Rotate 90 "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R "
        b"/Annots [6 0 R] >>",
        HELVETICA,
        content_obj(text(72, 700, 12, "CROPPED ROTATED")),
        b"<< /Type /Annot /Subtype /Link /Rect [100 600 200 640] "
        b"/A << /S /URI /URI (http://example.invalid/detail) >> >>",
    ])


def generate_encrypted(source: bytes, path: Path) -> None:
    import io

    import pypdf

    reader = pypdf.PdfReader(io.BytesIO(source))
    writer = pypdf.PdfWriter()
    writer.append(reader)
    writer.encrypt(user_password="fixture-password-2026", algorithm="AES-256")
    with open(path, "wb") as fh:
        writer.write(fh)


def generate_active_content(path: Path) -> None:
    import io

    import pypdf
    from pypdf.generic import (
        ArrayObject, DictionaryObject, NameObject, NumberObject, TextStringObject,
    )

    base = one_page_pdf(text(72, 720, 12, "ACTIVE CONTENT TEST"))
    reader = pypdf.PdfReader(io.BytesIO(base))
    writer = pypdf.PdfWriter()
    writer.append(reader)
    writer.add_js("app.alert('fixture: never executed');")
    writer.add_attachment("notes.txt", b"embedded fixture attachment body")
    page = writer.pages[0]
    annotation = DictionaryObject({
        NameObject("/Type"): NameObject("/Annot"),
        NameObject("/Subtype"): NameObject("/Link"),
        NameObject("/Rect"): ArrayObject(
            [NumberObject(72), NumberObject(60), NumberObject(220), NumberObject(80)]
        ),
        NameObject("/A"): DictionaryObject({
            NameObject("/S"): NameObject("/URI"),
            NameObject("/URI"): TextStringObject("http://example.invalid/manual"),
        }),
    })
    page[NameObject("/Annots")] = ArrayObject([writer._add_object(annotation)])
    with open(path, "wb") as fh:
        writer.write(fh)


if __name__ == "__main__":
    manual = generate_manual()
    outputs = {
        "manual_multipage.pdf": manual,
        "table_page.pdf": generate_table(),
        "drawing_callouts.pdf": generate_drawing(),
        "scanned_only.pdf": generate_scanned_only(),
        "mixed_text_image.pdf": generate_mixed(),
        "rotated_page.pdf": generate_rotated(),
        "malformed.pdf": manual[: int(len(manual) * 0.6)],
    }
    for name, data in outputs.items():
        (FIXTURES_DIR / name).write_bytes(data)
        print(f"wrote {name} ({len(data)} bytes)")
    generate_encrypted(manual, FIXTURES_DIR / "encrypted.pdf")
    print("wrote encrypted.pdf")
    generate_active_content(FIXTURES_DIR / "active_content.pdf")
    print("wrote active_content.pdf")
