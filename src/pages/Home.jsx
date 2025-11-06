/**
 * Home Page
 * Landing page with earnings calculator and feature highlights
 */

import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Shield, DollarSign, Zap, ChevronDown, ChevronUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Home() {
  const { darkMode, currentTheme, textColor, cardBg, borderColor, bgColor } = useTheme();
  const navigate = useNavigate();
  const [calcHours, setCalcHours] = useState(8);
  const [calcGPUs, setCalcGPUs] = useState(1);
  const [earningsCalcOpen, setEarningsCalcOpen] = useState(false);

  const dailyEarnings = (calcHours * 0.90 * calcGPUs).toFixed(2);
  const monthlyEarnings = (dailyEarnings * 30).toFixed(2);
  const yearlyEarnings = (monthlyEarnings * 12).toFixed(0);

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="text-center mb-16">
        <h1 className={`text-5xl font-bold mb-4 ${textColor}`}>
          Share Your GPU, Earn Passive Income
        </h1>
        <p className={`text-xl ${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-8`}>
          The easiest way to monetize your idle computing power
        </p>
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => navigate('/dashboard')}
            className={`${currentTheme.primary} text-white px-8 py-4 rounded-lg font-semibold hover:opacity-90 transition`}
          >
            Start Earning Today
          </button>
          <button
            onClick={() => navigate('/marketplace')}
            className={`${cardBg} ${textColor} px-8 py-4 rounded-lg font-semibold border ${borderColor} hover:border-blue-500 transition`}
          >
            Browse GPUs
          </button>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-8 mb-16">
        {[
          {
            icon: Shield,
            title: 'Safe & Secure',
            desc: 'Your money and data are protected with bank-level encryption and escrow services',
            color: 'text-green-500'
          },
          {
            icon: DollarSign,
            title: 'Best Prices Guaranteed',
            desc: 'Our arbitrage engine automatically finds the cheapest GPUs across all major providers',
            color: currentTheme.accent
          },
          {
            icon: Zap,
            title: 'Instant Setup',
            desc: 'Start earning in minutes. No technical knowledge required',
            color: 'text-purple-500'
          },
        ].map((feature, i) => (
          <div
            key={i}
            className={`${cardBg} p-6 rounded-xl border ${borderColor} hover:border-blue-500 transition cursor-pointer`}
          >
            <feature.icon className={feature.color} size={40} />
            <h3 className={`text-xl font-bold mt-4 mb-2 ${textColor}`}>{feature.title}</h3>
            <p className={darkMode ? 'text-gray-400' : 'text-gray-600'}>{feature.desc}</p>
          </div>
        ))}
      </div>

      {/* Compact Earnings Calculator */}
      <div className={`${cardBg} p-6 rounded-xl border ${borderColor} max-w-2xl mx-auto`}>
        <button
          onClick={() => setEarningsCalcOpen(!earningsCalcOpen)}
          className="w-full flex items-center justify-between"
        >
          <h2 className={`text-2xl font-bold ${textColor}`}>💰 Earnings Calculator</h2>
          {earningsCalcOpen ? <ChevronUp className={textColor} /> : <ChevronDown className={textColor} />}
        </button>

        {earningsCalcOpen && (
          <div className="mt-6 space-y-4">
            <div>
              <label className={`block text-sm font-medium mb-2 ${textColor}`}>Hours per day</label>
              <input
                type="range"
                min="1"
                max="24"
                value={calcHours}
                onChange={(e) => setCalcHours(parseInt(e.target.value))}
                className="w-full"
              />
              <div className="text-center mt-2">
                <span className={`text-2xl font-bold ${textColor}`}>{calcHours} hours</span>
              </div>
            </div>

            <div>
              <label className={`block text-sm font-medium mb-2 ${textColor}`}>Number of GPUs</label>
              <input
                type="range"
                min="1"
                max="10"
                value={calcGPUs}
                onChange={(e) => setCalcGPUs(parseInt(e.target.value))}
                className="w-full"
              />
              <div className="text-center mt-2">
                <span className={`text-2xl font-bold ${textColor}`}>{calcGPUs} GPU{calcGPUs > 1 ? 's' : ''}</span>
              </div>
            </div>

            <div className={`grid grid-cols-3 gap-4 pt-4 border-t ${borderColor}`}>
              <div className="text-center">
                <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Daily</div>
                <div className={`text-2xl font-bold text-green-500`}>${dailyEarnings}</div>
              </div>
              <div className="text-center">
                <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Monthly</div>
                <div className={`text-2xl font-bold ${currentTheme.accent}`}>${monthlyEarnings}</div>
              </div>
              <div className="text-center">
                <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Yearly</div>
                <div className={`text-2xl font-bold text-purple-500`}>${yearlyEarnings}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
