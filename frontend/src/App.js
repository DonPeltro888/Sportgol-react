import React, { useEffect } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route, Navigate, useParams, useLocation } from 'react-router-dom';
import Home from './pages/Home';
import EventDetail from './pages/EventDetail';
import TeamPage from './pages/TeamPage';
import LeaguePage from './pages/LeaguePage';
import DemoScraping from './pages/DemoScraping';
import { Toaster } from './components/ui/sonner';

// Language Context
import { LanguageProvider } from './contexts/LanguageContext';

// ScrollToTop component - scrolls to top on route change
const ScrollToTop = () => {
  const { pathname } = useLocation();
  
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  
  return null;
};

// Known league slugs for routing
const LEAGUE_SLUGS = [
  'serie-a', 'premier-league', 'la-liga', 'bundesliga', 'ligue-1',
  'champions-league', 'europa-league', 'coppa-italia', 'fa-cup', 'copa-del-rey'
];

// Dynamic Router component to handle translated URLs
// REGOLE URL (MEMORIZZATO):
// - IT: /biglietti-{name} (biglietti PRIMA con trattino)
// - EN: /{name}-tickets (tickets DOPO con trattino)  
// - ES: /entradas-{name} (entradas PRIMA con trattino)
const DynamicRouter = () => {
  const { dynamicPath } = useParams();
  
  if (!dynamicPath) return <Home />;
  
  // Check if it's a league or team URL
  let slug = '';
  let isLeague = false;
  
  // IT: /biglietti-inter or /biglietti-serie-a
  if (dynamicPath.startsWith('biglietti-')) {
    slug = dynamicPath.replace('biglietti-', '');
  }
  // ES: /entradas-inter or /entradas-serie-a
  else if (dynamicPath.startsWith('entradas-')) {
    slug = dynamicPath.replace('entradas-', '');
  }
  // EN: /inter-tickets or /serie-a-tickets
  else if (dynamicPath.endsWith('-tickets')) {
    slug = dynamicPath.replace(/-tickets$/, '');
  }
  else {
    // Not a translated URL, let fallback handle it
    return <Home />;
  }
  
  // Determine if it's a league or team based on known slugs
  isLeague = LEAGUE_SLUGS.includes(slug);
  
  if (isLeague) {
    return <LeaguePage />;
  } else {
    return <TeamPage />;
  }
};

// Admin imports
import { AdminAuthProvider, useAdminAuth } from './contexts/AdminAuthContext';
import {
  AdminLogin,
  AdminDashboard,
  AdminEvents,
  AdminCategories,
  AdminPages,
  AdminTranslations,
  AdminSettings,
  AdminSectors
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
  return (
    <Router>
      <ScrollToTop />
      <LanguageProvider>
        <AdminAuthProvider>
          <div className="App min-h-screen bg-black">
            <Toaster position="top-right" richColors />
            <Routes>
            {/* Public Routes */}
            <Route path="/" element={<Home />} />
            <Route path="/event/:id" element={<EventDetail />} />
            
            {/* Demo Scraping Page - URL separato */}
            <Route path="/demo-scraping" element={<DemoScraping />} />
            
            {/* 
              URL STRUCTURE (MEMORIZZATO):
              - IT: /biglietti-{name} (biglietti PRIMA con trattino)
              - EN: /{name}-tickets (tickets DOPO con trattino)  
              - ES: /entradas-{name} (entradas PRIMA con trattino)
              
              React Router non supporta pattern con trattino come /:slug-tickets
              Usiamo catch-all routes e estraiamo lo slug nel componente
            */}
            
            {/* Catch-all route for team/league pages with translated URLs */}
            <Route path="/:dynamicPath" element={<DynamicRouter />} />
            
            {/* Fallback routes */}
            <Route path="/team/:slug" element={<TeamPage />} />
            <Route path="/league/:league" element={<LeaguePage />} />
            
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
            <Route path="/admin/sectors" element={
              <ProtectedRoute><AdminSectors /></ProtectedRoute>
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
