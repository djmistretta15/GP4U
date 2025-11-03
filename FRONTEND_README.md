# GP4U Frontend

Modern React application for the GP4U GPU marketplace platform.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn
- GP4U Backend running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

## 📁 Project Structure

```
/src
  /components         # Reusable React components
    WalletManager.jsx      # Wallet operations (deposit, withdraw, transactions)
    ReservationBooking.jsx # GPU booking calendar
  /context           # React Context providers
    AuthContext.jsx        # Authentication state management
  /pages             # Page components
    Login.jsx             # User login
    Signup.jsx            # User registration
  /services          # API clients
    api.js                # Complete FastAPI integration
```

## 🔑 Features Implemented

### Phase 5 (Frontend Integration) - IN PROGRESS

- ✅ **API Client Service**
  - Complete FastAPI v1 integration
  - JWT token management with auto-refresh
  - Request/response interceptors
  - 40+ endpoint wrappers

- ✅ **Authentication System**
  - Login/Signup pages with validation
  - Auth context with React hooks
  - Token persistence in localStorage
  - Auto-redirect on 401 errors
  - Password strength indicator

- ✅ **Wallet Manager Component**
  - Real-time balance display
  - Deposit USDC (blockchain-ready)
  - Withdraw USDC with address
  - Transaction history with filters
  - 30-day spending analytics
  - Lifetime earnings/spending totals

- ✅ **Reservation Booking Component**
  - Interactive date/time picker
  - Real-time cost calculation
  - 7-day availability calendar
  - Conflict detection
  - Payment on activation workflow

- ⏳ **Cluster Creation Wizard** (Next)
- ⏳ **GPU Marketplace Updates** (Next)
- ⏳ **Main App Integration** (Next)

## 🔌 API Endpoints

All API calls use the centralized `src/services/api.js` client:

```javascript
import { authAPI, gpuAPI, walletAPI, reservationAPI, clusterAPI } from './services/api';

// Authentication
await authAPI.login(email, password);
await authAPI.signup(email, password);
const user = await authAPI.getCurrentUser();

// GPU Search
const gpus = await gpuAPI.search({ model: 'RTX 4090', max_price: 5.0 });

// Wallet Operations
const balance = await walletAPI.getBalance();
await walletAPI.deposit(1000);
const transactions = await walletAPI.getTransactions();

// Reservations
await reservationAPI.create(gpuId, startTime, endTime);
const bookings = await reservationAPI.getMyBookings();

// Clusters
await clusterAPI.create('AI Training', 5000, 24, 48);
```

## 🎨 Theming

The existing frontend has:
- Dark/Light mode toggle
- Multiple community themes (Professional, Gaming, Creative, Developer, Senior)
- Responsive design (mobile-first)
- Tailwind CSS for styling

## 🧪 Testing

```bash
# Run linter
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🔄 Migration Status

### Original Frontend (App.jsx - 905 lines)
- ❌ Connected to old Flask backend
- ✅ Has working UI components
- ❌ Needs route updates

### New Frontend (Phase 5)
- ✅ Authentication pages built
- ✅ Wallet manager built
- ✅ Reservation booking built
- ✅ API client complete
- ⏳ Integration with existing App.jsx

## 📋 Next Steps

1. **Build Cluster Creation Wizard**
   - Multi-step form for DPP parameters
   - Cost simulation before booking
   - Cluster management dashboard

2. **Update Existing App.jsx**
   - Replace old API calls with new API client
   - Integrate AuthContext
   - Add WalletManager to wallet page
   - Add ReservationBooking to marketplace

3. **Add Routing**
   - Implement React Router
   - Protected routes for authenticated pages
   - Public routes for login/signup

4. **Polish & Testing**
   - Error boundary components
   - Loading states
   - Toast notifications
   - E2E testing

## 🌐 Environment Variables

```env
VITE_API_URL=http://localhost:8000
VITE_DEV_MODE=true
```

## 💡 Development Tips

- Backend must be running before starting frontend
- Check browser console for API errors
- JWT tokens expire after 30 minutes (configurable in backend)
- Use React DevTools for debugging component state

## 🚀 Production Deployment

```bash
# Build optimized production bundle
npm run build

# Output will be in /dist folder
# Deploy to:
# - Vercel (recommended)
# - Netlify
# - AWS S3 + CloudFront
# - Your own server
```

## 📞 Support

For backend API documentation, visit: `http://localhost:8000/api/v1/docs`

---

**Status:** Phase 5 (Frontend Integration) - 60% Complete
**Last Updated:** 2025-11-03
