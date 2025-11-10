import React, { useState } from 'react';
import { Sun, Moon, Zap, Server, Wallet, Settings, Home, TrendingUp, Clock, DollarSign, Cpu, Activity, Menu, X, ChevronDown, ChevronUp, Lock, Unlock, Star, GitCompare, Award, Info, BarChart2, Lightbulb } from 'lucide-react';

export default function GP4UPlatform() {
  const [currentPage, setCurrentPage] = useState('home');
  const [darkMode, setDarkMode] = useState(false);
  const [skillMode, setSkillMode] = useState('beginner');
  const [profitMode, setProfitMode] = useState('rental');
  const [communityTheme, setCommunityTheme] = useState('professional');
  const [language, setLanguage] = useState('en');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [myGPUsOpen, setMyGPUsOpen] = useState(false);
  const [earningsCalcOpen, setEarningsCalcOpen] = useState(false);
  const [compareMode, setCompareMode] = useState(false);
  const [selectedForCompare, setSelectedForCompare] = useState([]);
  const [showPriceHistory, setShowPriceHistory] = useState(null);
  const [balance, setBalance] = useState(1250.75);
  const [earnings, setEarnings] = useState(3847.92);

  const communityThemes = {
    professional: { 
      name: 'Professional', 
      primary: 'bg-blue-500', 
      secondary: 'bg-blue-100',
      accent: 'text-blue-500',
      description: 'Clean, corporate, business-focused'
    },
    gaming: { 
      name: 'Gaming', 
      primary: 'bg-purple-500', 
      secondary: 'bg-purple-100',
      accent: 'text-purple-500',
      description: 'Bold, energetic, gamer aesthetic'
    },
    creative: { 
      name: 'Creative', 
      primary: 'bg-pink-500', 
      secondary: 'bg-pink-100',
      accent: 'text-pink-500',
      description: 'Artistic, vibrant, designer-friendly'
    },
    developer: { 
      name: 'Developer', 
      primary: 'bg-green-500', 
      secondary: 'bg-green-100',
      accent: 'text-green-500',
      description: 'Terminal-inspired, minimal, code-focused'
    },
    senior: { 
      name: 'Senior Friendly', 
      primary: 'bg-orange-500', 
      secondary: 'bg-orange-100',
      accent: 'text-orange-500',
      description: 'Large text, high contrast, simple'
    },
  };

  const currentTheme = communityThemes[communityTheme];

  const [bookmarkedGPUs, setBookmarkedGPUs] = useState([]);

  const [myGPUs, setMyGPUs] = useState([
    { id: 1, name: 'RTX 4090', status: 'renting', locked: false, uptime: 98.7, earnings: 124.50, todayEarnings: 18.40, efficiency: 95, schedule: { mon: [9, 17], tue: [9, 17], wed: [9, 17] } },
    { id: 2, name: 'RTX 3090', status: 'idle', locked: false, uptime: 95.2, earnings: 87.30, todayEarnings: 0, efficiency: 78, schedule: { thu: [18, 23], fri: [18, 23] } },
    { id: 3, name: 'RTX 4080', status: 'offline', locked: true, uptime: 0, earnings: 0, todayEarnings: 0, efficiency: 0, schedule: {} },
  ]);

  const [calcHours, setCalcHours] = useState(8);
  const [calcGPUs, setCalcGPUs] = useState(1);

  const [availableGPUs, setAvailableGPUs] = useState([
    { id: 1, name: 'RTX 4090', provider: 'Akash', price: 2.80, available: 3, vram: '24GB', performance: 95, bestDeal: true, providerScore: 4.8, favorites: 1240, priceHistory: [3.2, 3.1, 2.95, 2.88, 2.80] },
    { id: 2, name: 'RTX 4080', provider: 'Vast.ai', price: 1.90, available: 7, vram: '16GB', performance: 85, providerScore: 4.5, favorites: 890, priceHistory: [2.1, 2.0, 1.95, 1.92, 1.90] },
    { id: 3, name: 'RTX 3090', provider: 'Render', price: 1.50, available: 12, vram: '24GB', performance: 75, providerScore: 4.6, favorites: 1050, priceHistory: [1.65, 1.60, 1.58, 1.52, 1.50] },
    { id: 4, name: 'A100 40GB', provider: 'io.net', price: 4.20, available: 0, vram: '40GB', performance: 98, providerScore: 4.9, favorites: 2100, priceHistory: [4.5, 4.4, 4.35, 4.25, 4.20] },
    { id: 5, name: 'RTX 4070 Ti', provider: 'Akash', price: 1.40, available: 5, vram: '12GB', performance: 70, providerScore: 4.7, favorites: 650, priceHistory: [1.55, 1.50, 1.48, 1.42, 1.40] },
  ]);

  const bgColor = darkMode ? 'bg-gray-900' : 'bg-gray-50';
  const textColor = darkMode ? 'text-white' : 'text-gray-900';
  const cardBg = darkMode ? 'bg-gray-800' : 'bg-white';
  const borderColor = darkMode ? 'border-gray-700' : 'border-gray-200';

  const translations = {
    en: { home: 'Home', dashboard: 'Dashboard', marketplace: 'Marketplace', wallet: 'Wallet', earnings: 'Earnings', settings: 'Settings', myGPUs: 'My GPUs' },
    es: { home: 'Inicio', dashboard: 'Panel', marketplace: 'Mercado', wallet: 'Cartera', earnings: 'Ganancias', settings: 'Ajustes', myGPUs: 'Mis GPUs' },
    zh: { home: '首页', dashboard: '仪表板', marketplace: '市场', wallet: '钱包', earnings: '收益', settings: '设置', myGPUs: '我的GPU' },
  };

  const t = translations[language] || translations.en;

  const skillLevels = {
    beginner: { label: 'Beginner', color: currentTheme.primary, description: 'Simple and easy' },
    intermediate: { label: 'Intermediate', color: currentTheme.primary, description: 'More options' },
    expert: { label: 'Expert', color: currentTheme.primary, description: 'Full control' },
  };

  const toggleBookmark = (gpuId) => {
    setBookmarkedGPUs(prev => 
      prev.includes(gpuId) ? prev.filter(id => id !== gpuId) : [...prev, gpuId]
    );
  };

  const toggleCompareSelection = (gpuId) => {
    setSelectedForCompare(prev => 
      prev.includes(gpuId) ? prev.filter(id => id !== gpuId) : prev.length < 3 ? [...prev, gpuId] : prev
    );
  };

  const PerformanceInsights = ({ gpu }) => (
    <div className={`mt-4 p-4 rounded-lg ${darkMode ? 'bg-blue-900/20 border-blue-700' : 'bg-blue-50 border-blue-200'} border`}>
      <div className="flex items-center space-x-2 mb-3">
        <Lightbulb className="text-yellow-500" size={20} />
        <span className={`font-bold ${darkMode ? 'text-blue-300' : 'text-blue-700'}`}>Performance Insights</span>
      </div>
      <div className="space-y-2 text-sm">
        {gpu.efficiency < 85 && (
          <div className={darkMode ? 'text-yellow-300' : 'text-yellow-700'}>
            ⚡ Your efficiency is {gpu.efficiency}%. Consider adjusting your schedule for peak demand hours.
          </div>
        )}
        {gpu.status === 'idle' && (
          <div className={darkMode ? 'text-orange-300' : 'text-orange-700'}>
            💡 Your GPU is idle. Turn it on to start earning! Estimated: ${(8 * 0.9 * gpu.efficiency / 100).toFixed(2)}/day
          </div>
        )}
        {gpu.uptime > 95 && (
          <div className={darkMode ? 'text-green-300' : 'text-green-700'}>
            ✅ Excellent uptime! You're in the top 10% of providers.
          </div>
        )}
        {gpu.todayEarnings > 15 && (
          <div className={darkMode ? 'text-green-300' : 'text-green-700'}>
            🎉 Great day! You've earned ${gpu.todayEarnings} so far.
          </div>
        )}
      </div>
    </div>
  );

  const PriceHistoryChart = ({ history, currentPrice }) => (
    <div className="mt-4 p-4 rounded-lg bg-gray-100 dark:bg-gray-700">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-bold">5-Day Price Trend</span>
        <span className="text-xs text-green-500">📉 Trending Down</span>
      </div>
      <div className="h-24 flex items-end space-x-2">
        {history.map((price, i) => {
          const maxPrice = Math.max(...history);
          const heightPercent = (price / maxPrice) * 100;
          return (
            <div key={i} className="flex-1 flex flex-col items-center">
              <div className="text-xs mb-1">${price}</div>
              <div 
                className={`w-full ${i === history.length - 1 ? currentTheme.primary : 'bg-gray-400'} rounded-t transition-all`}
                style={{ height: `${heightPercent}%` }}
              />
            </div>
          );
        })}
      </div>
      <div className="text-xs text-center mt-2 text-gray-500">Day 1 → Day 5</div>
    </div>
  );

  const CompareModal = () => {
    if (selectedForCompare.length === 0) return null;
    
    const compareGPUs = availableGPUs.filter(gpu => selectedForCompare.includes(gpu.id));
    
    return (
      <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
        <div className={`${cardBg} rounded-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto`}>
          <div className={`p-6 border-b ${borderColor} flex items-center justify-between sticky top-0 ${cardBg}`}>
            <h2 className={`text-2xl font-bold ${textColor}`}>Compare GPUs</h2>
            <button onClick={() => setCompareMode(false)}>
              <X size={24} className={textColor} />
            </button>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {compareGPUs.map(gpu => (
                <div key={gpu.id} className={`${darkMode ? 'bg-gray-700' : 'bg-gray-50'} p-4 rounded-lg`}>
                  <div className="text-center mb-4">
                    <Cpu className={currentTheme.accent} size={40} />
                    <h3 className={`text-xl font-bold mt-2 ${textColor}`}>{gpu.name}</h3>
                    <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>{gpu.provider}</div>
                  </div>
                  
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Price</span>
                      <span className={`font-bold ${textColor}`}>${gpu.price}/hr</span>
                    </div>
                    <div className="flex justify-between">
                      <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>VRAM</span>
                      <span className={`font-bold ${textColor}`}>{gpu.vram}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Performance</span>
                      <span className={`font-bold ${textColor}`}>{gpu.performance}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Provider Score</span>
                      <span className={`font-bold ${textColor}`}>⭐ {gpu.providerScore}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Available</span>
                      <span className={`font-bold ${gpu.available > 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {gpu.available > 0 ? `${gpu.available} units` : 'Sold out'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Popularity</span>
                      <span className={`font-bold ${textColor}`}>❤️ {gpu.favorites}</span>
                    </div>
                  </div>

                  <button 
                    disabled={gpu.available === 0}
                    className={`w-full mt-4 py-3 rounded-lg font-semibold ${
                      gpu.available > 0 ? currentTheme.primary + ' text-white' : 'bg-gray-300 text-gray-500'
                    }`}
                  >
                    {gpu.available > 0 ? 'Rent Now' : 'Unavailable'}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const MyGPUsWidget = () => (
    <div className="fixed right-4 top-20 z-40">
      <button
        onClick={() => setMyGPUsOpen(!myGPUsOpen)}
        className={`${currentTheme.primary} text-white px-4 py-2 rounded-lg font-semibold shadow-lg hover:opacity-90 flex items-center space-x-2`}>
        <Cpu size={20} />
        <span>{t.myGPUs}</span>
        <span className="bg-white text-blue-500 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
          {myGPUs.length}
        </span>
      </button>

      {myGPUsOpen && (
        <div className={`${cardBg} border ${borderColor} rounded-xl shadow-2xl mt-2 w-80 max-h-[600px] overflow-y-auto`}>
          <div className={`p-4 border-b ${borderColor} flex items-center justify-between`}>
            <h3 className={`font-bold ${textColor}`}>My GPU Dashboard</h3>
            <button onClick={() => setMyGPUsOpen(false)}>
              <X size={20} className={darkMode ? 'text-gray-400' : 'text-gray-600'} />
            </button>
          </div>

          <div className="p-4 space-y-4">
            {myGPUs.map(gpu => (
              <div key={gpu.id} className={`p-4 rounded-lg border-2 ${gpu.status === 'renting' ? 'border-green-500 bg-green-500/5' : gpu.status === 'offline' ? 'border-gray-500 bg-gray-500/5' : 'border-yellow-500 bg-yellow-500/5'}`}>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Cpu className={gpu.status === 'renting' ? 'text-green-500' : gpu.status === 'offline' ? 'text-gray-500' : 'text-yellow-500'} size={24} />
                    <div>
                      <div className={`font-bold ${textColor}`}>{gpu.name}</div>
                      <div className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-600'} capitalize`}>{gpu.status}</div>
                    </div>
                  </div>
                  <button onClick={() => {
                    const updated = myGPUs.map(g => g.id === gpu.id ? {...g, locked: !g.locked} : g);
                    setMyGPUs(updated);
                  }}>
                    {gpu.locked ? <Lock size={20} className="text-red-500" /> : <Unlock size={20} className="text-gray-400" />}
                  </button>
                </div>

                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Uptime</span>
                    <span className={`font-semibold ${textColor}`}>{gpu.uptime}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Efficiency</span>
                    <span className={`font-semibold ${gpu.efficiency > 85 ? 'text-green-500' : 'text-yellow-500'}`}>{gpu.efficiency}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Earned Today</span>
                    <span className="font-semibold text-green-500">${gpu.todayEarnings}</span>
                  </div>
                </div>

                {skillMode !== 'beginner' && (
                  <PerformanceInsights gpu={gpu} />
                )}

                <div className="flex space-x-2 mt-3">
                  {gpu.status === 'offline' ? (
                    <button className="flex-1 bg-green-500 text-white py-2 rounded-lg text-sm font-semibold hover:bg-green-600">
                      Turn On
                    </button>
                  ) : (
                    <button className="flex-1 bg-gray-500 text-white py-2 rounded-lg text-sm font-semibold hover:bg-gray-600">
                      Turn Off
                    </button>
                  )}
                  <button className={`flex-1 ${darkMode ? 'bg-gray-700' : 'bg-gray-200'} ${textColor} py-2 rounded-lg text-sm font-semibold`}>
                    Edit
                  </button>
                </div>
              </div>
            ))}

            <button className={`w-full ${currentTheme.primary} text-white py-3 rounded-lg font-semibold hover:opacity-90 flex items-center justify-center space-x-2`}>
              <span>+</span>
              <span>Add GPU</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );

  const NavBar = () => (
    <nav className={`${cardBg} border-b ${borderColor} sticky top-0 z-50`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-2">
              <Zap className={currentTheme.accent} size={32} />
              <span className={`text-xl font-bold ${textColor}`}>GP4U</span>
            </div>
            
            <div className="hidden md:flex space-x-1">
              {[
                { id: 'home', icon: Home, label: t.home },
                { id: 'dashboard', icon: Activity, label: t.dashboard },
                { id: 'marketplace', icon: Server, label: t.marketplace },
                { id: 'wallet', icon: Wallet, label: t.wallet },
                { id: 'earnings', icon: TrendingUp, label: t.earnings },
              ].map(item => (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${
                    currentPage === item.id 
                      ? currentTheme.primary + ' text-white'
                      : `${darkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-600 hover:bg-gray-100'}`
                  }`}>
                  <item.icon size={18} />
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="hidden lg:flex items-center space-x-2">
              {Object.entries(skillLevels).map(([key, val]) => (
                <button
                  key={key}
                  onClick={() => setSkillMode(key)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition ${
                    skillMode === key 
                      ? val.color + ' text-white'
                      : `${darkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-200 text-gray-600'}`
                  }`}>
                  {val.label}
                </button>
              ))}
            </div>

            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className={`hidden sm:block px-3 py-1 rounded-lg text-sm ${cardBg} ${textColor} border ${borderColor}`}>
              <option value="en">EN</option>
              <option value="es">ES</option>
              <option value="zh">中文</option>
            </select>

            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`p-2 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-200'}`}>
              {darkMode ? <Sun size={20} className="text-yellow-400" /> : <Moon size={20} className="text-gray-600" />}
            </button>

            <button
              onClick={() => setCurrentPage('settings')}
              className={`p-2 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-200'}`}>
              <Settings size={20} className={darkMode ? 'text-gray-300' : 'text-gray-600'} />
            </button>

            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg"
            >
              {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {mobileMenuOpen && (
        <div className={`md:hidden ${cardBg} border-t ${borderColor}`}>
          <div className="px-4 py-4 space-y-2">
            {[
              { id: 'home', icon: Home, label: t.home },
              { id: 'dashboard', icon: Activity, label: t.dashboard },
              { id: 'marketplace', icon: Server, label: t.marketplace },
              { id: 'wallet', icon: Wallet, label: t.wallet },
              { id: 'earnings', icon: TrendingUp, label: t.earnings },
            ].map(item => (
              <button
                key={item.id}
                onClick={() => handlePageChange(item.id)}
                className={`flex items-center space-x-3 w-full px-4 py-3 rounded-lg ${currentPage === item.id ? currentTheme.primary + ' text-white' : `${darkMode ? 'text-gray-300' : 'text-gray-600'}`}`}>
                <item.icon size={20} />
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </nav>
  );

  const handlePageChange = (page) => { setCurrentPage(page); setMobileMenuOpen(false); };

  const HomePage = () => {
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
            <button className={`${currentTheme.primary} text-white px-8 py-4 rounded-lg font-semibold hover:opacity-90 transition`}>
              Start Earning Today
            </button>
            <button 
              onClick={() => setCurrentPage('marketplace')}
              className={`${cardBg} ${textColor} px-8 py-4 rounded-lg font-semibold border ${borderColor} hover:border-blue-500 transition`}>
              Browse GPUs
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {[
            { icon: 'Shield', title: 'Safe & Secure', desc: 'Your money and data are protected with bank-level encryption and escrow services', color: 'text-green-500' },
            { icon: DollarSign, title: 'Best Prices Guaranteed', desc: 'Our arbitrage engine automatically finds the cheapest GPUs across all major providers', color: currentTheme.accent },
            { icon: Zap, title: 'Instant Setup', desc: 'Start earning in minutes. No technical knowledge required', color: 'text-purple-500' },
          ].map((feature, i) => (
            <div key={i} className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
              {/* Icon placeholder */}
              <div className="h-10" />
              <h3 className={`text-xl font-bold mt-4 mb-2 ${textColor}`}>{feature.title}</h3>
              <p className={darkMode ? 'text-gray-400' : 'text-gray-600'}>{feature.desc}</p>
            </div>
          ))}
        </div>

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
                  <span className="text-2xl font-bold">{calcGPUs} GPU{calcGPUs > 1 ? 's' : ''}</span>
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
  };

  // Render simplified; other pages above are defined inline as needed
  return (
    <div className={`min-h-screen ${bgColor} ${textColor} transition-colors duration-200`}>
      <NavBar />
      <MyGPUsWidget />
      {currentPage === 'home' && <HomePage />}
      {currentPage === 'dashboard' && <Dashboard />}
      {currentPage === 'marketplace' && <Marketplace />}
      {currentPage === 'wallet' && <WalletPage />}
      {currentPage === 'earnings' && <EarningsPage />}
      {currentPage === 'settings' && <SettingsPage />}
    </div>
  );
}
