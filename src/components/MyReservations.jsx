/**
 * My Reservations Component
 * Displays and manages user's GPU reservations
 */

import React, { useState, useEffect } from 'react';
import { reservationAPI } from '../services/api';
import { useToast } from '../context/ToastContext';
import {
  Calendar, Clock, DollarSign, Loader, X, Plus,
  CheckCircle, XCircle, AlertCircle, RefreshCw
} from 'lucide-react';

export default function MyReservations({ darkMode }) {
  const [reservations, setReservations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState(null); // null, PENDING, ACTIVE, COMPLETED, CANCELLED
  const toast = useToast();

  const cardBg = darkMode ? 'bg-gray-800' : 'bg-white';
  const textColor = darkMode ? 'text-white' : 'text-gray-900';
  const borderColor = darkMode ? 'border-gray-700' : 'border-gray-200';

  useEffect(() => {
    loadReservations();
  }, [filter]);

  const loadReservations = async () => {
    try {
      setLoading(true);
      const data = await reservationAPI.getMyBookings(filter);
      setReservations(data);
    } catch (err) {
      toast.error('Failed to load reservations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (reservationId) => {
    if (!confirm('Are you sure you want to cancel this reservation? You will receive a full refund.')) {
      return;
    }

    try {
      await reservationAPI.cancel(reservationId);
      toast.success('Reservation cancelled and refunded');
      loadReservations();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to cancel reservation');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getDuration = (start, end) => {
    const hours = (new Date(end) - new Date(start)) / (1000 * 60 * 60);
    return hours.toFixed(1);
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
        icon: <CheckCircle size={14} />
      },
      COMPLETED: {
        bg: 'bg-blue-100 dark:bg-blue-900/30',
        text: 'text-blue-800 dark:text-blue-300',
        icon: <CheckCircle size={14} />
      },
      CANCELLED: {
        bg: 'bg-gray-100 dark:bg-gray-700',
        text: 'text-gray-800 dark:text-gray-300',
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

  const canCancel = (reservation) => {
    return (
      (reservation.status === 'PENDING' || reservation.status === 'ACTIVE') &&
      new Date(reservation.start_time) > new Date()
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
        <h2 className={`text-2xl font-bold ${textColor}`}>My Reservations</h2>
        <button
          onClick={loadReservations}
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
        {['PENDING', 'ACTIVE', 'COMPLETED', 'CANCELLED'].map((status) => (
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

      {/* Reservations List */}
      {reservations.length === 0 ? (
        <div className={`${cardBg} rounded-xl p-12 border ${borderColor} text-center`}>
          <Calendar size={48} className="mx-auto mb-4 text-gray-400" />
          <p className="text-gray-500 mb-4">No reservations found</p>
          <p className="text-sm text-gray-400">Book your first GPU to get started!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {reservations.map((reservation) => (
            <div
              key={reservation.id}
              className={`${cardBg} rounded-xl p-6 border ${borderColor} hover:border-blue-300 dark:hover:border-blue-700 transition-colors`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className={`text-lg font-bold ${textColor}`}>
                      Reservation #{reservation.id.substring(0, 8)}
                    </h3>
                    {getStatusBadge(reservation.status)}
                  </div>
                  <p className="text-sm text-gray-500">
                    Created {formatDate(reservation.created_at)}
                  </p>
                </div>

                <div className="text-right">
                  <p className="text-2xl font-bold text-blue-500">
                    ${parseFloat(reservation.total_cost).toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500">Total Cost</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className={`p-3 border ${borderColor} rounded-lg`}>
                  <div className="flex items-center space-x-2 mb-1">
                    <Calendar size={16} className="text-blue-500" />
                    <span className="text-xs text-gray-500">Start Time</span>
                  </div>
                  <p className={`text-sm font-medium ${textColor}`}>
                    {formatDate(reservation.start_time)}
                  </p>
                </div>

                <div className={`p-3 border ${borderColor} rounded-lg`}>
                  <div className="flex items-center space-x-2 mb-1">
                    <Calendar size={16} className="text-green-500" />
                    <span className="text-xs text-gray-500">End Time</span>
                  </div>
                  <p className={`text-sm font-medium ${textColor}`}>
                    {formatDate(reservation.end_time)}
                  </p>
                </div>

                <div className={`p-3 border ${borderColor} rounded-lg`}>
                  <div className="flex items-center space-x-2 mb-1">
                    <Clock size={16} className="text-purple-500" />
                    <span className="text-xs text-gray-500">Duration</span>
                  </div>
                  <p className={`text-sm font-medium ${textColor}`}>
                    {getDuration(reservation.start_time, reservation.end_time)} hours
                  </p>
                </div>
              </div>

              {/* Actions */}
              {canCancel(reservation) && (
                <div className="flex items-center justify-end space-x-2 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button
                    onClick={() => handleCancel(reservation.id)}
                    className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white text-sm rounded-lg transition-colors flex items-center space-x-2"
                  >
                    <X size={16} />
                    <span>Cancel & Refund</span>
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
