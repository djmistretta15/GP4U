/**
 * GPU Detail Page (MVP)
 * Shows GPU details and provenance timeline
 */

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  Server, ArrowLeft, Activity, Clock, CheckCircle, 
  AlertCircle, Tool, Package, Calendar 
} from 'lucide-react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export default function GPUDetail() {
  const { id } = useParams();
  const [gpu, setGpu] = useState(null);
  const [provenance, setProvenance] = useState([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    loadGPUDetails();
  }, [id]);

  const loadGPUDetails = async () => {
    try {
      const [gpuRes, provenanceRes] = await Promise.all([
        axios.get(`${API_BASE}/gpus/${id}`),
        axios.get(`${API_BASE}/gpus/${id}/provenance`)
      ]);
      setGpu(gpuRes.data);
      setProvenance(provenanceRes.data);
    } catch (error) {
      console.error('Failed to load GPU details:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (newStatus) => {
    setUpdating(true);
    try {
      await axios.patch(`${API_BASE}/gpus/${id}`, { status: newStatus });
      await loadGPUDetails();
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
        return 'bg-green-100 text-green-800 border-green-200';
      case 'leased':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
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
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <Activity className="animate-spin mx-auto mb-4 text-blue-500" size={48} />
          <p className="text-gray-600">Loading GPU details...</p>
        </div>
      </div>
    );
  }

  if (!gpu) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <AlertCircle className="mx-auto mb-4 text-red-500" size={48} />
          <p className="text-gray-600">GPU not found</p>
          <Link to="/dashboard/gpus" className="mt-4 text-blue-600 hover:text-blue-700">
            ← Back to GPU list
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <Link
          to="/dashboard/gpus"
          className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-6 font-medium"
        >
          <ArrowLeft size={20} className="mr-2" />
          Back to GPU List
        </Link>

        {/* GPU Details Card */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center">
              <Server className="text-blue-500 mr-4" size={48} />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{gpu.model}</h1>
                <p className="text-gray-600 mt-1">{gpu.vram_gb} GB VRAM</p>
              </div>
            </div>
            <span className={`inline-flex px-4 py-2 text-sm font-medium rounded-full border ${getStatusColor(gpu.status)}`}>
              {gpu.status || 'unknown'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div>
              <p className="text-sm text-gray-600 mb-1">GPU ID</p>
              <p className="text-sm font-mono text-gray-900 break-all">{gpu.id}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Provider</p>
              <p className="font-medium text-gray-900">{gpu.provider}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600 mb-1">Registered</p>
              <p className="font-medium text-gray-900">
                {new Date(gpu.created_at).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Status Actions */}
          <div className="border-t border-gray-200 pt-6">
            <p className="text-sm font-medium text-gray-700 mb-3">Update Status</p>
            <div className="flex gap-3">
              <button
                onClick={() => updateStatus('available')}
                disabled={updating || gpu.status === 'available'}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  gpu.status === 'available'
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
              >
                Mark Available
              </button>
              <button
                onClick={() => updateStatus('leased')}
                disabled={updating || gpu.status === 'leased'}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  gpu.status === 'leased'
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                Mark Leased
              </button>
              <button
                onClick={() => updateStatus('maintenance')}
                disabled={updating || gpu.status === 'maintenance'}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  gpu.status === 'maintenance'
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-yellow-600 hover:bg-yellow-700 text-white'
                }`}
              >
                Mark Maintenance
              </button>
            </div>
          </div>
        </div>

        {/* Provenance Timeline */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
            <Clock className="mr-3 text-blue-500" size={28} />
            Provenance Timeline
          </h2>

          {provenance.length === 0 ? (
            <div className="text-center py-12">
              <Clock className="mx-auto mb-3 text-gray-400" size={48} />
              <p className="text-gray-500">No provenance events yet</p>
            </div>
          ) : (
            <div className="space-y-6">
              {provenance.map((event, index) => {
                const payload = event.payload_json ? JSON.parse(event.payload_json) : {};
                return (
                  <div key={event.id} className="flex">
                    <div className="flex flex-col items-center mr-4">
                      <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gray-100 border-2 border-gray-300">
                        {getEventIcon(event.event_type)}
                      </div>
                      {index < provenance.length - 1 && (
                        <div className="w-0.5 h-full bg-gray-300 mt-2" />
                      )}
                    </div>
                    <div className="flex-1 pb-8">
                      <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-semibold text-gray-900 capitalize">
                            {event.event_type.replace(/_/g, ' ')}
                          </h3>
                          <span className="text-sm text-gray-500">
                            {new Date(event.created_at).toLocaleString()}
                          </span>
                        </div>
                        {Object.keys(payload).length > 0 && (
                          <div className="mt-2">
                            <pre className="text-sm text-gray-700 bg-white rounded p-3 border border-gray-200 overflow-x-auto">
                              {JSON.stringify(payload, null, 2)}
                            </pre>
                          </div>
                        )}
                        <p className="text-xs text-gray-500 mt-2 font-mono">
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
    </div>
  );
}
