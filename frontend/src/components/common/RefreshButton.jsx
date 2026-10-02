import React from 'react';
import { RefreshCw } from 'lucide-react';
import { useLanguage } from '../../i18n/languageContext';
export default function RefreshButton({ onClick, busy }) { const { t } = useLanguage(); return <button className="live-refresh" onClick={onClick} disabled={busy}><RefreshCw size={14} className={busy ? 'spin' : ''}/> {t('refresh')}</button>; }
