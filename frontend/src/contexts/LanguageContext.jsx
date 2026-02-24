import React, { createContext, useContext, useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const LanguageContext = createContext(null);

const SUPPORTED_LANGS = ['it', 'es', 'en'];
const DEFAULT_LANG = 'it';

export const LanguageProvider = ({ children }) => {
  const [lang, setLang] = useState(() => {
    const saved = localStorage.getItem('golevents_lang');
    if (saved && SUPPORTED_LANGS.includes(saved)) return saved;
    
    // Detect browser language
    const browserLang = navigator.language?.slice(0, 2);
    if (SUPPORTED_LANGS.includes(browserLang)) return browserLang;
    
    return DEFAULT_LANG;
  });
  
  const [translations, setTranslations] = useState({});
  const [siteSettings, setSiteSettings] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    localStorage.setItem('golevents_lang', lang);
    fetchTranslations();
    fetchSiteSettings();
  }, [lang]);

  const fetchTranslations = async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin/public/translations?lang=${lang}`);
      const data = await response.json();
      setTranslations(data || {});
    } catch (error) {
      console.error('Error fetching translations:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSiteSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/admin/public/settings?lang=${lang}`);
      const data = await response.json();
      setSiteSettings(data || {});
    } catch (error) {
      console.error('Error fetching site settings:', error);
    }
  };

  const t = (key, fallback = '') => {
    return translations[key] || fallback || key;
  };

  const getMultiLang = (obj, fallback = '') => {
    if (!obj) return fallback;
    if (typeof obj === 'string') return obj;
    return obj[lang] || obj.it || obj.en || obj.es || fallback;
  };

  const changeLang = (newLang) => {
    if (SUPPORTED_LANGS.includes(newLang)) {
      setLang(newLang);
    }
  };

  // Listen for language change events from mobile menu
  useEffect(() => {
    const handleLangChange = (event) => {
      if (SUPPORTED_LANGS.includes(event.detail)) {
        setLang(event.detail);
      }
    };
    window.addEventListener('changeLanguage', handleLangChange);
    return () => window.removeEventListener('changeLanguage', handleLangChange);
  }, []);

  return (
    <LanguageContext.Provider value={{
      lang,
      setLang: changeLang,
      t,
      getMultiLang,
      translations,
      siteSettings,
      loading,
      supportedLangs: SUPPORTED_LANGS
    }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider');
  }
  return context;
};

export default LanguageContext;
