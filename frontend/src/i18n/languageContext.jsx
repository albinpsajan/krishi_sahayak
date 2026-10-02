import React, { createContext, useContext, useMemo, useState } from 'react';
import { translations } from './translations';
const LanguageContext = createContext(null);
export function LanguageProvider({ children }) { const [language, setLanguageState] = useState(localStorage.getItem('krishi_language') || 'en'); const setLanguage = value => { localStorage.setItem('krishi_language', value); setLanguageState(value); }; const value = useMemo(() => ({ language, setLanguage, t: key => translations[language]?.[key] || translations.en[key] || key }), [language]); return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>; }
export const useLanguage = () => useContext(LanguageContext);
