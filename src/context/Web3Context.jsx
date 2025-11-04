import { createContext, useContext, useState, useEffect } from 'react';
import web3Service from '../services/web3Service';

const Web3Context = createContext(null);

export function Web3Provider({ children }) {
  const [isConnected, setIsConnected] = useState(false);
  const [account, setAccount] = useState(null);
  const [chainId, setChainId] = useState(null);
  const [networkName, setNetworkName] = useState(null);
  const [usdcBalance, setUsdcBalance] = useState('0');
  const [nativeBalance, setNativeBalance] = useState('0');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Check if wallet is already connected on mount
  useEffect(() => {
    checkConnection();
    setupEventListeners();
  }, []);

  // Auto-refresh balances when connected
  useEffect(() => {
    if (isConnected && account) {
      loadBalances();
      const interval = setInterval(loadBalances, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [isConnected, account, chainId]);

  /**
   * Check if wallet is already connected (on page load)
   */
  const checkConnection = async () => {
    if (!web3Service.isWalletAvailable()) {
      return;
    }

    try {
      // Check if we have permission to access accounts
      const accounts = await window.ethereum.request({ method: 'eth_accounts' });
      if (accounts && accounts.length > 0) {
        // Wallet is already connected, initialize
        await connectWallet();
      }
    } catch (err) {
      console.error('Error checking wallet connection:', err);
    }
  };

  /**
   * Set up event listeners for wallet changes
   */
  const setupEventListeners = () => {
    // Listen for account changes
    window.addEventListener('walletAccountChanged', handleAccountChanged);

    // Listen for disconnect
    window.addEventListener('walletDisconnected', handleDisconnect);

    return () => {
      window.removeEventListener('walletAccountChanged', handleAccountChanged);
      window.removeEventListener('walletDisconnected', handleDisconnect);
    };
  };

  /**
   * Handle account changed event
   */
  const handleAccountChanged = (event) => {
    const { account: newAccount } = event.detail;
    setAccount(newAccount);
    loadBalances();
  };

  /**
   * Handle wallet disconnected event
   */
  const handleDisconnect = () => {
    setIsConnected(false);
    setAccount(null);
    setChainId(null);
    setNetworkName(null);
    setUsdcBalance('0');
    setNativeBalance('0');
    setError(null);
  };

  /**
   * Connect to user's wallet
   */
  const connectWallet = async () => {
    if (!web3Service.isWalletAvailable()) {
      setError('Please install MetaMask or another Web3 wallet');
      return false;
    }

    setIsLoading(true);
    setError(null);

    try {
      const connection = await web3Service.connectWallet();

      setIsConnected(true);
      setAccount(connection.account);
      setChainId(connection.chainId);
      setNetworkName(connection.networkName);

      // Load balances
      await loadBalances();

      return true;
    } catch (err) {
      console.error('Error connecting wallet:', err);
      setError(err.message || 'Failed to connect wallet');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Disconnect wallet
   */
  const disconnectWallet = () => {
    web3Service.disconnect();
    handleDisconnect();
  };

  /**
   * Load USDC and native token balances
   */
  const loadBalances = async () => {
    if (!isConnected && !web3Service.getAccount()) {
      return;
    }

    try {
      // Load balances in parallel
      const [usdc, native] = await Promise.all([
        web3Service.getUSDCBalance().catch(() => '0'),
        web3Service.getNativeBalance().catch(() => '0'),
      ]);

      setUsdcBalance(usdc);
      setNativeBalance(native);
    } catch (err) {
      console.error('Error loading balances:', err);
    }
  };

  /**
   * Switch to a different network
   */
  const switchNetwork = async (targetChainId) => {
    setIsLoading(true);
    setError(null);

    try {
      await web3Service.switchNetwork(targetChainId);
      // Page will reload automatically after network change
      return true;
    } catch (err) {
      console.error('Error switching network:', err);
      setError(err.message || 'Failed to switch network');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Transfer USDC to another address
   */
  const transferUSDC = async (toAddress, amount) => {
    if (!isConnected) {
      throw new Error('Wallet not connected');
    }

    setIsLoading(true);
    setError(null);

    try {
      const tx = await web3Service.transferUSDC(toAddress, amount);

      // Wait for transaction confirmation
      await tx.wait();

      // Refresh balances
      await loadBalances();

      return tx.hash;
    } catch (err) {
      console.error('Error transferring USDC:', err);
      setError(err.message || 'Failed to transfer USDC');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Deposit USDC to GP4U platform
   */
  const depositUSDC = async (amount, platformAddress) => {
    if (!isConnected) {
      throw new Error('Wallet not connected');
    }

    setIsLoading(true);
    setError(null);

    try {
      const tx = await web3Service.depositUSDC(amount, platformAddress);

      // Return transaction hash immediately, allow caller to wait if needed
      return {
        hash: tx.hash,
        wait: async () => {
          await tx.wait();
          await loadBalances();
        },
      };
    } catch (err) {
      console.error('Error depositing USDC:', err);
      setError(err.message || 'Failed to deposit USDC');
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Wait for a transaction to be confirmed
   */
  const waitForTransaction = async (txHash, confirmations = 1) => {
    try {
      const receipt = await web3Service.waitForTransaction(txHash, confirmations);

      // Refresh balances after transaction is confirmed
      if (receipt.success) {
        await loadBalances();
      }

      return receipt;
    } catch (err) {
      console.error('Error waiting for transaction:', err);
      throw err;
    }
  };

  /**
   * Get transaction receipt
   */
  const getTransactionReceipt = async (txHash) => {
    try {
      return await web3Service.getTransactionReceipt(txHash);
    } catch (err) {
      console.error('Error getting transaction receipt:', err);
      throw err;
    }
  };

  /**
   * Get current gas price
   */
  const getGasPrice = async () => {
    try {
      return await web3Service.getGasPrice();
    } catch (err) {
      console.error('Error getting gas price:', err);
      throw err;
    }
  };

  /**
   * Estimate gas for a transfer
   */
  const estimateTransferGas = async (toAddress, amount) => {
    try {
      return await web3Service.estimateTransferGas(toAddress, amount);
    } catch (err) {
      console.error('Error estimating gas:', err);
      throw err;
    }
  };

  /**
   * Sign a message
   */
  const signMessage = async (message) => {
    if (!isConnected) {
      throw new Error('Wallet not connected');
    }

    try {
      return await web3Service.signMessage(message);
    } catch (err) {
      console.error('Error signing message:', err);
      throw err;
    }
  };

  /**
   * Format wallet address for display (0x1234...5678)
   */
  const formatAddress = (address) => {
    if (!address) return '';
    return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
  };

  /**
   * Get block explorer URL for transaction
   */
  const getExplorerUrl = (txHash) => {
    const networkInfo = web3Service.getNetworkInfo();
    if (!networkInfo) return null;
    return `${networkInfo.blockExplorer}/tx/${txHash}`;
  };

  /**
   * Check if on supported network
   */
  const isSupportedNetwork = () => {
    return web3Service.isSupportedNetwork();
  };

  const value = {
    // State
    isConnected,
    account,
    chainId,
    networkName,
    usdcBalance,
    nativeBalance,
    isLoading,
    error,

    // Actions
    connectWallet,
    disconnectWallet,
    switchNetwork,
    transferUSDC,
    depositUSDC,
    loadBalances,
    waitForTransaction,
    getTransactionReceipt,
    getGasPrice,
    estimateTransferGas,
    signMessage,

    // Utilities
    formatAddress,
    getExplorerUrl,
    isSupportedNetwork,
    isWalletAvailable: web3Service.isWalletAvailable(),
  };

  return <Web3Context.Provider value={value}>{children}</Web3Context.Provider>;
}

/**
 * Hook to use Web3 context
 */
export function useWeb3() {
  const context = useContext(Web3Context);
  if (!context) {
    throw new Error('useWeb3 must be used within a Web3Provider');
  }
  return context;
}

export default Web3Context;
