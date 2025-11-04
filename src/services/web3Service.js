import { BrowserProvider, Contract, formatUnits, parseUnits } from 'ethers';

// USDC Contract Addresses
const USDC_CONTRACTS = {
  // Ethereum Mainnet
  1: '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
  // Polygon PoS
  137: '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359',
  // Sepolia Testnet (for development)
  11155111: '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
  // Polygon Mumbai Testnet (for development)
  80001: '0x0FA8781a83E46826621b3BC094Ea2A0212e71B23',
};

// Network configurations
const NETWORKS = {
  1: {
    name: 'Ethereum Mainnet',
    chainId: '0x1',
    rpcUrl: 'https://eth.llamarpc.com',
    blockExplorer: 'https://etherscan.io',
  },
  137: {
    name: 'Polygon PoS',
    chainId: '0x89',
    rpcUrl: 'https://polygon-rpc.com',
    blockExplorer: 'https://polygonscan.com',
  },
  11155111: {
    name: 'Sepolia Testnet',
    chainId: '0xaa36a7',
    rpcUrl: 'https://rpc.sepolia.org',
    blockExplorer: 'https://sepolia.etherscan.io',
  },
  80001: {
    name: 'Polygon Mumbai',
    chainId: '0x13881',
    rpcUrl: 'https://rpc-mumbai.maticvigil.com',
    blockExplorer: 'https://mumbai.polygonscan.com',
  },
};

// ERC-20 USDC ABI (minimal for our needs)
const USDC_ABI = [
  'function balanceOf(address owner) view returns (uint256)',
  'function transfer(address to, uint256 amount) returns (bool)',
  'function approve(address spender, uint256 amount) returns (bool)',
  'function allowance(address owner, address spender) view returns (uint256)',
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
  'function name() view returns (string)',
];

class Web3Service {
  constructor() {
    this.provider = null;
    this.signer = null;
    this.account = null;
    this.chainId = null;
    this.usdcContract = null;
  }

  /**
   * Check if MetaMask or another Web3 wallet is installed
   */
  isWalletAvailable() {
    return typeof window !== 'undefined' && typeof window.ethereum !== 'undefined';
  }

  /**
   * Connect to the user's wallet (MetaMask, etc.)
   */
  async connectWallet() {
    if (!this.isWalletAvailable()) {
      throw new Error('Please install MetaMask or another Web3 wallet to use this feature');
    }

    try {
      // Request account access
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      });

      if (!accounts || accounts.length === 0) {
        throw new Error('No accounts found. Please unlock your wallet.');
      }

      // Initialize provider and signer
      this.provider = new BrowserProvider(window.ethereum);
      this.signer = await this.provider.getSigner();
      this.account = accounts[0];

      // Get current network
      const network = await this.provider.getNetwork();
      this.chainId = Number(network.chainId);

      // Initialize USDC contract
      this.initializeUSDCContract();

      // Set up event listeners for account and network changes
      this.setupEventListeners();

      return {
        account: this.account,
        chainId: this.chainId,
        networkName: NETWORKS[this.chainId]?.name || 'Unknown Network',
      };
    } catch (error) {
      console.error('Error connecting wallet:', error);
      throw error;
    }
  }

  /**
   * Initialize USDC contract for current network
   */
  initializeUSDCContract() {
    const usdcAddress = USDC_CONTRACTS[this.chainId];
    if (!usdcAddress) {
      console.warn(`USDC contract not configured for chain ID ${this.chainId}`);
      this.usdcContract = null;
      return;
    }

    this.usdcContract = new Contract(usdcAddress, USDC_ABI, this.signer);
  }

  /**
   * Set up event listeners for wallet changes
   */
  setupEventListeners() {
    if (!window.ethereum) return;

    // Account changed
    window.ethereum.on('accountsChanged', async (accounts) => {
      if (accounts.length === 0) {
        // User disconnected wallet
        this.disconnect();
      } else if (accounts[0] !== this.account) {
        // User switched accounts
        this.account = accounts[0];
        this.signer = await this.provider.getSigner();
        this.initializeUSDCContract();
        window.dispatchEvent(new CustomEvent('walletAccountChanged', { detail: { account: this.account } }));
      }
    });

    // Network changed
    window.ethereum.on('chainChanged', (chainIdHex) => {
      // Reload the page as recommended by MetaMask
      window.location.reload();
    });
  }

  /**
   * Disconnect wallet
   */
  disconnect() {
    this.provider = null;
    this.signer = null;
    this.account = null;
    this.chainId = null;
    this.usdcContract = null;
    window.dispatchEvent(new CustomEvent('walletDisconnected'));
  }

  /**
   * Get current connected account
   */
  getAccount() {
    return this.account;
  }

  /**
   * Get current network chain ID
   */
  getChainId() {
    return this.chainId;
  }

  /**
   * Get network information
   */
  getNetworkInfo() {
    return NETWORKS[this.chainId] || null;
  }

  /**
   * Check if on a supported network
   */
  isSupportedNetwork() {
    return this.chainId && USDC_CONTRACTS[this.chainId] !== undefined;
  }

  /**
   * Switch to a different network
   */
  async switchNetwork(chainId) {
    if (!this.isWalletAvailable()) {
      throw new Error('Wallet not available');
    }

    const network = NETWORKS[chainId];
    if (!network) {
      throw new Error(`Network ${chainId} not supported`);
    }

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: network.chainId }],
      });
    } catch (error) {
      // This error code indicates that the chain has not been added to MetaMask
      if (error.code === 4902) {
        await this.addNetwork(chainId);
      } else {
        throw error;
      }
    }
  }

  /**
   * Add a new network to the wallet
   */
  async addNetwork(chainId) {
    const network = NETWORKS[chainId];
    if (!network) {
      throw new Error(`Network ${chainId} not supported`);
    }

    try {
      await window.ethereum.request({
        method: 'wallet_addEthereumChain',
        params: [
          {
            chainId: network.chainId,
            chainName: network.name,
            rpcUrls: [network.rpcUrl],
            blockExplorerUrls: [network.blockExplorer],
          },
        ],
      });
    } catch (error) {
      console.error('Error adding network:', error);
      throw error;
    }
  }

  /**
   * Get USDC balance for connected wallet
   */
  async getUSDCBalance() {
    if (!this.usdcContract || !this.account) {
      throw new Error('Wallet not connected or USDC not available on this network');
    }

    try {
      const balance = await this.usdcContract.balanceOf(this.account);
      // USDC uses 6 decimals
      return formatUnits(balance, 6);
    } catch (error) {
      console.error('Error getting USDC balance:', error);
      throw error;
    }
  }

  /**
   * Get ETH/MATIC balance for gas fees
   */
  async getNativeBalance() {
    if (!this.provider || !this.account) {
      throw new Error('Wallet not connected');
    }

    try {
      const balance = await this.provider.getBalance(this.account);
      return formatUnits(balance, 18);
    } catch (error) {
      console.error('Error getting native balance:', error);
      throw error;
    }
  }

  /**
   * Transfer USDC to another address
   */
  async transferUSDC(toAddress, amount) {
    if (!this.usdcContract) {
      throw new Error('USDC contract not initialized');
    }

    try {
      // Convert amount to USDC units (6 decimals)
      const amountInUnits = parseUnits(amount.toString(), 6);

      // Send transaction
      const tx = await this.usdcContract.transfer(toAddress, amountInUnits);

      // Return transaction hash immediately
      return {
        hash: tx.hash,
        wait: () => tx.wait(), // Allow caller to wait for confirmation
      };
    } catch (error) {
      console.error('Error transferring USDC:', error);
      throw error;
    }
  }

  /**
   * Deposit USDC to GP4U platform (approve + transfer to backend)
   */
  async depositUSDC(amount, platformAddress) {
    if (!this.usdcContract) {
      throw new Error('USDC contract not initialized');
    }

    try {
      // Convert amount to USDC units (6 decimals)
      const amountInUnits = parseUnits(amount.toString(), 6);

      // Step 1: Approve platform to spend USDC
      const approveTx = await this.usdcContract.approve(platformAddress, amountInUnits);
      await approveTx.wait(); // Wait for approval confirmation

      // Step 2: Transfer USDC to platform
      const transferTx = await this.usdcContract.transfer(platformAddress, amountInUnits);

      return {
        hash: transferTx.hash,
        wait: () => transferTx.wait(),
      };
    } catch (error) {
      console.error('Error depositing USDC:', error);
      throw error;
    }
  }

  /**
   * Wait for transaction confirmation
   */
  async waitForTransaction(txHash, confirmations = 1) {
    if (!this.provider) {
      throw new Error('Provider not initialized');
    }

    try {
      const receipt = await this.provider.waitForTransaction(txHash, confirmations);
      return {
        success: receipt.status === 1,
        blockNumber: receipt.blockNumber,
        gasUsed: receipt.gasUsed.toString(),
        transactionHash: receipt.hash,
      };
    } catch (error) {
      console.error('Error waiting for transaction:', error);
      throw error;
    }
  }

  /**
   * Get transaction receipt
   */
  async getTransactionReceipt(txHash) {
    if (!this.provider) {
      throw new Error('Provider not initialized');
    }

    try {
      const receipt = await this.provider.getTransactionReceipt(txHash);
      if (!receipt) {
        return null;
      }

      return {
        success: receipt.status === 1,
        blockNumber: receipt.blockNumber,
        gasUsed: receipt.gasUsed.toString(),
        transactionHash: receipt.hash,
        from: receipt.from,
        to: receipt.to,
      };
    } catch (error) {
      console.error('Error getting transaction receipt:', error);
      throw error;
    }
  }

  /**
   * Estimate gas for a USDC transfer
   */
  async estimateTransferGas(toAddress, amount) {
    if (!this.usdcContract) {
      throw new Error('USDC contract not initialized');
    }

    try {
      const amountInUnits = parseUnits(amount.toString(), 6);
      const gasEstimate = await this.usdcContract.transfer.estimateGas(toAddress, amountInUnits);
      return gasEstimate.toString();
    } catch (error) {
      console.error('Error estimating gas:', error);
      throw error;
    }
  }

  /**
   * Get current gas price
   */
  async getGasPrice() {
    if (!this.provider) {
      throw new Error('Provider not initialized');
    }

    try {
      const feeData = await this.provider.getFeeData();
      return {
        gasPrice: feeData.gasPrice ? formatUnits(feeData.gasPrice, 'gwei') : null,
        maxFeePerGas: feeData.maxFeePerGas ? formatUnits(feeData.maxFeePerGas, 'gwei') : null,
        maxPriorityFeePerGas: feeData.maxPriorityFeePerGas ? formatUnits(feeData.maxPriorityFeePerGas, 'gwei') : null,
      };
    } catch (error) {
      console.error('Error getting gas price:', error);
      throw error;
    }
  }

  /**
   * Sign a message with the user's wallet
   */
  async signMessage(message) {
    if (!this.signer) {
      throw new Error('Signer not initialized');
    }

    try {
      const signature = await this.signer.signMessage(message);
      return signature;
    } catch (error) {
      console.error('Error signing message:', error);
      throw error;
    }
  }
}

// Export singleton instance
const web3Service = new Web3Service();
export default web3Service;
