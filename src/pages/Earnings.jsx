/**
 * Earnings Page
 * Detailed view of user earnings and payouts
 */

import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';

export default function Earnings() {
  const { darkMode, currentTheme, textColor, cardBg, borderColor } = useTheme();
  const [earnings, setEarnings] = useState({
    total: 3847.92,
    today: 18.40,
    week: 124.80,
    breakdown: [
      { source: 'GPU Rental', amount: 2840.50, percentage: 74 },
      { source: 'Cluster Computing', amount: 890.25, percentage: 23 },
      { source: 'Referral Bonus', amount: 117.17, percentage: 3 },
    ]
  });

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className={`text-3xl font-bold mb-8 ${textColor}`}>Earnings Overview</h1>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {[
          { label: 'Today', amount: `$${earnings.today}`, change: '+12%' },
          { label: 'This Week', amount: `$${earnings.week}`, change: '+8%' },
          { label: 'All Time', amount: `$${earnings.total.toFixed(2)}`, change: '+245%' },
        ].map((stat, i) => (
          <div key={i} className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
            <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-2`}>{stat.label}</div>
            <div className={`text-3xl font-bold mb-1 ${textColor}`}>{stat.amount}</div>
            <div className="text-sm text-green-500">{stat.change}</div>
          </div>
        ))}
      </div>

      <div className={`${cardBg} p-6 rounded-xl border ${borderColor} mb-8`}>
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>Earnings Breakdown</h2>
        <div className="space-y-4">
          {earnings.breakdown.map((item, i) => (
            <div key={i}>
              <div className="flex justify-between mb-2">
                <span className={textColor}>{item.source}</span>
                <span className={`font-bold ${textColor}`}>${item.amount}</span>
              </div>
              <div className="w-full bg-gray-300 rounded-full h-2">
                <div
                  className={`${currentTheme.primary} h-2 rounded-full transition-all`}
                  style={{ width: `${item.percentage}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>Payout Schedule</h2>
        <div className={`p-4 rounded-lg ${darkMode ? 'bg-blue-900/20 border-blue-700' : 'bg-blue-50 border-blue-200'} border mb-4`}>
          <p className={`text-sm ${darkMode ? 'text-blue-300' : 'text-blue-700'}`}>
            Next automatic payout in 3 days: <span className="font-bold">${earnings.week}</span>
          </p>
        </div>
        <button className={`${currentTheme.primary} text-white w-full py-3 rounded-lg font-semibold hover:opacity-90`}>
          Request Early Payout (2% fee)
        </button>
      </div>
    </div>
  );
}
