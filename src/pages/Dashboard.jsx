/**
 * Dashboard Page
 * Overview of user's GPU rental activity and earnings
 */

import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { Wallet, TrendingUp, Clock, Activity } from 'lucide-react';
import { gpuAPI } from '../services/api';

export default function Dashboard() {
  const { darkMode, currentTheme, textColor, cardBg, borderColor, skillMode, profitMode } = useTheme();
  const { user } = useAuth();
  const [stats, setStats] = useState({
    balance: 0,
    earnings: 0,
    activeBookings: 0,
    uptime: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // TODO: Replace with actual API calls
      setStats({
        balance: 1250.75,
        earnings: 3847.92,
        activeBookings: 2,
        uptime: 98.7
      });
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <h1 className={`text-3xl font-bold ${textColor}`}>Dashboard</h1>
        <div className="flex items-center space-x-4">
          <div className={`px-4 py-2 rounded-lg ${currentTheme.primary} text-white text-sm font-medium`}>
            {skillMode.charAt(0).toUpperCase() + skillMode.slice(1)} Mode
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-4 gap-6 mb-8">
        {[
          { label: 'Wallet Balance', value: `$${stats.balance.toFixed(2)}`, icon: Wallet, color: 'text-green-500' },
          { label: 'Total Earnings', value: `$${stats.earnings.toFixed(2)}`, icon: TrendingUp, color: currentTheme.accent },
          { label: 'Active Bookings', value: stats.activeBookings.toString(), icon: Clock, color: 'text-purple-500' },
          { label: 'GPU Uptime', value: `${stats.uptime}%`, icon: Activity, color: 'text-orange-500' },
        ].map((stat, i) => (
          <div key={i} className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
            <div className="flex items-center justify-between mb-2">
              <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>{stat.label}</span>
              <stat.icon className={stat.color} size={24} />
            </div>
            <div className={`text-2xl font-bold ${textColor}`}>{stat.value}</div>
          </div>
        ))}
      </div>

      {profitMode === 'rental' ? (
        <div className={`${cardBg} p-6 rounded-xl border ${borderColor} mb-8`}>
          <h2 className={`text-xl font-bold mb-4 ${textColor}`}>Rental Mode Dashboard</h2>
          <div className={`p-4 rounded-lg mb-4 ${darkMode ? 'bg-blue-900/20 border-blue-700' : 'bg-blue-50 border-blue-200'} border`}>
            <p className={`text-sm ${darkMode ? 'text-blue-300' : 'text-blue-700'}`}>
              Your GPUs are available for rent. Auto-arbitrage is active and finding the best rates.
            </p>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Current Average Rate</span>
              <span className={`font-semibold ${textColor}`}>$2.40/hour</span>
            </div>
            <div className="flex justify-between items-center">
              <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Today's Earnings</span>
              <span className={`font-semibold text-green-500`}>+$18.40</span>
            </div>
            <div className="flex justify-between items-center">
              <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Hours Shared Today</span>
              <span className={`font-semibold ${textColor}`}>6.5 hrs</span>
            </div>
          </div>
        </div>
      ) : (
        <div className={`${cardBg} p-6 rounded-xl border ${borderColor} mb-8`}>
          <h2 className={`text-xl font-bold mb-4 ${textColor}`}>Cluster Mode Dashboard</h2>
          <div className={`p-4 rounded-lg mb-4 ${darkMode ? 'bg-purple-900/20 border-purple-700' : 'bg-purple-50 border-purple-200'} border`}>
            <p className={`text-sm ${darkMode ? 'text-purple-300' : 'text-purple-700'}`}>
              Your GPUs are pooled for maximum efficiency. Earning from distributed tasks.
            </p>
          </div>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>GPUs in Cluster</span>
              <span className={`font-semibold ${textColor}`}>3 Active</span>
            </div>
            <div className="flex justify-between items-center">
              <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Cluster Efficiency</span>
              <span className={`font-semibold text-green-500`}>94.2%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Network Share</span>
              <span className={`font-semibold ${textColor}`}>0.0234%</span>
            </div>
          </div>
        </div>
      )}

      {skillMode !== 'beginner' && (
        <div className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
          <h2 className={`text-xl font-bold mb-4 ${textColor}`}>Performance Analytics</h2>
          <div className="h-48 flex items-end space-x-2">
            {[65, 72, 58, 80, 75, 88, 92, 85, 78, 90, 95, 88].map((height, i) => (
              <div key={i} className="flex-1 flex flex-col items-center">
                <div
                  className={`w-full ${currentTheme.primary} rounded-t transition-all hover:opacity-80`}
                  style={{ height: `${height}%` }}
                />
                <span className={`text-xs mt-2 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>{i + 1}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
