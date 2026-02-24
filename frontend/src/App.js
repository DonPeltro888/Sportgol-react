import React, { useEffect } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import EventDetail from './pages/EventDetail';
import TeamPage from './pages/TeamPage';
import LeaguePage from './pages/LeaguePage';
import { Toaster } from './components/ui/sonner';

// Language Context
import { LanguageProvider } from './contexts/LanguageContext';

// Admin imports
import { AdminAuthProvider, useAdminAuth } from './contexts/AdminAuthContext';
import {
  AdminLogin,
  AdminDashboard,
  AdminEvents,
  AdminCategories,
  AdminPages,
  AdminTranslations,
  AdminSettings
} from './pages/admin';

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { token, loading } = useAdminAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }
  
  if (!token) {
    return <Navigate to="/admin/login" replace />;
  }
  
  return children;
};

function App() {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <Router>
      <LanguageProvider>
        <AdminAuthProvider>
          <div className="App min-h-screen bg-black">
            <Toaster position="top-right" richColors />
            <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Home />} />
            <Route path="/event/:id" element={<EventDetail />} />
            
            {/* Team Routes - IT: /biglietti/inter, EN: /inter/tickets, ES: /entradas/inter */}
            <Route path="/biglietti/:slug" element={<TeamPage />} />
            <Route path="/:slug/tickets" element={<TeamPage />} />
            <Route path="/entradas/:slug" element={<TeamPage />} />
            <Route path="/team/:slug" element={<TeamPage />} /> {/* Fallback */}
            
            {/* League Routes - IT: /biglietti-campionato/serie-a, EN: /league/serie-a/tickets, ES: /entradas-liga/serie-a */}
            <Route path="/biglietti-campionato/:league" element={<LeaguePage />} />
            <Route path="/league/:league/tickets" element={<LeaguePage />} />
            <Route path="/entradas-liga/:league" element={<LeaguePage />} />
            <Route path="/league/:league" element={<LeaguePage />} /> {/* Fallback */}
            
            {/* Admin Routes */}
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin/dashboard" element={
              <ProtectedRoute><AdminDashboard /></ProtectedRoute>
            } />
            <Route path="/admin/events" element={
              <ProtectedRoute><AdminEvents /></ProtectedRoute>
            } />
            <Route path="/admin/categories" element={
              <ProtectedRoute><AdminCategories /></ProtectedRoute>
            } />
            <Route path="/admin/pages" element={
              <ProtectedRoute><AdminPages /></ProtectedRoute>
            } />
            <Route path="/admin/seo" element={
              <ProtectedRoute><AdminPages /></ProtectedRoute>
            } />
            <Route path="/admin/translations" element={
              <ProtectedRoute><AdminTranslations /></ProtectedRoute>
            } />
            <Route path="/admin/settings" element={
              <ProtectedRoute><AdminSettings /></ProtectedRoute>
            } />
            
            {/* Redirect /admin to dashboard */}
            <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
          </Routes>
        </div>
      </AdminAuthProvider>
    </LanguageProvider>
    </Router>
  );
}

export default App;
