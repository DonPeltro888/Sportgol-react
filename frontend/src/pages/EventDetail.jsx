import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Breadcrumbs from '../components/Breadcrumbs';
import { EventSchema, BreadcrumbSchema } from '../components/SchemaOrg';
import SanSiroMap from '../components/SanSiroMap';
import UrgencyBadges from '../components/UrgencyBadges';
import TrustBadges from '../components/TrustBadges';
import { Calendar, MapPin, MessageCircle, ChevronDown, Loader2, Info } from 'lucide-react';
import { toast } from 'sonner';
import SEOHead from '../components/SEOHead';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';
import { getSeoTitle, getSeoDescription, getTeamUrl, getLeagueUrl } from '../utils/seoHelpers';
import { getTeamLogo } from '../data/teamLogos';

const EventDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { lang, getMultiLang } = useLanguage();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSector, setSelectedSector] = useState(null);
  const [activeTab, setActiveTab] = useState('tickets');
  const [openFaq, setOpenFaq] = useState(null);
  const t = (key) => getTranslation(lang, key);

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

  const getTicketCategories = () => {
    if (event?.ticket_categories?.length > 0) {
      return event.ticket_categories.map(cat => ({
        name: getMultiLang(cat.name) || cat.name,
        price: cat.price || cat.price_max || cat.price_min || 100,
        available: cat.available !== false,
        notes: getMultiLang(cat.notes) || cat.notes || ''
      }));
    }
    const basePrice = event?.price_range?.min || 50;
    return [
      { name: 'CAT 1 - VIP', price: basePrice * 4, available: true },
      { name: 'CAT 2', price: basePrice * 2.5, available: true },
      { name: 'CAT 3', price: basePrice * 1.5, available: true },
      { name: 'CAT 4', price: basePrice, available: true },
    ];
  };

  const handleSectorSelect = (sector) => {
    setSelectedSector(sector);
  };

  const handleContactUs = () => {
    toast.success('Reindirizzamento a WhatsApp...');
    window.open('https://wa.me/', '_blank');
  };

  const hasStadiumMap = event?.has_stadium_map === true;

  const getFaqItems = () => {
    const customFaq = [];
    if (event?.faq_1_q && getMultiLang(event.faq_1_q)) {
      customFaq.push({ question: getMultiLang(event.faq_1_q), answer: getMultiLang(event.faq_1_a) || '' });
    }
    if (event?.faq_2_q && getMultiLang(event.faq_2_q)) {
      customFaq.push({ question: getMultiLang(event.faq_2_q), answer: getMultiLang(event.faq_2_a) || '' });
    }
    if (event?.faq_3_q && getMultiLang(event.faq_3_q)) {
      customFaq.push({ question: getMultiLang(event.faq_3_q), answer: getMultiLang(event.faq_3_a) || '' });
    }
    return customFaq;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-white">
        <Header />
        <div className="flex items-center justify-center py-40">
          <Loader2 className="w-16 h-16 text-[#0984E3] animate-spin" />
        </div>
        <Footer />
      </div>
    );
  }

  if (!event) {
    return (
      <div className="min-h-screen bg-white">
        <Header />
        <div className="flex flex-col items-center justify-center py-20">
          <p className="text-gray-400 text-xl mb-4">{t('eventNotFound')}</p>
          <button onClick={() => navigate('/')} className="text-[#0984E3] hover:underline">{t('backToHome')}</button>
        </div>
        <Footer />
      </div>
    );
  }

  const ticketCategories = getTicketCategories();
  const faqItems = getFaqItems();
  const eventTitle = event.title || `${event.home_team} vs ${event.away_team}`;
  const eventLocation = event.location || 'TBA';
  
  const homeTeamLogo = getTeamLogo(event.home_team || event.categories?.[0]);
  const awayTeamLogo = getTeamLogo(event.away_team || event.categories?.[1]);
  
  const seoTitle = getSeoTitle('event', eventTitle, lang);
  const seoDescription = getSeoDescription('event', eventTitle, lang, { stadium: event.stadium, date: event.date });
  const canonicalUrl = `${window.location.origin}/event/${id}`;

  return (
    <div className="min-h-screen bg-gray-50">
      <SEOHead title={seoTitle} description={seoDescription} canonicalUrl={canonicalUrl} ogImage={event.imageUrl || event.image} />
      <EventSchema event={event} lang={lang} />
      <BreadcrumbSchema items={[{ name: 'Home', url: '/' }, { name: event.league, url: getLeagueUrl(event.league?.toLowerCase().replace(/\s+/g, '-'), lang) }, { name: eventTitle, url: null }]} />
      
      <Header />
      
      {/* Hero Section */}
      <div className="bg-[#2D3436] py-6 px-4">
        <div className="container mx-auto">
          <Breadcrumbs items={[{ name: event.league, url: getLeagueUrl(event.league?.toLowerCase().replace(/\s+/g, '-'), lang) }, { name: eventTitle, url: null }]} />
          
          <div className="flex flex-col items-center mt-4">
            {/* Team Logos */}
            <div className="flex items-center justify-center gap-6 mb-4">
              <div className="w-16 h-16 md:w-20 md:h-20 bg-white rounded-xl p-2 flex items-center justify-center">
                {homeTeamLogo ? <img src={homeTeamLogo} alt={`Logo ${event.home_team}`} loading="eager" decoding="async" className="w-full h-full object-contain" /> : <span className="text-2xl font-bold">{event.home_team?.[0]}</span>}
              </div>
              <span className="text-white text-2xl font-bold">vs</span>
              <div className="w-16 h-16 md:w-20 md:h-20 bg-white rounded-xl p-2 flex items-center justify-center">
                {awayTeamLogo ? <img src={awayTeamLogo} alt={`Logo ${event.away_team}`} loading="eager" decoding="async" className="w-full h-full object-contain" /> : <span className="text-2xl font-bold">{event.away_team?.[0]}</span>}
              </div>
            </div>
            
            <h1 className="text-xl md:text-2xl font-bold text-white text-center">{lang === 'en' ? `${eventTitle} Tickets` : `Biglietti ${eventTitle}`}</h1>
            
            <div className="flex flex-wrap items-center justify-center gap-4 mt-3 text-gray-300 text-sm">
              <span className="flex items-center gap-1"><Calendar className="w-4 h-4" /> {event.date}</span>
              <span className="flex items-center gap-1"><MapPin className="w-4 h-4" /> {event.stadium}, {eventLocation}</span>
            </div>
            
            {/* Tags */}
            <div className="flex flex-wrap justify-center gap-2 mt-4">
              {event.categories?.map((cat, idx) => (
                <span key={idx} onClick={() => navigate(getTeamUrl(cat.toLowerCase().replace(/\s+/g, '-'), lang))} 
                  className="bg-[#0984E3] hover:bg-[#0984E3]/80 text-white text-xs font-semibold px-3 py-1.5 rounded-md cursor-pointer">
                  {cat}
                </span>
              ))}
              {event.league && (
                <span onClick={() => navigate(getLeagueUrl(event.league.toLowerCase().replace(/\s+/g, '-'), lang))} 
                  className="bg-[#FF6B35] hover:bg-[#FF6B35]/80 text-white text-xs font-semibold px-3 py-1.5 rounded-md cursor-pointer">
                  {event.league}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content - Viagogo Style Layout */}
      <div className="container mx-auto px-4 py-8">
        {hasStadiumMap ? (
          /* VIAGOGO STYLE: Tickets Left, Map Right */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Left Column: Tickets */}
            <div>
              <h2 className="text-xl font-bold text-[#2D3436] mb-4">Seleziona i tuoi biglietti</h2>
              
              {selectedSector && (
                <div className="bg-green-50 border-2 border-green-500 rounded-xl p-4 mb-4 flex items-center justify-between">
                  <div>
                    <div className="text-sm text-green-600 font-medium">Settore Selezionato</div>
                    <div className="font-bold text-green-800">{selectedSector.name}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-green-600">€{selectedSector.price}</div>
                    <button onClick={handleContactUs} className="mt-1 bg-green-600 hover:bg-green-700 text-white text-sm font-bold py-2 px-4 rounded-lg">
                      Acquista
                    </button>
                  </div>
                </div>
              )}

              <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                {ticketCategories.map((cat, idx) => (
                  <div key={idx} 
                    onClick={() => cat.available && handleSectorSelect(cat)}
                    className={`bg-white border-2 rounded-xl p-4 cursor-pointer transition-all ${
                      !cat.available ? 'opacity-50 cursor-not-allowed border-gray-200' :
                      selectedSector?.name === cat.name ? 'border-green-500 bg-green-50' :
                      'border-gray-200 hover:border-[#0984E3] hover:shadow-md'
                    }`}>
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-[#2D3436]">{cat.name}</span>
                          {!cat.available && <span className="px-2 py-0.5 bg-red-100 text-red-600 text-xs font-bold rounded">ESAURITO</span>}
                        </div>
                        {cat.notes && <p className="text-gray-500 text-xs mt-1">{cat.notes}</p>}
                      </div>
                      <div className="text-right ml-4">
                        <div className={`text-xl font-bold ${cat.available ? 'text-[#FF6B35]' : 'text-gray-400'}`}>€{Math.round(cat.price)}</div>
                        <div className="text-xs text-gray-400">cad.</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Column: Stadium Map */}
            <div className="lg:sticky lg:top-4 h-fit">
              <div className="bg-[#0f1419] rounded-2xl p-6 shadow-xl">
                <div className="text-center mb-4">
                  <h3 className="text-white font-bold text-lg">{event.stadium}</h3>
                  <p className="text-gray-400 text-sm">Clicca su un settore per selezionarlo</p>
                </div>
                <SanSiroMap 
                  sectors={ticketCategories} 
                  onSectorClick={handleSectorSelect}
                  selectedSector={selectedSector?.name}
                />
              </div>
            </div>
          </div>
        ) : (
          /* Standard Layout without map */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              {/* Tabs */}
              <div className="bg-white border border-gray-200 rounded-xl p-1 mb-6 flex gap-1">
                <button onClick={() => setActiveTab('tickets')} className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${activeTab === 'tickets' ? 'bg-[#0984E3] text-white' : 'text-gray-500 hover:bg-gray-100'}`}>Biglietti</button>
                <button onClick={() => setActiveTab('details')} className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${activeTab === 'details' ? 'bg-[#0984E3] text-white' : 'text-gray-500 hover:bg-gray-100'}`}>Dettagli</button>
                <button onClick={() => setActiveTab('faq')} className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${activeTab === 'faq' ? 'bg-[#0984E3] text-white' : 'text-gray-500 hover:bg-gray-100'}`}>FAQ</button>
              </div>

              {activeTab === 'tickets' && (
                <div className="space-y-4">
                  {/* Urgency badges */}
                  <UrgencyBadges
                    eventId={id}
                    availableTickets={event.available_tickets}
                    featured={event.featured}
                  />
                  {ticketCategories.map((cat, idx) => (
                    <div key={idx} className="bg-white border border-gray-200 rounded-xl p-5 hover:border-[#0984E3] hover:shadow-lg transition-all">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h3 className="font-bold text-[#2D3436]">{cat.name}</h3>
                          {cat.notes && <p className="text-[#0984E3] text-xs mt-1">{cat.notes}</p>}
                        </div>
                      </div>
                      <button onClick={handleContactUs} className="w-full bg-[#0984E3] hover:bg-[#0984E3]/90 text-white font-bold py-2.5 rounded-lg flex items-center justify-center gap-2">
                        <MessageCircle className="w-4 h-4" /> Contattaci
                      </button>
                    </div>
                  ))}
                  {/* Trust badges below tickets */}
                  <TrustBadges />
                </div>
              )}

              {activeTab === 'details' && (
                <div className="bg-white border border-gray-200 rounded-xl p-6">
                  <h2 className="text-lg font-bold text-[#2D3436] mb-4 flex items-center gap-2"><Info className="w-5 h-5 text-[#0984E3]" />Informazioni Evento</h2>
                  <div className="space-y-3 text-gray-600">
                    <p><strong>Evento:</strong> {eventTitle}</p>
                    <p><strong>Data:</strong> {event.date} {event.time && `alle ${event.time}`}</p>
                    <p><strong>Stadio:</strong> {event.stadium}</p>
                    <p><strong>Città:</strong> {eventLocation}</p>
                    <p><strong>Competizione:</strong> {event.league}</p>
                  </div>
                </div>
              )}

              {activeTab === 'faq' && (
                <div className="space-y-3">
                  {faqItems.length > 0 ? faqItems.map((item, idx) => (
                    <div key={idx} className="bg-white border border-gray-200 rounded-xl overflow-hidden">
                      <button onClick={() => setOpenFaq(openFaq === idx ? null : idx)} className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-gray-50">
                        <span className="font-semibold text-[#2D3436]">{item.question}</span>
                        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${openFaq === idx ? 'rotate-180' : ''}`} />
                      </button>
                      {openFaq === idx && <div className="px-5 pb-4 text-gray-600">{item.answer}</div>}
                    </div>
                  )) : (
                    <div className="bg-white border border-gray-200 rounded-xl p-8 text-center">
                      <MessageCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-500">Hai domande? Contattaci via WhatsApp!</p>
                      <button onClick={handleContactUs} className="mt-4 bg-green-600 hover:bg-green-500 text-white font-bold py-2.5 px-6 rounded-lg inline-flex items-center gap-2">
                        <MessageCircle className="w-5 h-5" /> Contattaci
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div>
              <div className="bg-white border border-gray-200 rounded-xl p-5 sticky top-4 space-y-4">
                <button onClick={handleContactUs} className="w-full bg-green-600 hover:bg-green-500 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2">
                  <MessageCircle className="w-5 h-5" /> Contattaci su WhatsApp
                </button>
                <TrustBadges />
              </div>
            </div>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default EventDetail;
