import React from 'react';
import { CloudRain, Droplets, Wind, ThermometerSun } from 'lucide-react';
import RefreshButton from '../common/RefreshButton';
import LastUpdatedText from '../common/LastUpdatedText';
import FarmImage from '../media/FarmImage';
import WeatherActionSuggestion from './WeatherActionSuggestion';
import { useLanguage } from '../../i18n/languageContext';
import '../../featureImages.css';

const photoCaptions = {
  en: 'Field photograph · not live weather',
  ml: 'വയലിന്റെ ചിത്രം · തത്സമയ കാലാവസ്ഥയല്ല',
  hi: 'खेत का चित्र · लाइव मौसम नहीं',
  ta: 'வயல் புகைப்படம் · நேரடி வானிலை அல்ல',
};

export default function WeatherCard({ data, loading, onRefresh }) {
  const { t, language } = useLanguage();
  if (loading && !data) return <section className="live-card"><div className="eyebrow">{t('weather')}</div><p>Loading weather…</p></section>;
  if (!data) return null;

  return <section className="live-card weather-live-card">
    <figure className="feature-photo-strip">
      <FarmImage asset="weather" sizes="(max-width: 760px) 100vw, 440px"/>
      <figcaption>{photoCaptions[language] || photoCaptions.en}</figcaption>
    </figure>
    <div className="live-card-head">
      <div>
        <div className="eyebrow">{t('weather')}</div>
        <h2>{t('weatherTitle')}</h2>
        <p className="live-location">{data.location?.name || 'Your farm'}</p>
      </div>
      <RefreshButton onClick={onRefresh} busy={loading}/>
    </div>
    <div className="weather-metrics">
      <div><ThermometerSun size={18}/><strong>{data.temperature_c == null ? '—' : `${data.temperature_c}°C`}</strong><span>{data.condition}</span></div>
      <div><CloudRain size={18}/><strong>{data.rain_chance == null ? '—' : `${data.rain_chance}%`}</strong><span>Rain chance</span></div>
      <div><Droplets size={18}/><strong>{data.humidity == null ? '—' : `${data.humidity}%`}</strong><span>Humidity</span></div>
      <div><Wind size={18}/><strong>{data.wind_kmh == null ? '—' : `${data.wind_kmh} km/h`}</strong><span>Wind</span></div>
    </div>
    <WeatherActionSuggestion text={data.action}/>
    <LastUpdatedText value={data.updated_at} warning={data.warning}/>
  </section>;
}
