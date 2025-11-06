/**
 * Theme Context
 * Manages dark mode, community themes, skill levels, and language
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

// Community Themes
export const communityThemes = {
  professional: {
    name: 'Professional',
    primary: 'bg-blue-500',
    secondary: 'bg-blue-100',
    accent: 'text-blue-500',
    gradient: 'from-blue-500 to-blue-600',
    description: 'Clean, corporate, business-focused'
  },
  gaming: {
    name: 'Gaming',
    primary: 'bg-purple-500',
    secondary: 'bg-purple-100',
    accent: 'text-purple-500',
    gradient: 'from-purple-500 to-purple-600',
    description: 'Bold, energetic, gamer aesthetic'
  },
  creative: {
    name: 'Creative',
    primary: 'bg-pink-500',
    secondary: 'bg-pink-100',
    accent: 'text-pink-500',
    gradient: 'from-pink-500 to-pink-600',
    description: 'Artistic, vibrant, designer-friendly'
  },
  developer: {
    name: 'Developer',
    primary: 'bg-green-500',
    secondary: 'bg-green-100',
    accent: 'text-green-500',
    gradient: 'from-green-500 to-green-600',
    description: 'Terminal-inspired, minimal, code-focused'
  },
  crypto: {
    name: 'Crypto',
    primary: 'bg-orange-500',
    secondary: 'bg-orange-100',
    accent: 'text-orange-500',
    gradient: 'from-orange-500 to-orange-600',
    description: 'Gold & orange for crypto enthusiasts'
  }
};

// Translations
export const translations = {
  en: {
    home: 'Home',
    dashboard: 'Dashboard',
    marketplace: 'Marketplace',
    wallet: 'Wallet',
    earnings: 'Earnings',
    settings: 'Settings',
    myGPUs: 'My GPUs',
    myReservations: 'My Reservations',
    myClusters: 'My Clusters',
    comparison: 'Comparison',
    quickBook: 'Quick Book'
  },
  es: {
    home: 'Inicio',
    dashboard: 'Panel',
    marketplace: 'Mercado',
    wallet: 'Cartera',
    earnings: 'Ganancias',
    settings: 'Ajustes',
    myGPUs: 'Mis GPUs',
    myReservations: 'Mis Reservas',
    myClusters: 'Mis Clústeres',
    comparison: 'Comparación',
    quickBook: 'Reserva Rápida'
  },
  zh: {
    home: '首页',
    dashboard: '仪表板',
    marketplace: '市场',
    wallet: '钱包',
    earnings: '收益',
    settings: '设置',
    myGPUs: '我的GPU',
    myReservations: '我的预订',
    myClusters: '我的集群',
    comparison: '比较',
    quickBook: '快速预订'
  }
};

// Skill Levels
export const skillLevels = {
  beginner: {
    label: 'Beginner',
    description: 'Simple and easy',
    features: ['basic']
  },
  intermediate: {
    label: 'Intermediate',
    description: 'More options',
    features: ['basic', 'advanced']
  },
  expert: {
    label: 'Expert',
    description: 'Full control',
    features: ['basic', 'advanced', 'expert']
  }
};

export const ThemeProvider = ({ children }) => {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('gp4u-darkMode');
    return saved ? JSON.parse(saved) : false;
  });

  const [communityTheme, setCommunityTheme] = useState(() => {
    const saved = localStorage.getItem('gp4u-communityTheme');
    return saved || 'professional';
  });

  const [skillMode, setSkillMode] = useState(() => {
    const saved = localStorage.getItem('gp4u-skillMode');
    return saved || 'beginner';
  });

  const [language, setLanguage] = useState(() => {
    const saved = localStorage.getItem('gp4u-language');
    return saved || 'en';
  });

  const [profitMode, setProfitMode] = useState(() => {
    const saved = localStorage.getItem('gp4u-profitMode');
    return saved || 'rental';
  });

  // Save to localStorage whenever values change
  useEffect(() => {
    localStorage.setItem('gp4u-darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  useEffect(() => {
    localStorage.setItem('gp4u-communityTheme', communityTheme);
  }, [communityTheme]);

  useEffect(() => {
    localStorage.setItem('gp4u-skillMode', skillMode);
  }, [skillMode]);

  useEffect(() => {
    localStorage.setItem('gp4u-language', language);
  }, [language]);

  useEffect(() => {
    localStorage.setItem('gp4u-profitMode', profitMode);
  }, [profitMode]);

  const currentTheme = communityThemes[communityTheme];
  const t = translations[language] || translations.en;

  const bgColor = darkMode ? 'bg-gray-900' : 'bg-gray-50';
  const textColor = darkMode ? 'text-white' : 'text-gray-900';
  const cardBg = darkMode ? 'bg-gray-800' : 'bg-white';
  const borderColor = darkMode ? 'border-gray-700' : 'border-gray-200';

  const value = {
    darkMode,
    setDarkMode,
    communityTheme,
    setCommunityTheme,
    skillMode,
    setSkillMode,
    language,
    setLanguage,
    profitMode,
    setProfitMode,
    currentTheme,
    t,
    bgColor,
    textColor,
    cardBg,
    borderColor
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};
