import React, { useState, useEffect } from 'react';
import { Sun, Moon, Zap, Server, Wallet, Settings, Home, TrendingUp, Clock, DollarSign, Cpu, Activity, User, Menu, X, ChevronDown, ChevronUp, Lock, Unlock, Star, GitCompare, Award, Info, BarChart2, Lightbulb, Shield } from 'lucide-react';
import axios from 'axios';

export default function GP4UPlatform() {
  const [currentPage, setCurrentPage] = useState('marketplace');
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

  // Backend data state
  const [availableGPUs, setAvailableGPUs] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [arbitrageOpps, setArbitrageOpps] = useState([]);
  const [loading, setLoading] = useState(true);

  // Community Themes
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

  // Load data from backend
  useEffect(() => {
    loadBackendData();
    const interval = setInterval(loadBackendData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadBackendData = async () => {
    try {
      const [statsRes, gpusRes, arbRes] = await Promise.all([
        axios.get('/api/dashboard'),
        axios.get('/api/gpus'),
        axios.get('/api/arbitrage')
      ]);

      setDashboardStats(statsRes.data);
      
      // Transform backend GPU data to match component format
      const transformedGPUs = gpusRes.data
        .filter(g => g.availability === 'Available')
        .map(g => ({
          id: g.id,
          name: g.gpu_model,
          provider: g.provider,
          price: g.total_price,
          available: 1,
          vram: `${g.vram_gb}GB`,
          performance: Math.round(g.uptime_percent),
          bestDeal: false,
          providerScore: (g.uptime_percent / 20).toFixed(1),
          favorites: Math.floor(Math.random() * 2000),
          priceHistory: [
            g.total_price * 1.1,
            g.total_price * 1.05,
            g.total_price * 1.02,
            g.total_price * 1.01,
            g.total_price
          ],
          location: g.location,
          uptime: g.uptime_percent
        }));

      setAvailableGPUs(transformedGPUs);
      setArbitrageOpps(arbRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading backend data:', error);
      setLoading(false);
    }
  };

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

  // Performance Insights Component
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

  // Price History Chart
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
              <div className="text-xs mb-1">${price.toFixed(2)}</div>
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

  // Compare Modal
  const CompareModal = () => {
    const compareGPUs = availableGPUs.filter(g => selectedForCompare.includes(g.id));
    if (compareGPUs.length === 0) return null;

    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div className={`${cardBg} rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto`}>
          <div className="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
            <h2 className={`text-2xl font-bold ${textColor}`}>Compare GPUs</h2>
            <button onClick={() => setCompareMode(false)} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded">
              <X size={24} />
            </button>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {compareGPUs.map(gpu => (
                <div key={gpu.id} className={`p-4 border ${borderColor} rounded-lg`}>
                  <h3 className={`font-bold text-lg mb-2 ${textColor}`}>{gpu.name}</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Provider:</span>
                      <span className={textColor}>{gpu.provider}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Price:</span>
                      <span className={`font-bold ${currentTheme.accent}`}>${gpu.price}/hr</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">VRAM:</span>
                      <span className={textColor}>{gpu.vram}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Performance:</span>
                      <span className={textColor}>{gpu.performance}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Rating:</span>
                      <span className={textColor}>⭐ {gpu.providerScore}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Navigation Bar
  const NavBar = () => (
    <nav className={`${cardBg} border-b ${borderColor} sticky top-0 z-40`}>
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-2">
              <Zap className={currentTheme.accent} size={28} />
              <span className={`text-xl font-bold ${textColor}`}>GP4U</span>
            </div>

            <div className="hidden md:flex space-x-4">
              {[
                { name: 'home', icon: Home, label: t.home },
                { name: 'marketplace', icon: Server, label: t.marketplace },
                { name: 'dashboard', icon: Activity, label: t.dashboard },
                { name: 'wallet', icon: Wallet, label: t.wallet },
                { name: 'earnings', icon: TrendingUp, label: t.earnings },
              ].map(item => (
                <button
                  key={item.name}
                  onClick={() => setCurrentPage(item.name)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition ${
                    currentPage === item.name
                      ? `${currentTheme.primary} text-white`
                      : `${darkMode ? 'text-gray-300 hover:bg-gray-700' : 'text-gray-600 hover:bg-gray-100'}`
                  }`}
                >
                  <item.icon size={18} />
                  <span>{item.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`p-2 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`}
            >
              {darkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            <button
              onClick={() => setCurrentPage('settings')}
              className={`p-2 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`}
            >
              <Settings size={20} />
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
    </nav>
  );

  // My GPUs Widget (Floating)
  const MyGPUsWidget = () => (
    <div className="fixed bottom-4 right-4 z-30">
      <button
        onClick={() => setMyGPUsOpen(!myGPUsOpen)}
        className={`${currentTheme.primary} text-white px-6 py-3 rounded-full shadow-lg hover:shadow-xl transition flex items-center space-x-2`}
      >
        <Server size={20} />
        <span className="font-bold">{t.myGPUs} ({myGPUs.length})</span>
        {myGPUsOpen ? <ChevronDown size={16} /> : <ChevronUp size={16} />}
      </button>

      {myGPUsOpen && (
        <div className={`${cardBg} rounded-lg shadow-xl mt-2 w-80 max-h-96 overflow-y-auto border ${borderColor}`}>
          <div className="p-4 space-y-3">
            {myGPUs.map(gpu => (
              <div key={gpu.id} className={`p-3 border ${borderColor} rounded-lg`}>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <div className={`font-bold ${textColor}`}>{gpu.name}</div>
                    <div className="text-sm text-gray-500">
                      {gpu.status === 'renting' && '🟢 Renting'}
                      {gpu.status === 'idle' && '🟡 Idle'}
                      {gpu.status === 'offline' && '🔴 Offline'}
                    </div>
                  </div>
                  <button onClick={() => {
                    setMyGPUs(prev => prev.map(g => 
                      g.id === gpu.id ? {...g, locked: !g.locked} : g
                    ));
                  }}>
                    {gpu.locked ? <Lock size={18} className="text-red-500" /> : <Unlock size={18} className="text-green-500" />}
                  </button>
                </div>
                <div className="text-sm space-y-1">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Uptime:</span>
                    <span className={textColor}>{gpu.uptime}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Total Earned:</span>
                    <span className="font-bold text-green-500">${gpu.earnings}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Today:</span>
                    <span className="font-bold text-green-500">${gpu.todayEarnings}</span>
                  </div>
                </div>
                {skillMode !== 'beginner' && <PerformanceInsights gpu={gpu} />}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  // Home Page
  const HomePage = () => (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className={`text-5xl font-bold mb-4 ${textColor}`}>
          Welcome to GP4U
        </h1>
        <p className={`text-xl ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
          The Kayak of GPUs - Compare • Deploy • Save
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className={`${cardBg} p-6 rounded-xl border ${borderColor} text-center`}>
          <Server className={`${currentTheme.accent} mx-auto mb-4`} size={48} />
          <h3 className={`text-xl font-bold mb-2 ${textColor}`}>Compare Prices</h3>
          <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Find the best GPU deals across multiple providers
          </p>
        </div>

        <div className={`${cardBg} p-6 rounded-xl border ${borderColor} text-center`}>
          <DollarSign className={`${currentTheme.accent} mx-auto mb-4`} size={48} />
          <h3 className={`text-xl font-bold mb-2 ${textColor}`}>Save Money</h3>
          <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            Up to 40% savings with arbitrage detection
          </p>
        </div>

        <div className={`${cardBg} p-6 rounded-xl border ${borderColor} text-center`}>
          <Zap className={`${currentTheme.accent} mx-auto mb-4`} size={48} />
          <h3 className={`text-xl font-bold mb-2 ${textColor}`}>Deploy Fast</h3>
          <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
            One-click deployment to the best provider
          </p>
        </div>
      </div>

      {dashboardStats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className={`${cardBg} p-6 rounded-xl border ${borderColor} text-center`}>
            <div className={`text-3xl font-bold ${currentTheme.accent}`}>
              {dashboardStats.total_listings}
            </div>
            <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>GPUs Available</div>
          </div>
          <div className={`${cardBg} p-6 rounded-xl border ${borderColor} text-center`}>
            <div className={`text-3xl font-bold ${currentTheme.accent}`}>
              ${dashboardStats.avg_price}
            </div>
            <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Avg Price/hr</div>
          </div>
          <div className={`${cardBg} p-6 rounded-xl border ${borderColor} text-center`}>
            <div className={`text-3xl font-bold ${currentTheme.accent}`}>
              ${dashboardStats.cheapest_gpu}
            </div>
            <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Best Deal</div>
          </div>
          <div className={`${cardBg} p-6 rounded-xl border ${borderColor} text-center`}>
            <div className={`text-3xl font-bold ${currentTheme.accent}`}>
              {dashboardStats.best_arbitrage_percent}%
            </div>
            <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Best Arbitrage</div>
          </div>
        </div>
      )}
    </div>
  );

  // Marketplace Page
  const Marketplace = () => (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className={`text-3xl font-bold ${textColor}`}>GPU Marketplace</h1>
        <div className="flex space-x-2">
          <button
            onClick={() => setCompareMode(!compareMode)}
            className={`px-4 py-2 rounded-lg font-semibold ${
              compareMode ? `${currentTheme.primary} text-white` : `${darkMode ? 'bg-gray-700' : 'bg-gray-200'} ${textColor}`
            }`}
          >
            <GitCompare size={18} className="inline mr-2" />
            Compare Mode {selectedForCompare.length > 0 && `(${selectedForCompare.length})`}
          </button>
          {selectedForCompare.length >= 2 && (
            <button
              onClick={() => setCompareMode(true)}
              className={`${currentTheme.primary} text-white px-4 py-2 rounded-lg font-semibold`}
            >
              View Comparison
            </button>
          )}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="text-xl">Loading GPUs...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {availableGPUs.map(gpu => (
            <div key={gpu.id} className={`${cardBg} rounded-xl border ${borderColor} p-6 hover:shadow-lg transition`}>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className={`text-xl font-bold ${textColor} mb-1`}>{gpu.name}</h3>
                  <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                    {gpu.provider} • {gpu.vram}
                  </p>
                </div>
                <div className="flex space-x-2">
                  {compareMode && (
                    <button
                      onClick={() => toggleCompareSelection(gpu.id)}
                      className={`p-2 rounded ${
                        selectedForCompare.includes(gpu.id)
                          ? `${currentTheme.primary} text-white`
                          : `${darkMode ? 'bg-gray-700' : 'bg-gray-200'}`
                      }`}
                    >
                      <GitCompare size={18} />
                    </button>
                  )}
                  <button
                    onClick={() => toggleBookmark(gpu.id)}
                    className={`p-2 rounded ${
                      bookmarkedGPUs.includes(gpu.id)
                        ? 'bg-yellow-500 text-white'
                        : `${darkMode ? 'bg-gray-700' : 'bg-gray-200'}`
                    }`}
                  >
                    <Star size={18} />
                  </button>
                </div>
              </div>

              <div className="mb-4">
                <div className={`text-3xl font-bold ${currentTheme.accent}`}>
                  ${gpu.price.toFixed(2)}<span className="text-lg">/hr</span>
                </div>
                <div className="text-sm text-gray-500">
                  ⭐ {gpu.providerScore} • 💝 {gpu.favorites} favorites
                </div>
              </div>

              <div className="space-y-2 mb-4 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Performance:</span>
                  <span className={textColor}>{gpu.performance}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Available:</span>
                  <span className={textColor}>{gpu.available} units</span>
                </div>
                {skillMode !== 'beginner' && (
                  <div className="flex justify-between">
                    <span className="text-gray-500">Location:</span>
                    <span className={textColor}>{gpu.location}</span>
                  </div>
                )}
              </div>

              {skillMode === 'expert' && (
                <button
                  onClick={() => setShowPriceHistory(showPriceHistory === gpu.id ? null : gpu.id)}
                  className={`text-sm ${currentTheme.accent} mb-2`}
                >
                  {showPriceHistory === gpu.id ? 'Hide' : 'Show'} Price History
                </button>
              )}

              {showPriceHistory === gpu.id && (
                <PriceHistoryChart history={gpu.priceHistory} currentPrice={gpu.price} />
              )}

              <button className={`${currentTheme.primary} text-white w-full py-3 rounded-lg font-semibold hover:opacity-90 transition`}>
                Deploy Now
              </button>
            </div>
          ))}
        </div>
      )}

      {compareMode && <CompareModal />}
    </div>
  );

  // Dashboard Page
  const Dashboard = () => (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className={`text-3xl font-bold mb-8 ${textColor}`}>Dashboard</h1>
      
      {dashboardStats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
            <div className="flex items-center space-x-3 mb-2">
              <Server className={currentTheme.accent} size={24} />
              <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Total GPUs</span>
            </div>
            <div className={`text-3xl font-bold ${textColor}`}>{dashboardStats.total_listings}</div>
          </div>

          <div className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
            <div className="flex items-center space-x-3 mb-2">
              <DollarSign className={currentTheme.accent} size={24} />
              <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Avg Price</span>
            </div>
            <div className={`text-3xl font-bold ${textColor}`}>${dashboardStats.avg_price}/hr</div>
          </div>

          <div className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
            <div className="flex items-center space-x-3 mb-2">
              <TrendingUp className={currentTheme.accent} size={24} />
              <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Arbitrage</span>
            </div>
            <div className={`text-3xl font-bold ${textColor}`}>{dashboardStats.best_arbitrage_percent}%</div>
          </div>

          <div className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
            <div className="flex items-center space-x-3 mb-2">
              <Award className={currentTheme.accent} size={24} />
              <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Best Deal</span>
            </div>
            <div className={`text-3xl font-bold ${textColor}`}>${dashboardStats.cheapest_gpu}/hr</div>
          </div>
        </div>
      )}

      {/* Arbitrage Opportunities */}
      {arbitrageOpps.length > 0 && (
        <div className="mb-8">
          <h2 className={`text-2xl font-bold mb-4 ${textColor}`}>Arbitrage Opportunities</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {arbitrageOpps.slice(0, 4).map((opp, i) => (
              <div key={i} className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
                <h3 className={`font-bold text-lg mb-3 ${textColor}`}>{opp.gpu_model}</h3>
                <div className="flex justify-between items-center">
                  <div>
                    <div className="text-sm text-gray-500">Cheapest</div>
                    <div className={`font-bold ${currentTheme.accent}`}>{opp.cheapest_provider}</div>
                    <div className={`text-lg font-bold ${textColor}`}>${opp.cheapest_price.toFixed(2)}/hr</div>
                  </div>
                  <div className="text-center">
                    <div className={`text-2xl font-bold text-green-500`}>
                      {opp.savings_percent.toFixed(1)}%
                    </div>
                    <div className="text-sm text-gray-500">savings</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Most Expensive</div>
                    <div className={`font-bold ${textColor}`}>{opp.expensive_provider}</div>
                    <div className={`text-lg font-bold ${textColor}`}>${opp.expensive_price.toFixed(2)}/hr</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  // Wallet Page
  const WalletPage = () => (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className={`text-3xl font-bold mb-8 ${textColor}`}>Wallet</h1>

      <div className={`${cardBg} p-6 rounded-xl border ${borderColor} mb-6`}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>Current Balance</div>
            <div className={`text-4xl font-bold ${currentTheme.accent}`}>${balance.toFixed(2)}</div>
          </div>
          <Wallet className={currentTheme.accent} size={48} />
        </div>
        <div className="flex space-x-3">
          <button className={`${currentTheme.primary} text-white px-6 py-3 rounded-lg font-semibold flex-1`}>
            Add Funds
          </button>
          <button className={`${darkMode ? 'bg-gray-700' : 'bg-gray-200'} ${textColor} px-6 py-3 rounded-lg font-semibold flex-1`}>
            Withdraw
          </button>
        </div>
      </div>

      <div className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>Recent Transactions</h2>
        <div className="space-y-3">
          {[
            { type: 'earning', amount: 18.40, desc: 'RTX 4090 Rental', time: '2 hours ago' },
            { type: 'withdraw', amount: -50.00, desc: 'Withdrawal to Bank', time: '1 day ago' },
            { type: 'earning', amount: 12.75, desc: 'RTX 3090 Rental', time: '2 days ago' },
          ].map((tx, i) => (
            <div key={i} className={`flex justify-between items-center p-3 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
              <div className="flex items-center space-x-3">
                <div className={`w-10 h-10 rounded-full ${tx.type === 'earning' ? 'bg-green-500' : 'bg-red-500'} flex items-center justify-center text-white`}>
                  {tx.type === 'earning' ? '↑' : '↓'}
                </div>
                <div>
                  <div className={`font-medium ${textColor}`}>{tx.desc}</div>
                  <div className="text-sm text-gray-500">{tx.time}</div>
                </div>
              </div>
              <div className={`font-bold ${tx.type === 'earning' ? 'text-green-500' : 'text-red-500'}`}>
                {tx.type === 'earning' ? '+' : ''${tx.amount.toFixed(2)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  // Earnings Page
  const EarningsPage = () => (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className={`text-3xl font-bold mb-8 ${textColor}`}>Earnings</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {[
          { label: 'Today', amount: myGPUs.reduce((sum, gpu) => sum + gpu.todayEarnings, 0), icon: Clock },
          { label: 'This Month', amount: earnings, icon: TrendingUp },
          { label: 'All Time', amount: earnings * 2.5, icon: Award },
        ].map((stat, i) => (
          <div key={i} className={`${cardBg} p-6 rounded-xl border ${borderColor}`}>
            <div className="flex items-center space-x-3 mb-2">
              <stat.icon className={currentTheme.accent} size={24} />
              <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>{stat.label}</span>
            </div>
            <div className={`text-3xl font-bold text-green-500`}>${stat.amount.toFixed(2)}</div>
          </div>
        ))}
      </div>

      <div className={`${cardBg} p-6 rounded-xl border ${borderColor} mb-6`}>
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>Earnings by GPU</h2>
        <div className="space-y-4">
          {myGPUs.map(gpu => (
            <div key={gpu.id}>
              <div className="flex justify-between mb-2">
                <span className={`font-medium ${textColor}`}>{gpu.name}</span>
                <span className="font-bold text-green-500">${gpu.earnings.toFixed(2)}</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className={`${currentTheme.primary} h-2 rounded-full`}
                  style={{ width: `${(gpu.earnings / Math.max(...myGPUs.map(g => g.earnings))) * 100}%` }}
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
            Next automatic payout in 3 days: <span className="font-bold">$124.80</span>
          </p>
        </div>
        <button className={`${currentTheme.primary} text-white w-full py-3 rounded-lg font-semibold hover:opacity-90`}>
          Request Early Payout (2% fee)
        </button>
      </div>
    </div>
  );

  // Settings Page
  const SettingsPage = () => (
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
              className={`p-4 rounded-lg text-left border-2 transition ${
                communityTheme === key
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
              className={`px-4 py-2 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-200'} font-medium`}
            >
              {darkMode ? '🌙 Dark' : '☀️ Light'}
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <div className={`font-medium ${textColor}`}>Skill Level</div>
              <div className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>{skillLevels[skillMode].description}</div>
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

      <div className={`${cardBg} p-6 rounded-xl border ${borderColor} mb-6`}>
        <h2 className={`text-xl font-bold mb-4 ${textColor}`}>Profit Mode</h2>
        <div className="space-y-4">
          <button
            onClick={() => setProfitMode('rental')}
            className={`w-full p-4 rounded-lg text-left border-2 transition ${
              profitMode === 'rental'
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
            className={`w-full p-4 rounded-lg text-left border-2 transition ${
              profitMode === 'cluster'
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
