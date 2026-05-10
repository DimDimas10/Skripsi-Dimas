import React from 'react';
import { Activity, ShieldCheck, Moon, Sun, Languages } from 'lucide-react';
import { useAppContext } from '../AppContext';

const Navbar = () => {
  const { theme, toggleTheme, lang, toggleLang, t } = useAppContext();

  return (
    <header className="navbar glass-panel">
      <div className="navbar-brand">
        <Activity size={28} color="#60a5fa" />
        <span>{t('brandName')}</span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          <ShieldCheck size={18} color="#10b981" />
          <span className="navbar-status-text">{t('systemActive')}</span>
        </span>

        {/* Language Toggle */}
        <button
          id="lang-toggle"
          onClick={toggleLang}
          className="navbar-btn"
          title={lang === 'id' ? 'Switch to English' : 'Ganti ke Bahasa Indonesia'}
        >
          <Languages size={16} />
          <span>{lang === 'id' ? 'EN' : 'ID'}</span>
        </button>

        {/* Theme Toggle */}
        <button
          id="theme-toggle"
          onClick={toggleTheme}
          className="navbar-btn"
          title={theme === 'dark' ? t('lightMode') : t('darkMode')}
        >
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
          <span className="navbar-btn-label">{theme === 'dark' ? t('lightMode') : t('darkMode')}</span>
        </button>
      </div>
    </header>
  );
};

export default Navbar;
