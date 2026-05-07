import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import EventListItem from '../components/EventListItem';
import SEOHead from '../components/SEOHead';
import Breadcrumbs from '../components/Breadcrumbs';
import { TeamSchema, BreadcrumbSchema } from '../components/SchemaOrg';
import SeoContentBlock, { getSeoMetaTitle, getSeoMetaDescription, getSeoH1 } from '../components/SeoContentBlock';
import SeoSchemaInjector from '../components/SeoSchemaInjector';
import { ArrowLeft, Loader2, Users } from 'lucide-react';
import { toast } from 'sonner';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';
import { getTeamUrl, getSeoTitle, getSeoDescription } from '../utils/seoHelpers';
import { getTeamLogo } from '../data/teamLogos';
import { resolveSeoHeroUrl } from '../utils/seoHero';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TeamPage = ({ urlType }) => {
  const { slug, '*': wildcardSlug } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [teamName, setTeamName] = useState('');
  const [teamData, setTeamData] = useState(null);
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);

  // Extract slug from URL based on pattern
  // REGOLE URL (MEMORIZZATO):
  // - IT: /biglietti-inter -> estrai "inter"
  // - EN: /inter-tickets -> estrai "inter"
  // - ES: /entradas-inter -> estrai "inter"
  const extractSlugFromUrl = () => {
    const path = location.pathname;
    
    // IT: /biglietti-inter -> remove "biglietti-" prefix
    if (path.startsWith('/biglietti-')) {
      return path.replace('/biglietti-', '');
    }
    // ES: /entradas-inter -> remove "entradas-" prefix
    if (path.startsWith('/entradas-')) {
      return path.replace('/entradas-', '');
    }
    // EN: /inter-tickets -> remove "-tickets" suffix
    if (path.endsWith('-tickets')) {
      return path.slice(1).replace(/-tickets$/, '');
    }
    // Fallback: /team/inter
    return slug || wildcardSlug || '';
  };

  useEffect(() => {
    fetchTeamEvents();
  }, [slug, wildcardSlug, location.pathname]);

  const fetchTeamEvents = async () => {
    try {
      setLoading(true);
      const actualSlug = extractSlugFromUrl();
      if (!actualSlug) {
        setLoading(false);
        return;
      }
      // Fetch team data (con SEO fields)
      try {
        const teamRes = await fetch(`${API_URL}/api/teams/${actualSlug}`);
        if (teamRes.ok) {
          const td = await teamRes.json();
          setTeamData(td);
          setTeamName(td.name || actualSlug);
        }
      } catch (e) { /* ignore */ }

      // Fallback name dal slug
      const formattedName = actualSlug.split('-').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');
      setTeamName(prev => prev || formattedName);

      // EXACT match per evitare confusione (es. Inter ≠ Inter Miami)
      try {
        const r = await fetch(`${API_URL}/api/events/by-team-slug/${actualSlug}?limit=50`);
        if (r.ok) {
          const d = await r.json();
          setEvents(d.events || []);
        } else {
          // Fallback: search per nome (legacy)
          const response = await eventsAPI.getAll({ search: formattedName });
          setEvents(response.events || []);
        }
      } catch (e) {
        const response = await eventsAPI.getAll({ search: formattedName });
        setEvents(response.events || []);
      }
    } catch (error) {
      console.error('Error fetching team events:', error);
      toast.error('Failed to load team events');
    } finally {
      setLoading(false);
    }
  };

  const actualSlug = extractSlugFromUrl();
  const teamLogo = teamData?.logo_url || getTeamLogo(teamName);
  const fallbackTitle = getSeoTitle('team', teamName, lang);
  const fallbackDesc = getSeoDescription('team', teamName, lang);
  const seoTitle = getSeoMetaTitle(teamData, lang, fallbackTitle);
  const seoDescription = getSeoMetaDescription(teamData, lang, fallbackDesc);
  const customH1 = getSeoH1(teamData, lang, '');
  const canonicalUrl = `${window.location.origin}${getTeamUrl(actualSlug, lang)}`;
  const heroImageUrl = resolveSeoHeroUrl(teamData?.seo_hero_image_url);

  return (
    <div className="min-h-screen bg-white">
      <SEOHead 
        title={seoTitle}
        description={seoDescription}
        canonicalUrl={canonicalUrl}
        ogImage={heroImageUrl || teamLogo || "https://images.unsplash.com/photo-1574629810360-7efbbe195018"}
      />
      <TeamSchema teamName={teamName} lang={lang} />
      <BreadcrumbSchema items={[
        { name: 'Home', url: '/' },
        { name: teamName, url: null }
      ]} />
      
      <Header />
      
      {/* Hero Section - Compact */}
      <div
        className="relative py-8 md:py-12 px-4 bg-[#2D3436] overflow-hidden"
        style={heroImageUrl ? { backgroundImage: `url(${heroImageUrl})`, backgroundSize: 'cover', backgroundPosition: 'center' } : {}}
        data-testid="team-hero-section"
      >
        {heroImageUrl && (
          <div className="absolute inset-0 bg-gradient-to-r from-black/80 via-black/60 to-black/40 pointer-events-none" data-testid="team-hero-overlay" />
        )}
        <div className="container mx-auto max-w-4xl relative z-10">
          <button
            onClick={() => navigate('/')}
            className="text-gray-300 hover:text-white flex items-center gap-1 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-xs">{t('home')}</span>
          </button>
          
          <div className="flex items-center gap-3">
            {teamLogo ? (
              <div className="w-12 h-12 md:w-14 md:h-14 flex items-center justify-center bg-white rounded-lg p-1">
                <img 
                  src={teamLogo} 
                  alt={`Logo ${teamName} - Biglietti calcio ufficiali`}
                  loading="eager"
                  decoding="async"
                  referrerPolicy="no-referrer"
                  className="w-full h-full object-contain"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.style.display = 'none';
                    if (e.target.parentElement) {
                      e.target.parentElement.innerHTML = `<div class="w-full h-full bg-gradient-to-br from-[#FF6B35] to-[#0984E3] rounded flex items-center justify-center text-white font-bold text-lg">${(teamName || '?').slice(0,2).toUpperCase()}</div>`;
                    }
                  }}
                />
              </div>
            ) : (
              <div className="w-12 h-12 md:w-14 md:h-14 bg-gradient-to-br from-[#FF6B35] to-[#0984E3] rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 md:w-7 md:h-7 text-white" />
              </div>
            )}
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white leading-tight">
                {lang === 'en' ? `${teamName} ${t('seoTickets')}` : `${t('seoTickets')} ${teamName}`}
              </h1>
              <p className="text-gray-300 text-xs md:text-sm mt-1">{t('seoAllMatches')} - {t('seoHomeAway')}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Events List Section */}
      <div className="py-6 px-4 bg-gray-50">
        <div className="container mx-auto max-w-4xl">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-[#0984E3] animate-spin mb-3" />
              <p className="text-gray-500 text-sm">{t('loadingEvents')}</p>
            </div>
          ) : events.length > 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
              {/* Header */}
              <div className="px-3 py-2 border-b border-gray-200 bg-gray-50">
                <span className="text-xs text-gray-500 font-medium">
                  {events.length} {events.length > 1 ? t('eventsFound') : t('eventFound')}
                </span>
              </div>
              
              {/* Events List */}
              <div>
                {events.map((event) => (
                  <EventListItem key={event.id || event._id} event={event} />
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-4xl mb-3">⚽</div>
              <div className="text-[#2D3436] text-base mb-2">{t('noEventsFound')}</div>
              <p className="text-gray-500 text-sm mb-4">{t('adjustSearch')}</p>
              <Link
                to="/"
                className="inline-flex items-center gap-1 text-[#0984E3] hover:text-[#FF6B35] text-sm font-medium"
              >
                <ArrowLeft className="w-3 h-3" />
                {t('home')}
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* SEO Content (intro/CTA/etc. dal SEO Admin) */}
      <SeoContentBlock data={teamData} lang={lang} />
      <SeoSchemaInjector schema={teamData?.seo_meta_schema_jsonld} />

      <Footer />
    </div>
  );
};

export default TeamPage;
