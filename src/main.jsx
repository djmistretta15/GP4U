import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { Web3Provider } from './context/Web3Context';
import { ThemeProvider } from './context/ThemeContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Signup from './pages/Signup';
import AppWrapper from './AppWrapper';
import GPUs from './pages/GPUs';
import GPUDetail from './pages/GPUDetail';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <Web3Provider>
            <ThemeProvider>
              <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route path="/auth/login" element={<Login />} />

                {/* MVP GPU Routes */}
                <Route
                  path="/dashboard/gpus"
                  element={
                    <ProtectedRoute>
                      <GPUs />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/dashboard/gpus/:id"
                  element={
                    <ProtectedRoute>
                      <GPUDetail />
                    </ProtectedRoute>
                  }
                />
                <Route path="/dashboard" element={<Navigate to="/dashboard/gpus" replace />} />

                {/* Protected Routes */}
                <Route
                  path="/*"
                  element={
                    <ProtectedRoute>
                      <AppWrapper />
                    </ProtectedRoute>
                  }
                />

                {/* Redirect root to dashboard */}
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </ThemeProvider>
          </Web3Provider>
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
);
