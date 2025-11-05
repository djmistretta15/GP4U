/**
 * My Clusters Component
 * Displays and manages user's GPU clusters
 */

import React, { useState, useEffect } from 'react';
import { clusterAPI } from '../services/api';
import { useToast } from '../context/ToastContext';
import {
  Cpu, Loader, Play, Square, CheckCircle, XCircle,
  Clock, DollarSign, RefreshCw, ChevronDown, ChevronUp, Zap
} from 'lucide-react';

export default function MyClusters({ darkMode }) {
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState(null);
  const [expandedCluster, setExpandedCluster] = useState(null);
  const [members, setMembers] = useState({});
  const toast = useToast();

  const cardBg = darkMode ? 'bg-gray-800' : 'bg-white';
  const textColor = darkMode ? 'text-white' : 'text-gray-900';
  const borderColor = darkMode ? 'border-gray-700' : 'border-gray-200';

  useEffect(() => {
    loadClusters();
  }, [filter]);

  const loadClusters = async () => {
    try {
      setLoading(true);
      const data = await clusterAPI.getMyClusters(filter);
      setClusters(data);
    } catch (err) {
      toast.error('Failed to load clusters');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadClusterMembers = async (clusterId) => {
    if (members[clusterId]) {
      setExpandedCluster(expandedCluster === clusterId ? null : clusterId);
      return;
    }

    try {
      const data = await clusterAPI.getMembers(clusterId);
      setMembers(prev => ({ ...prev, [clusterId]: data }));
      setExpandedCluster(clusterId);
    } catch (err) {
      toast.error('Failed to load cluster members');
    }
  };

  const handleStart = async (clusterId) => {
    if (!confirm('Start this cluster? Payment will be processed immediately.')) {
      return;
    }

    try {
      await clusterAPI.start(clusterId);
      toast.success('Cluster started successfully');
      loadClusters();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to start cluster');
    }
  };

  const handleStop = async (clusterId, success = true) => {
    const message = success
      ? 'Mark this cluster as completed? Earnings will be distributed to GPU providers.'
      : 'Mark this cluster as failed? No earnings will be distributed.';

    if (!confirm(message)) {
      return;
    }

    try {
      await clusterAPI.stop(clusterId, success);
      toast.success(success ? 'Cluster completed and earnings distributed' : 'Cluster marked as failed');
      loadClusters();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to stop cluster');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status) => {
    const badges = {
      PENDING: {
        bg: 'bg-yellow-100 dark:bg-yellow-900/30',
        text: 'text-yellow-800 dark:text-yellow-300',
        icon: <Clock size={14} />
      },
      ACTIVE: {
        bg: 'bg-green-100 dark:bg-green-900/30',
        text: 'text-green-800 dark:text-green-300',
        icon: <Zap size={14} />
      },
      COMPLETED: {
        bg: 'bg-blue-100 dark:bg-blue-900/30',
        text: 'text-blue-800 dark:text-blue-300',
        icon: <CheckCircle size={14} />
      },
      FAILED: {
        bg: 'bg-red-100 dark:bg-red-900/30',
        text: 'text-red-800 dark:text-red-300',
        icon: <XCircle size={14} />
      }
    };

    const badge = badges[status] || badges.PENDING;

    return (
      <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
        {badge.icon}
        <span>{status}</span>
      </span>
    );
  };

  if (loading) {
    return (
      <div className={`${cardBg} rounded-xl p-8 flex items-center justify-center`}>
        <Loader className="animate-spin text-blue-500" size={32} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className={`text-2xl font-bold ${textColor}`}>My Clusters</h2>
        <button
          onClick={loadClusters}
          className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-2"
        >
          <RefreshCw size={16} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-2">
        <button
          onClick={() => setFilter(null)}
          className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
            filter === null
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
          }`}
        >
          All
        </button>
        {['PENDING', 'ACTIVE', 'COMPLETED', 'FAILED'].map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
              filter === status
                ? 'bg-blue-500 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            {status}
          </button>
        ))}
      </div>

      {/* Clusters List */}
      {clusters.length === 0 ? (
        <div className={`${cardBg} rounded-xl p-12 border ${borderColor} text-center`}>
          <Cpu size={48} className="mx-auto mb-4 text-gray-400" />
          <p className="text-gray-500 mb-4">No clusters found</p>
          <p className="text-sm text-gray-400">Create your first multi-GPU cluster to get started!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {clusters.map((cluster) => (
            <div
              key={cluster.id}
              className={`${cardBg} rounded-xl border ${borderColor} hover:border-blue-300 dark:hover:border-blue-700 transition-colors overflow-hidden`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className={`text-lg font-bold ${textColor}`}>{cluster.job_name}</h3>
                      {getStatusBadge(cluster.status)}
                    </div>
                    <p className="text-sm text-gray-500">
                      Created {formatDate(cluster.created_at)}
                      {cluster.completed_at && ` • Completed ${formatDate(cluster.completed_at)}`}
                    </p>
                  </div>

                  <div className="text-right">
                    <p className="text-2xl font-bold text-blue-500">
                      ${parseFloat(cluster.total_cost).toFixed(2)}
                    </p>
                    <p className="text-xs text-gray-500">Total Cost</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                  <div className={`p-3 border ${borderColor} rounded-lg`}>
                    <div className="flex items-center space-x-2 mb-1">
                      <Cpu size={16} className="text-blue-500" />
                      <span className="text-xs text-gray-500">GPU Count</span>
                    </div>
                    <p className={`text-sm font-medium ${textColor}`}>{cluster.gpu_count} GPUs</p>
                  </div>

                  <div className={`p-3 border ${borderColor} rounded-lg`}>
                    <div className="flex items-center space-x-2 mb-1">
                      <DollarSign size={16} className="text-green-500" />
                      <span className="text-xs text-gray-500">Cost per GPU</span>
                    </div>
                    <p className={`text-sm font-medium ${textColor}`}>
                      ${(parseFloat(cluster.total_cost) / cluster.gpu_count).toFixed(2)}
                    </p>
                  </div>

                  <div className={`p-3 border ${borderColor} rounded-lg`}>
                    <div className="flex items-center space-x-2 mb-1">
                      <Clock size={16} className="text-purple-500" />
                      <span className="text-xs text-gray-500">Cluster ID</span>
                    </div>
                    <p className={`text-sm font-medium ${textColor}`}>
                      {cluster.id.substring(0, 8)}...
                    </p>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={() => loadClusterMembers(cluster.id)}
                    className="text-sm text-blue-500 hover:text-blue-600 flex items-center space-x-1"
                  >
                    <span>View GPUs</span>
                    {expandedCluster === cluster.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </button>

                  <div className="flex items-center space-x-2">
                    {cluster.status === 'PENDING' && (
                      <button
                        onClick={() => handleStart(cluster.id)}
                        className="px-4 py-2 bg-green-500 hover:bg-green-600 text-white text-sm rounded-lg transition-colors flex items-center space-x-2"
                      >
                        <Play size={16} />
                        <span>Start</span>
                      </button>
                    )}

                    {cluster.status === 'ACTIVE' && (
                      <>
                        <button
                          onClick={() => handleStop(cluster.id, true)}
                          className="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white text-sm rounded-lg transition-colors flex items-center space-x-2"
                        >
                          <CheckCircle size={16} />
                          <span>Complete</span>
                        </button>
                        <button
                          onClick={() => handleStop(cluster.id, false)}
                          className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white text-sm rounded-lg transition-colors flex items-center space-x-2"
                        >
                          <Square size={16} />
                          <span>Mark Failed</span>
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Expanded Members */}
              {expandedCluster === cluster.id && members[cluster.id] && (
                <div className="bg-gray-50 dark:bg-gray-900/50 p-6 border-t border-gray-200 dark:border-gray-700">
                  <h4 className={`text-sm font-bold ${textColor} mb-3`}>Cluster GPUs</h4>
                  <div className="space-y-2">
                    {members[cluster.id].map((member, idx) => (
                      <div
                        key={idx}
                        className={`p-3 ${cardBg} border ${borderColor} rounded-lg flex items-center justify-between`}
                      >
                        <div className="flex-1">
                          <p className={`font-medium ${textColor}`}>{member.gpu.model}</p>
                          <p className="text-xs text-gray-500">
                            {member.gpu.provider} • {member.gpu.vram_gb}GB VRAM • G-Score: {member.gpu.g_score || 'N/A'}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-bold text-blue-500">
                            {(member.contribution_score * 100).toFixed(1)}%
                          </p>
                          <p className="text-xs text-gray-500">Contribution</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
