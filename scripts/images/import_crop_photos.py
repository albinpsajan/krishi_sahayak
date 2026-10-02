"""Rebuild the six local crop-photo variants from reviewed Commons sources.

Run from the repository root with Python + Pillow. Downloads are only made by
this maintenance script; the frontend always serves its own local image files.
Source licenses and attribution are retained in crop-sources.json.
The unmodified downloads are cached in the operating-system temporary directory
under krishi-sahayak-crop-import, keyed by SHA-256 of the exact source URL. This
keeps large originals out of the public bundle and makes reruns polite to Commons.
"""

from __future__ import annotations

import html
import io
import json
import hashlib
from pathlib import Path
import re
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "frontend/public/assets/images"
SOURCES = [
    ("banana", "Banana in Kerala.jpg", "Banana fruit growing in Kerala"),
    ("coconut", "Coconut Tree in Kerala.jpg", "Coconut palm in Kavvayi, Kerala"),
    ("paddy", "Kerala PaddyFields.jpg", "Rice paddy fields in Kerala"),
    ("pepper", "Piper nigrum 04236.jpg", "Black pepper growing in Kozhikode, Kerala"),
    ("ginger", "Ginger rhizomes.jpg", "Fresh ginger rhizomes on a table"),
    ("turmeric", "Turmeric rhizomes.jpg", "Turmeric rhizomes with a cut orange centre"),
]
USER_AGENT = "KrishiSahayakAssetImporter/1.0 (local agriculture image library)"


def fetch(url: str) -> bytes:
    cache = Path(tempfile.gettempdir()) / "krishi-sahayak-crop-import"
    cache.mkdir(exist_ok=True)
    cached_file = cache / hashlib.sha256(url.encode()).hexdigest()
    if cached_file.exists():
        return cached_file.read_bytes()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = response.read()
            cached_file.write_bytes(result)
            time.sleep(2)
            return result
        except urllib.error.HTTPError as error:
            if error.code not in (429, 503) or attempt == 3:
                raise
            time.sleep(min(10 * (attempt + 1), 30))
    raise RuntimeError("Download failed")


def plain(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value)).replace(" (talk)", "").strip()


def main() -> None:
    destination = ASSETS / "crops"
    destination.mkdir(parents=True, exist_ok=True)
    records = []
    for crop, title, description in SOURCES:
        query = urllib.parse.urlencode({
            "action": "query", "format": "json", "prop": "imageinfo",
            "iiprop": "url|extmetadata|size", "titles": f"File:{title}",
        })
        response = json.loads(fetch("https://commons.wikimedia.org/w/api.php?" + query))
        page = next(iter(response["query"]["pages"].values()))
        info = page["imageinfo"][0]
        metadata = info["extmetadata"]
        license_name = metadata["LicenseShortName"]["value"]
        allowed = ("CC BY-SA", "CC BY", "CC0", "Public domain")
        if not license_name.startswith(allowed):
            raise ValueError(f"Review required for unexpected license: {license_name}")
        source_url = info["url"].split("?")[0]
        image = ImageOps.exif_transpose(Image.open(io.BytesIO(fetch(source_url)))).convert("RGB")
        if image.width < 800 or image.height < 600:
            raise ValueError(f"Source for {crop} is too small: {image.size}")
        # Exclude peripheral packaging from the ginger photograph; retain roots.
        if crop == "ginger":
            image = image.crop((round(image.width * .10), round(image.height * .13),
                                round(image.width * .90), round(image.height * .90)))
        cover = ImageOps.fit(image, (800, 600), method=Image.Resampling.LANCZOS)
        cover.save(destination / f"{crop}.webp", "WEBP", quality=80, method=6)
        cover.resize((400, 300), Image.Resampling.LANCZOS).save(
            destination / f"{crop}-400.webp", "WEBP", quality=78, method=6,
        )
        cover.save(destination / f"{crop}.jpg", "JPEG", quality=82, optimize=True, progressive=True)
        records.append({
            "id": crop,
            "file": f"crops/{crop}",
            "files": [f"crops/{crop}.webp", f"crops/{crop}-400.webp", f"crops/{crop}.jpg"],
            "source": "Wikimedia Commons",
            "originalUrl": info["descriptionurl"],
            "downloadUrl": source_url,
            "author": plain(metadata["Artist"]["value"]),
            "license": license_name,
            "licenseUrl": metadata.get("LicenseUrl", {}).get("value", info["descriptionurl"] + "#Licensing"),
            "attributionRequired": metadata.get("AttributionRequired", {}).get("value") == "true",
            "description": description,
            "notes": ("Peripheral packaging cropped out. " if crop == "ginger" else "") + "Centre-cropped to 4:3; resized to 800x600 and 400x300; compressed as WebP (quality 80/78) and progressive JPEG (quality 82); embedded metadata removed. No generative editing. CC BY-SA adaptations retain the source license.",
            "width": 800,
            "height": 600,
            "usedIn": "Farm crop cards, dashboard crop strip and selected-crop thumbnails",
        })
        print(f"Prepared {crop}: {license_name}; {plain(metadata['Artist']['value'])}", flush=True)
    (ASSETS / "crop-sources.json").write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
