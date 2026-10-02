"""Import reviewed photographs and produce local, responsive variants.

python scripts/images/build_feature_assets.py
Requires Pillow. Only this opt-in maintenance command downloads source photos;
the application never contacts a stock photo host. Source crops remain natural:
no compositing, generative editing, filters or colour grading are applied.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tempfile
import urllib.request

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "frontend/public/assets/images"
CACHE = ROOT / ".image-work"


def source_bytes(source):
    cached = CACHE / f"{source['id']}.jpg"
    if cached.exists():
        return cached.read_bytes()
    # Reuse the crop importer's original download, never a recompressed derivative.
    crop_cache = Path(tempfile.gettempdir()) / "krishi-sahayak-crop-import"
    crop_original = crop_cache / hashlib.sha256(source["downloadUrl"].encode()).hexdigest()
    if crop_original.exists():
        content = crop_original.read_bytes()
    else:
        request = urllib.request.Request(source["downloadUrl"], headers={
            "User-Agent": "KrishiSahayakAssetImporter/1.0 (licensed local image library)"
        })
        with urllib.request.urlopen(request, timeout=45) as response:
            content = response.read()
    cached.write_bytes(content)
    return content


def main():
    CACHE.mkdir(exist_ok=True)
    sources = json.loads(Path(__file__).with_name("feature_sources.json").read_text(encoding="utf-8"))
    records = []
    for source in sources:
        content = source_bytes(source)
        image = ImageOps.exif_transpose(Image.open(io.BytesIO(content))).convert("RGB")
        for variant in source["variants"]:
            width, height = variant["width"], variant["height"]
            if image.width < width or image.height < height:
                raise ValueError(f"Source too small for {variant['file']}: {image.size}")
            cover = ImageOps.fit(image, (width, height), method=Image.Resampling.LANCZOS,
                                 centering=tuple(variant.get("centering", [0.5, 0.5])))
            base = ASSETS / variant["file"]
            base.parent.mkdir(parents=True, exist_ok=True)
            files = []
            for size in [400, 800, width]:
                suffix = "" if size == width else f"-{size}"
                path = base.with_name(base.name + suffix).with_suffix(".webp")
                cover.resize((size, round(size * height / width)), Image.Resampling.LANCZOS).save(
                    path, "WEBP", quality=78, method=6)
                files.append(path.relative_to(ASSETS).as_posix())
            cover.save(base.with_suffix(".jpg"), "JPEG", quality=80, optimize=True, progressive=True)
            files.append(base.with_suffix(".jpg").relative_to(ASSETS).as_posix())
            records.append({**{key: value for key, value in source.items() if key not in ("variants", "id")},
                            **variant, "files": files, "reviewedOn": "2026-10-02",
                            "sourceSha256": hashlib.sha256(content).hexdigest(),
                            "notes": "Cropped to the recorded aspect ratio; resized to 400/800/maximum width; WebP quality 78 and progressive JPEG quality 80; EXIF stripped. No generative edits."})
            print(f"Prepared {variant['file']}", flush=True)
    (ASSETS / "feature-sources.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
