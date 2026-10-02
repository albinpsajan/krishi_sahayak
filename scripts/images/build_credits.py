"""Generate human-readable attribution from the reviewed asset manifests.

Run after either image importer. Kept dependency-free so updating credits does
not require downloading sources or installing an image processing library.
"""
import html
import json
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[2] / "frontend/public/assets/images"


def main():
    records = []
    for name in ("feature-sources.json", "crop-sources.json"):
        records.extend(json.loads((ASSETS / name).read_text(encoding="utf-8")))
    introduction = (
        "Real documentary photographs, downloaded and reviewed on 2 October 2026. "
        "These images illustrate crops and farming; they are not photographs of the user's farm, "
        "current weather, actual market listings or platform staff. No AI images, composites, "
        "inspiration-site images or externally hosted stock photographs are used in the UI. "
        "Several assets intentionally share an original photograph with different crops."
    )
    markdown = ["# Image credits — Krishi Sahayak", "", introduction, "",
                "All listed variants inherit the stated source license. CC BY-SA adaptations are "
                "distributed under the same CC BY-SA version as their source. This applies to the "
                "photographs, not automatically to the separate application code. Retain these "
                "credits and source/license links when distributing the assets.", "",
                "UI icons remain the existing Lucide React icon set (ISC license); no downloaded "
                "icon pack is required. Localized descriptions are in `src/data/imageAssets.js`.", ""]
    cards = []
    escape = html.escape
    for item in records:
        files = item["files"]
        markdown.extend([
            f"## {item['file']}", "", f"- Image files: {', '.join(f'`{f}`' for f in files)}",
            f"- Source: {item['source']}", f"- Original URL: {item['originalUrl']}",
            f"- Photographer/author: {item['author']}",
            f"- License: [{item['license']}]({item['licenseUrl']})",
            f"- Attribution required: {'Yes' if item['attributionRequired'] else 'No (credited voluntarily)'}",
            f"- Used in: {item['usedIn']}", f"- Subject: {item['description']}",
            f"- Notes: {item['notes']}", "",
        ])
        thumb = next(f for f in files if f.endswith('-400.webp'))
        cards.append(f'''<article id="{escape(item['id'])}">
<img src="{escape(thumb)}" alt="{escape(item['description'])}" width="400" height="{round(400*item['height']/item['width'])}" loading="lazy" decoding="async">
<div><h2>{escape(item['file'])}</h2><p>{escape(item['description'])}</p>
<p>Photo by <strong>{escape(item['author'])}</strong> · {escape(item['source'])}</p>
<p><a href="{escape(item['originalUrl'])}">Original photograph</a> · <a href="{escape(item['licenseUrl'])}">{escape(item['license'])}</a></p>
<p>Attribution required: {'Yes' if item['attributionRequired'] else 'No; credited voluntarily'}.</p>
<p><strong>Used in:</strong> {escape(item['usedIn'])}</p><p>{escape(item['notes'])}</p>
<details><summary>Local image variants</summary><ul>{''.join(f'<li><a href="{escape(f)}">{escape(f)}</a></li>' for f in files)}</ul></details></div></article>''')
    (ASSETS / "README_IMAGE_CREDITS.md").write_text("\n".join(markdown), encoding="utf-8")
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Photography credits · Krishi Sahayak</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#f5f5ef;color:#192d3e;font:16px/1.65 system-ui,sans-serif}}
main{{max-width:1100px;margin:auto;padding:clamp(20px,5vw,65px)}}h1,h2{{font-family:Georgia,serif;font-weight:400;line-height:1.2}}h1{{font-size:clamp(36px,6vw,64px)}}h2{{font-size:25px;overflow-wrap:anywhere}}a{{color:#3156ae;text-underline-offset:4px}}a:focus-visible,summary:focus-visible{{outline:2px solid #3156ae;outline-offset:4px}}
header{{margin-bottom:50px}}header>p{{max-width:800px}}.eyebrow{{letter-spacing:.15em;font-size:11px}}article{{display:grid;grid-template-columns:minmax(180px,280px) 1fr;gap:30px;border-top:1px solid #ccd3d0;padding:30px 0}}article img{{width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;border-radius:4px}}article p{{font-size:14px}}li{{overflow-wrap:anywhere}}summary{{cursor:pointer}}@media(max-width:620px){{article{{grid-template-columns:1fr;gap:10px}}article img{{max-height:230px}}}}
</style></head><body><main><header><a href="/#today">← Back to Krishi Sahayak</a><p class="eyebrow">THE PEOPLE BEHIND THE PICTURES</p><h1>Rooted in real places.</h1><p>{escape(introduction)}</p><p>CC BY-SA image adaptations retain the original license. Source and license links accompany every image below. Icons use the existing Lucide set under its ISC license.</p><a href="README_IMAGE_CREDITS.md">Download the complete credits</a></header>{''.join(cards)}</main></body></html>'''
    (ASSETS / "credits.html").write_text(page, encoding="utf-8")
    print(f"Generated credits for {len(records)} image assets ({sum(len(x['files']) for x in records)} files).")


if __name__ == "__main__":
    main()
