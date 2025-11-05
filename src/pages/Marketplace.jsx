/**
 * GPU Marketplace Page
 * Browse, search, and book GPUs with arbitrage detection
 */

import React, { useState, useEffect } from 'react';
import { gpuAPI, arbitrageAPI } from '../services/api';
import { useToast } from '../context/ToastContext';
import ReservationBooking from '../components/ReservationBooking';
import {
  Search, Filter, Zap, Server, TrendingDown, Star,
  Loader, DollarSign, Cpu, MapPin, Activity, ChevronDown
} from 'lucide-react';

export default function Marketplace({ darkMode, onCreateCluster }) {
  const [gpus, setGpus] = useState([]);
  const [filteredGPUs, setFilteredGPUs] = useState([]);
  const [arbitrageOpps, setArbitrageOpps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    model: '',
    minVram: null,
    maxPrice: null,
    provider: '',
    location: ''
  });
  const [showFilters, setShowFilters] = useState(false);
  const [selectedGpu, setSelectedGpu] = useState(null);
  const [showBooking, setShowBooking] = useState(false);
  const toast = useToast();

  const cardBg = darkMode ? 'bg-gray-800' : 'bg-white';
  const textColor = darkMode ? 'text-white' : 'text-gray-900';
  const borderColor = darkMode ? 'border-gray-700' : 'border-gray-200';

  useEffect(() => {
    loadMarketplaceData();
    const interval = setInterval(loadMarketplaceData, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    applyFilters();
  }, [gpus, searchTerm, filters]);

  const loadMarketplaceData = async () => {
    try {
      setLoading(true);
      const [gpusData, arbData] = await Promise.all([
        gpuAPI.search(),
        arbitrageAPI.getOpportunities()
      ]);

      setGpus(gpusData);
      setArbitrageOpps(arbData);
    } catch (err) {
      toast.error('Failed to load marketplace data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...gpus];

    // Search term
    if (searchTerm) {
      filtered = filtered.filter(gpu =>
        gpu.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
        gpu.provider.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filters
    if (filters.model) {
      filtered = filtered.filter(gpu => gpu.model.includes(filters.model));
    }
    if (filters.minVram) {
      filtered = filtered.filter(gpu => gpu.vram_gb >= filters.minVram);
    }
    if (filters.maxPrice) {
      filtered = filtered.filter(gpu => parseFloat(gpu.price_per_hour) <= filters.maxPrice);
    }
    if (filters.provider) {
      filtered = filtered.filter(gpu => gpu.provider === filters.provider);
    }
    if (filters.location) {
      filtered = filtered.filter(gpu => gpu.location.includes(filters.location));
    }

    setFilteredGPUs(filtered);
  };

  const handleBook = (gpu) => {
    setSelectedGpu(gpu);
    setShowBooking(true);
  };

  const getBestDealBadge = (gpu) => {
    const isArbitrage = arbitrageOpps.some(opp =>
      opp.cheapest_provider === gpu.provider &&
      opp.gpu_type.includes(gpu.model.split(' ')[0])
    );

    if (isArbitrage) {
      return (
        <span className="inline-flex items-center space-x-1 px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-full text-xs font-medium">
          <TrendingDown size={12} />
          <span>Best Deal</span>
        </span>
      );
    }
    return null;
  };

  const getProviders = () => {
    return [...new Set(gpus.map(gpu => gpu.provider))];
  };

  const getModels = () => {
    return [...new Set(gpus.map(gpu => gpu.model))];
  };

  if (loading) {
    return (
      <div className={`${cardBg} rounded-xl p-12 flex flex-col items-center justify-center`}>
        <Loader className="animate-spin text-blue-500 mb-4" size={48} />
        <p className="text-gray-500">Loading marketplace...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-3xl font-bold ${textColor} mb-2`}>GPU Marketplace</h2>
          <p className="text-gray-500">
            {filteredGPUs.length} GPUs available • {arbitrageOpps.length} arbitrage opportunities
          </p>
        </div>
        <button
          onClick={onCreateCluster}
          className="px-4 py-2 bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 text-white rounded-lg font-medium transition-all flex items-center space-x-2 shadow-lg"
        >
          <Zap size={20} />
          <span>Create Cluster</span>
        </button>
      </div>

      {/* Arbitrage Highlights */}
      {arbitrageOpps.length > 0 && (
        <div className={`${cardBg} rounded-xl p-6 border-2 border-green-500 dark:border-green-700`}>
          <div className="flex items-center space-x-3 mb-4">
            <TrendingDown className="text-green-500" size={24} />
            <h3 className={`text-lg font-bold ${textColor}`}>Top Arbitrage Opportunities</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {arbitrageOpps.slice(0, 3).map((opp, idx) => (
              <div key={idx} className={`p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border ${borderColor}`}>
                <p className={`font-bold ${textColor} mb-1`}>{opp.gpu_type}</p>
                <p className="text-sm text-green-600 dark:text-green-400 mb-2">
                  Save {parseFloat(opp.spread_pct).toFixed(1)}% with {opp.cheapest_provider}
                </p>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500">${parseFloat(opp.cheapest_price).toFixed(2)}/hr</span>
                  <span className="text-gray-400 line-through">${parseFloat(opp.expensive_price).toFixed(2)}/hr</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Search and Filter Bar */}
      <div className={`${cardBg} rounded-xl p-4 border ${borderColor}`}>
        <div className="flex items-center space-x-3 mb-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search GPUs by model or provider..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-4 py-2 border ${borderColor} rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-2`}
          >
            <Filter size={20} />
            <span>Filters</span>
            <ChevronDown size={16} className={`transform transition-transform ${showFilters ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <select
              value={filters.model}
              onChange={(e) => setFilters({...filters, model: e.target.value})}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
            >
              <option value="">All Models</option>
              {getModels().map(model => (
                <option key={model} value={model}>{model}</option>
              ))}
            </select>

            <select
              value={filters.provider}
              onChange={(e) => setFilters({...filters, provider: e.target.value})}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
            >
              <option value="">All Providers</option>
              {getProviders().map(provider => (
                <option key={provider} value={provider}>{provider}</option>
              ))}
            </select>

            <input
              type="number"
              value={filters.maxPrice || ''}
              onChange={(e) => setFilters({...filters, maxPrice: parseFloat(e.target.value) || null})}
              placeholder="Max price per hour"
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
            />
          </div>
        )}
      </div>

      {/* GPU Grid */}
      {filteredGPUs.length === 0 ? (
        <div className={`${cardBg} rounded-xl p-12 border ${borderColor} text-center`}>
          <Server size={48} className="mx-auto mb-4 text-gray-400" />
          <p className="text-gray-500">No GPUs found matching your criteria</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredGPUs.map((gpu) => (
            <div
              key={gpu.id}
              className={`${cardBg} rounded-xl p-6 border ${borderColor} hover:border-blue-500 dark:hover:border-blue-400 transition-all hover:shadow-lg`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className={`text-lg font-bold ${textColor} mb-1`}>{gpu.model}</h3>
                  <p className="text-sm text-gray-500">{gpu.provider}</p>
                </div>
                {getBestDealBadge(gpu)}
              </div>

              {/* Stats */}
              <div className="space-y-3 mb-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500 flex items-center space-x-1">
                    <Cpu size={16} />
                    <span>VRAM</span>
                  </span>
                  <span className={`font-medium ${textColor}`}>{gpu.vram_gb}GB</span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500 flex items-center space-x-1">
                    <MapPin size={16} />
                    <span>Location</span>
                  </span>
                  <span className={`font-medium ${textColor}`}>{gpu.location}</span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500 flex items-center space-x-1">
                    <Activity size={16} />
                    <span>G-Score</span>
                  </span>
                  <span className={`font-medium ${textColor}`}>
                    {gpu.g_score ? parseFloat(gpu.g_score).toFixed(2) : 'N/A'}
                  </span>
                </div>

                {gpu.available && (
                  <div className="flex items-center space-x-1 text-green-600 dark:text-green-400 text-sm">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span>Available Now</span>
                  </div>
                )}
              </div>

              {/* Price and Action */}
              <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                <div>
                  <p className="text-2xl font-bold text-blue-500">
                    ${parseFloat(gpu.price_per_hour).toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500">per hour</p>
                </div>
                <button
                  onClick={() => handleBook(gpu)}
                  disabled={!gpu.available}
                  className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Book Now
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Booking Modal */}
      {showBooking && selectedGpu && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 max-w-3xl w-full my-8">
            <ReservationBooking
              gpuId={selectedGpu.id}
              onClose={() => {
                setShowBooking(false);
                setSelectedGpu(null);
              }}
              darkMode={darkMode}
            />
          </div>
        </div>
      )}
    </div>
  );
}
