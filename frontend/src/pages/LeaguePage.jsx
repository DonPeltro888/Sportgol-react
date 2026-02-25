import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import EventListItem from '../components/EventListItem';
import SEOHead from '../components/SEOHead';
import Breadcrumbs from '../components/Breadcrumbs';
import { LeagueSchema, BreadcrumbSchema } from '../components/SchemaOrg';
import { ArrowLeft, Loader2, Trophy } from 'lucide-react';
import { toast } from 'sonner';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';
import { getLeagueUrl, getTeamUrl, getSeoTitle, getSeoDescription } from '../utils/seoHelpers';
import { getTeamLogo, getLeagueLogo } from '../data/teamLogos';

const LeaguePage = ({ urlType }) => {
  const { league, '*': wildcardLeague } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [leagueName, setLeagueName] = useState('');
  const [isCup, setIsCup] = useState(false);
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);

  // Extract league from URL based on pattern
  // REGOLE URL (MEMORIZZATO):
  // - IT: /biglietti-serie-a -> estrai "serie-a"
  // - EN: /serie-a-tickets -> estrai "serie-a"
  // - ES: /entradas-serie-a -> estrai "serie-a"
  const extractLeagueFromUrl = () => {
    const path = location.pathname;
    
    // IT: /biglietti-serie-a -> remove "biglietti-" prefix
    if (path.startsWith('/biglietti-')) {
      return path.replace('/biglietti-', '');
    }
    // ES: /entradas-serie-a -> remove "entradas-" prefix
    if (path.startsWith('/entradas-')) {
      return path.replace('/entradas-', '');
    }
    // EN: /serie-a-tickets -> remove "-tickets" suffix
    if (path.endsWith('-tickets')) {
      return path.slice(1).replace(/-tickets$/, '');
    }
    // Fallback: /league/serie-a
    return league || wildcardLeague || '';
  };

  const actualLeague = extractLeagueFromUrl();

  const leagueTeams = {
    'serie-a': {
      name: 'Serie A',
      country: 'Italy',
      isCup: false,
      teams: [
        'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina',
        'Genoa', 'Hellas Verona', 'Inter', 'Juventus', 'Lazio', 'Lecce',
        'Milan', 'Napoli', 'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese'
      ]
    },
    'premier-league': {
      name: 'Premier League',
      country: 'England',
      isCup: false,
      teams: [
        'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Burnley',
        'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Leeds United', 'Liverpool',
        'Manchester City', 'Manchester United', 'Newcastle United', 'Nottingham Forest',
        'Sunderland', 'Tottenham', 'West Ham', 'Wolves'
      ]
    },
    'la-liga': {
      name: 'La Liga',
      country: 'Spain',
      isCup: false,
      teams: [
        'Alavés', 'Athletic Bilbao', 'Atlético Madrid', 'Barcelona', 'Betis', 'Celta Vigo',
        'Elche', 'Espanyol', 'Getafe', 'Girona', 'Levante', 'Mallorca',
        'Osasuna', 'Oviedo', 'Rayo Vallecano', 'Real Madrid', 'Real Sociedad', 'Sevilla',
        'Valencia', 'Villarreal'
      ]
    },
    'bundesliga': {
      name: 'Bundesliga',
      country: 'Germany',
      isCup: false,
      teams: [
        'Augsburg', 'Bayern Munich', 'Borussia Dortmund', 'Borussia Mönchengladbach',
        'Eintracht Frankfurt', 'FC Köln', 'Freiburg', 'Hamburger SV', 'Heidenheim',
        'Hoffenheim', 'Leverkusen', 'Mainz', 'RB Leipzig', 'St. Pauli',
        'Stuttgart', 'Union Berlin', 'Werder Bremen', 'Wolfsburg'
      ]
    },
    'liga-portugal': {
      name: 'Liga Portugal',
      country: 'Portugal',
      isCup: false,
      teams: [
        'Arouca', 'AVS', 'Benfica', 'Boavista', 'Braga', 'Casa Pia',
        'Estoril', 'Farense', 'Famalicão', 'Gil Vicente', 'Moreirense', 'Nacional',
        'Porto', 'Rio Ave', 'Santa Clara', 'Sporting CP', 'Estrela', 'Vitória Guimarães'
      ]
    },
    'champions-league': {
      name: 'Champions League',
      country: 'Europe',
      isCup: true
    },
    'coppa-italia': {
      name: 'Coppa Italia',
      country: 'Italy',
      isCup: true
    },
    'copa-del-rey': {
      name: 'Copa del Rey',
      country: 'Spain',
      isCup: true
    },
    'fa-cup': {
      name: 'FA Cup',
      country: 'England',
      isCup: true
    },
    'dfb-pokal': {
      name: 'DFB Pokal',
      country: 'Germany',
      isCup: true
    }
  };

  useEffect(() => {
    const leagueData = leagueTeams[actualLeague];
    if (leagueData) {
      setLeagueName(leagueData.name);
      setIsCup(leagueData.isCup);
      if (leagueData.isCup) {
        fetchCupEvents();
      }
    }
    setLoading(false);
  }, [league, location.pathname]);

  const fetchCupEvents = async () => {
    try {
      setLoading(true);
      const leagueData = leagueTeams[actualLeague];
      const data = await eventsAPI.getAll({ league: leagueData.name.toUpperCase() });
      setEvents(data.events || []);
    } catch (error) {
      console.error('Error fetching cup events:', error);
      toast.error('Failed to load cup events');
    } finally {
      setLoading(false);
    }
  };

  const getTeamSlug = (teamName) => {
    return teamName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  };

  const leagueData = leagueTeams[actualLeague];
  const seoTitle = getSeoTitle('league', leagueName, lang);
  const seoDescription = getSeoDescription('league', leagueName, lang, { 
    teamCount: leagueData?.teams?.length 
  });
  const canonicalUrl = `${window.location.origin}${getLeagueUrl(actualLeague, lang)}`;

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Loader2 className="w-16 h-16 text-blue-500 animate-spin" />
      </div>
    );
  }

  if (!leagueTeams[actualLeague]) {
    return (
      <div className="min-h-screen bg-black">
        <Header />
        <div className="flex flex-col items-center justify-center py-20">
          <p className="text-gray-400 text-xl mb-4">{t('noEventsFound')}</p>
          <button
            onClick={() => navigate('/')}
            className="text-blue-400 hover:text-blue-300"
          >
            {t('home')}
          </button>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <SEOHead 
        title={seoTitle}
        description={seoDescription}
        canonicalUrl={canonicalUrl}
        ogImage="https://images.unsplash.com/photo-1574629810360-7efbbe195018"
      />
      <LeagueSchema leagueName={leagueName} teams={leagueData?.teams} lang={lang} />
      <BreadcrumbSchema items={[
        { name: 'Home', url: '/' },
        { name: leagueName, url: null }
      ]} />
      
      <Header />
      
      {/* Hero Section - Compatto */}
      <div className="relative py-6 md:py-8 px-4 bg-[#2D3436]">
        <div className="container mx-auto">
          {/* Breadcrumbs */}
          <Breadcrumbs items={[
            { name: leagueName, url: null }
          ]} />
          
          <div className="flex items-center gap-3 mt-3">
            {/* League/Cup Logo */}
            <div className="w-12 h-12 md:w-14 md:h-14 flex items-center justify-center bg-white rounded-lg p-1 relative flex-shrink-0">
              {getLeagueLogo(actualLeague) && (
                <img 
                  src={getLeagueLogo(actualLeague)} 
                  alt={leagueName}
                  className="w-full h-full object-contain absolute inset-0 p-1"
                  onLoad={(e) => {
                    const fallback = e.target.parentElement.querySelector('.league-fallback');
                    if (fallback) fallback.style.display = 'none';
                  }}
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              )}
              <div className="league-fallback w-12 h-12 md:w-14 md:h-14 bg-gradient-to-br from-[#FF6B35] to-[#0984E3] rounded-full flex items-center justify-center">
                <Trophy className="w-6 h-6 text-white" />
              </div>
            </div>
            <div>
              <h1 className="text-lg md:text-xl lg:text-2xl font-black text-white leading-tight">
                {lang === 'en' ? `${leagueName} ${t('seoTickets')}` : `${t('seoTickets')} ${leagueName}`}
              </h1>
              <p className="text-gray-400 text-xs md:text-sm mt-0.5">
                {leagueTeams[actualLeague]?.country} 
                {!isCup && ` • ${leagueTeams[actualLeague]?.teams?.length} Teams`}
                {isCup && ' • Cup Competition'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="py-8 px-4 bg-gray-50">
        <div className="container mx-auto max-w-4xl">
          {isCup ? (
            // Cup Events View - Same style as TeamPage
            <>
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
                  <div className="text-4xl mb-3">🏆</div>
                  <div className="text-[#2D3436] text-base mb-2">{t('noEventsFound')}</div>
                  <p className="text-gray-500 text-sm">{t('adjustSearch')}</p>
                </div>
              )}
            </>
          ) : (
            // Teams Grid View
            <>
              <h2 className="text-xl md:text-2xl font-bold text-[#2D3436] mb-6">{t('teamsTitle')}</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                {leagueTeams[actualLeague]?.teams?.map((team, index) => {
                  const teamLogo = getTeamLogo(team);
                  return (
                    <Link
                      key={index}
                      to={getTeamUrl(getTeamSlug(team), lang)}
                      className="group bg-white border border-gray-200 hover:border-[#0984E3] rounded-xl p-6 text-center transition-all duration-300 transform hover:-translate-y-2 hover:shadow-lg"
                    >
                      {/* Team Logo or Fallback Initial */}
                      <div className="w-16 h-16 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform relative">
                        {teamLogo && (
                          <img 
                            src={teamLogo} 
                            alt={`${t('seoTickets')} ${team}`}
                            className="w-full h-full object-contain absolute inset-0"
                            onLoad={(e) => {
                              // Hide fallback when image loads
                              const fallback = e.target.parentElement.querySelector('.team-fallback');
                              if (fallback) fallback.style.display = 'none';
                            }}
                            onError={(e) => {
                              // Hide broken image
                              e.target.style.display = 'none';
                            }}
                          />
                        )}
                        <div className={`team-fallback w-16 h-16 bg-gradient-to-br from-[#FF6B35] to-[#0984E3] rounded-full flex items-center justify-center`}>
                          <span className="text-2xl font-bold text-white">
                            {team.charAt(0)}
                          </span>
                        </div>
                      </div>
                      <h3 className="font-bold text-[#2D3436] text-sm group-hover:text-[#0984E3] transition-colors">
                        {lang === 'en' ? `${team} ${t('seoTickets')}` : `${t('seoTickets')} ${team}`}
                      </h3>
                    </Link>
                  );
                })}
              </div>
            </>
          )}
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default LeaguePage;