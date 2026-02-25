import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import EventListItem from '../components/EventListItem';
import SEOHead from '../components/SEOHead';
import { ArrowLeft, Loader2, Users } from 'lucide-react';
import { toast } from 'sonner';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';
import { getTeamUrl, getSeoTitle, getSeoDescription } from '../utils/seoHelpers';
import { getTeamLogo } from '../data/teamLogos';

const TeamPage = ({ urlType }) => {
  const { slug, '*': wildcardSlug } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [teamName, setTeamName] = useState('');
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
      // Search for team name from slug
      const formattedName = actualSlug.split('-').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ');
      
      setTeamName(formattedName);
      
      // Search events with team name
      const response = await eventsAPI.getAll({ search: formattedName });
      setEvents(response.events || []);
    } catch (error) {
      console.error('Error fetching team events:', error);
      toast.error('Failed to load team events');
    } finally {
      setLoading(false);
    }
  };

  const actualSlug = extractSlugFromUrl();
  const teamLogo = getTeamLogo(teamName);
  const seoTitle = getSeoTitle('team', teamName, lang);
  const seoDescription = getSeoDescription('team', teamName, lang);
  const canonicalUrl = `${window.location.origin}${getTeamUrl(actualSlug, lang)}`;

  return (
    <div className="min-h-screen bg-white">
      <SEOHead 
        title={seoTitle}
        description={seoDescription}
        canonicalUrl={canonicalUrl}
        ogImage={teamLogo || "https://images.unsplash.com/photo-1574629810360-7efbbe195018"}
      />
      
      <Header />
      
      {/* Hero Section - Compact */}
      <div className="relative py-8 md:py-12 px-4 bg-[#2D3436]">
        <div className="container mx-auto max-w-4xl">
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
                  alt={`${t('seoTickets')} ${teamName}`}
                  className="w-full h-full object-contain"
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
              <p className="text-gray-400 text-xs md:text-sm mt-1">{t('seoAllMatches')} - {t('seoHomeAway')}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Events List Section */}
      <div className="py-4 px-4">
        <div className="container mx-auto max-w-4xl">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-3" />
              <p className="text-gray-400 text-sm">{t('loadingEvents')}</p>
            </div>
          ) : events.length > 0 ? (
            <div className="bg-gray-800/30 backdrop-blur rounded-xl border border-gray-700/50 overflow-hidden">
              {/* Header */}
              <div className="px-3 py-2 border-b border-gray-700/50">
                <span className="text-xs text-gray-400 font-medium">
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
              <div className="text-gray-300 text-base mb-2">{t('noEventsFound')}</div>
              <p className="text-gray-500 text-sm mb-4">{t('adjustSearch')}</p>
              <Link
                to="/"
                className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300 text-sm font-medium"
              >
                <ArrowLeft className="w-3 h-3" />
                {t('home')}
              </Link>
            </div>
          )}
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default TeamPage;
