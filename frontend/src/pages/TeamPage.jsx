import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import EventCard from '../components/EventCard';
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
              <Users className="w-10 h-10 text-white" />
            </div>
            <div>
              <h1 className="text-5xl md:text-6xl font-black text-white">Biglietti {teamName}</h1>
              <p className="text-gray-300 text-lg mt-2">All matches - Home & Away</p>
            </div>
          </div>
        </div>
      </div>

      {/* Events Section */}
      <div className="py-16 px-4 bg-gradient-to-b from-gray-900 to-black">
        <div className="container mx-auto">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20">
              <Loader2 className="w-16 h-16 text-blue-500 animate-spin mb-4" />
              <p className="text-gray-400 text-lg">Loading {teamName} events...</p>
            </div>
          ) : events.length > 0 ? (
            <>
              <h2 className="text-3xl font-bold text-white mb-8">
                {events.length} Match{events.length > 1 ? 'es' : ''} Found
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
                {events.map((event) => (
                  <EventCard key={event.id || event._id} event={event} />
                ))}
              </div>
            </>
          ) : (
            <div className="text-center py-20">
              <div className="text-6xl mb-4">⚽</div>
              <div className="text-gray-400 text-xl mb-2">No matches found for {teamName}</div>
              <p className="text-gray-500 mb-6">Check back soon for upcoming fixtures</p>
              <Link
                to="/"
                className="text-blue-400 hover:text-blue-300 underline"
              >
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