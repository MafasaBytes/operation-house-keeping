"""PDF coordinate transforms between raw user space and displayed frames.

Definitions:

- **Raw source space**: unrotated PDF user space — x right, y up, absolute
  coordinates including box offsets (a CropBox need not start at 0,0).
- **Canonical space**: the *displayed* box-relative frame — top-left
  origin, y downward, pdf points — after applying the page /Rotate value
  (clockwise, multiples of 90).

Six-element affine convention ``[a, b, c, d, e, f]``, applied as::

    x' = a*x + b*y + e
    y' = c*x + d*y + f

i.e. row-per-output-component; there is no implicit matrix multiplication
order beyond this single application. All four bbox corners are
transformed and the result normalized to an axis-aligned bbox.

Forward matrices (raw → canonical) for a box ``(bx0, by0, bx1, by1)``::

    rot 0:   x' =  x - bx0        y' = by1 - y
    rot 90:  x' =  y - by0        y' =  x - bx0
    rot 180: x' = bx1 - x         y' =  y - by0
    rot 270: x' = by1 - y         y' = bx1 - x

Derived and verified empirically against pdfplumber's displayed
coordinates (which use this mapping with the MediaBox as the box).
"""

from backend.data_sources.contracts import ExtractionError

SUPPORTED_ROTATIONS = (0, 90, 180, 270)

Box = tuple[float, float, float, float]
Affine = list[float]


def normalize_rotation(rotation: int) -> int:
    """Validate and normalize a /Rotate value.

    The PDF specification only permits multiples of 90; anything else is
    rejected explicitly rather than silently normalized to a wrong frame.
    Negative multiples are normalized into [0, 360).
    """
    if rotation % 90 != 0:
        raise ExtractionError(
            "EXTRACT_PDF_UNSUPPORTED_ROTATION",
            f"page /Rotate value {rotation} is not a multiple of 90 and "
            "cannot be displayed-normalized honestly",
        )
    return rotation % 360


def forward_matrix(rotation: int, box: Box) -> Affine:
    bx0, by0, bx1, by1 = box
    rotation = normalize_rotation(rotation)
    if rotation == 0:
        return [1.0, 0.0, 0.0, -1.0, -bx0, by1]
    if rotation == 90:
        return [0.0, 1.0, 1.0, 0.0, -by0, -bx0]
    if rotation == 180:
        return [-1.0, 0.0, 0.0, 1.0, bx1, -by0]
    return [0.0, -1.0, -1.0, 0.0, by1, bx1]  # 270


def inverse_matrix(rotation: int, box: Box) -> Affine:
    bx0, by0, bx1, by1 = box
    rotation = normalize_rotation(rotation)
    if rotation == 0:
        return [1.0, 0.0, 0.0, -1.0, bx0, by1]
    if rotation == 90:
        return [0.0, 1.0, 1.0, 0.0, bx0, by0]
    if rotation == 180:
        return [-1.0, 0.0, 0.0, 1.0, bx1, by0]
    return [0.0, -1.0, -1.0, 0.0, bx1, by1]  # 270


def apply_affine(matrix: Affine, x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = matrix
    return (a * x + b * y + e, c * x + d * y + f)


def transform_bbox(matrix: Affine, bbox: list[float]) -> list[float]:
    """Transform all four corners and normalize to an axis-aligned bbox."""
    x0, y0, x1, y1 = bbox
    corners = [
        apply_affine(matrix, x0, y0),
        apply_affine(matrix, x0, y1),
        apply_affine(matrix, x1, y0),
        apply_affine(matrix, x1, y1),
    ]
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    return [min(xs), min(ys), max(xs), max(ys)]


def canonical_page_size(rotation: int, box: Box) -> tuple[float, float]:
    bx0, by0, bx1, by1 = box
    width, height = bx1 - bx0, by1 - by0
    if normalize_rotation(rotation) in (90, 270):
        return (height, width)
    return (width, height)
