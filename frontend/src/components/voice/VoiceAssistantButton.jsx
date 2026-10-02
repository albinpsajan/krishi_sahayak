import React from 'react';
import { Mic } from 'lucide-react';
import { useLanguage } from '../../i18n/languageContext';
export default function VoiceAssistantButton({ onClick }) { const { t } = useLanguage(); return <button className="voice-fab" onClick={onClick}><Mic size={18}/><span>{t('voice')}</span></button>; }
