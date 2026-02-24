import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import { Calendar, MapPin, ArrowLeft, Ticket, Info, MessageCircle, ChevronDown, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import SEOHead from '../components/SEOHead';
import { useLanguage } from '../contexts/LanguageContext';

const EventDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { lang, getMultiLang, t } = useLanguage();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('tickets');
  const [openFaq, setOpenFaq] = useState(null);

  useEffect(() => {
    fetchEventDetail();
  }, [id]);

  const fetchEventDetail = async () => {
    try {
      setLoading(true);
      const data = await eventsAPI.getById(id);
      setEvent(data);
    } catch (error) {
      console.error('Error fetching event:', error);
      toast.error('Failed to load event details');
    } finally {
      setLoading(false);
    }
  };

  const ticketCategories = [
    { name: 'CAT 1', description: 'Premium seats with best view', price: event?.price_range?.max || 250 },
    { name: 'CAT 2', description: 'Excellent view seats', price: event?.price_range?.max * 0.75 || 180 },
    { name: 'CAT 3', description: 'Good view seats', price: event?.price_range?.max * 0.5 || 120 },
    { name: 'CAT 4', description: 'Standard seats', price: event?.price_range?.min || 45 },
  ];

  const faqItems = [
    {
      question: "What's included in your ticket?",
      answer: `• Event admission: Your ticket grants you access to the event.\n• Ticket delivery: You will receive your tickets securely.\n• Hotel accommodation: Enjoy a night in a hotel with a double room.\n• Single room: If you prefer a single room, please let us know in advance.\n• Additional night: Want more fun? You can add an additional night to your package upon request.\n• Upgrade to a 4-star hotel: Elevate your experience by staying in a 4-star hotel.\n• 24/7 phone support: Our phone support team is available 24 hours a day, 7 days a week.`
    },
    {
      question: 'How do I receive my tickets?',
      answer: 'Tickets will be delivered via email in PDF format 48 hours before the event. You can print them or show them on your mobile device at the entrance.'
    },
    {
      question: 'Can I cancel or modify my booking?',
      answer: 'Cancellations are accepted up to 7 days before the event with a full refund. Modifications can be made up to 3 days before the event date.'
    },
    {
      question: 'Are there any age restrictions?',
      answer: 'Children under 14 must be accompanied by an adult. All attendees must have a valid ticket regardless of age.'
    }
  ];

  const handleContactUs = () => {
    toast.success('Redirecting to WhatsApp...');
    window.open('https://wa.me/', '_blank');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-16 h-16 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-400 text-lg">Loading event details...</p>
        </div>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 text-xl mb-4">Event not found</p>
          <button
            onClick={() => navigate('/')}
            className="text-blue-400 hover:text-blue-300 flex items-center gap-2 mx-auto"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to events
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
      {/* Hero Section */}
      <div className="relative h-96 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-gray-900/50 to-gray-900"></div>
        <img
          src={event.image}
          alt={event.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 flex items-end">
          <div className="container mx-auto px-4 pb-8">
            <button
              onClick={() => navigate('/')}
              className="text-white hover:text-blue-400 flex items-center gap-2 mb-4 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="text-sm">Back to Events</span>
            </button>
            <h1 className="text-5xl md:text-6xl font-black text-white mb-4">
              Biglietti {event.title}
            </h1>
            <div className="flex flex-wrap gap-2">
              {event.categories.map((cat, idx) => (
                <span
                  key={idx}
                  className="bg-blue-600 text-white text-sm font-bold px-4 py-2 rounded-lg"
                >
                  {cat}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Tabs */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-2 mb-8 flex gap-2">
              <button
                onClick={() => setActiveTab('tickets')}
                className={`flex-1 px-6 py-3 rounded-xl font-semibold transition-all ${
                  activeTab === 'tickets'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Available Tickets
              </button>
              <button
                onClick={() => setActiveTab('details')}
                className={`flex-1 px-6 py-3 rounded-xl font-semibold transition-all ${
                  activeTab === 'details'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                Details
              </button>
              <button
                onClick={() => setActiveTab('faq')}
                className={`flex-1 px-6 py-3 rounded-xl font-semibold transition-all ${
                  activeTab === 'faq'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                FAQ
              </button>
            </div>

            {/* Tickets Tab */}
            {activeTab === 'tickets' && (
              <div className="space-y-4">
                {ticketCategories.map((category, idx) => (
                  <div
                    key={idx}
                    className="bg-gray-800/50 border border-gray-700 rounded-2xl p-6 hover:border-blue-500 transition-all"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-2xl font-bold text-white mb-1">{category.name}</h3>
                        <p className="text-gray-400">{category.description}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-3xl font-bold text-blue-400">€{category.price}</div>
                        <div className="text-sm text-gray-500">per ticket</div>
                      </div>
                    </div>
                    <button
                      onClick={handleContactUs}
                      className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-3 rounded-xl transition-all flex items-center justify-center gap-2"
                    >
                      <MessageCircle className="w-5 h-5" />
                      Contact Us
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Details Tab */}
            {activeTab === 'details' && (
              <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8">
                <h3 className="text-2xl font-bold text-white mb-6">Event Information</h3>
                <div className="space-y-6 text-gray-300">
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-2">About This Event</h4>
                    <p className="leading-relaxed">
                      Experience the thrill of live football action at {event.stadium}. This exciting {event.league} match promises an unforgettable atmosphere.
                    </p>
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-2">Stadium Information</h4>
                    <p className="leading-relaxed">
                      {event.stadium} is one of the premier football venues, offering excellent facilities and an electric atmosphere for fans.
                    </p>
                  </div>
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-2">Getting There</h4>
                    <p className="leading-relaxed">
                      The stadium is easily accessible by public transport. We recommend arriving at least 1 hour before kickoff to ensure smooth entry.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* FAQ Tab */}
            {activeTab === 'faq' && (
              <div className="space-y-4">
                {faqItems.map((item, idx) => (
                  <div
                    key={idx}
                    className="bg-gray-800/50 border border-gray-700 rounded-2xl overflow-hidden"
                  >
                    <button
                      onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                      className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-800/50 transition-all"
                    >
                      <span className="text-lg font-semibold text-white">{item.question}</span>
                      <ChevronDown
                        className={`w-5 h-5 text-gray-400 transition-transform ${
                          openFaq === idx ? 'transform rotate-180' : ''
                        }`}
                      />
                    </button>
                    {openFaq === idx && (
                      <div className="px-6 pb-4 text-gray-300 whitespace-pre-line">
                        {item.answer}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-6 sticky top-24">
              <h3 className="text-xl font-bold text-white mb-6">Event Details</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <Calendar className="w-5 h-5 text-blue-400 mt-1" />
                  <div>
                    <div className="text-sm text-gray-500 mb-1">Date</div>
                    <div className="text-white font-semibold">{event.date}</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-purple-400 mt-1" />
                  <div>
                    <div className="text-sm text-gray-500 mb-1">Venue</div>
                    <div className="text-white font-semibold">{event.stadium}</div>
                    <div className="text-sm text-gray-400">{event.location}</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Ticket className="w-5 h-5 text-pink-400 mt-1" />
                  <div>
                    <div className="text-sm text-gray-500 mb-1">Available Tickets</div>
                    <div className="text-white font-semibold">{event.available_tickets}+</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-green-400 mt-1" />
                  <div>
                    <div className="text-sm text-gray-500 mb-1">League</div>
                    <div className="text-white font-semibold">{event.league}</div>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-700">
                <div className="text-sm text-gray-500 mb-2">Price Range</div>
                <div className="text-3xl font-bold text-white mb-4">
                  €{event.price_range?.min} - €{event.price_range?.max}
                </div>
                <button
                  onClick={handleContactUs}
                  className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold py-3 rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg"
                >
                  <MessageCircle className="w-5 h-5" />
                  Book Now via WhatsApp
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventDetail;