import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Calendar, MapPin, ArrowLeft, Ticket, Info, MessageCircle, ChevronDown, Loader2, Users, Euro, Clock, Star, CheckCircle } from 'lucide-react';
import { toast } from 'sonner';
import SEOHead from '../components/SEOHead';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';
import { getSeoTitle, getSeoDescription } from '../utils/seoHelpers';

const EventDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { lang, getMultiLang } = useLanguage();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
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

  // Default ticket categories
  const getTicketCategories = () => {
    if (event?.ticket_categories?.length > 0) {
      return event.ticket_categories.map(cat => ({
        name: getMultiLang(cat.name) || cat.name,
        description: getMultiLang(cat.description) || cat.description,
        price: cat.price_max || cat.price_min || 100,
        notes: getMultiLang(cat.notes) || ''
      }));
    }
    
    const basePrice = event?.price_range?.min || 50;
    return [
      { name: 'CAT 1 - VIP', price: basePrice * 4 },
      { name: 'CAT 2', price: basePrice * 2.5 },
      { name: 'CAT 3', price: basePrice * 1.5 },
      { name: 'CAT 4', price: basePrice },
    ];
  };

  // Get FAQ items
  const getFaqItems = () => {
    const customFaq = [];
    
    if (event?.faq_1_q && getMultiLang(event.faq_1_q)) {
      customFaq.push({
        question: getMultiLang(event.faq_1_q),
        answer: getMultiLang(event.faq_1_a) || ''
      });
    }
    if (event?.faq_2_q && getMultiLang(event.faq_2_q)) {
      customFaq.push({
        question: getMultiLang(event.faq_2_q),
        answer: getMultiLang(event.faq_2_a) || ''
      });
    }
    if (event?.faq_3_q && getMultiLang(event.faq_3_q)) {
      customFaq.push({
        question: getMultiLang(event.faq_3_q),
        answer: getMultiLang(event.faq_3_a) || ''
      });
    }
    
    return customFaq;
  };

  const handleContactUs = () => {
    toast.success('Reindirizzamento a WhatsApp...');
    window.open('https://wa.me/', '_blank');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
        <Header />
        <div className="flex items-center justify-center py-40">
          <Loader2 className="w-16 h-16 text-blue-500 animate-spin" />
        </div>
        <Footer />
      </div>
    );
  }

  if (!event) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
        <Header />
        <div className="flex items-center justify-center py-40">
          <div className="text-center">
            <p className="text-gray-400 text-xl mb-4">Evento non trovato</p>
            <button onClick={() => navigate('/')} className="text-blue-400 hover:text-blue-300 flex items-center gap-2 mx-auto">
              <ArrowLeft className="w-5 h-5" /> Torna agli eventi
            </button>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  const eventTitle = typeof event?.title === 'object' ? getMultiLang(event.title) : event?.title;
  const eventLocation = typeof event?.location === 'object' ? getMultiLang(event.location) : event?.location;
  const ticketCategories = getTicketCategories();
  const faqItems = getFaqItems();

  // SEO content from database
  const seoIntro = getMultiLang(event?.seo_intro);
  const seoEventInfo = getMultiLang(event?.seo_event_info);
  const seoTicketsInfo = getMultiLang(event?.seo_tickets_info);
  const seoSectors = getMultiLang(event?.seo_sectors);
  const seoPricing = getMultiLang(event?.seo_pricing);
  const seoVenue = getMultiLang(event?.seo_venue);
  const seoCta = getMultiLang(event?.seo_cta);
  
  // Generate SEO title and description with translations
  const seoTitle = getMultiLang(event?.seo_title) || getSeoTitle('event', eventTitle, lang);
  const seoDescription = getMultiLang(event?.seo_description) || getSeoDescription('event', eventTitle, lang, { 
    date: event.date, 
    location: eventLocation 
  });
  const canonicalUrl = `${window.location.origin}/event/${id}`;

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
      <Header />
      
      {/* SEO */}
      <SEOHead 
        title={seoTitle}
        description={seoDescription}
        canonicalUrl={canonicalUrl}
        ogImage={event.imageUrl || event.image}
        type="event"
        event={{
          title: eventTitle,
          date: event.date,
          stadium: event.stadium,
          location: eventLocation,
          categories: event.categories,
          imageUrl: event.imageUrl || event.image
        }}
      />
      
      {/* Hero Section */}
      <div className="relative h-80 md:h-96 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-gray-900/50 to-gray-900"></div>
        <img src={event.imageUrl || event.image} alt={`${t('seoTickets')} ${eventTitle}`} className="w-full h-full object-cover" />
        <div className="absolute inset-0 flex items-end">
          <div className="container mx-auto px-4 pb-8">
            <button onClick={() => navigate('/')} className="text-white hover:text-blue-400 flex items-center gap-2 mb-4 transition-colors">
              <ArrowLeft className="w-5 h-5" />
              <span className="text-sm">{t('home')}</span>
            </button>
            {/* H1 from SEO or default */}
            <h1 className="text-2xl md:text-3xl lg:text-4xl font-black text-white mb-3">
              {getMultiLang(event?.seo_h1) || (lang === 'en' ? `${eventTitle} ${t('seoTickets')}` : `${t('seoTickets')} ${eventTitle}`)}
            </h1>
            <div className="flex flex-wrap gap-2">
              {event.categories?.map((cat, idx) => (
                <span key={idx} onClick={() => navigate(`/team/${cat.toLowerCase().replace(/\s+/g, '-')}`)} 
                  className="bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold px-4 py-2 rounded-lg cursor-pointer transition-colors">
                  {cat}
                </span>
              ))}
              <span className="bg-purple-600 text-white text-sm font-bold px-4 py-2 rounded-lg">{event.league}</span>
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
              <button onClick={() => setActiveTab('tickets')}
                className={`flex-1 px-4 py-3 rounded-xl font-semibold transition-all ${activeTab === 'tickets' ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' : 'text-gray-400 hover:text-white'}`}>
                Biglietti
              </button>
              <button onClick={() => setActiveTab('details')}
                className={`flex-1 px-4 py-3 rounded-xl font-semibold transition-all ${activeTab === 'details' ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' : 'text-gray-400 hover:text-white'}`}>
                Dettagli
              </button>
              <button onClick={() => setActiveTab('faq')}
                className={`flex-1 px-4 py-3 rounded-xl font-semibold transition-all ${activeTab === 'faq' ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white' : 'text-gray-400 hover:text-white'}`}>
                FAQ
              </button>
            </div>

            {/* Tickets Tab */}
            {activeTab === 'tickets' && (
              <div className="space-y-4">
                {ticketCategories.map((category, idx) => (
                  <div key={idx} className="bg-gray-800/50 border border-gray-700 rounded-2xl p-6 hover:border-blue-500 transition-all">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="text-base md:text-lg font-bold text-white mb-1">{category.name}</h3>
                        {category.description && <p className="text-gray-400 text-sm">{category.description}</p>}
                        {category.notes && <p className="text-blue-400 text-xs mt-1">{category.notes}</p>}
                      </div>
                      <div className="text-right">
                        <div className="text-xl md:text-2xl font-bold text-green-400">€{Math.round(category.price)}</div>
                        <div className="text-xs text-gray-500">per biglietto</div>
                      </div>
                    </div>
                    <button onClick={handleContactUs}
                      className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-3 rounded-xl transition-all flex items-center justify-center gap-2">
                      <MessageCircle className="w-5 h-5" /> Contattaci
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Details Tab - SEO Content */}
            {activeTab === 'details' && (
              <div className="space-y-6">
                {/* 4) Intro */}
                {seoIntro && (
                  <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-6 md:p-8">
                    <p className="text-gray-300 leading-relaxed text-lg">{seoIntro}</p>
                  </div>
                )}

                {/* 5) Informazioni Evento */}
                {seoEventInfo && (
                  <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-5 md:p-6">
                    <h2 className="text-lg md:text-xl font-bold text-white mb-3 flex items-center gap-2">
                      <Info className="w-5 h-5 text-blue-400" />
                      Informazioni Evento
                    </h2>
                    <div className="text-gray-300 leading-relaxed whitespace-pre-line" dangerouslySetInnerHTML={{ __html: seoEventInfo }} />
                  </div>
                )}

                {/* 6) Biglietti Disponibili */}
                {seoTicketsInfo && (
                  <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-5 md:p-6">
                    <h2 className="text-lg md:text-xl font-bold text-white mb-3 flex items-center gap-2">
                      <Ticket className="w-5 h-5 text-green-400" />
                      Biglietti Disponibili
                    </h2>
                    <div className="text-gray-300 leading-relaxed whitespace-pre-line" dangerouslySetInnerHTML={{ __html: seoTicketsInfo }} />
                  </div>
                )}

                {/* 7) Settori Consigliati */}
                {seoSectors && (
                  <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-5 md:p-6">
                    <h2 className="text-lg md:text-xl font-bold text-white mb-3 flex items-center gap-2">
                      <Star className="w-5 h-5 text-yellow-400" />
                      Settori Consigliati
                    </h2>
                    <div className="text-gray-300 leading-relaxed whitespace-pre-line" dangerouslySetInnerHTML={{ __html: seoSectors }} />
                  </div>
                )}

                {/* 8) Prezzi e Domanda */}
                {seoPricing && (
                  <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-5 md:p-6">
                    <h2 className="text-lg md:text-xl font-bold text-white mb-3 flex items-center gap-2">
                      <Euro className="w-5 h-5 text-green-400" />
                      Prezzi e Domanda
                    </h2>
                    <p className="text-gray-300 leading-relaxed">{seoPricing}</p>
                  </div>
                )}

                {/* 9) Venue */}
                {seoVenue && (
                  <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-5 md:p-6">
                    <h2 className="text-lg md:text-xl font-bold text-white mb-3 flex items-center gap-2">
                      <MapPin className="w-5 h-5 text-purple-400" />
                      Lo Stadio
                    </h2>
                    <p className="text-gray-300 leading-relaxed">{seoVenue}</p>
                  </div>
                )}

                {/* 11) CTA */}
                {seoCta && (
                  <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-2xl p-5 md:p-6 text-center">
                    <p className="text-white text-base mb-3">{seoCta}</p>
                    <button onClick={handleContactUs}
                      className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-3 px-8 rounded-xl transition-all inline-flex items-center gap-2">
                      <Ticket className="w-5 h-5" /> Acquista Ora
                    </button>
                  </div>
                )}

                {/* If no SEO content, show default message */}
                {!seoIntro && !seoEventInfo && !seoVenue && (
                  <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8 text-center">
                    <Info className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-400">Dettagli evento in arrivo. Contattaci per maggiori informazioni.</p>
                  </div>
                )}
              </div>
            )}

            {/* FAQ Tab */}
            {activeTab === 'faq' && (
              <div className="space-y-4">
                {faqItems.length > 0 ? (
                  faqItems.map((item, idx) => (
                    <div key={idx} className="bg-gray-800/50 border border-gray-700 rounded-2xl overflow-hidden">
                      <button onClick={() => setOpenFaq(openFaq === idx ? null : idx)}
                        className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-800/80 transition-all">
                        <span className="text-lg font-semibold text-white">{item.question}</span>
                        <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${openFaq === idx ? 'rotate-180' : ''}`} />
                      </button>
                      {openFaq === idx && (
                        <div className="px-6 pb-4 text-gray-300 whitespace-pre-line">{item.answer}</div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-8 text-center">
                    <MessageCircle className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-400">Hai domande? Contattaci direttamente via WhatsApp!</p>
                    <button onClick={handleContactUs}
                      className="mt-4 bg-green-600 hover:bg-green-500 text-white font-bold py-3 px-6 rounded-xl transition-all inline-flex items-center gap-2">
                      <MessageCircle className="w-5 h-5" /> Contattaci
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-5 sticky top-24">
              <h3 className="text-base font-bold text-white mb-4">Dettagli Evento</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <Calendar className="w-5 h-5 text-blue-400 mt-1" />
                  <div>
                    <div className="text-sm text-gray-500 mb-1">Data</div>
                    <div className="text-white font-semibold">{event.date}</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-purple-400 mt-1" />
                  <div>
                    <div className="text-sm text-gray-500 mb-1">Stadio</div>
                    <div className="text-white font-semibold">{event.stadium}</div>
                    <div className="text-sm text-gray-400">{eventLocation}</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Euro className="w-5 h-5 text-green-400 mt-1" />
                  <div>
                    <div className="text-sm text-gray-500 mb-1">Prezzo da</div>
                    <div className="text-green-400 font-bold text-xl">€{event.price_range?.min || 45}</div>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-5 border-t border-gray-700">
                <button onClick={handleContactUs}
                  className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white font-bold py-3 rounded-xl transition-all flex items-center justify-center gap-2 text-base">
                  <MessageCircle className="w-5 h-5" /> Contattaci
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default EventDetail;
