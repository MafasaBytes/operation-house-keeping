"""Unit tests for the PDF coordinate transforms (pure math, no closure).

Conventions under test (documented in the module): six-element affine
[a, b, c, d, e, f] applied as x' = a*x + b*y + e ; y' = c*x + d*y + f.
Raw source space is unrotated PDF user space (y-up, box offsets included);
canonical space is the displayed box-relative top-left/y-down frame.
"""

import pytest

from backend.data_sources.contracts import ExtractionError
from backend.data_sources.extractors.pdf.coordinates import (
    apply_affine,
    canonical_page_size,
    forward_matrix,
    inverse_matrix,
    normalize_rotation,
    transform_bbox,
)

MEDIA = (0.0, 0.0, 612.0, 792.0)
CROP = (50.0, 40.0, 562.0, 742.0)


class TestRotationValidation:
    def test_multiples_of_90_normalize(self):
        assert normalize_rotation(0) == 0
        assert normalize_rotation(450) == 90
        assert normalize_rotation(-90) == 270

    def test_unsupported_rotation_rejected(self):
        with pytest.raises(ExtractionError) as excinfo:
            normalize_rotation(45)
        assert excinfo.value.error_code == "EXTRACT_PDF_UNSUPPORTED_ROTATION"


class TestForwardMappings:
    """Raw corner points mapped to their designed displayed positions."""

    def test_rot0_with_offset_box(self):
        m = forward_matrix(0, CROP)
        # raw box top-left corner (cx0, cy1) is the displayed origin
        assert apply_affine(m, 50.0, 742.0) == pytest.approx((0.0, 0.0))
        assert apply_affine(m, 562.0, 40.0) == pytest.approx((512.0, 702.0))
        assert canonical_page_size(0, CROP) == (512.0, 702.0)

    def test_rot90_with_offset_box(self):
        m = forward_matrix(90, CROP)
        # raw bottom-left corner (cx0, cy0) becomes the displayed top-left
        assert apply_affine(m, 50.0, 40.0) == pytest.approx((0.0, 0.0))
        assert apply_affine(m, 50.0, 742.0) == pytest.approx((702.0, 0.0))
        assert canonical_page_size(90, CROP) == (702.0, 512.0)

    def test_rot180_with_offset_box(self):
        m = forward_matrix(180, CROP)
        # raw bottom-right corner becomes the displayed top-left
        assert apply_affine(m, 562.0, 40.0) == pytest.approx((0.0, 0.0))
        assert canonical_page_size(180, CROP) == (512.0, 702.0)

    def test_rot270_with_offset_box(self):
        m = forward_matrix(270, CROP)
        # raw top-right corner becomes the displayed top-left
        assert apply_affine(m, 562.0, 742.0) == pytest.approx((0.0, 0.0))
        assert canonical_page_size(270, CROP) == (702.0, 512.0)


class TestRoundTrip:
    @pytest.mark.parametrize("rotation", [0, 90, 180, 270])
    @pytest.mark.parametrize("box", [MEDIA, CROP])
    def test_forward_then_inverse_is_identity(self, rotation, box):
        forward = forward_matrix(rotation, box)
        inverse = inverse_matrix(rotation, box)
        for point in [(72.0, 720.0), (50.0, 40.0), (561.9, 741.9), (300.123, 456.789)]:
            canon = apply_affine(forward, *point)
            back = apply_affine(inverse, *canon)
            assert back == pytest.approx(point, abs=1e-9)

    @pytest.mark.parametrize("rotation", [0, 90, 180, 270])
    def test_bbox_transform_normalizes_axis_aligned(self, rotation):
        forward = forward_matrix(rotation, CROP)
        bbox = transform_bbox(forward, [72.0, 697.5, 130.0, 709.5])
        assert bbox[0] <= bbox[2] and bbox[1] <= bbox[3]
        inverse = inverse_matrix(rotation, CROP)
        back = transform_bbox(inverse, bbox)
        assert back == pytest.approx([72.0, 697.5, 130.0, 709.5], abs=1e-9)


class TestAgainstPdfplumberObservations:
    """Values observed from pdfplumber on generated probes (MediaBox frame)."""

    def test_rot90_media_matches_pdfplumber(self):
        # raw glyph bbox for baseline (72, 720) at 12pt: y in [717.516, 729.516]
        m = forward_matrix(90, MEDIA)
        bbox = transform_bbox(m, [72.0, 717.516, 114.012, 729.516])
        assert bbox == pytest.approx([717.516, 72.0, 729.516, 114.012], abs=1e-6)

    def test_rot180_media_matches_pdfplumber(self):
        m = forward_matrix(180, MEDIA)
        bbox = transform_bbox(m, [72.0, 717.516, 114.012, 729.516])
        assert bbox == pytest.approx([497.988, 717.516, 540.0, 729.516], abs=1e-6)

    def test_rot270_media_matches_pdfplumber(self):
        m = forward_matrix(270, MEDIA)
        bbox = transform_bbox(m, [72.0, 717.516, 114.012, 729.516])
        assert bbox == pytest.approx([62.484, 497.988, 74.484, 540.0], abs=1e-6)
