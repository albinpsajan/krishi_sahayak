"""Offline validation for the deployable photo library and its credit coverage."""
import json
from pathlib import Path
import re

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "frontend/public/assets/images"


def main():
    records = []
    for name in ("feature-sources.json", "crop-sources.json"):
        records.extend(json.loads((ASSETS / name).read_text(encoding="utf-8")))
    expected, ids, total = set(), set(), 0
    credits = (ASSETS / "README_IMAGE_CREDITS.md").read_text(encoding="utf-8")
    for record in records:
        assert record['id'] not in ids, f"Duplicate asset id: {record['id']}"
        ids.add(record['id'])
        for key in ('source', 'originalUrl', 'author', 'license', 'licenseUrl', 'usedIn', 'notes'):
            assert record.get(key), f"Missing {key}: {record['id']}"
        assert record['originalUrl'] in credits and record['author'] in credits
        for name in record['files']:
            path = (ASSETS / name).resolve()
            assert path.is_relative_to(ASSETS.resolve()), f"Path outside assets: {name}"
            expected.add(path)
            assert path.exists(), f"Missing file: {name}"
            assert name in credits, f"Missing credit: {name}"
            size = path.stat().st_size
            assert size <= 400_000, f"Photo exceeds 400KB budget: {name}: {size}"
            total += size
            with Image.open(path) as photo:
                photo.load()
                suffix = re.search(r'-(400|800)$', path.stem)
                width = int(suffix[1]) if suffix else record['width']
                assert photo.width == width, f"Incorrect width: {name}"
                assert photo.height == round(width * record['height'] / record['width']), name
                assert not photo.getexif(), f"Unexpected EXIF retained: {name}"
    actual = {p.resolve() for p in ASSETS.rglob('*') if p.suffix in ('.webp', '.jpg', '.png')}
    assert expected == actual, f"Uncredited/extra photos: {actual - expected}"
    # Stock photo sources belong only in attribution/import manifests. Existing
    # satellite tiles, uploads and external data sources are separate integrations.
    for file in (ROOT / 'frontend/src').rglob('*'):
        if file.suffix in ('.js', '.jsx', '.css'):
            assert not re.search(r'https?://(?:images\.unsplash\.com|images\.pexels\.com|upload\.wikimedia\.org)',
                                 file.read_text(encoding='utf-8')), f"Remote stock image in UI: {file}"
    print(f"Validated {len(records)} assets / {len(expected)} files; {total:,} bytes total. All files credited, decoded, sized and local.")


if __name__ == '__main__':
    main()
