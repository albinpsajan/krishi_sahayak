import React from 'react';
import { Store } from 'lucide-react';
import RefreshButton from '../common/RefreshButton';
import FarmImage from '../media/FarmImage';
import { useLanguage } from '../../i18n/languageContext';
import { cropLabels } from '../../i18n/translations';
import '../../featureImages.css';

const crops = ['banana', 'coconut', 'paddy', 'pepper', 'tomato', 'onion', 'potato', 'arecanut', 'rubber', 'ginger', 'turmeric'];
const money = value => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(value);
const photoCaptions = { en: 'From field to market', ml: 'വയലിൽ നിന്ന് വിപണിയിലേക്ക്', hi: 'खेत से बाज़ार तक', ta: 'வயலில் இருந்து சந்தைக்கு' };

export default function MarketPriceCard({ data, loading, onRefresh, crop = 'banana', onCropChange }) {
  const { t, language } = useLanguage();
  const cropLabel = key => cropLabels[language]?.[key] || cropLabels.en[key] || key;
  const available = !loading && data?.available === true && data.requested_commodity === crop;
  return <section className="live-card market-live-card" aria-busy={loading}>
    <figure className="feature-photo-strip market-photo-strip">
      <FarmImage asset="marketPrice" sizes="(max-width: 760px) 100vw, 440px"/>
      <figcaption>{photoCaptions[language] || photoCaptions.en}</figcaption>
    </figure>
    <div className="live-card-head"><div><div className="eyebrow">{t('market')}</div><h2>{t('marketTitle')}</h2>
      <p className="live-location"><Store size={14}/> {cropLabel(crop)} · {available ? [data.market, data.district].join(', ') : 'Thrissur, Kerala'}</p>
    </div><RefreshButton onClick={onRefresh} busy={loading}/></div>
    <div className="market-crop-choice">
      <FarmImage crop={crop} className="market-crop-photo" sizes="52px"/>
      <label className="market-crop-select">{t('selectCrop')}
        <select value={crop} onChange={e => onCropChange?.(e.target.value)}>
          {crops.map(key => <option key={key} value={key}>{cropLabel(key)}</option>)}
        </select>
      </label>
    </div>
    <div aria-live="polite">
      {loading ? <p>{t('loadingPrices')}</p> : !available ? <p role="status">{data?.warning || 'No verified price is available for this crop.'}</p> : <>
        <p>{data.commodity} · {data.variety || 'Variety not reported'}{data.grade ? ' · ' + data.grade : ''}</p>
        <div className="price-grid">{[['min_price', 'minimum'], ['max_price', 'maximum'], ['modal_price', 'modal']].map(([key, label]) =>
          <div key={key} className={key === 'modal_price' ? 'modal-price' : ''}><span>{t(label)}</span><strong>{money(data[key])}</strong><small>/ {t('quintal')}</small></div>)}
        </div>
        <p><strong>Market report: {data.arrival_date}</strong></p>
        {data.warning && <p role="status">{data.warning}</p>}
        <p className="muted">{data.suggestion}</p>
        <small><a href={data.source_url} target="_blank" rel="noreferrer">{data.source}</a> · Retrieved {new Date(data.fetched_at).toLocaleTimeString()}</small>
      </>}
    </div>
  </section>;
}
