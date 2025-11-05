/**
 * AppWrapper Component
 * Integrates new components with existing App.jsx
 * Manages routing and component rendering
 */

import React, { useState } from 'react';
import { useAuth } from './context/AuthContext';
import { useToast } from './context/ToastContext';
import Marketplace from './pages/Marketplace';
import WalletManager from './components/WalletManager';
import MyReservations from './components/MyReservations';
import MyClusters from './components/MyClusters';
import ClusterWizard from './components/ClusterWizard';

export default function AppWrapper() {
  const { user, logout } = useAuth();
  const toast = useToast();
  const [currentPage, setCurrentPage] = useState('marketplace');
  const [darkMode, setDarkMode] = useState(false);
  const [showClusterWizard, setShowClusterWizard] = useState(false);

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleCreateCluster = () => {
    setShowClusterWizard(true);
  };

  const handleClusterSuccess = (cluster) => {
    toast.success(`Cluster "${cluster.job_name}" created successfully!`);
    setShowClusterWizard(false);
    setCurrentPage('clusters');
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'dark bg-gray-900' : 'bg-gray-50'}`}>
      {/* Simple Navigation */}
      <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-8">
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">GP4U</h1>
              <div className="flex space-x-4">
                <button
                  onClick={() => handlePageChange('marketplace')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    currentPage === 'marketplace'
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  Marketplace
                </button>
                <button
                  onClick={() => handlePageChange('reservations')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    currentPage === 'reservations'
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  My Reservations
                </button>
                <button
                  onClick={() => handlePageChange('clusters')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    currentPage === 'clusters'
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  My Clusters
                </button>
                <button
                  onClick={() => handlePageChange('wallet')}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    currentPage === 'wallet'
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  Wallet
                </button>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700 dark:text-gray-300">{user?.email}</span>
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="px-3 py-2 rounded-md text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
              <button
                onClick={logout}
                className="px-3 py-2 rounded-md text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {currentPage === 'marketplace' && (
          <Marketplace darkMode={darkMode} onCreateCluster={handleCreateCluster} />
        )}

        {currentPage === 'reservations' && <MyReservations darkMode={darkMode} />}
        {currentPage === 'clusters' && <MyClusters darkMode={darkMode} />}
        {currentPage === 'wallet' && <WalletManager darkMode={darkMode} />}
      </main>

      {/* Cluster Creation Modal */}
      {showClusterWizard && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-5xl w-full my-8">
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
