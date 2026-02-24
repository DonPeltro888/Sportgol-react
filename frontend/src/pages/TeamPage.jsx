import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import EventListItem from '../components/EventListItem';
import { ArrowLeft, Loader2, Users } from 'lucide-react';
import { toast } from 'sonner';

const TeamPage = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [teamName, setTeamName] = useState('');

  useEffect(() => {
    fetchTeamEvents();
  }, [slug]);

  const fetchTeamEvents = async () => {
    try {
      setLoading(true);
      // Search for team name from slug
      const formattedName = slug.split('-').map(word => 
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

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
      <Header />
      
      {/* Hero Section - Compact */}
      <div className="relative py-8 md:py-12 px-4 bg-gradient-to-br from-blue-900 via-purple-900 to-gray-900">
        <div className="container mx-auto max-w-4xl">
          <button
            onClick={() => navigate('/')}
            className="text-white hover:text-blue-400 flex items-center gap-1 mb-4 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-xs">Back to Home</span>
          </button>
          
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 md:w-14 md:h-14 bg-gradient-to-br from-blue-500 to-purple-500 rounded-xl flex items-center justify-center">
              <Users className="w-6 h-6 md:w-7 md:h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-white leading-tight">
                Biglietti {teamName}
              </h1>
              <p className="text-gray-400 text-xs md:text-sm mt-1">All matches - Home & Away</p>
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
              <p className="text-gray-400 text-sm">Loading {teamName} events...</p>
            </div>
          ) : events.length > 0 ? (
            <div className="bg-gray-800/30 backdrop-blur rounded-xl border border-gray-700/50 overflow-hidden">
              {/* Header */}
              <div className="px-3 py-2 border-b border-gray-700/50">
                <span className="text-xs text-gray-400 font-medium">
                  {events.length} Match{events.length > 1 ? 'es' : ''} Found
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
              <div className="text-gray-300 text-base mb-2">No matches found for {teamName}</div>
              <p className="text-gray-500 text-sm mb-4">Check back soon for upcoming fixtures</p>
              <Link
                to="/"
                className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300 text-sm font-medium"
              >
                <ArrowLeft className="w-3 h-3" />
                Browse all events
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
