/**
 * Enhanced Marketplace with Multiple View Modes
 * Combines SmartGPUFinder, Comparison, and Standard views
 */

import React, { useState, useEffect } from 'react';
import { useTheme } from '../context/ThemeContext';
import { useToast } from '../context/ToastContext';
import { gpuAPI, arbitrageAPI } from '../services/api';
import { Zap, Loader, Grid, Table, Sparkles } from 'lucide-react';
import SmartGPUFinder from '../components/SmartGPUFinder';
import GPUComparison from '../components/GPUComparison';
import ReservationBooking from '../components/ReservationBooking';

export default function EnhancedMarketplace({ onCreateCluster }) {
  const { darkMode, currentTheme, textColor, cardBg, borderColor } = useTheme();
  const [viewMode, setViewMode] = useState('smart'); // smart, comparison, grid
  const [gpus, setGpus] = useState([]);
  const [arbitrageOpps, setArbitrageOpps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedGpu, setSelectedGpu] = useState(null);
  const [showBooking, setShowBooking] = useState(false);
  const toast = useToast();

  useEffect(() => {
    loadMarketplaceData();
    const interval = setInterval(loadMarketplaceData, 30000);
    return () => clearInterval(interval);
  }, []);

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

  const handleBook = (gpu) => {
    setSelectedGpu(gpu);
    setShowBooking(true);
  };

  if (loading) {
    return (
      <div className={`${cardBg} rounded-xl p-12 flex flex-col items-center justify-center`}>
        <Loader className="animate-spin text-blue-500 mb-4" size={48} />
        <p className={`${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Loading marketplace...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with View Switcher */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className={`text-3xl font-bold ${textColor} mb-2`}>GPU Marketplace</h2>
          <p className={`${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
            {gpus.length} GPUs available • {arbitrageOpps.length} arbitrage opportunities
          </p>
        </div>

        <div className="flex items-center space-x-4">
          {/* View Mode Switcher */}
          <div className={`flex items-center space-x-2 ${cardBg} rounded-lg p-1 border ${borderColor}`}>
            <button
              onClick={() => setViewMode('smart')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${viewMode === 'smart'
                  ? `${currentTheme.primary} text-white`
                  : `${textColor} hover:bg-gray-100 dark:hover:bg-gray-700`
                }`}
            >
              <Sparkles size={18} />
              <span className="text-sm font-medium">AI Search</span>
            </button>
            <button
              onClick={() => setViewMode('comparison')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${viewMode === 'comparison'
                  ? `${currentTheme.primary} text-white`
                  : `${textColor} hover:bg-gray-100 dark:hover:bg-gray-700`
                }`}
            >
              <Table size={18} />
              <span className="text-sm font-medium">Compare</span>
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition ${viewMode === 'grid'
                  ? `${currentTheme.primary} text-white`
                  : `${textColor} hover:bg-gray-100 dark:hover:bg-gray-700`
                }`}
            >
              <Grid size={18} />
              <span className="text-sm font-medium">Grid</span>
            </button>
          </div>

          <button
            onClick={onCreateCluster}
            className={`px-4 py-2 bg-gradient-to-r ${currentTheme.gradient} hover:opacity-90 text-white rounded-lg font-medium transition-all flex items-center space-x-2 shadow-lg`}
          >
            <Zap size={20} />
            <span>Create Cluster</span>
          </button>
        </div>
      </div>

      {/* View Content */}
      {viewMode === 'smart' && <SmartGPUFinder gpus={gpus} onBook={handleBook} />}
      {viewMode === 'comparison' && <GPUComparison gpus={gpus} onBook={handleBook} />}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {gpus.map((gpu) => (
            <div
              key={gpu.id}
              className={`${cardBg} rounded-xl p-6 border ${borderColor} hover:border-blue-500 transition-all hover:shadow-lg`}
            >
              <h3 className={`text-lg font-bold ${textColor} mb-1`}>{gpu.model}</h3>
              <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-4`}>{gpu.provider}</p>

              <div className="space-y-2 mb-4 text-sm">
                <div className="flex justify-between">
                  <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>VRAM</span>
                  <span className={`font-medium ${textColor}`}>{gpu.vram_gb}GB</span>
                </div>
                <div className="flex justify-between">
                  <span className={darkMode ? 'text-gray-400' : 'text-gray-600'}>Location</span>
                  <span className={`font-medium ${textColor}`}>{gpu.location}</span>
                </div>
              </div>

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
                  className={`px-4 py-2 ${currentTheme.primary} hover:opacity-90 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
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
