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

const API_URL = process.env.REACT_APP_BACKEND_URL;

const LeaguePage = ({ urlType }) => {
  const { league, '*': wildcardLeague } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [leagueData, setLeagueData] = useState(null);
  const [teams, setTeams] = useState([]);
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);

  // Extract league from URL based on pattern
  const extractLeagueFromUrl = () => {
    const path = location.pathname;
    
    if (path.startsWith('/biglietti-')) {
      return path.replace('/biglietti-', '');
    }
    if (path.startsWith('/entradas-')) {
      return path.replace('/entradas-', '');
    }
    if (path.endsWith('-tickets')) {
      return path.slice(1).replace(/-tickets$/, '');
    }
    return league || wildcardLeague || '';
  };

  const actualLeague = extractLeagueFromUrl();

  useEffect(() => {
    fetchLeagueData();
  }, [actualLeague, location.pathname]);

  const fetchLeagueData = async () => {
    try {
      setLoading(true);
      
      // Fetch league info from DB
      const response = await fetch(`${API_URL}/api/leagues/${actualLeague}`);
      
      if (response.ok) {
        const data = await response.json();
        setLeagueData(data);
        setTeams(data.teams || []);
        
        // If it's a cup, fetch events
        if (data.type === 'cup') {
          fetchCupEvents(data.name);
        }
      } else {
        // Fallback to hardcoded data if API fails
        const fallbackData = getFallbackLeagueData(actualLeague);
        if (fallbackData) {
          setLeagueData(fallbackData);
          setTeams(fallbackData.teams?.map(name => ({ name, slug: name.toLowerCase().replace(/\s+/g, '-') })) || []);
          if (fallbackData.type === 'cup') {
            fetchCupEvents(fallbackData.name);
          }
        }
      }
    } catch (error) {
      console.error('Error fetching league:', error);
      const fallbackData = getFallbackLeagueData(actualLeague);
      if (fallbackData) {
        setLeagueData(fallbackData);
        setTeams(fallbackData.teams?.map(name => ({ name, slug: name.toLowerCase().replace(/\s+/g, '-') })) || []);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchCupEvents = async (leagueName) => {
    try {
      const data = await eventsAPI.getAll({ league: leagueName.toUpperCase(), limit: 100 });
      setEvents(data.events || []);
    } catch (error) {
      console.error('Error fetching cup events:', error);
    }
  };

  // Fallback data for when DB is empty
  const getFallbackLeagueData = (slug) => {
    const fallbackLeagues = {
      'serie-a': { name: 'Serie A', country: 'Italy', type: 'league', teams: ['Atalanta', 'Bologna', 'Cagliari', 'Como', 'Fiorentina', 'Genoa', 'Hellas Verona', 'Inter', 'Juventus', 'Lazio', 'Lecce', 'Milan', 'Monza', 'Napoli', 'Parma', 'Roma', 'Sassuolo', 'Torino', 'Udinese', 'Venezia'] },
      'premier-league': { name: 'Premier League', country: 'England', type: 'league', teams: ['Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Liverpool', 'Manchester City', 'Manchester United', 'Newcastle United', 'Nottingham Forest', 'Tottenham', 'West Ham', 'Wolves'] },
      'la-liga': { name: 'La Liga', country: 'Spain', type: 'league', teams: ['Athletic Bilbao', 'Atlético Madrid', 'Barcelona', 'Betis', 'Celta Vigo', 'Getafe', 'Girona', 'Mallorca', 'Osasuna', 'Rayo Vallecano', 'Real Madrid', 'Real Sociedad', 'Sevilla', 'Valencia', 'Villarreal'] },
      'bundesliga': { name: 'Bundesliga', country: 'Germany', type: 'league', teams: ['Augsburg', 'Bayern Munich', 'Borussia Dortmund', 'Eintracht Frankfurt', 'Freiburg', 'Hoffenheim', 'Leverkusen', 'Mainz', 'RB Leipzig', 'Stuttgart', 'Union Berlin', 'Werder Bremen', 'Wolfsburg'] },
      'ligue-1': { name: 'Ligue 1', country: 'France', type: 'league', teams: ['Lens', 'Lille', 'Lyon', 'Marseille', 'Monaco', 'Nice', 'PSG', 'Rennes'] },
      'liga-portugal': { name: 'Liga Portugal', country: 'Portugal', type: 'league', teams: ['Benfica', 'Braga', 'Porto', 'Sporting CP'] },
      'super-lig': { name: 'Super Lig', country: 'Turkey', type: 'league', teams: ['Beşiktaş', 'Fenerbahçe', 'Galatasaray', 'Trabzonspor'] },
      'champions-league': { name: 'Champions League', country: 'Europe', type: 'cup' },
      'europa-league': { name: 'Europa League', country: 'Europe', type: 'cup' },
      'coppa-italia': { name: 'Coppa Italia', country: 'Italy', type: 'cup' },
      'fa-cup': { name: 'FA Cup', country: 'England', type: 'cup' },
      'copa-del-rey': { name: 'Copa del Rey', country: 'Spain', type: 'cup' },
      'dfb-pokal': { name: 'DFB Pokal', country: 'Germany', type: 'cup' },
    };
    return fallbackLeagues[slug] || null;
  };

  const getTeamSlug = (team) => {
    if (typeof team === 'object') return team.slug;
    return team.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  };

  const getTeamName = (team) => {
    if (typeof team === 'object') return team.name;
    return team;
  };

  const leagueName = leagueData?.name || '';
  const isCup = leagueData?.type === 'cup';
  const country = leagueData?.country || '';
  
  const seoTitle = getSeoTitle('league', leagueName, lang);
  const seoDescription = getSeoDescription('league', leagueName, lang, { 
    teamCount: teams.length 
  });
  const canonicalUrl = `${window.location.origin}${getLeagueUrl(actualLeague, lang)}`;

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <Loader2 className="w-16 h-16 text-blue-500 animate-spin" />
      </div>
    );
  }

  if (!leagueData) {
    return (
      <div className="min-h-screen bg-white">
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
      <LeagueSchema leagueName={leagueName} teams={teams.map(getTeamName)} lang={lang} />
      <BreadcrumbSchema items={[
        { name: 'Home', url: '/' },
        { name: leagueName, url: null }
      ]} />
      
      <Header />
      
      {/* Hero Section */}
      <div className="relative py-6 md:py-8 px-4 bg-[#2D3436]">
        <div className="container mx-auto">
          <Breadcrumbs items={[
            { name: leagueName, url: null }
          ]} />
          
          <div className="flex items-center gap-3 mt-3">
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
                {country} 
                {!isCup && teams.length > 0 && ` • ${teams.length} Teams`}
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
            // Cup Events View
            <>
              {loading ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 text-[#0984E3] animate-spin mb-3" />
                  <p className="text-gray-500 text-sm">{t('loadingEvents')}</p>
                </div>
              ) : events.length > 0 ? (
                <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
                  <div className="px-3 py-2 border-b border-gray-200 bg-gray-50">
                    <span className="text-xs text-gray-500 font-medium">
                      {events.length} {events.length > 1 ? t('eventsFound') : t('eventFound')}
                    </span>
                  </div>
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
                {teams.map((team, index) => {
                  const teamName = getTeamName(team);
                  const teamSlug = getTeamSlug(team);
                  const teamLogo = getTeamLogo(teamName);
                  
                  return (
                    <Link
                      key={index}
                      to={getTeamUrl(teamSlug, lang)}
                      className="group bg-white border border-gray-200 hover:border-[#0984E3] rounded-xl p-6 text-center transition-all duration-300 transform hover:-translate-y-2 hover:shadow-lg"
                    >
                      <div className="w-16 h-16 flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform relative">
                        {teamLogo && (
                          <img 
                            src={teamLogo} 
                            alt={`${t('seoTickets')} ${teamName}`}
                            className="w-full h-full object-contain absolute inset-0"
                            onLoad={(e) => {
                              const fallback = e.target.parentElement.querySelector('.team-fallback');
                              if (fallback) fallback.style.display = 'none';
                            }}
                            onError={(e) => {
                              e.target.style.display = 'none';
                            }}
                          />
                        )}
                        <div className="team-fallback w-16 h-16 bg-gradient-to-br from-[#FF6B35] to-[#0984E3] rounded-full flex items-center justify-center">
                          <span className="text-2xl font-bold text-white">
                            {teamName.charAt(0)}
                          </span>
                        </div>
                      </div>
                      <h3 className="font-bold text-[#2D3436] text-sm group-hover:text-[#0984E3] transition-colors">
                        {lang === 'en' ? `${teamName} ${t('seoTickets')}` : `${t('seoTickets')} ${teamName}`}
                      </h3>
                    </Link>
                  );
                })}
              </div>
              
              {teams.length === 0 && (
                <div className="text-center py-12">
                  <Trophy className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Nessuna squadra disponibile</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default LeaguePage;
