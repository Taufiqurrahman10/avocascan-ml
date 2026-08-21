import numpy as np
from PIL import Image, ImageDraw

from app.config import Settings
from app.image_processing import (
    apply_stage2_base_transform,
    standardize_stage2_object_scale,
)


def foreground_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    pixels = np.asarray(image.convert("RGB"))
    ys, xs = np.nonzero(np.min(pixels, axis=2) < 245)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def test_standardize_stage2_object_scale_centers_at_80_percent() -> None:
    source = Image.new("RGB", (360, 640), "white")
    draw = ImageDraw.Draw(source)
    draw.ellipse((30, 180, 180, 500), fill=(30, 110, 45))

    settings = Settings()
    result = standardize_stage2_object_scale(source, settings)
    left, top, right, bottom = foreground_bbox(result)
    bbox_width = right - left
    bbox_height = bottom - top
    occupancy = max(
        bbox_width / settings.stage2_canvas_width,
        bbox_height / settings.stage2_canvas_height,
    )

    assert result.size == (1200, 1600)
    assert abs(occupancy - 0.80) <= 0.005
    assert abs((left + right) / 2 - settings.stage2_canvas_width / 2) <= 2
    assert abs((top + bottom) / 2 - settings.stage2_canvas_height / 2) <= 2


def test_standardize_stage2_object_scale_preserves_aspect_ratio() -> None:
    source = Image.new("RGB", (800, 500), "white")
    draw = ImageDraw.Draw(source)
    draw.rectangle((100, 150, 700, 350), fill=(75, 35, 20))
    source_bbox = foreground_bbox(source)
    source_ratio = (
        (source_bbox[2] - source_bbox[0]) / (source_bbox[3] - source_bbox[1])
    )

    result = standardize_stage2_object_scale(source, Settings())
    result_bbox = foreground_bbox(result)
    result_ratio = (
        (result_bbox[2] - result_bbox[0]) / (result_bbox[3] - result_bbox[1])
    )

    assert abs(result_ratio - source_ratio) / source_ratio <= 0.01


def test_stage2_model_transform_still_outputs_224_square() -> None:
    source = Image.new("RGB", (500, 900), "white")
    draw = ImageDraw.Draw(source)
    draw.ellipse((120, 200, 420, 750), fill=(40, 130, 50))

    standardized = standardize_stage2_object_scale(source, Settings())
    transformed = apply_stage2_base_transform(standardized, Settings())

    assert standardized.size == (1200, 1600)
    assert transformed.size == (224, 224)
