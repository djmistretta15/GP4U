/**
 * GPUs Page (MVP)
 * List and manage GPUs with provenance tracking
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Server, Plus, Filter, Search, Activity, Cpu } from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export default function GPUs() {
  const [gpus, setGpus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddGPU, setShowAddGPU] = useState(false);
  const [newGPU, setNewGPU] = useState({ model: '', vram_gb: 24 });

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

  const handleAddGPU = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE}/gpus/?model=${encodeURIComponent(newGPU.model)}&vram_gb=${newGPU.vram_gb}`);
      setNewGPU({ model: '', vram_gb: 24 });
      setShowAddGPU(false);
      loadGPUs();
    } catch (error) {
      console.error('Failed to add GPU:', error);
      alert('Failed to add GPU');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'available':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'leased':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Activity className="animate-spin mx-auto mb-4 text-blue-500" size={48} />
          <p className="text-gray-600">Loading GPUs...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <Server className="mr-3 text-blue-500" size={32} />
              GPU Lease Ledger
            </h1>
            <p className="mt-1 text-gray-600">Track and manage GPU inventory with blockchain provenance</p>
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
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6 border border-gray-200">
            <h2 className="text-lg font-semibold mb-4">Register New GPU</h2>
            <form onSubmit={handleAddGPU} className="flex gap-4">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-1">GPU Model</label>
                <input
                  type="text"
                  value={newGPU.model}
                  onChange={(e) => setNewGPU({ ...newGPU, model: e.target.value })}
                  placeholder="e.g., RTX 4090"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>
              <div className="w-48">
                <label className="block text-sm font-medium text-gray-700 mb-1">VRAM (GB)</label>
                <input
                  type="number"
                  value={newGPU.vram_gb}
                  onChange={(e) => setNewGPU({ ...newGPU, vram_gb: parseInt(e.target.value) })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                  min="1"
                />
              </div>
              <div className="flex items-end gap-2">
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
                >
                  Add GPU
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddGPU(false)}
                  className="px-6 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* GPU List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    GPU Model
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    VRAM
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Registered
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {gpus.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-12 text-center text-gray-500">
                      <Server className="mx-auto mb-3 text-gray-400" size={48} />
                      <p>No GPUs registered yet</p>
                      <button
                        onClick={() => setShowAddGPU(true)}
                        className="mt-4 text-blue-600 hover:text-blue-700 font-medium"
                      >
                        Register your first GPU
                      </button>
                    </td>
                  </tr>
                ) : (
                  gpus.map((gpu) => (
                    <tr key={gpu.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <Cpu className="text-blue-500 mr-3" size={20} />
                          <span className="font-medium text-gray-900">{gpu.model}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                        {gpu.vram_gb} GB
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-3 py-1 text-xs font-medium rounded-full border ${getStatusColor(gpu.status)}`}>
                          {gpu.status || 'unknown'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(gpu.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Link
                          to={`/dashboard/gpus/${gpu.id}`}
                          className="text-blue-600 hover:text-blue-900 font-medium"
                        >
                          View Details →
                        </Link>
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
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total GPUs</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{gpus.length}</p>
                </div>
                <Server className="text-blue-500" size={32} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Available</p>
                  <p className="text-2xl font-bold text-green-600 mt-1">
                    {gpus.filter(g => g.status === 'available').length}
                  </p>
                </div>
                <Activity className="text-green-500" size={32} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Leased</p>
                  <p className="text-2xl font-bold text-blue-600 mt-1">
                    {gpus.filter(g => g.status === 'leased').length}
                  </p>
                </div>
                <Cpu className="text-blue-500" size={32} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
