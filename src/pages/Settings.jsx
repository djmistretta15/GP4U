/**
 * Settings Page
 * User preferences and configuration
 */

import React from 'react';
import { useTheme, communityThemes, skillLevels, translations } from '../context/ThemeContext';
import { Sparkles, Sun, Moon } from 'lucide-react';

export default function Settings() {
  const {
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
    textColor,
    cardBg,
    borderColor
  } = useTheme();

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className={`text-3xl font-bold mb-8 ${textColor}`}>Settings</h1>

      {/* Community Theme Selection */}
      <div className={`${cardBg} p-6 rounded-xl border ${borderColor} mb-6`}>
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>Community Theme</h2>
        <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-4`}>
          Choose a visual theme that matches your community and style
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(communityThemes).map(([key, theme]) => (
            <button
              key={key}
              onClick={() => setCommunityTheme(key)}
              className={`p-4 rounded-lg text-left border-2 transition ${communityTheme === key
                  ? `${theme.primary.replace('bg-', 'border-')} bg-opacity-10`
                  : `border-transparent ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`
                }`}
            >
              <div className="flex items-center space-x-3 mb-2">
                <div className={`w-4 h-4 rounded-full ${theme.primary}`} />
                <div className={`font-bold ${textColor}`}>{theme.name}</div>
              </div>
              <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                {theme.description}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Appearance */}
      <div className={`${cardBg} p-6 rounded-xl border ${borderColor} mb-6`}>
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>Appearance</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className={`font-medium ${textColor}`}>Theme</div>
              <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Choose your preferred color scheme</div>
            </div>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`px-4 py-2 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-200'} font-medium flex items-center space-x-2`}
            >
              {darkMode ? (
                <>
                  <Moon className="w-5 h-5" />
                  <span>Dark</span>
                </>
              ) : (
                <>
                  <Sun className="w-5 h-5" />
                  <span>Light</span>
                </>
              )}
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className={`font-medium ${textColor}`}>Skill Level</div>
              <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                {skillLevels[skillMode].description}
              </div>
            </div>
            <select
              value={skillMode}
              onChange={(e) => setSkillMode(e.target.value)}
              className={`px-4 py-2 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-200'} ${textColor} font-medium`}
            >
              {Object.entries(skillLevels).map(([key, val]) => (
                <option key={key} value={key}>{val.label}</option>
              ))}
            </select>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className={`font-medium ${textColor}`}>Language</div>
              <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Select your preferred language</div>
            </div>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className={`px-4 py-2 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-200'} ${textColor} font-medium`}
            >
              <option value="en">English</option>
              <option value="es">Español</option>
              <option value="zh">中文</option>
            </select>
          </div>
        </div>
      </div>

      {/* Profit Mode */}
      <div className={`${cardBg} p-6 rounded-xl border ${borderColor} mb-6`}>
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>Profit Mode</h2>
        <div className="space-y-4">
          <button
            onClick={() => setProfitMode('rental')}
            className={`w-full p-4 rounded-lg text-left border-2 transition ${profitMode === 'rental'
                ? `${currentTheme.primary.replace('bg-', 'border-')} bg-opacity-10`
                : `border-transparent ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`
              }`}
          >
            <div className={`font-bold mb-1 ${textColor}`}>Rental Mode</div>
            <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              Rent out your GPU to individual users. Best for occasional sharing.
            </div>
          </button>

          <button
            onClick={() => setProfitMode('cluster')}
            className={`w-full p-4 rounded-lg text-left border-2 transition ${profitMode === 'cluster'
                ? 'border-purple-500 bg-purple-500/10'
                : `border-transparent ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`
              }`}
          >
            <div className={`font-bold mb-1 ${textColor}`}>Cluster Mode</div>
            <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
              Pool your GPU with others for distributed computing. Best for 24/7 earnings.
            </div>
          </button>
        </div>
      </div>

      {/* Account */}
      <div className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>Account</h2>
        <div className="space-y-3">
          <button className={`w-full text-left px-4 py-3 rounded-lg ${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'} transition`}>
            <div className={`font-medium ${textColor}`}>Profile Settings</div>
          </button>
          <button className={`w-full text-left px-4 py-3 rounded-lg ${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'} transition`}>
            <div className={`font-medium ${textColor}`}>Security & Privacy</div>
          </button>
          <button className={`w-full text-left px-4 py-3 rounded-lg ${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'} transition`}>
            <div className={`font-medium ${textColor}`}>Notifications</div>
          </button>
          <button className={`w-full text-left px-4 py-3 rounded-lg ${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'} transition`}>
            <div className={`font-medium ${textColor}`}>Payment Methods</div>
          </button>
        </div>
      </div>
    </div>
  );
}
