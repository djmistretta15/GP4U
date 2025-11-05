/**
 * Reservation Booking Component
 * Allows users to book GPU time blocks with calendar view
 */

import React, { useState, useEffect } from 'react';
import { reservationAPI, gpuAPI } from '../services/api';
import { Calendar, Clock, DollarSign, CheckCircle, XCircle, Loader, AlertCircle } from 'lucide-react';

export default function ReservationBooking({ gpuId, onClose, darkMode }) {
  const [gpu, setGpu] = useState(null);
  const [calendar, setCalendar] = useState([]);
  const [startTime, setStartTime] = useState('');
  const [endTime, setEndTime] = useState('');
  const [estimatedCost, setEstimatedCost] = useState(0);
  const [loading, setLoading] = useState(true);
  const [booking, setBooking] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const cardBg = darkMode ? 'bg-gray-800' : 'bg-white';
  const textColor = darkMode ? 'text-white' : 'text-gray-900';
  const borderColor = darkMode ? 'border-gray-700' : 'border-gray-200';

  useEffect(() => {
    loadGpuDetails();
    loadCalendar();
  }, [gpuId]);

  useEffect(() => {
    calculateCost();
  }, [startTime, endTime, gpu]);

  const loadGpuDetails = async () => {
    try {
      const gpuData = await gpuAPI.getById(gpuId);
      setGpu(gpuData);
    } catch (err) {
      setError('Failed to load GPU details');
    }
  };

  const loadCalendar = async () => {
    try {
      setLoading(true);
      const calendarData = await reservationAPI.getCalendar(gpuId, 7);
      setCalendar(calendarData);
    } catch (err) {
      console.error('Failed to load calendar:', err);
    } finally {
      setLoading(false);
    }
  };

  const calculateCost = () => {
    if (!startTime || !endTime || !gpu) {
      setEstimatedCost(0);
      return;
    }

    const start = new Date(startTime);
    const end = new Date(endTime);
    const hours = (end - start) / (1000 * 60 * 60);

    if (hours > 0) {
      setEstimatedCost(hours * parseFloat(gpu.price_per_hour));
    } else {
      setEstimatedCost(0);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setBooking(true);

    try {
      const reservation = await reservationAPI.create(
        gpuId,
        new Date(startTime).toISOString(),
        new Date(endTime).toISOString()
      );

      setSuccess(`Reservation created successfully! ID: ${reservation.id.substring(0, 8)}...`);
      setTimeout(() => {
        if (onClose) onClose();
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create reservation');
    } finally {
      setBooking(false);
    }
  };

  const getMinStartTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 30); // Allow booking 30 minutes from now
    return now.toISOString().slice(0, 16);
  };

  const getMinEndTime = () => {
    if (!startTime) return '';
    const start = new Date(startTime);
    start.setHours(start.getHours() + 1); // Minimum 1 hour
    return start.toISOString().slice(0, 16);
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
      {/* GPU Info Header */}
      {gpu && (
        <div className={`${cardBg} rounded-xl p-6 border ${borderColor}`}>
          <h3 className={`text-xl font-bold ${textColor} mb-2`}>{gpu.model}</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Provider:</span>
              <span className={`ml-2 font-medium ${textColor}`}>{gpu.provider}</span>
            </div>
            <div>
              <span className="text-gray-500">Price:</span>
              <span className={`ml-2 font-medium text-blue-500`}>
                ${parseFloat(gpu.price_per_hour).toFixed(2)}/hr
              </span>
            </div>
            <div>
              <span className="text-gray-500">VRAM:</span>
              <span className={`ml-2 font-medium ${textColor}`}>{gpu.vram_gb}GB</span>
            </div>
            <div>
              <span className="text-gray-500">Location:</span>
              <span className={`ml-2 font-medium ${textColor}`}>{gpu.location}</span>
            </div>
          </div>
        </div>
      )}

      {/* Booking Form */}
      <div className={`${cardBg} rounded-xl p-6 border ${borderColor}`}>
        <h4 className={`text-lg font-bold ${textColor} mb-4 flex items-center space-x-2`}>
          <Calendar size={20} />
          <span>Book Time Slot</span>
        </h4>

        {error && (
          <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-start space-x-3">
            <AlertCircle className="text-red-500 flex-shrink-0" size={20} />
            <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg flex items-start space-x-3">
            <CheckCircle className="text-green-500 flex-shrink-0" size={20} />
            <p className="text-sm text-green-700 dark:text-green-400">{success}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Start Time */}
            <div>
              <label className={`block text-sm font-medium ${textColor} mb-2`}>
                Start Time
              </label>
              <input
                type="datetime-local"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                min={getMinStartTime()}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
              />
            </div>

            {/* End Time */}
            <div>
              <label className={`block text-sm font-medium ${textColor} mb-2`}>
                End Time
              </label>
              <input
                type="datetime-local"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                min={getMinEndTime()}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                required
                disabled={!startTime}
              />
            </div>
          </div>

          {/* Cost Estimate */}
          {estimatedCost > 0 && (
            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <DollarSign className="text-blue-500" size={20} />
                  <span className="font-medium text-blue-900 dark:text-blue-300">Estimated Cost</span>
                </div>
                <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  ${estimatedCost.toFixed(2)}
                </span>
              </div>
              <p className="text-xs text-blue-700 dark:text-blue-400 mt-2">
                Duration: {((new Date(endTime) - new Date(startTime)) / (1000 * 60 * 60)).toFixed(1)} hours
              </p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={booking || !startTime || !endTime || estimatedCost === 0}
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            {booking ? (
              <>
                <Loader className="animate-spin" size={20} />
                <span>Creating Reservation...</span>
              </>
            ) : (
              <>
                <CheckCircle size={20} />
                <span>Book Now</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Calendar View */}
      {calendar.length > 0 && (
        <div className={`${cardBg} rounded-xl p-6 border ${borderColor}`}>
          <h4 className={`text-lg font-bold ${textColor} mb-4`}>7-Day Availability</h4>
          <div className="space-y-2">
            {calendar.map((day, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <span className={`text-sm font-medium ${textColor}`}>
                  {new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                </span>
                <span className={`text-sm ${day.available ? 'text-green-500' : 'text-red-500'}`}>
                  {day.available ? '✓ Available' : '✗ Booked'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Notes */}
      <div className="text-xs text-gray-500 dark:text-gray-400 space-y-1">
        <p>• Payment will be processed when your reservation starts</p>
        <p>• You can cancel anytime before the start time for a full refund</p>
        <p>• Minimum booking: 1 hour</p>
      </div>
    </div>
  );
}
