# Local image library

The UI uses downloaded documentary photographs, with a shared responsive component.
No stock-photo service or image API is called at runtime. Map tiles, user uploads and
live-data providers keep their existing behavior.

## Files and responsibilities

- `frontend/public/assets/images/`: deployable WebP/JPEG files, separated into
  `hero`, `backgrounds`, `features` and `crops`; Vite copies them into `dist/assets/images`.
- `README_IMAGE_CREDITS.md` and `credits.html` in that directory: attribution,
  original pages, license links, modifications and actual usage. The workspace footer
  links to the public credits page so Commons attribution travels with the UI.
- `crop-sources.json` / `feature-sources.json`: machine-readable provenance.
- `frontend/src/data/imageAssets.js`: centralized local paths, dimensions, responsive
  widths and alt text in English, Malayalam, Hindi and Tamil.
- `components/media/FarmImage.jsx`: `picture`/WebP `srcset`, JPEG fallback, lazy
  loading, priority hero, reserved dimensions and a neutral missing-photo state.
- `imageAssets.css`: shared image behavior and subtle decorative section backgrounds.
  `dashboardImages.css` and `featureImages.css` own page-specific composition.
- Existing Lucide React icons remain in use; no duplicate downloaded icon set.

## Usage

```jsx
<FarmImage asset="farmHero" priority sizes="(max-width: 760px) 100vw, 65vw" />
<FarmImage crop={selectedCrop} sizes="52px" />
```

Only the hero is eager/high priority. Other pictures load lazily and decode
asynchronously. The supplied `sizes` controls the browser's choice of 400, 800,
1200 or 1600 pixel variants. Photos have proper localized alt text; CSS textures
are decorative. Reduced-motion settings disable photo zoom.

Supported crop photos: banana, coconut, paddy (rice), black pepper, ginger,
turmeric. Other crops retain their existing selectors/data and show a labeled
neutral icon. Never substitute an unrelated crop photo or a fake price.

Photos in weather/market/planner panels are illustrative. The coconut grove was
photographed in Bekal Beach Park, not a surveyed plantation. The drip-system
reference is from Catalonia, not a local installation. The officer-support image
shows a Kerala field, not an invented staff member or endorsement.

## Updating photos

1. Verify the original source page and its specific license; avoid identifiable
   people and brands. Keep the photographer, source page and license URL.
2. Add a reviewed record to `scripts/images/feature_sources.json`, or the crop
   importer for crop additions. Re-check source licensing before regenerating.
3. With Python and Pillow available, run from the repository root:

   ```powershell
   python scripts/images/import_crop_photos.py
   python scripts/images/build_feature_assets.py
   python scripts/images/build_credits.py
   python scripts/images/validate_assets.py
   cd frontend
   npm run build
   ```

4. Inspect the resulting crops locally, especially for packaging, faces and
   misleading context. Update the manifest/alt text and component usage.
5. Check small and desktop layouts. Keep source dimensions, avoid upscaling,
   retain source licenses on derivatives, and commit optimized files plus credits.

Original downloads are caches outside the production asset folder. `.image-work/`
is git-ignored; Commons crop originals are in the system temporary directory.
Regeneration needs network access, but normal builds and runtime image delivery do not.

The 1600px hero and 1200px section images use WebP quality 78 with progressive
JPEG quality 80; crop cards use 800px WebP quality 80/JPEG quality 82 with 400px
WebP thumbnails. No generative editing or artificial enhancement is applied.
