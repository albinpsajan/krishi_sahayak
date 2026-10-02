import React from 'react';
import { useLanguage } from '../../i18n/languageContext';
import { imageLabels } from '../../data/imageAssets';

export default function PhotoCreditsLink() {
  const { language } = useLanguage();
  return <a className="photo-credits-link" href="/assets/images/credits.html" target="_blank" rel="noreferrer">
    {(imageLabels[language] || imageLabels.en).credits}
  </a>;
}
