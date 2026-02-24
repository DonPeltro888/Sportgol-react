import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { ArrowLeft, Loader2, Trophy } from 'lucide-react';
import { toast } from 'sonner';

const LeaguePage = () => {
  const { league } = useParams();
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [leagueName, setLeagueName] = useState('');
  const [isCup, setIsCup] = useState(false);

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
    const leagueData = leagueTeams[league];
    if (leagueData) {
      setLeagueName(leagueData.name);
      setIsCup(leagueData.isCup);
      if (leagueData.isCup) {
        fetchCupEvents();
      }
    }
    setLoading(false);
  }, [league]);

  const fetchCupEvents = async () => {
    try {
      setLoading(true);
      const leagueData = leagueTeams[league];
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

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Loader2 className="w-16 h-16 text-blue-500 animate-spin" />
      </div>
    );
  }

  if (!leagueTeams[league]) {
    return (
      <div className="min-h-screen bg-black">
        <Header />
        <div className="flex flex-col items-center justify-center py-20">
          <p className="text-gray-400 text-xl mb-4">League not found</p>
          <button
            onClick={() => navigate('/')}
            className="text-blue-400 hover:text-blue-300"
          >
            Back to Home
          </button>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black">
      <Header />
      
      {/* Hero Section */}
      <div className="relative py-20 px-4 bg-gradient-to-br from-blue-900 via-purple-900 to-gray-900">
        <div className="container mx-auto">
          <button
            onClick={() => navigate('/')}
            className="text-white hover:text-blue-400 flex items-center gap-2 mb-6 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="text-sm">Back to Home</span>
          </button>
          
          <div className="flex items-center gap-4 mb-4">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
              <Trophy className="w-10 h-10 text-white" />
            </div>
            <div>
              <h1 className="text-5xl md:text-6xl font-black text-white">{leagueName}</h1>
              <p className="text-gray-300 text-lg mt-2">
                {leagueTeams[league]?.country} 
                {!isCup && ` • ${leagueTeams[league]?.teams?.length} Teams`}
                {isCup && ' • Cup Competition'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Content Section */}
      <div className="py-16 px-4 bg-gradient-to-b from-gray-900 to-black">
        <div className="container mx-auto">
          {isCup ? (
            // Cup Events View
            <>
              <h2 className="text-3xl font-bold text-white mb-8">Upcoming Matches</h2>
              {loading ? (
                <div className="flex flex-col items-center justify-center py-20">
                  <Loader2 className="w-16 h-16 text-blue-500 animate-spin mb-4" />
                  <p className="text-gray-400 text-lg">Loading matches...</p>
                </div>
              ) : events.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                  {events.map((event) => (
                    <EventCard key={event.id || event._id} event={event} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-20">
                  <div className="text-6xl mb-4">🏆</div>
                  <div className="text-gray-400 text-xl mb-2">No matches scheduled yet</div>
                  <p className="text-gray-500">Check back soon for upcoming fixtures</p>
                </div>
              )}
            </>
          ) : (
            // Teams Grid View
            <>
              <h2 className="text-3xl font-bold text-white mb-8">All Teams</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
                {leagueTeams[league]?.teams?.map((team, index) => (
                  <Link
                    key={index}
                    to={`/team/${getTeamSlug(team)}`}
                    className="group bg-gray-800/50 border border-gray-700 hover:border-blue-500 rounded-xl p-6 text-center transition-all duration-300 transform hover:-translate-y-2 hover:shadow-2xl hover:shadow-blue-500/20"
                  >
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                      <span className="text-2xl font-bold text-white">
                        {team.charAt(0)}
                      </span>
                    </div>
                    <h3 className="font-bold text-white text-sm group-hover:text-blue-400 transition-colors">
                      {team}
                    </h3>
                  </Link>
                ))}
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