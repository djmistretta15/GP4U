/**
 * GPU Management Component (MVP)
 * Integrated with GP4U interface - manages GPU list and detail views
 */

import React, { useState, useEffect } from 'react';
import { 
  Server, Plus, ArrowLeft, Activity, Clock, CheckCircle, 
  AlertCircle, Tool, Package, Cpu 
} from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export default function GPUManagement({ darkMode }) {
  const [gpus, setGpus] = useState([]);
  const [selectedGPU, setSelectedGPU] = useState(null);
  const [provenance, setProvenance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddGPU, setShowAddGPU] = useState(false);
  const [updating, setUpdating] = useState(false);
  const [newGPU, setNewGPU] = useState({ 
    model: '', 
    vram_gb: 24,
    price_per_hour: '',
    location: ''
  });

  // Theme classes
  const bgColor = darkMode ? 'bg-gray-900' : 'bg-gray-50';
  const cardBg = darkMode ? 'bg-gray-800' : 'bg-white';
  const textColor = darkMode ? 'text-white' : 'text-gray-900';
  const textSecondary = darkMode ? 'text-gray-400' : 'text-gray-600';
  const borderColor = darkMode ? 'border-gray-700' : 'border-gray-200';
  const hoverBg = darkMode ? 'hover:bg-gray-700' : 'hover:bg-gray-50';
  const inputBg = darkMode ? 'bg-gray-700' : 'bg-white';
  const inputBorder = darkMode ? 'border-gray-600' : 'border-gray-300';

  useEffect(() => {
    loadGPUs();
  }, []);

  const loadGPUs = async () => {
    try {
      const response = await axios.get(`${API_BASE}/gpus/`);
      setGpus(response.data);
    } catch (error) {
      console.error('Failed to load GPUs:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadGPUDetails = async (gpuId) => {
    try {
      const [gpuRes, provenanceRes] = await Promise.all([
        axios.get(`${API_BASE}/gpus/${gpuId}`),
        axios.get(`${API_BASE}/gpus/${gpuId}/provenance`)
      ]);
      setSelectedGPU(gpuRes.data);
      setProvenance(provenanceRes.data);
    } catch (error) {
      console.error('Failed to load GPU details:', error);
    }
  };

  const handleViewDetails = (gpu) => {
    setSelectedGPU(gpu);
    loadGPUDetails(gpu.id);
  };

  const handleBackToList = () => {
    setSelectedGPU(null);
    setProvenance([]);
    loadGPUs();
  };

  const handleAddGPU = async (e) => {
    e.preventDefault();
    try {
      const params = new URLSearchParams({
        model: newGPU.model,
        vram_gb: newGPU.vram_gb.toString()
      });
      
      // Add optional params for marketplace integration
      if (newGPU.price_per_hour) {
        params.append('price_per_hour', newGPU.price_per_hour);
      }
      if (newGPU.location) {
        params.append('location', newGPU.location);
      }
      
      await axios.post(`${API_BASE}/gpus/?${params.toString()}`);
      setNewGPU({ model: '', vram_gb: 24, price_per_hour: '', location: '' });
      setShowAddGPU(false);
      loadGPUs();
    } catch (error) {
      console.error('Failed to add GPU:', error);
      alert('Failed to add GPU');
    }
  };

  const updateStatus = async (newStatus) => {
    setUpdating(true);
    try {
      await axios.patch(`${API_BASE}/gpus/${selectedGPU.id}`, { status: newStatus });
      await loadGPUDetails(selectedGPU.id);
      alert(`GPU status updated to ${newStatus}`);
    } catch (error) {
      console.error('Failed to update status:', error);
      alert('Failed to update status');
    } finally {
      setUpdating(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'available':
        return 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-400';
      case 'leased':
        return 'bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/20 dark:text-blue-400';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200 dark:bg-gray-700 dark:text-gray-400';
    }
  };

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'registered':
        return <Package className="text-blue-500" size={20} />;
      case 'status_changed':
        return <Activity className="text-purple-500" size={20} />;
      case 'leased':
        return <CheckCircle className="text-green-500" size={20} />;
      case 'returned':
        return <ArrowLeft className="text-gray-500" size={20} />;
      case 'maintenance_start':
        return <Tool className="text-yellow-500" size={20} />;
      case 'maintenance_end':
        return <CheckCircle className="text-green-500" size={20} />;
      default:
        return <Activity className="text-gray-500" size={20} />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <Activity className={`animate-spin mx-auto mb-4 ${darkMode ? 'text-blue-400' : 'text-blue-500'}`} size={48} />
          <p className={textSecondary}>Loading GPUs...</p>
        </div>
      </div>
    );
  }

  // Detail View
  if (selectedGPU) {
    return (
      <div>
        {/* Back Button */}
        <button
          onClick={handleBackToList}
          className={`inline-flex items-center ${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-700'} mb-6 font-medium`}
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to GPU List
        </button>

        {/* GPU Details Card */}
        <div className={`${cardBg} rounded-lg shadow-sm border ${borderColor} p-8 mb-6`}>
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center">
              <Server className={darkMode ? 'text-blue-400' : 'text-blue-500'} size={48} />
              <div className="ml-4">
                <h1 className={`text-3xl font-bold ${textColor}`}>{selectedGPU.model}</h1>
                <p className={`${textSecondary} mt-1`}>{selectedGPU.vram_gb} GB VRAM</p>
              </div>
            </div>
            <span className={`inline-flex px-4 py-2 text-sm font-medium rounded-full border ${getStatusColor(selectedGPU.status)}`}>
              {selectedGPU.status || 'unknown'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div>
              <p className={`text-sm ${textSecondary} mb-1`}>GPU ID</p>
              <p className={`text-sm font-mono ${textColor} break-all`}>{selectedGPU.id}</p>
            </div>
            <div>
              <p className={`text-sm ${textSecondary} mb-1`}>Provider</p>
              <p className={`font-medium ${textColor}`}>{selectedGPU.provider}</p>
            </div>
            <div>
              <p className={`text-sm ${textSecondary} mb-1`}>Registered</p>
              <p className={`font-medium ${textColor}`}>
                {new Date(selectedGPU.created_at).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Status Actions */}
          <div className={`border-t ${borderColor} pt-6`}>
            <p className={`text-sm font-medium ${textColor} mb-3`}>Update Status</p>
            <div className="flex gap-3">
              <button
                onClick={() => updateStatus('available')}
                disabled={updating || selectedGPU.status === 'available'}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedGPU.status === 'available'
                    ? `${darkMode ? 'bg-gray-700 text-gray-500' : 'bg-gray-100 text-gray-400'} cursor-not-allowed`
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
              >
                Mark Available
              </button>
              <button
                onClick={() => updateStatus('leased')}
                disabled={updating || selectedGPU.status === 'leased'}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedGPU.status === 'leased'
                    ? `${darkMode ? 'bg-gray-700 text-gray-500' : 'bg-gray-100 text-gray-400'} cursor-not-allowed`
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                Mark Leased
              </button>
              <button
                onClick={() => updateStatus('maintenance')}
                disabled={updating || selectedGPU.status === 'maintenance'}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedGPU.status === 'maintenance'
                    ? `${darkMode ? 'bg-gray-700 text-gray-500' : 'bg-gray-100 text-gray-400'} cursor-not-allowed`
                    : 'bg-yellow-600 hover:bg-yellow-700 text-white'
                }`}
              >
                Mark Maintenance
              </button>
            </div>
          </div>
        </div>

        {/* Provenance Timeline */}
        <div className={`${cardBg} rounded-lg shadow-sm border ${borderColor} p-8`}>
          <h2 className={`text-2xl font-bold ${textColor} mb-6 flex items-center`}>
            <Clock className={`mr-3 ${darkMode ? 'text-blue-400' : 'text-blue-500'}`} size={28} />
            Provenance Timeline
          </h2>

          {provenance.length === 0 ? (
            <div className="text-center py-12">
              <Clock className={`mx-auto mb-3 ${darkMode ? 'text-gray-600' : 'text-gray-400'}`} size={48} />
              <p className={textSecondary}>No provenance events yet</p>
            </div>
          ) : (
            <div className="space-y-6">
              {provenance.map((event, index) => {
                const payload = event.payload_json ? JSON.parse(event.payload_json) : {};
                return (
                  <div key={event.id} className="flex">
                    <div className="flex flex-col items-center mr-4">
                      <div className={`flex items-center justify-center w-10 h-10 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-gray-100'} border-2 ${borderColor}`}>
                        {getEventIcon(event.event_type)}
                      </div>
                      {index < provenance.length - 1 && (
                        <div className={`w-0.5 h-full ${darkMode ? 'bg-gray-700' : 'bg-gray-300'} mt-2`} />
                      )}
                    </div>
                    <div className="flex-1 pb-8">
                      <div className={`${darkMode ? 'bg-gray-700/50' : 'bg-gray-50'} rounded-lg p-4 border ${borderColor}`}>
                        <div className="flex items-center justify-between mb-2">
                          <h3 className={`font-semibold ${textColor} capitalize`}>
                            {event.event_type.replace(/_/g, ' ')}
                          </h3>
                          <span className={`text-sm ${textSecondary}`}>
                            {new Date(event.created_at).toLocaleString()}
                          </span>
                        </div>
                        {Object.keys(payload).length > 0 && (
                          <div className="mt-2">
                            <pre className={`text-sm ${textColor} ${inputBg} rounded p-3 border ${borderColor} overflow-x-auto`}>
                              {JSON.stringify(payload, null, 2)}
                            </pre>
                          </div>
                        )}
                        <p className={`text-xs ${textSecondary} mt-2 font-mono`}>
                          Event ID: {event.id}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    );
  }

  // List View
  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className={`text-3xl font-bold ${textColor} flex items-center`}>
            <Server className={`mr-3 ${darkMode ? 'text-blue-400' : 'text-blue-500'}`} size={32} />
            GPU Lease Ledger
          </h1>
          <p className={`mt-1 ${textSecondary}`}>Track and manage GPU inventory with blockchain provenance</p>
        </div>
        <button
          onClick={() => setShowAddGPU(!showAddGPU)}
          className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
        >
          <Plus size={20} className="mr-2" />
          Register GPU
        </button>
      </div>

      {/* Add GPU Form */}
      {showAddGPU && (
        <div className={`${cardBg} rounded-lg shadow-sm p-6 mb-6 border ${borderColor}`}>
          <h2 className={`text-lg font-semibold ${textColor} mb-4`}>Register New GPU (Lease Ledger + Marketplace)</h2>
          <p className={`text-sm ${textSecondary} mb-4`}>Add price and location to enable marketplace arbitrage</p>
          <form onSubmit={handleAddGPU} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className={`block text-sm font-medium ${textColor} mb-1`}>GPU Model *</label>
                <input
                  type="text"
                  value={newGPU.model}
                  onChange={(e) => setNewGPU({ ...newGPU, model: e.target.value })}
                  placeholder="e.g., RTX 4090"
                  className={`w-full px-4 py-2 ${inputBg} border ${inputBorder} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${textColor}`}
                  required
                />
              </div>
              <div>
                <label className={`block text-sm font-medium ${textColor} mb-1`}>VRAM (GB) *</label>
                <input
                  type="number"
                  value={newGPU.vram_gb}
                  onChange={(e) => setNewGPU({ ...newGPU, vram_gb: parseInt(e.target.value) })}
                  className={`w-full px-4 py-2 ${inputBg} border ${inputBorder} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${textColor}`}
                  required
                  min="1"
                />
              </div>
              <div>
                <label className={`block text-sm font-medium ${textColor} mb-1`}>
                  Price/Hour (USD)
                  <span className="text-xs ml-2 text-blue-500">→ Enables Marketplace</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={newGPU.price_per_hour}
                  onChange={(e) => setNewGPU({ ...newGPU, price_per_hour: e.target.value })}
                  placeholder="e.g., 2.50"
                  className={`w-full px-4 py-2 ${inputBg} border ${inputBorder} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${textColor}`}
                />
              </div>
              <div>
                <label className={`block text-sm font-medium ${textColor} mb-1`}>
                  Location
                  <span className="text-xs ml-2 text-blue-500">→ Enables Arbitrage</span>
                </label>
                <input
                  type="text"
                  value={newGPU.location}
                  onChange={(e) => setNewGPU({ ...newGPU, location: e.target.value })}
                  placeholder="e.g., US-East, EU-West"
                  className={`w-full px-4 py-2 ${inputBg} border ${inputBorder} rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${textColor}`}
                />
              </div>
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="submit"
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                Register GPU
              </button>
              <button
                type="button"
                onClick={() => setShowAddGPU(false)}
                className={`px-6 py-2 ${darkMode ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'} ${textColor} rounded-lg font-medium transition-colors`}
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* GPU List */}
      <div className={`${cardBg} rounded-lg shadow-sm border ${borderColor}`}>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className={`${darkMode ? 'bg-gray-700/50' : 'bg-gray-50'} border-b ${borderColor}`}>
              <tr>
                <th className={`px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase tracking-wider`}>
                  GPU Model
                </th>
                <th className={`px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase tracking-wider`}>
                  VRAM
                </th>
                <th className={`px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase tracking-wider`}>
                  Price/Hour
                </th>
                <th className={`px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase tracking-wider`}>
                  Status
                </th>
                <th className={`px-6 py-3 text-left text-xs font-medium ${textSecondary} uppercase tracking-wider`}>
                  Location
                </th>
                <th className={`px-6 py-3 text-right text-xs font-medium ${textSecondary} uppercase tracking-wider`}>
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className={`divide-y ${borderColor}`}>
              {gpus.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center">
                    <Server className={`mx-auto mb-3 ${darkMode ? 'text-gray-600' : 'text-gray-400'}`} size={48} />
                    <p className={textSecondary}>No GPUs registered yet</p>
                    <button
                      onClick={() => setShowAddGPU(true)}
                      className={`mt-4 ${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-700'} font-medium`}
                    >
                      Register your first GPU
                    </button>
                  </td>
                </tr>
              ) : (
                gpus.map((gpu) => (
                  <tr key={gpu.id} className={`${hoverBg} transition-colors`}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Cpu className={darkMode ? 'text-blue-400' : 'text-blue-500'} size={20} />
                        <span className={`font-medium ${textColor} ml-3`}>{gpu.model}</span>
                      </div>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap ${textSecondary}`}>
                      {gpu.vram_gb} GB
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap ${textColor}`}>
                      {gpu.price_per_hour > 0 ? (
                        <div className="flex items-center">
                          <span className="font-medium">${gpu.price_per_hour}</span>
                          <span className={`ml-1 text-xs px-2 py-0.5 rounded ${darkMode ? 'bg-green-900/20 text-green-400' : 'bg-green-100 text-green-700'}`}>
                            marketplace
                          </span>
                        </div>
                      ) : (
                        <span className={textSecondary}>—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-3 py-1 text-xs font-medium rounded-full border ${getStatusColor(gpu.status)}`}>
                        {gpu.status || 'unknown'}
                      </span>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-sm ${textSecondary}`}>
                      {gpu.location || '—'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleViewDetails(gpu)}
                        className={`${darkMode ? 'text-blue-400 hover:text-blue-300' : 'text-blue-600 hover:text-blue-900'} font-medium`}
                      >
                        View Details →
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Stats */}
      {gpus.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
          <div className={`${cardBg} rounded-lg shadow-sm p-6 border ${borderColor}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm ${textSecondary}`}>Total GPUs</p>
                <p className={`text-2xl font-bold ${textColor} mt-1`}>{gpus.length}</p>
              </div>
              <Server className={darkMode ? 'text-blue-400' : 'text-blue-500'} size={32} />
            </div>
          </div>
          <div className={`${cardBg} rounded-lg shadow-sm p-6 border ${borderColor}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm ${textSecondary}`}>Available</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  {gpus.filter(g => g.status === 'available').length}
                </p>
              </div>
              <Activity className="text-green-500" size={32} />
            </div>
          </div>
          <div className={`${cardBg} rounded-lg shadow-sm p-6 border ${borderColor}`}>
            <div className="flex items-center justify-between">
              <div>
                <p className={`text-sm ${textSecondary}`}>Leased</p>
                <p className={`text-2xl font-bold ${darkMode ? 'text-blue-400' : 'text-blue-600'} mt-1`}>
                  {gpus.filter(g => g.status === 'leased').length}
                </p>
              </div>
              <Cpu className={darkMode ? 'text-blue-400' : 'text-blue-500'} size={32} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
