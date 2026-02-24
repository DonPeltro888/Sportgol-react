import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Calendar, MapPin, ArrowLeft, Ticket, Info, MessageCircle, ChevronDown, Loader2, Users, Euro, Clock, Star } from 'lucide-react';
import { toast } from 'sonner';
import SEOHead from '../components/SEOHead';
import { useLanguage } from '../contexts/LanguageContext';

const EventDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { lang, getMultiLang } = useLanguage();
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
      { name: 'CAT 1 - VIP', description: lang === 'it' ? 'Posti premium con vista ottimale' : lang === 'es' ? 'Asientos premium con vista óptima' : 'Premium seats with best view', price: basePrice * 4 },
      { name: 'CAT 2', description: lang === 'it' ? 'Posti con ottima visibilità' : lang === 'es' ? 'Asientos con excelente visibilidad' : 'Excellent view seats', price: basePrice * 2.5 },
      { name: 'CAT 3', description: lang === 'it' ? 'Posti con buona visuale' : lang === 'es' ? 'Asientos con buena vista' : 'Good view seats', price: basePrice * 1.5 },
      { name: 'CAT 4', description: lang === 'it' ? 'Posti standard' : lang === 'es' ? 'Asientos estándar' : 'Standard seats', price: basePrice },
    ];
  };

  // Default FAQ items based on language
  const getDefaultFaq = () => {
    if (lang === 'it') {
      return [
        {
          question: "Cosa include il biglietto?",
          answer: "• Ingresso all'evento\n• Consegna biglietto digitale via email\n• Posto assegnato nella categoria selezionata\n• Assistenza clienti 24/7"
        },
        {
          question: "Come ricevo i biglietti?",
          answer: "I biglietti vengono inviati via email in formato PDF 48 ore prima dell'evento. Puoi stamparli o mostrarli sul tuo smartphone all'ingresso."
        },
        {
          question: "Posso cancellare o modificare la prenotazione?",
          answer: "Le cancellazioni sono accettate fino a 7 giorni prima dell'evento con rimborso completo. Le modifiche possono essere effettuate fino a 3 giorni prima."
        }
      ];
    } else if (lang === 'es') {
      return [
        {
          question: "¿Qué incluye la entrada?",
          answer: "• Acceso al evento\n• Entrega de entrada digital por email\n• Asiento asignado en la categoría seleccionada\n• Atención al cliente 24/7"
        },
        {
          question: "¿Cómo recibo las entradas?",
          answer: "Las entradas se envían por email en formato PDF 48 horas antes del evento. Puedes imprimirlas o mostrarlas en tu smartphone."
        },
        {
          question: "¿Puedo cancelar o modificar mi reserva?",
          answer: "Las cancelaciones se aceptan hasta 7 días antes del evento con reembolso completo. Las modificaciones pueden hacerse hasta 3 días antes."
        }
      ];
    }
    return [
      {
        question: "What's included in your ticket?",
        answer: "• Event admission\n• Digital ticket delivery via email\n• Assigned seat in selected category\n• 24/7 customer support"
      },
      {
        question: "How do I receive my tickets?",
        answer: "Tickets are sent via email in PDF format 48 hours before the event. You can print them or show them on your smartphone."
      },
      {
        question: "Can I cancel or modify my booking?",
        answer: "Cancellations are accepted up to 7 days before the event with full refund. Modifications can be made up to 3 days before."
      }
    ];
  };

  // Get FAQ items (from event or default)
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
    
    return customFaq.length > 0 ? customFaq : getDefaultFaq();
  };

  const handleContactUs = () => {
    toast.success(lang === 'it' ? 'Reindirizzamento a WhatsApp...' : lang === 'es' ? 'Redirigiendo a WhatsApp...' : 'Redirecting to WhatsApp...');
    window.open('https://wa.me/', '_blank');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
        <Header />
        <div className="flex items-center justify-center py-40">
          <div className="text-center">
            <Loader2 className="w-16 h-16 text-blue-500 animate-spin mx-auto mb-4" />
            <p className="text-gray-400 text-lg">
              {lang === 'it' ? 'Caricamento dettagli evento...' : lang === 'es' ? 'Cargando detalles del evento...' : 'Loading event details...'}
            </p>
          </div>
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
            <p className="text-gray-400 text-xl mb-4">
              {lang === 'it' ? 'Evento non trovato' : lang === 'es' ? 'Evento no encontrado' : 'Event not found'}
            </p>
            <button
              onClick={() => navigate('/')}
              className="text-blue-400 hover:text-blue-300 flex items-center gap-2 mx-auto"
            >
              <ArrowLeft className="w-5 h-5" />
              {lang === 'it' ? 'Torna agli eventi' : lang === 'es' ? 'Volver a eventos' : 'Back to events'}
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

  // SEO content
  const seoIntro = getMultiLang(event?.seo_intro);
  const seoVenueInfo = getMultiLang(event?.seo_venue_info);
  const seoSectors = getMultiLang(event?.seo_sectors);
  const seoPricing = getMultiLang(event?.seo_pricing);
  const seoCta = getMultiLang(event?.seo_cta);

  // Labels based on language
  const labels = {
    backToEvents: lang === 'it' ? 'Torna agli eventi' : lang === 'es' ? 'Volver a eventos' : 'Back to Events',
    tickets: lang === 'it' ? 'Biglietti' : lang === 'es' ? 'Entradas' : 'Tickets',
    availableTickets: lang === 'it' ? 'Biglietti Disponibili' : lang === 'es' ? 'Entradas Disponibles' : 'Available Tickets',
    details: lang === 'it' ? 'Dettagli' : lang === 'es' ? 'Detalles' : 'Details',
    faq: 'FAQ',
    eventDetails: lang === 'it' ? 'Dettagli Evento' : lang === 'es' ? 'Detalles del Evento' : 'Event Details',
    date: lang === 'it' ? 'Data' : lang === 'es' ? 'Fecha' : 'Date',
    venue: lang === 'it' ? 'Stadio' : lang === 'es' ? 'Estadio' : 'Venue',
    priceFrom: lang === 'it' ? 'Prezzo da' : lang === 'es' ? 'Precio desde' : 'Price from',
    contactUs: lang === 'it' ? 'Contattaci' : lang === 'es' ? 'Contáctanos' : 'Contact Us',
    perTicket: lang === 'it' ? 'per biglietto' : lang === 'es' ? 'por entrada' : 'per ticket',
    aboutEvent: lang === 'it' ? 'Informazioni Evento' : lang === 'es' ? 'Información del Evento' : 'About This Event',
    venueInfo: lang === 'it' ? 'Lo Stadio' : lang === 'es' ? 'El Estadio' : 'The Venue',
    sectorsTitle: lang === 'it' ? 'Settori Consigliati' : lang === 'es' ? 'Sectores Recomendados' : 'Recommended Sectors',
    pricingTitle: lang === 'it' ? 'Prezzi e Disponibilità' : lang === 'es' ? 'Precios y Disponibilidad' : 'Pricing & Availability',
    buyNow: lang === 'it' ? 'Acquista Ora' : lang === 'es' ? 'Comprar Ahora' : 'Buy Now'
  };

  // Default content if SEO content is not set
  const defaultIntro = lang === 'it' 
    ? `Acquista i biglietti per ${eventTitle}. Un'esperienza indimenticabile ti aspetta allo ${event.stadium}. Questa partita di ${event.league} promette emozioni uniche e un'atmosfera elettrizzante.`
    : lang === 'es'
    ? `Compra entradas para ${eventTitle}. Una experiencia inolvidable te espera en ${event.stadium}. Este partido de ${event.league} promete emociones únicas.`
    : `Buy tickets for ${eventTitle}. An unforgettable experience awaits at ${event.stadium}. This ${event.league} match promises unique emotions.`;

  const defaultVenueInfo = lang === 'it'
    ? `${event.stadium} è uno degli stadi più iconici, situato nel cuore di ${eventLocation}. Con una capienza eccezionale e strutture all'avanguardia, offre un'esperienza di visione superiore da ogni settore.`
    : lang === 'es'
    ? `${event.stadium} es uno de los estadios más icónicos, ubicado en el corazón de ${eventLocation}. Con capacidad excepcional e instalaciones de vanguardia.`
    : `${event.stadium} is one of the most iconic stadiums, located in the heart of ${eventLocation}. With exceptional capacity and state-of-the-art facilities.`;

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black">
      <Header />
      
      {/* SEO */}
      <SEOHead 
        title={getMultiLang(event?.seo_title) || `${labels.tickets} ${eventTitle} | GOLEVENTS`}
        description={getMultiLang(event?.seo_description) || `${labels.tickets} ${eventTitle}. ${event.date} - ${eventLocation}. ${labels.priceFrom} €${event.price_range?.min || 45}.`}
        keywords={`${labels.tickets.toLowerCase()} ${eventTitle}, ${event.league}, calcio, tickets`}
        ogImage={event.imageUrl || event.image}
        type="event"
        event={{
          title: eventTitle,
          date: event.date,
          dateISO: event.sort_date,
          stadium: event.stadium,
          location: eventLocation,
          categories: event.categories,
          ticket_categories: ticketCategories,
          imageUrl: event.imageUrl || event.image
        }}
      />
      
      {/* Hero Section */}
      <div className="relative h-80 md:h-96 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-gray-900/50 to-gray-900"></div>
        <img
          src={event.imageUrl || event.image}
          alt={eventTitle}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 flex items-end">
          <div className="container mx-auto px-4 pb-8">
            <button
              onClick={() => navigate('/')}
              className="text-white hover:text-blue-400 flex items-center gap-2 mb-4 transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="text-sm">{labels.backToEvents}</span>
            </button>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black text-white mb-4">
              {labels.tickets} {eventTitle}
            </h1>
            <div className="flex flex-wrap gap-2">
              {event.categories?.map((cat, idx) => (
                <span
                  key={idx}
                  onClick={() => navigate(`/team/${cat.toLowerCase().replace(/\s+/g, '-')}`)}
                  className="bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold px-4 py-2 rounded-lg cursor-pointer transition-colors"
                >
                  {cat}
                </span>
              ))}
              <span className="bg-purple-600 text-white text-sm font-bold px-4 py-2 rounded-lg">
                {event.league}
              </span>
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
                className={`flex-1 px-4 py-3 rounded-xl font-semibold transition-all text-sm md:text-base ${
                  activeTab === 'tickets'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {labels.availableTickets}
              </button>
              <button
                onClick={() => setActiveTab('details')}
                className={`flex-1 px-4 py-3 rounded-xl font-semibold transition-all text-sm md:text-base ${
                  activeTab === 'details'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {labels.details}
              </button>
              <button
                onClick={() => setActiveTab('faq')}
                className={`flex-1 px-4 py-3 rounded-xl font-semibold transition-all text-sm md:text-base ${
                  activeTab === 'faq'
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {labels.faq}
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
                        <h3 className="text-xl md:text-2xl font-bold text-white mb-1">{category.name}</h3>
                        <p className="text-gray-400">{category.description}</p>
                        {category.notes && (
                          <p className="text-blue-400 text-sm mt-1">{category.notes}</p>
                        )}
                      </div>
                      <div className="text-right">
                        <div className="text-2xl md:text-3xl font-bold text-green-400">€{Math.round(category.price)}</div>
                        <div className="text-sm text-gray-500">{labels.perTicket}</div>
                      </div>
                    </div>
                    <button
                      onClick={handleContactUs}
                      className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-3 rounded-xl transition-all flex items-center justify-center gap-2"
                    >
                      <MessageCircle className="w-5 h-5" />
                      {labels.contactUs}
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Details Tab */}
            {activeTab === 'details' && (
              <div className="space-y-6">
                {/* Intro Section */}
                <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-6 md:p-8">
                  <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                    <Info className="w-6 h-6 text-blue-400" />
                    {labels.aboutEvent}
                  </h2>
                  <p className="text-gray-300 leading-relaxed text-base md:text-lg">
                    {seoIntro || defaultIntro}
                  </p>
                </div>

                {/* Venue Section */}
                <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-6 md:p-8">
                  <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                    <MapPin className="w-6 h-6 text-purple-400" />
                    {labels.venueInfo}
                  </h2>
                  <p className="text-gray-300 leading-relaxed">
                    {seoVenueInfo || defaultVenueInfo}
                  </p>
                </div>

                {/* Sectors Section */}
                {seoSectors && (
                  <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-6 md:p-8">
                    <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                      <Star className="w-6 h-6 text-yellow-400" />
                      {labels.sectorsTitle}
                    </h2>
                    <div className="text-gray-300 leading-relaxed whitespace-pre-line" dangerouslySetInnerHTML={{ __html: seoSectors }} />
                  </div>
                )}

                {/* Pricing Section */}
                {seoPricing && (
                  <div className="bg-gray-800/50 border border-gray-700 rounded-2xl p-6 md:p-8">
                    <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
                      <Euro className="w-6 h-6 text-green-400" />
                      {labels.pricingTitle}
                    </h2>
                    <p className="text-gray-300 leading-relaxed">
                      {seoPricing}
                    </p>
                  </div>
                )}

                {/* CTA Section */}
                {seoCta && (
                  <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-2xl p-6 md:p-8 text-center">
                    <p className="text-white text-lg mb-4">{seoCta}</p>
                    <button
                      onClick={handleContactUs}
                      className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-3 px-8 rounded-xl transition-all inline-flex items-center gap-2"
                    >
                      <Ticket className="w-5 h-5" />
                      {labels.buyNow}
                    </button>
                  </div>
                )}
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
                      className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-800/80 transition-all"
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
              <h3 className="text-xl font-bold text-white mb-6">{labels.eventDetails}</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <Calendar className="w-5 h-5 text-blue-400 mt-1" />
                  <div>
                    <div className="text-sm text-gray-500 mb-1">{labels.date}</div>
                    <div className="text-white font-semibold">{event.date}</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <MapPin className="w-5 h-5 text-purple-400 mt-1" />
                  <div>
                    <div className="text-sm text-gray-500 mb-1">{labels.venue}</div>
                    <div className="text-white font-semibold">{event.stadium}</div>
                    <div className="text-sm text-gray-400">{eventLocation}</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <Euro className="w-5 h-5 text-green-400 mt-1" />
                  <div>
                    <div className="text-sm text-gray-500 mb-1">{labels.priceFrom}</div>
                    <div className="text-green-400 font-bold text-xl">€{event.price_range?.min || 45}</div>
                  </div>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-700">
                <button
                  onClick={handleContactUs}
                  className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white font-bold py-4 rounded-xl transition-all flex items-center justify-center gap-2 text-lg"
                >
                  <MessageCircle className="w-6 h-6" />
                  {labels.contactUs}
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
