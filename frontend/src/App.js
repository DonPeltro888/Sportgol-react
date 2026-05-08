import React, { useEffect, lazy, Suspense } from 'react';
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

// Admin imports — AdminLogin stays sync (first paint critical), rest lazy-loaded (CWV-2)
import { AdminAuthProvider, useAdminAuth } from './contexts/AdminAuthContext';
import { AdminLogin } from './pages/admin';
const AdminDashboard      = lazy(() => import('./pages/admin/AdminDashboard'));
const AdminEvents         = lazy(() => import('./pages/admin/AdminEvents'));
const AdminCategories     = lazy(() => import('./pages/admin/AdminCategories'));
const AdminPages          = lazy(() => import('./pages/admin/AdminPages'));
const AdminTranslations   = lazy(() => import('./pages/admin/AdminTranslations'));
const AdminSettings       = lazy(() => import('./pages/admin/AdminSettings'));
const AdminSectors        = lazy(() => import('./pages/admin/AdminSectors'));
const AdminLeaguesTeams   = lazy(() => import('./pages/admin/AdminLeaguesTeams'));
const AdminSync           = lazy(() => import('./pages/admin/AdminSync'));
const AdminTeams          = lazy(() => import('./pages/admin/AdminTeams'));
const AdminIntegrations   = lazy(() => import('./pages/admin/AdminIntegrations'));
const AdminProviders      = lazy(() => import('./pages/admin/AdminProviders'));
const SeoDashboard        = lazy(() => import('./pages/admin/seo/SeoDashboard'));
const SeoApiTools         = lazy(() => import('./pages/admin/seo/SeoApiTools'));
const SeoPagesList        = lazy(() => import('./pages/admin/seo/SeoPagesList'));
const SeoTargetEditor     = lazy(() => import('./pages/admin/seo/SeoTargetEditor'));
const SeoBulkRunner       = lazy(() => import('./pages/admin/seo/SeoBulkRunner'));
const CostObservatory     = lazy(() => import('./pages/admin/seo/CostObservatory'));
const SeoIntelligenceHub  = lazy(() => import('./pages/admin/seo/intelligence/SeoIntelligenceHub'));
const SeoIntTopicCluster  = lazy(() => import('./pages/admin/seo/intelligence/TopicCluster'));
const SeoIntCannibalization = lazy(() => import('./pages/admin/seo/intelligence/Cannibalization'));
const SeoIntHreflang      = lazy(() => import('./pages/admin/seo/intelligence/Hreflang'));
const SeoIntFaqGenerator  = lazy(() => import('./pages/admin/seo/intelligence/FaqGenerator'));
const SeoIntJsonLdValidator = lazy(() => import('./pages/admin/seo/intelligence/JsonLdValidator'));
const GoogleSuite         = lazy(() => import('./pages/admin/seo/GoogleSuite'));
const CwvAutomation       = lazy(() => import('./pages/admin/seo/CwvAutomation'));
const DataToolsDashboard  = lazy(() => import('./pages/admin/data-tools/DataToolsDashboard'));
const DataHealthDashboard = lazy(() => import('./pages/admin/data-tools/DataHealthDashboard'));
const SyncQualityDashboard = lazy(() => import('./pages/admin/data-tools/SyncQualityDashboard'));
const DataRecoveryDashboard = lazy(() => import('./pages/admin/data-tools/DataRecoveryDashboard'));
const DataToolsTeamVerifier = lazy(() => import('./pages/admin/data-tools/TeamVerifier'));
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
  
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    }>
      {children}
    </Suspense>
  );
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
            <Route path="/admin/seo/cost-observatory" element={
              <ProtectedRoute><CostObservatory /></ProtectedRoute>
            } />
            <Route path="/admin/seo/intelligence" element={
              <ProtectedRoute><SeoIntelligenceHub /></ProtectedRoute>
            } />
            <Route path="/admin/seo/intelligence/topic-cluster" element={
              <ProtectedRoute><SeoIntTopicCluster /></ProtectedRoute>
            } />
            <Route path="/admin/seo/intelligence/cannibalization" element={
              <ProtectedRoute><SeoIntCannibalization /></ProtectedRoute>
            } />
            <Route path="/admin/seo/intelligence/hreflang" element={
              <ProtectedRoute><SeoIntHreflang /></ProtectedRoute>
            } />
            <Route path="/admin/seo/intelligence/faq" element={
              <ProtectedRoute><SeoIntFaqGenerator /></ProtectedRoute>
            } />
            <Route path="/admin/seo/intelligence/jsonld-validator" element={
              <ProtectedRoute><SeoIntJsonLdValidator /></ProtectedRoute>
            } />
            <Route path="/admin/seo/google-suite" element={
              <ProtectedRoute><GoogleSuite /></ProtectedRoute>
            } />
            <Route path="/admin/seo/automation-center" element={
              <ProtectedRoute><CwvAutomation /></ProtectedRoute>
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
            <Route path="/admin/data-tools/team-verifier" element={
              <ProtectedRoute><DataToolsTeamVerifier /></ProtectedRoute>
            } />
            {/* Legacy redirect path (1 release) */}
            <Route path="/admin/seo/intelligence/team-verifier" element={
              <ProtectedRoute><DataToolsTeamVerifier /></ProtectedRoute>
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
