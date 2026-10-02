import React from 'react';
import { useLanguage } from '../../i18n/languageContext';
export default function LastUpdatedText({ value, warning }) { const { t } = useLanguage(); return <small className={`live-updated ${warning ? 'has-warning' : ''}`}>{t('lastUpdated')}: {value ? new Date(value).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : '—'}{warning ? ` · ${warning}` : ''}</small>; }
