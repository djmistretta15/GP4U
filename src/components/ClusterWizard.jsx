/**
 * Cluster Creation Wizard
 * Multi-step form for creating GPU clusters with DPP algorithm
 */

import React, { useState } from 'react';
import { clusterAPI } from '../services/api';
import {
  Cpu, Zap, Clock, DollarSign, CheckCircle, AlertCircle,
  Loader, ChevronRight, ChevronLeft, Info, Sparkles
} from 'lucide-react';

export default function ClusterWizard({ onClose, onSuccess, darkMode }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [simulation, setSimulation] = useState(null);
  const [simulating, setSimulating] = useState(false);

  // Form data
  const [formData, setFormData] = useState({
    jobName: '',
    computeIntensity: 1000,
    vramGb: 24,
    deadlineHours: 24,
    gpuCount: null // null means auto-calculate
  });

  const cardBg = darkMode ? 'bg-gray-800' : 'bg-white';
  const textColor = darkMode ? 'text-white' : 'text-gray-900';
  const borderColor = darkMode ? 'border-gray-700' : 'border-gray-200';

  const updateFormData = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSimulate = async () => {
    setError('');
    setSimulating(true);

    try {
      const result = await clusterAPI.simulateCost(
        formData.computeIntensity,
        formData.vramGb,
        formData.deadlineHours,
        formData.gpuCount
      );
      setSimulation(result);
      setStep(3); // Move to review step
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to simulate cluster');
    } finally {
      setSimulating(false);
    }
  };

  const handleCreate = async () => {
    setError('');
    setLoading(true);

    try {
      const cluster = await clusterAPI.create(
        formData.jobName,
        formData.computeIntensity,
        formData.vramGb,
        formData.deadlineHours,
        formData.gpuCount
      );

      if (onSuccess) {
        onSuccess(cluster);
      } else if (onClose) {
        onClose();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create cluster');
    } finally {
      setLoading(false);
    }
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return formData.jobName.trim().length > 0;
      case 2:
        return formData.computeIntensity > 0 && formData.vramGb > 0 && formData.deadlineHours > 0;
      case 3:
        return simulation !== null;
      default:
        return false;
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full mb-4">
          <Sparkles className="text-white" size={32} />
        </div>
        <h2 className={`text-3xl font-bold ${textColor} mb-2`}>Create GPU Cluster</h2>
        <p className="text-gray-500">Powered by Dynamic Pooling Protocol (DPP)</p>
      </div>

      {/* Progress Steps */}
      <div className="flex items-center justify-center mb-8">
        {[1, 2, 3].map((s) => (
          <React.Fragment key={s}>
            <div className="flex items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-colors ${
                  step === s
                    ? 'bg-blue-500 text-white'
                    : step > s
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-500'
                }`}
              >
                {step > s ? <CheckCircle size={20} /> : s}
              </div>
              <span className={`ml-2 text-sm font-medium ${step >= s ? textColor : 'text-gray-400'}`}>
                {s === 1 ? 'Job Info' : s === 2 ? 'Requirements' : 'Review'}
              </span>
            </div>
            {s < 3 && (
              <ChevronRight className="mx-4 text-gray-400" size={20} />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start space-x-3">
          <AlertCircle className="text-red-500 flex-shrink-0" size={20} />
          <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
        </div>
      )}

      {/* Step Content */}
      <div className={`${cardBg} rounded-xl p-8 border ${borderColor} mb-6`}>
        {/* Step 1: Job Information */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <label className={`block text-sm font-medium ${textColor} mb-2`}>
                Job Name
              </label>
              <input
                type="text"
                value={formData.jobName}
                onChange={(e) => updateFormData('jobName', e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="e.g., AI Model Training, Rendering Project"
                autoFocus
              />
              <p className="text-xs text-gray-500 mt-1">Give your cluster a descriptive name</p>
            </div>

            <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
              <div className="flex items-start space-x-3">
                <Info className="text-blue-500 flex-shrink-0 mt-0.5" size={20} />
                <div className="text-sm text-blue-900 dark:text-blue-300">
                  <p className="font-medium mb-1">What is a GPU Cluster?</p>
                  <p>A cluster distributes your compute-intensive job across multiple GPUs for faster processing. Our DPP algorithm selects the optimal GPUs based on performance, reliability, and cost.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Requirements */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <label className={`block text-sm font-medium ${textColor} mb-2 flex items-center space-x-2`}>
                <Zap size={16} />
                <span>Compute Intensity (TFLOPS)</span>
              </label>
              <input
                type="number"
                value={formData.computeIntensity}
                onChange={(e) => updateFormData('computeIntensity', parseInt(e.target.value) || 0)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                min="100"
                step="100"
              />
              <p className="text-xs text-gray-500 mt-1">Total computational power required (100-50000 TFLOPS)</p>
            </div>

            <div>
              <label className={`block text-sm font-medium ${textColor} mb-2 flex items-center space-x-2`}>
                <Cpu size={16} />
                <span>VRAM per GPU (GB)</span>
              </label>
              <select
                value={formData.vramGb}
                onChange={(e) => updateFormData('vramGb', parseInt(e.target.value))}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              >
                <option value={8}>8 GB</option>
                <option value={12}>12 GB</option>
                <option value={16}>16 GB</option>
                <option value={24}>24 GB</option>
                <option value={32}>32 GB</option>
                <option value={48}>48 GB</option>
                <option value={80}>80 GB</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">Minimum VRAM required per GPU</p>
            </div>

            <div>
              <label className={`block text-sm font-medium ${textColor} mb-2 flex items-center space-x-2`}>
                <Clock size={16} />
                <span>Deadline (Hours)</span>
              </label>
              <input
                type="number"
                value={formData.deadlineHours}
                onChange={(e) => updateFormData('deadlineHours', parseInt(e.target.value) || 0)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                min="1"
                max="720"
              />
              <p className="text-xs text-gray-500 mt-1">Time limit for job completion (1-720 hours)</p>
            </div>

            <div>
              <label className={`block text-sm font-medium ${textColor} mb-2`}>
                GPU Count (Optional)
              </label>
              <input
                type="number"
                value={formData.gpuCount || ''}
                onChange={(e) => updateFormData('gpuCount', e.target.value ? parseInt(e.target.value) : null)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                placeholder="Auto (recommended)"
                min="1"
                max="32"
              />
              <p className="text-xs text-gray-500 mt-1">Leave empty for DPP to calculate optimal count</p>
            </div>

            <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
              <div className="flex items-start space-x-3">
                <Sparkles className="text-purple-500 flex-shrink-0 mt-0.5" size={20} />
                <div className="text-sm text-purple-900 dark:text-purple-300">
                  <p className="font-medium mb-1">DPP Algorithm</p>
                  <p>Our Dynamic Pooling Protocol automatically selects the best GPUs based on G-Score (performance × reliability × efficiency) and calculates fair earnings distribution.</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Review & Simulation */}
        {step === 3 && simulation && (
          <div className="space-y-6">
            <div className="text-center pb-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className={`text-2xl font-bold ${textColor} mb-2`}>{formData.jobName}</h3>
              <p className="text-gray-500">Cluster Configuration Summary</p>
            </div>

            {/* Configuration Summary */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-4 border ${borderColor} rounded-lg`}>
                <div className="flex items-center space-x-2 mb-2">
                  <Zap className="text-blue-500" size={20} />
                  <span className="text-sm text-gray-500">Compute Intensity</span>
                </div>
                <p className={`text-xl font-bold ${textColor}`}>{formData.computeIntensity.toLocaleString()} TFLOPS</p>
              </div>

              <div className={`p-4 border ${borderColor} rounded-lg`}>
                <div className="flex items-center space-x-2 mb-2">
                  <Cpu className="text-green-500" size={20} />
                  <span className="text-sm text-gray-500">GPUs Selected</span>
                </div>
                <p className={`text-xl font-bold ${textColor}`}>{simulation.gpu_count} GPUs</p>
              </div>

              <div className={`p-4 border ${borderColor} rounded-lg`}>
                <div className="flex items-center space-x-2 mb-2">
                  <Clock className="text-orange-500" size={20} />
                  <span className="text-sm text-gray-500">Deadline</span>
                </div>
                <p className={`text-xl font-bold ${textColor}`}>{formData.deadlineHours} hours</p>
              </div>

              <div className={`p-4 border ${borderColor} rounded-lg`}>
                <div className="flex items-center space-x-2 mb-2">
                  <DollarSign className="text-purple-500" size={20} />
                  <span className="text-sm text-gray-500">Total Cost</span>
                </div>
                <p className={`text-xl font-bold ${textColor}`}>${parseFloat(simulation.total_cost).toFixed(2)}</p>
              </div>
            </div>

            {/* GPU List */}
            {simulation.selected_gpus && simulation.selected_gpus.length > 0 && (
              <div>
                <h4 className={`text-lg font-bold ${textColor} mb-3`}>Selected GPUs</h4>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {simulation.selected_gpus.map((gpu, idx) => (
                    <div
                      key={idx}
                      className={`p-3 border ${borderColor} rounded-lg flex items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors`}
                    >
                      <div>
                        <p className={`font-medium ${textColor}`}>{gpu.model}</p>
                        <p className="text-xs text-gray-500">
                          {gpu.provider} • {gpu.vram_gb}GB VRAM • G-Score: {gpu.g_score}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className={`font-bold text-blue-500`}>${parseFloat(gpu.price_per_hour).toFixed(2)}/hr</p>
                        <p className="text-xs text-gray-500">{gpu.location}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Cost Breakdown */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-6 border border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between mb-4">
                <span className="text-lg font-medium text-blue-900 dark:text-blue-300">Estimated Total Cost</span>
                <span className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  ${parseFloat(simulation.total_cost).toFixed(2)}
                </span>
              </div>
              <div className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                <p>• Payment processed when cluster starts</p>
                <p>• Earnings distributed to providers on completion</p>
                <p>• Fair compensation based on contribution scores</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => {
            if (step === 1 && onClose) {
              onClose();
            } else {
              setStep(step - 1);
            }
          }}
          className="px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors flex items-center space-x-2"
        >
          <ChevronLeft size={20} />
          <span>{step === 1 ? 'Cancel' : 'Back'}</span>
        </button>

        {step < 2 && (
          <button
            onClick={() => setStep(step + 1)}
            disabled={!canProceed()}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <span>Next</span>
            <ChevronRight size={20} />
          </button>
        )}

        {step === 2 && (
          <button
            onClick={handleSimulate}
            disabled={!canProceed() || simulating}
            className="px-6 py-3 bg-purple-500 hover:bg-purple-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {simulating ? (
              <>
                <Loader className="animate-spin" size={20} />
                <span>Simulating...</span>
              </>
            ) : (
              <>
                <Sparkles size={20} />
                <span>Simulate Cluster</span>
              </>
            )}
          </button>
        )}

        {step === 3 && (
          <button
            onClick={handleCreate}
            disabled={loading}
            className="px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {loading ? (
              <>
                <Loader className="animate-spin" size={20} />
                <span>Creating...</span>
              </>
            ) : (
              <>
                <CheckCircle size={20} />
                <span>Create Cluster</span>
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}
