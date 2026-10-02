import React, { useState } from 'react';
import { ImageOff, Sprout } from 'lucide-react';
import { useLanguage } from '../../i18n/languageContext';
import { getCropImage, imageAssets, imageLabels } from '../../data/imageAssets';

function PhotoFallback({ className, label, crop }) {
  const Icon = crop ? Sprout : ImageOff;
  return <span className={`farm-image farm-image-fallback ${className}`} role="img" aria-label={label}>
    <Icon size={28} strokeWidth={1.25} aria-hidden="true"/>
    <span>{label}</span>
  </span>;
}

function ResponsivePhoto({ photo, className, priority, sizes, language, missingLabel }) {
  const [format, setFormat] = useState('webp');
  if (format === 'failed') return <PhotoFallback className={className} label={missingLabel}/>;
  const srcSet = photo.widths.map(width => `${photo.file}${width === photo.width ? '' : `-${width}`}.webp ${width}w`).join(', ');
  return <picture className={`farm-image ${className}`}>
    {format === 'webp' && <source type="image/webp" srcSet={srcSet} sizes={sizes}/>}
    <img src={`${photo.file}.jpg`} alt={photo.alt[language] || photo.alt.en}
      width={photo.width} height={photo.height} sizes={sizes}
      loading={priority ? 'eager' : 'lazy'} fetchPriority={priority ? 'high' : 'auto'} decoding="async"
      onError={() => setFormat(current => current === 'webp' ? 'jpeg' : 'failed')}/>
  </picture>;
}

/** Responsive local photograph, with honest no-photo fallback for unlisted crops.
 * Native selects remain accessible; put this component beside the selected crop.
 * Keying by file resets load errors when a user switches crops.
 */
export default function FarmImage({ asset, crop, className = '', priority = false, sizes = '100vw' }) {
  const { language } = useLanguage();
  const photo = crop !== undefined ? getCropImage(crop) : imageAssets[asset];
  const labels = imageLabels[language] || imageLabels.en;
  if (!photo) return <PhotoFallback className={className} crop={crop !== undefined}
    label={crop !== undefined ? labels.cropMissing : labels.missing}/>;
  return <ResponsivePhoto key={photo.file} {...{ photo, className, priority, sizes, language }} missingLabel={labels.missing}/>;
}
