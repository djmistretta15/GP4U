/**
 * AppWrapper Component
 * Enhanced navigation and theme integration
 * Manages routing and component rendering
 */

import React, { useState } from 'react';
import { useAuth } from './context/AuthContext';
import { useToast } from './context/ToastContext';
import { useTheme } from './context/ThemeContext';
import { Zap, Home as HomeIcon, Activity, Server, Wallet, TrendingUp, Settings, Menu, X, Sun, Moon } from 'lucide-react';
import HomePage from './pages/Home';
import GP4UPlatform from './components/GP4UPlatform';
import Dashboard from './pages/Dashboard';
import EnhancedMarketplace from './pages/EnhancedMarketplace';
import Earnings from './pages/Earnings';
import SettingsPage from './pages/Settings';
import WalletManager from './components/WalletManager';
import MyReservations from './components/MyReservations';
import MyClusters from './components/MyClusters';
import ClusterWizard from './components/ClusterWizard';

export default function AppWrapper() {
  const { user, logout } = useAuth();
  const toast = useToast();
  const { darkMode, setDarkMode, currentTheme, textColor, cardBg, borderColor, bgColor, t, skillLevels, skillMode, setSkillMode } = useTheme();
  const [currentPage, setCurrentPage] = useState('home');
  const [showClusterWizard, setShowClusterWizard] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handlePageChange = (page) => {
    setCurrentPage(page);
    setMobileMenuOpen(false);
  };

  const handleCreateCluster = () => {
    setShowClusterWizard(true);
  };

  const handleClusterSuccess = (cluster) => {
    toast.success(`Cluster "${cluster.job_name}" created successfully!`);
    setShowClusterWizard(false);
    setCurrentPage('clusters');
  };

  const navItems = [
    { id: 'home', icon: HomeIcon, label: t.home },
    { id: 'dashboard', icon: Activity, label: t.dashboard },
    { id: 'marketplace', icon: Server, label: t.marketplace },
    { id: 'wallet', icon: Wallet, label: t.wallet },
    { id: 'earnings', icon: TrendingUp, label: t.earnings },
    { id: 'reservations', icon: Activity, label: t.myReservations },
    { id: 'clusters', icon: Server, label: t.myClusters },
  ];

  return (
    <div className={`min-h-screen ${bgColor} ${textColor} transition-colors duration-200`}>
      {/* Enhanced Navigation */}
      <nav className={`${cardBg} border-b ${borderColor} sticky top-0 z-50`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <div className="flex items-center space-x-2">
                <Zap className={currentTheme.accent} size={32} />
                <span className={`text-xl font-bold ${textColor}`}>GP4U</span>
              </div>

              <div className="hidden md:flex space-x-1">
                {navItems.map(item => (
                  <button
                    key={item.id}
                    onClick={() => handlePageChange(item.id)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${currentPage === item.id
                        ? `${currentTheme.primary} text-white`
                        : `${darkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-600 hover:bg-gray-100'}`
                      }`}
                  >
                    <item.icon size={18} />
                    <span className="text-sm font-medium">{item.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {/* Skill Level Selector */}
              <div className="hidden lg:flex items-center space-x-2">
                {Object.entries(skillLevels).map(([key, val]) => (
                  <button
                    key={key}
                    onClick={() => setSkillMode(key)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition ${skillMode === key
                        ? `${currentTheme.primary} text-white`
                        : `${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-600'}`
                      }`}
                  >
                    {val.label}
                  </button>
                ))}
              </div>

              {/* User Info */}
              <span className={`hidden sm:block text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                {user?.email}
              </span>

              {/* Dark Mode Toggle */}
              <button
                onClick={() => setDarkMode(!darkMode)}
                className={`p-2 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-200'}`}
              >
                {darkMode ? <Sun size={20} className="text-yellow-400" /> : <Moon size={20} className="text-gray-600" />}
              </button>

              {/* Settings */}
              <button
                onClick={() => handlePageChange('settings')}
                className={`p-2 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-200'}`}
              >
                <Settings size={20} className={darkMode ? 'text-gray-300' : 'text-gray-600'} />
              </button>

              {/* Logout */}
              <button
                onClick={logout}
                className="hidden sm:block px-3 py-2 rounded-md text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                Logout
              </button>

              {/* Mobile Menu Button */}
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 rounded-lg"
              >
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className={`md:hidden ${cardBg} border-t ${borderColor}`}>
            <div className="px-4 py-4 space-y-2">
              {navItems.map(item => (
                <button
                  key={item.id}
                  onClick={() => handlePageChange(item.id)}
                  className={`flex items-center space-x-3 w-full px-4 py-3 rounded-lg ${currentPage === item.id
                      ? `${currentTheme.primary} text-white`
                      : `${darkMode ? 'text-gray-300' : 'text-gray-600'}`
                    }`}
                >
                  <item.icon size={20} />
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
  {currentPage === 'home' && <GP4UPlatform />}
        {currentPage === 'dashboard' && <Dashboard />}
        {currentPage === 'marketplace' && <EnhancedMarketplace onCreateCluster={handleCreateCluster} />}
        {currentPage === 'wallet' && <WalletManager darkMode={darkMode} />}
        {currentPage === 'earnings' && <Earnings />}
        {currentPage === 'reservations' && <MyReservations darkMode={darkMode} />}
        {currentPage === 'clusters' && <MyClusters darkMode={darkMode} />}
        {currentPage === 'settings' && <SettingsPage />}
      </main>

      {/* Cluster Creation Modal */}
      {showClusterWizard && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className={`${cardBg} rounded-2xl p-8 max-w-5xl w-full my-8`}>
            <ClusterWizard
              onClose={() => setShowClusterWizard(false)}
              onSuccess={handleClusterSuccess}
              darkMode={darkMode}
            />
          </div>
        </div>
      )}
    </div>
  );
}
