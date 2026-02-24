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
    <div className="min-h-screen bg-gray-100">
      <Header />
      
      {/* Hero Section */}
      <div className="relative py-16 md:py-20 px-4 bg-gradient-to-br from-blue-900 via-purple-900 to-gray-900">
        <div className="container mx-auto max-w-4xl">
          <button
            onClick={() => navigate('/')}
            className="text-white hover:text-blue-400 flex items-center gap-2 mb-6 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="text-sm">Back to Home</span>
          </button>
          
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 md:w-20 md:h-20 bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center">
              <Users className="w-8 h-8 md:w-10 md:h-10 text-white" />
            </div>
            <div>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-white leading-tight">
                Biglietti<br/>{teamName}
              </h1>
              <p className="text-gray-300 text-base md:text-lg mt-2">All matches - Home & Away</p>
            </div>
          </div>
        </div>
      </div>

      {/* Events List Section */}
      <div className="py-8 px-4">
        <div className="container mx-auto max-w-4xl">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 bg-white rounded-xl">
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
              <p className="text-gray-500">Loading {teamName} events...</p>
            </div>
          ) : events.length > 0 ? (
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              {/* Header */}
              <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                <span className="text-sm text-gray-600 font-medium">
                  {events.length} Match{events.length > 1 ? 'es' : ''} Found
                </span>
              </div>
              
              {/* Events List */}
              <div className="divide-y divide-gray-100">
                {events.map((event) => (
                  <EventListItem key={event.id || event._id} event={event} />
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-20 bg-white rounded-xl">
              <div className="text-6xl mb-4">⚽</div>
              <div className="text-gray-600 text-xl mb-2">No matches found for {teamName}</div>
              <p className="text-gray-400 mb-6">Check back soon for upcoming fixtures</p>
              <Link
                to="/"
                className="inline-flex items-center gap-2 text-blue-500 hover:text-blue-600 font-medium"
              >
                <ArrowLeft className="w-4 h-4" />
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
