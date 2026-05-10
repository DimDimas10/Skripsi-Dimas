import React, { createContext, useContext, useState, useEffect } from 'react';
import translations from './i18n';

const AppContext = createContext();

export const useAppContext = () => useContext(AppContext);

export const AppProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('bankshield-theme') || 'dark';
  });

  const [lang, setLang] = useState(() => {
    return localStorage.getItem('bankshield-lang') || 'id';
  });

  const t = (key) => {
    return translations[lang]?.[key] || translations['id']?.[key] || key;
  };

  const toggleTheme = () => {
    // Matikan semua transition sementara saat ganti tema
    document.documentElement.classList.add('no-transition');
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    // Aktifkan kembali setelah 1 frame render
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        document.documentElement.classList.remove('no-transition');
      });
    });
  };

  const toggleLang = () => {
    setLang(prev => prev === 'id' ? 'en' : 'id');
  };

  useEffect(() => {
    localStorage.setItem('bankshield-theme', theme);
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    localStorage.setItem('bankshield-lang', lang);
  }, [lang]);

  return (
    <AppContext.Provider value={{ theme, toggleTheme, lang, toggleLang, t }}>
      {children}
    </AppContext.Provider>
  );
};

export default AppContext;
