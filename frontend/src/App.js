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

// Known league slugs for routing - ESTESO con tutti gli slug disponibili
// (auto-aggiornato dal sync matchesio.com - vedi ensure_league_in_db)
const LEAGUE_SLUGS = [
  // Top leagues
  'serie-a', 'premier-league', 'la-liga', 'bundesliga', 'ligue-1',
  'liga-portugal', 'super-lig',
  // Other European leagues
  'eredivisie', 'jupiler-pro-league', 'championship', '2-bundesliga', 'ligue-2',
  // Extra-Europe
  'mls', 'liga-mx', 'j1-league',
  // National cups
  'coppa-italia', 'copa-del-rey', 'fa-cup', 'dfb-pokal', 'coupe-de-france', 'knvb-beker',
  // European cups
  'champions-league', 'europa-league', 'conference-league', 'uefa-nations-league',
  // International
  'fifa-world-cup-2026', 'fifa-club-world-cup', 'euro-championship',
  'copa-america', 'africa-cup-of-nations', 'asian-cup',
  'copa-libertadores', 'afc-champions-league'
];

// Dynamic Router component to handle translated URLs
// REGOLE URL (MEMORIZZATO):
// - IT: /biglietti-{name} (biglietti PRIMA con trattino)
// - EN: /{name}-tickets (tickets DOPO con trattino)  
// - ES: /entradas-{name} (entradas PRIMA con trattino)
// Tipo di pagina determinato dal pattern dello slug:
// - Evento: slug contiene "-vs-" (es. inter-vs-parma)
// - Lega:   slug è in LEAGUE_SLUGS (es. serie-a, champions-league)
// - Squadra: tutto il resto (es. inter, real-madrid)
const DynamicRouter = () => {
  const { dynamicPath } = useParams();
  
  if (!dynamicPath) return <Home />;
  
  // Check if it's a league or team URL
  let slug = '';
  
  // IT: /biglietti-inter or /biglietti-serie-a or /biglietti-inter-vs-parma
  if (dynamicPath.startsWith('biglietti-')) {
    slug = dynamicPath.replace('biglietti-', '');
  }
  // ES: /entradas-inter or /entradas-serie-a or /entradas-inter-vs-parma
  else if (dynamicPath.startsWith('entradas-')) {
    slug = dynamicPath.replace('entradas-', '');
  }
  // EN: /inter-tickets or /serie-a-tickets or /inter-vs-parma-tickets
  else if (dynamicPath.endsWith('-tickets')) {
    slug = dynamicPath.replace(/-tickets$/, '');
  }
  else {
    // Not a translated URL → 404
    return <NotFound />;
  }
  
  // Event: slug contains "-vs-" (match home-vs-away)
  if (slug.includes('-vs-')) {
    return <EventDetail />;
  }
  
  // League: slug is in known league slugs
  if (LEAGUE_SLUGS.includes(slug)) {
    return <LeaguePage />;
  }
  
  // Team: default
  return <TeamPage />;
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
  AdminSectors,
  AdminLeaguesTeams,
  AdminSync,
  AdminTeams,
  AdminIntegrations,
  AdminProviders
} from './pages/admin';
import SeoDashboard from './pages/admin/seo/SeoDashboard';
import SeoApiTools from './pages/admin/seo/SeoApiTools';
import SeoPagesList from './pages/admin/seo/SeoPagesList';
import SeoTargetEditor from './pages/admin/seo/SeoTargetEditor';
import SeoBulkRunner from './pages/admin/seo/SeoBulkRunner';
import DataToolsDashboard from './pages/admin/data-tools/DataToolsDashboard';
import DataHealthDashboard from './pages/admin/data-tools/DataHealthDashboard';
import SyncQualityDashboard from './pages/admin/data-tools/SyncQualityDashboard';
import DataRecoveryDashboard from './pages/admin/data-tools/DataRecoveryDashboard';
import NotFound from './pages/NotFound';
import WhatsAppButton from './components/WhatsAppButton';

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
              <ProtectedRoute><SeoDashboard /></ProtectedRoute>
            } />
            <Route path="/admin/seo/api-tools" element={
              <ProtectedRoute><SeoApiTools /></ProtectedRoute>
            } />
            <Route path="/admin/seo/pages" element={
              <ProtectedRoute><SeoPagesList /></ProtectedRoute>
            } />
            <Route path="/admin/seo/pages/new" element={
              <ProtectedRoute><SeoPagesList /></ProtectedRoute>
            } />
            <Route path="/admin/seo/targets/:type/:id" element={
              <ProtectedRoute><SeoTargetEditor /></ProtectedRoute>
            } />
            <Route path="/admin/seo/bulk" element={
              <ProtectedRoute><SeoBulkRunner /></ProtectedRoute>
            } />
            <Route path="/admin/data-tools" element={
              <ProtectedRoute><DataToolsDashboard /></ProtectedRoute>
            } />
            <Route path="/admin/data-tools/health" element={
              <ProtectedRoute><DataHealthDashboard /></ProtectedRoute>
            } />
            <Route path="/admin/data-tools/sync-quality" element={
              <ProtectedRoute><SyncQualityDashboard /></ProtectedRoute>
            } />
            <Route path="/admin/data-tools/data-recovery" element={
              <ProtectedRoute><DataRecoveryDashboard /></ProtectedRoute>
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
            <Route path="/admin/leagues-teams" element={
              <ProtectedRoute><AdminLeaguesTeams /></ProtectedRoute>
            } />
            <Route path="/admin/sync" element={
              <ProtectedRoute><AdminSync /></ProtectedRoute>
            } />
            <Route path="/admin/teams-logos" element={
              <ProtectedRoute><AdminTeams /></ProtectedRoute>
            } />
            <Route path="/admin/integrations" element={
              <ProtectedRoute><AdminIntegrations /></ProtectedRoute>
            } />
            <Route path="/admin/providers" element={
              <ProtectedRoute><AdminProviders /></ProtectedRoute>
            } />
            
            {/* Redirect /admin to dashboard */}
            <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />

            {/* 404 - Catch all */}
            <Route path="*" element={<NotFound />} />
          </Routes>
          <ConditionalWhatsApp />
        </div>
      </AdminAuthProvider>
    </LanguageProvider>
    </Router>
  );
}

// Show WhatsApp button only on public pages (NOT in admin area)
const ConditionalWhatsApp = () => {
  const { pathname } = useLocation();
  if (pathname.startsWith('/admin')) return null;
  return <WhatsAppButton />;
};

export default App;
