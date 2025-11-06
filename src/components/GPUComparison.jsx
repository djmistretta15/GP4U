/**
 * GPU Comparison Component
 * Table view for comparing GPUs across providers
 */

import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { TrendingUp, Heart, Search, Filter } from 'lucide-react';

export default function GPUComparison({ gpus, onBook }) {
  const { darkMode, currentTheme, textColor, cardBg, borderColor } = useTheme();
  const [sortConfig, setSortConfig] = useState({ key: 'price_per_hour', direction: 'asc' });
  const [favorites, setFavorites] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const handleSort = (key) => {
    setSortConfig({
      key,
      direction: sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc'
    });
  };

  const toggleFavorite = (id) => {
    setFavorites(prev =>
      prev.includes(id) ? prev.filter(fav => fav !== id) : [...prev, id]
    );
  };

  const providers = [...new Set(gpus.map(g => g.provider))];

  const filteredGPUs = gpus
    .filter(gpu => {
      const matchesSearch = searchTerm === '' ||
        gpu.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
        gpu.provider.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesProvider = selectedProvider === 'all' || gpu.provider === selectedProvider;
      return matchesSearch && matchesProvider;
    })
    .sort((a, b) => {
      const aVal = sortConfig.key === 'price_per_hour'
        ? parseFloat(a[sortConfig.key])
        : a[sortConfig.key];
      const bVal = sortConfig.key === 'price_per_hour'
        ? parseFloat(b[sortConfig.key])
        : b[sortConfig.key];

      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });

  return (
    <div className="space-y-6">
      {/* Providers Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {providers.map(provider => (
          <button
            key={provider}
            onClick={() => setSelectedProvider(selectedProvider === provider ? 'all' : provider)}
            className={`p-4 rounded-lg ${cardBg} border ${borderColor} shadow-md hover:shadow-lg transition-shadow cursor-pointer ${selectedProvider === provider ? `border-2 ${currentTheme.primary.replace('bg-', 'border-')}` : ''
              }`}
          >
            <h3 className={`font-semibold text-sm ${textColor}`}>{provider}</h3>
            <span className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
              {gpus.filter(g => g.provider === provider).length} offers
            </span>
          </button>
        ))}
      </div>

      {/* Search and Filters */}
      <div className={`${cardBg} rounded-lg p-4 border ${borderColor}`}>
        <div className="relative">
          <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search GPU model or provider..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={`w-full pl-10 pr-4 py-2 rounded-lg border ${darkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-300'
              } ${textColor}`}
          />
        </div>
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          Showing {filteredGPUs.length} of {gpus.length} offers
          {selectedProvider !== 'all' && ` from ${selectedProvider}`}
        </p>
        {selectedProvider !== 'all' && (
          <button
            onClick={() => setSelectedProvider('all')}
            className="text-sm text-blue-500 hover:underline"
          >
            Clear filter
          </button>
        )}
      </div>

      {/* Table */}
      <div className={`${cardBg} rounded-lg shadow-md overflow-hidden border ${borderColor}`}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className={`${darkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  <button onClick={() => handleSort('provider')} className="flex items-center space-x-1">
                    <span>Provider</span>
                    <TrendingUp className="w-4 h-4" />
                  </button>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  <button onClick={() => handleSort('model')} className="flex items-center space-x-1">
                    <span>GPU Model</span>
                    <TrendingUp className="w-4 h-4" />
                  </button>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  <button onClick={() => handleSort('vram_gb')} className="flex items-center space-x-1">
                    <span>VRAM</span>
                    <TrendingUp className="w-4 h-4" />
                  </button>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  <button onClick={() => handleSort('price_per_hour')} className="flex items-center space-x-1">
                    <span>Price/Hour</span>
                    <TrendingUp className="w-4 h-4" />
                  </button>
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Availability
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className={`divide-y ${darkMode ? 'divide-gray-700' : 'divide-gray-200'}`}>
              {filteredGPUs.map((gpu) => (
                <tr key={gpu.id} className={`${darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50'} transition-colors`}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`font-medium ${textColor}`}>{gpu.provider}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="font-semibold text-blue-500">{gpu.model}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={textColor}>{gpu.vram_gb} GB</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-lg font-bold text-green-500">
                      ${parseFloat(gpu.price_per_hour).toFixed(2)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={textColor}>{gpu.location}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs ${gpu.available
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                      }`}>
                      {gpu.available ? 'Available' : 'Unavailable'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => toggleFavorite(gpu.id)}
                        className={`p-2 rounded-lg ${favorites.includes(gpu.id) ? 'text-red-500' : 'text-gray-400'
                          }`}
                      >
                        <Heart className={`w-5 h-5 ${favorites.includes(gpu.id) ? 'fill-current' : ''}`} />
                      </button>
                      <button
                        onClick={() => onBook(gpu)}
                        disabled={!gpu.available}
                        className={`px-4 py-2 ${currentTheme.primary} text-white rounded-lg font-medium hover:opacity-90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        Book
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredGPUs.length === 0 && (
        <div className="text-center py-12">
          <p className={`${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>No GPUs found matching your criteria.</p>
        </div>
      )}
    </div>
  );
}
