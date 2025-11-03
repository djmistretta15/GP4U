/**
 * Wallet Manager Component
 * Handles all wallet operations: balance, deposits, withdrawals, transactions
 */

import React, { useState, useEffect } from 'react';
import { walletAPI } from '../services/api';
import {
  Wallet, DollarSign, TrendingUp, TrendingDown, Clock,
  ArrowUpCircle, ArrowDownCircle, RefreshCw, AlertCircle,
  CheckCircle, Loader, Calendar, Filter
} from 'lucide-react';

export default function WalletManager({ darkMode }) {
  const [wallet, setWallet] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview'); // overview, deposit, withdraw, transactions
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Deposit/Withdraw form state
  const [amount, setAmount] = useState('');
  const [destinationAddress, setDestinationAddress] = useState('');
  const [processing, setProcessing] = useState(false);

  // Transaction filters
  const [transactionFilter, setTransactionFilter] = useState(null);
  const [transactionLimit, setTransactionLimit] = useState(50);

  const cardBg = darkMode ? 'bg-gray-800' : 'bg-white';
  const textColor = darkMode ? 'text-white' : 'text-gray-900';
  const borderColor = darkMode ? 'border-gray-700' : 'border-gray-200';

  useEffect(() => {
    loadWalletData();
  }, []);

  useEffect(() => {
    if (activeTab === 'transactions') {
      loadTransactions();
    }
  }, [activeTab, transactionFilter, transactionLimit]);

  const loadWalletData = async () => {
    try {
      setLoading(true);
      const [walletData, analyticsData] = await Promise.all([
        walletAPI.getBalance(),
        walletAPI.getAnalytics(30)
      ]);
      setWallet(walletData);
      setAnalytics(analyticsData);
    } catch (err) {
      setError('Failed to load wallet data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadTransactions = async () => {
    try {
      const txData = await walletAPI.getTransactions(
        transactionLimit,
        0,
        transactionFilter
      );
      setTransactions(txData);
    } catch (err) {
      console.error('Failed to load transactions:', err);
    }
  };

  const handleDeposit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setProcessing(true);

    try {
      await walletAPI.deposit(amount);
      setSuccess(`Successfully deposited $${amount} USDC`);
      setAmount('');
      await loadWalletData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Deposit failed');
    } finally {
      setProcessing(false);
    }
  };

  const handleWithdraw = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setProcessing(true);

    try {
      await walletAPI.withdraw(amount, destinationAddress);
      setSuccess(`Successfully withdrew $${amount} USDC`);
      setAmount('');
      setDestinationAddress('');
      await loadWalletData();
    } catch (err) {
      setError(err.response?.data?.detail || 'Withdrawal failed');
    } finally {
      setProcessing(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTransactionIcon = (type) => {
    const icons = {
      DEPOSIT: <ArrowDownCircle className="text-green-500" size={20} />,
      WITHDRAWAL: <ArrowUpCircle className="text-red-500" size={20} />,
      RESERVATION_PAYMENT: <Clock className="text-blue-500" size={20} />,
      RESERVATION_REFUND: <RefreshCw className="text-green-500" size={20} />,
      CLUSTER_PAYMENT: <TrendingDown className="text-blue-500" size={20} />,
      CLUSTER_EARNINGS: <TrendingUp className="text-green-500" size={20} />
    };
    return icons[type] || <DollarSign size={20} />;
  };

  const getTransactionColor = (type) => {
    const incoming = ['DEPOSIT', 'RESERVATION_REFUND', 'CLUSTER_EARNINGS'];
    return incoming.includes(type) ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400';
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
      {/* Balance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Current Balance */}
        <div className={`${cardBg} rounded-xl p-6 border ${borderColor}`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Current Balance</span>
            <Wallet className="text-blue-500" size={20} />
          </div>
          <p className={`text-3xl font-bold ${textColor}`}>
            ${parseFloat(wallet?.balance_usdc || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <p className="text-xs text-gray-500 mt-1">USDC</p>
        </div>

        {/* Total Earned */}
        <div className={`${cardBg} rounded-xl p-6 border ${borderColor}`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Total Earned</span>
            <TrendingUp className="text-green-500" size={20} />
          </div>
          <p className={`text-3xl font-bold ${textColor}`}>
            ${parseFloat(wallet?.total_earned || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <p className="text-xs text-gray-500 mt-1">Lifetime</p>
        </div>

        {/* Total Spent */}
        <div className={`${cardBg} rounded-xl p-6 border ${borderColor}`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500 dark:text-gray-400">Total Spent</span>
            <TrendingDown className="text-red-500" size={20} />
          </div>
          <p className={`text-3xl font-bold ${textColor}`}>
            ${parseFloat(wallet?.total_spent || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <p className="text-xs text-gray-500 mt-1">Lifetime</p>
        </div>
      </div>

      {/* Tabs */}
      <div className={`${cardBg} rounded-xl border ${borderColor} overflow-hidden`}>
        <div className="flex border-b border-gray-200 dark:border-gray-700">
          {['overview', 'deposit', 'withdraw', 'transactions'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 py-3 px-4 text-sm font-medium transition-colors ${
                activeTab === tab
                  ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-b-2 border-blue-500'
                  : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        <div className="p-6">
          {/* Alerts */}
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

          {/* Overview Tab */}
          {activeTab === 'overview' && analytics && (
            <div className="space-y-4">
              <h3 className={`text-lg font-bold ${textColor} mb-4`}>30-Day Analytics</h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className={`p-4 border ${borderColor} rounded-lg`}>
                  <p className="text-sm text-gray-500 mb-1">Total Spent (30 days)</p>
                  <p className={`text-2xl font-bold ${textColor}`}>
                    ${parseFloat(analytics.total_spent).toFixed(2)}
                  </p>
                </div>

                <div className={`p-4 border ${borderColor} rounded-lg`}>
                  <p className="text-sm text-gray-500 mb-1">Transactions (30 days)</p>
                  <p className={`text-2xl font-bold ${textColor}`}>
                    {analytics.total_transactions}
                  </p>
                </div>
              </div>

              {analytics.breakdown && Object.keys(analytics.breakdown).length > 0 && (
                <div>
                  <h4 className={`text-sm font-bold ${textColor} mb-3`}>Spending Breakdown</h4>
                  <div className="space-y-2">
                    {Object.entries(analytics.breakdown).map(([type, data]) => (
                      <div key={type} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <span className={`text-sm ${textColor}`}>{type.replace('_', ' ')}</span>
                        <div className="text-right">
                          <p className={`font-bold ${textColor}`}>${parseFloat(data.total).toFixed(2)}</p>
                          <p className="text-xs text-gray-500">{data.count} transactions</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Deposit Tab */}
          {activeTab === 'deposit' && (
            <form onSubmit={handleDeposit} className="space-y-4">
              <div>
                <label className={`block text-sm font-medium ${textColor} mb-2`}>
                  Deposit Amount (USDC)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="0.00"
                  required
                />
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  <strong>Note:</strong> In production, this will connect to your Web3 wallet for USDC deposits.
                  For MVP testing, deposits are simulated.
                </p>
              </div>

              <button
                type="submit"
                disabled={processing || !amount}
                className="w-full bg-green-500 hover:bg-green-600 text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {processing ? (
                  <>
                    <Loader className="animate-spin" size={20} />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <ArrowDownCircle size={20} />
                    <span>Deposit Funds</span>
                  </>
                )}
              </button>
            </form>
          )}

          {/* Withdraw Tab */}
          {activeTab === 'withdraw' && (
            <form onSubmit={handleWithdraw} className="space-y-4">
              <div>
                <label className={`block text-sm font-medium ${textColor} mb-2`}>
                  Withdrawal Amount (USDC)
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  max={wallet?.balance_usdc}
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="0.00"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Available: ${parseFloat(wallet?.balance_usdc || 0).toFixed(2)} USDC
                </p>
              </div>

              <div>
                <label className={`block text-sm font-medium ${textColor} mb-2`}>
                  Destination Wallet Address (Optional)
                </label>
                <input
                  type="text"
                  value={destinationAddress}
                  onChange={(e) => setDestinationAddress(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="0x..."
                />
              </div>

              <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
                <p className="text-sm text-yellow-700 dark:text-yellow-300">
                  <strong>Note:</strong> In production, withdrawals will be sent to your specified USDC wallet address.
                  For MVP testing, withdrawals are simulated.
                </p>
              </div>

              <button
                type="submit"
                disabled={processing || !amount}
                className="w-full bg-red-500 hover:bg-red-600 text-white font-medium py-3 px-4 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {processing ? (
                  <>
                    <Loader className="animate-spin" size={20} />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <ArrowUpCircle size={20} />
                    <span>Withdraw Funds</span>
                  </>
                )}
              </button>
            </form>
          )}

          {/* Transactions Tab */}
          {activeTab === 'transactions' && (
            <div className="space-y-4">
              {/* Filters */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Filter size={16} className="text-gray-500" />
                  <select
                    value={transactionFilter || ''}
                    onChange={(e) => setTransactionFilter(e.target.value || null)}
                    className="text-sm border border-gray-300 dark:border-gray-600 rounded px-3 py-1 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="">All Types</option>
                    <option value="DEPOSIT">Deposits</option>
                    <option value="WITHDRAWAL">Withdrawals</option>
                    <option value="RESERVATION_PAYMENT">Reservation Payments</option>
                    <option value="CLUSTER_PAYMENT">Cluster Payments</option>
                    <option value="CLUSTER_EARNINGS">Earnings</option>
                  </select>
                </div>

                <button
                  onClick={loadTransactions}
                  className="text-sm text-blue-500 hover:text-blue-600 flex items-center space-x-1"
                >
                  <RefreshCw size={16} />
                  <span>Refresh</span>
                </button>
              </div>

              {/* Transaction List */}
              <div className="space-y-2">
                {transactions.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <DollarSign size={48} className="mx-auto mb-2 opacity-30" />
                    <p>No transactions yet</p>
                  </div>
                ) : (
                  transactions.map((tx) => (
                    <div
                      key={tx.id}
                      className={`p-4 border ${borderColor} rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {getTransactionIcon(tx.type)}
                          <div>
                            <p className={`font-medium ${textColor}`}>{tx.description}</p>
                            <p className="text-xs text-gray-500">{formatDate(tx.created_at)}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className={`font-bold ${getTransactionColor(tx.type)}`}>
                            {['DEPOSIT', 'RESERVATION_REFUND', 'CLUSTER_EARNINGS'].includes(tx.type) ? '+' : '-'}
                            ${parseFloat(tx.amount).toFixed(2)}
                          </p>
                          <p className="text-xs text-gray-500">
                            Balance: ${parseFloat(tx.balance_after).toFixed(2)}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
