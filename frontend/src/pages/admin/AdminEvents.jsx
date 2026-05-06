import React, { useState, useEffect } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { Plus, Pencil, Trash2, Search, X, Save, ChevronDown, Ticket } from 'lucide-react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import ImageUploader from '../../components/admin/ImageUploader';
import GoogleSnippetPreview, { SocialPreview } from '../../components/admin/GoogleSnippetPreview';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminEvents = () => {
  const { authFetch, token } = useAdminAuth();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [showModal, setShowModal] = useState(false);
  const [editingEvent, setEditingEvent] = useState(null);
  const [activeTab, setActiveTab] = useState('basic');
  const [activeLang, setActiveLang] = useState('it');

  const defaultEvent = {
    title: { it: '', es: '', en: '' },
    slug: { it: '', es: '', en: '' },
    categories: [],
    date: '',
    location: { it: '', es: '', en: '' },
    stadium: '',
    league: '',
    featured: false,
    imageUrl: '',
    ticket_categories: [],
    // SEO Meta
    seo_title: { it: '', es: '', en: '' },
    seo_description: { it: '', es: '', en: '' },
    seo_h1: { it: '', es: '', en: '' },
    // SEO Content (following prompt structure)
    seo_intro: { it: '', es: '', en: '' },           // 4) Intro
    seo_event_info: { it: '', es: '', en: '' },      // 5) Informazioni Evento
    seo_tickets_info: { it: '', es: '', en: '' },    // 6) Biglietti disponibili
    seo_sectors: { it: '', es: '', en: '' },         // 7) Settori consigliati
    seo_pricing: { it: '', es: '', en: '' },         // 8) Prezzi e domanda
    seo_venue: { it: '', es: '', en: '' },           // 9) Venue personalizzata
    seo_cta: { it: '', es: '', en: '' },             // 11) CTA finale
    // 10) FAQ
    faq_1_q: { it: '', es: '', en: '' },
    faq_1_a: { it: '', es: '', en: '' },
    faq_2_q: { it: '', es: '', en: '' },
    faq_2_a: { it: '', es: '', en: '' },
    faq_3_q: { it: '', es: '', en: '' },
    faq_3_a: { it: '', es: '', en: '' }
  };

  const [formData, setFormData] = useState(defaultEvent);

  useEffect(() => {
    fetchEvents();
  }, [page, search]);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page, limit: 20 });
      if (search) params.append('search', search);
      
      const response = await authFetch(`${API_URL}/api/admin/events?${params}`);
      const data = await response.json();
      setEvents(data.events || []);
      setTotalPages(data.pages || 1);
    } catch (error) {
      console.error('Error fetching events:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingEvent(null);
    setFormData(defaultEvent);
    setActiveTab('basic');
    setShowModal(true);
  };

  const handleEdit = (event) => {
    setEditingEvent(event);
    // Handle both old format (string) and new format (multilang object)
    setFormData({
      title: typeof event.title === 'object' ? event.title : { it: event.title || '', es: '', en: '' },
      slug: typeof event.slug === 'object' ? event.slug : { it: '', es: '', en: '' },
      categories: event.categories || [],
      date: event.date || '',
      location: typeof event.location === 'object' ? event.location : { it: event.location || '', es: '', en: '' },
      stadium: event.stadium || '',
      league: event.league || '',
      featured: event.featured || false,
      imageUrl: event.imageUrl || '',
      ticket_categories: event.ticket_categories || [],
      // SEO Meta
      seo_title: event.seo_title || { it: '', es: '', en: '' },
      seo_description: event.seo_description || { it: '', es: '', en: '' },
      seo_h1: event.seo_h1 || { it: '', es: '', en: '' },
      // SEO Content
      seo_intro: event.seo_intro || { it: '', es: '', en: '' },
      seo_event_info: event.seo_event_info || { it: '', es: '', en: '' },
      seo_tickets_info: event.seo_tickets_info || { it: '', es: '', en: '' },
      seo_sectors: event.seo_sectors || { it: '', es: '', en: '' },
      seo_pricing: event.seo_pricing || { it: '', es: '', en: '' },
      seo_venue: event.seo_venue || { it: '', es: '', en: '' },
      seo_cta: event.seo_cta || { it: '', es: '', en: '' },
      // FAQ
      faq_1_q: event.faq_1_q || { it: '', es: '', en: '' },
      faq_1_a: event.faq_1_a || { it: '', es: '', en: '' },
      faq_2_q: event.faq_2_q || { it: '', es: '', en: '' },
      faq_2_a: event.faq_2_a || { it: '', es: '', en: '' },
      faq_3_q: event.faq_3_q || { it: '', es: '', en: '' },
      faq_3_a: event.faq_3_a || { it: '', es: '', en: '' }
    });
    setActiveTab('basic');
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Sei sicuro di voler eliminare questo evento?')) return;
    
    try {
      await authFetch(`${API_URL}/api/admin/events/${id}`, { method: 'DELETE' });
      fetchEvents();
    } catch (error) {
      console.error('Error deleting event:', error);
    }
  };

  const handleSave = async () => {
    try {
      const method = editingEvent ? 'PUT' : 'POST';
      const url = editingEvent 
        ? `${API_URL}/api/admin/events/${editingEvent.id}`
        : `${API_URL}/api/admin/events`;
      
      await authFetch(url, {
        method,
        body: JSON.stringify(formData)
      });
      
      setShowModal(false);
      fetchEvents();
    } catch (error) {
      console.error('Error saving event:', error);
    }
  };

  const updateMultiLang = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: { ...prev[field], [activeLang]: value }
    }));
  };

  const addTicketCategory = () => {
    setFormData(prev => ({
      ...prev,
      ticket_categories: [...prev.ticket_categories, {
        id: Date.now().toString(),
        name: { it: '', es: '', en: '' },
        description: { it: '', es: '', en: '' },
        price_min: 0,
        price_max: 0,
        available: 0,
        notes: { it: '', es: '', en: '' }
      }]
    }));
  };

  const updateTicketCategory = (index, field, value) => {
    setFormData(prev => {
      const updated = [...prev.ticket_categories];
      if (field.includes('.')) {
        const [mainField, subField] = field.split('.');
        updated[index][mainField] = { ...updated[index][mainField], [subField]: value };
      } else {
        updated[index][field] = value;
      }
      return { ...prev, ticket_categories: updated };
    });
  };

  const removeTicketCategory = (index) => {
    setFormData(prev => ({
      ...prev,
      ticket_categories: prev.ticket_categories.filter((_, i) => i !== index)
    }));
  };

  const getDisplayTitle = (event) => {
    if (typeof event.title === 'object') {
      return event.title.it || event.title.en || event.title.es || '-';
    }
    return event.title || '-';
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white">Eventi</h1>
            <p className="text-gray-400">Gestisci gli eventi e i biglietti</p>
          </div>
          <button
            onClick={handleCreate}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
            data-testid="create-event-btn"
          >
            <Plus className="w-5 h-5" />
            Nuovo Evento
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Cerca eventi..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Events Table */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-900/50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Titolo</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Data</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Campionato</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Biglietti</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase">Azioni</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-400">
                      Caricamento...
                    </td>
                  </tr>
                ) : events.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-4 py-8 text-center text-gray-400">
                      Nessun evento trovato
                    </td>
                  </tr>
                ) : events.map((event) => (
                  <tr key={event.id} className="hover:bg-gray-700/30">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        {event.imageUrl && (
                          <img src={event.imageUrl} alt="" className="w-10 h-10 rounded object-cover" />
                        )}
                        <div>
                          <p className="text-white font-medium">{getDisplayTitle(event)}</p>
                          <p className="text-gray-400 text-sm">{event.stadium}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-gray-300">{event.date}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 bg-blue-600/20 text-blue-400 rounded text-xs">
                        {event.league}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-gray-300">
                      {event.ticket_categories?.length || 0} cat.
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleEdit(event)}
                          className="p-2 text-gray-400 hover:text-blue-400 transition-colors"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(event.id)}
                          className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-4 py-3 border-t border-gray-700 flex items-center justify-between">
              <span className="text-gray-400 text-sm">Pagina {page} di {totalPages}</span>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1 bg-gray-700 text-white rounded disabled:opacity-50"
                >
                  Precedente
                </button>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-3 py-1 bg-gray-700 text-white rounded disabled:opacity-50"
                >
                  Successivo
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">
                {editingEvent ? 'Modifica Evento' : 'Nuovo Evento'}
              </h2>
              <div className="flex items-center gap-2">
                {editingEvent && (editingEvent.slug || editingEvent.id) && (
                  <a
                    href={`/admin/seo/targets/event/${editingEvent.slug || editingEvent.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    data-testid="seo-ai-from-event-edit"
                    className="text-xs px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white inline-flex items-center gap-1.5 font-semibold"
                    title="Apri il SEO Admin per generare con AI"
                  >
                    ✨ Genera SEO con AI
                  </a>
                )}
                <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Language Tabs */}
            <div className="px-6 py-2 border-b border-gray-700 flex gap-2">
              {['it', 'es', 'en'].map(lang => (
                <button
                  key={lang}
                  onClick={() => setActiveLang(lang)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    activeLang === lang 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {lang.toUpperCase()}
                </button>
              ))}
            </div>

            {/* Content Tabs */}
            <div className="px-6 py-2 border-b border-gray-700 flex gap-2 overflow-x-auto">
              {[
                { id: 'basic', label: 'Info Base' },
                { id: 'tickets', label: 'Biglietti' },
                { id: 'content', label: 'Contenuti SEO' },
                { id: 'faq', label: 'FAQ' },
                { id: 'seo', label: 'Meta SEO' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                    activeTab === tab.id 
                      ? 'bg-purple-600 text-white' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6">
              {activeTab === 'basic' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Titolo ({activeLang.toUpperCase()})</label>
                    <input
                      type="text"
                      value={formData.title[activeLang] || ''}
                      onChange={(e) => updateMultiLang('title', e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      placeholder="Es: Inter vs Milan"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-1">Data</label>
                      <input
                        type="text"
                        value={formData.date}
                        onChange={(e) => setFormData({...formData, date: e.target.value})}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        placeholder="March 15, 2026"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-1">Campionato</label>
                      <input
                        type="text"
                        value={formData.league}
                        onChange={(e) => setFormData({...formData, league: e.target.value})}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        placeholder="SERIE A"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-1">Stadio</label>
                      <input
                        type="text"
                        value={formData.stadium}
                        onChange={(e) => setFormData({...formData, stadium: e.target.value})}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        placeholder="San Siro"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-1">Località ({activeLang.toUpperCase()})</label>
                      <input
                        type="text"
                        value={formData.location[activeLang] || ''}
                        onChange={(e) => updateMultiLang('location', e.target.value)}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        placeholder="Milano"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Immagine</label>
                    <ImageUploader
                      value={formData.imageUrl}
                      onChange={(url) => setFormData({...formData, imageUrl: url})}
                      token={token}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Squadre (separate da virgola)</label>
                    <input
                      type="text"
                      value={formData.categories.join(', ')}
                      onChange={(e) => setFormData({...formData, categories: e.target.value.split(',').map(s => s.trim()).filter(Boolean)})}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      placeholder="INTER, MILAN"
                    />
                  </div>

                  <div className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      id="featured"
                      checked={formData.featured}
                      onChange={(e) => setFormData({...formData, featured: e.target.checked})}
                      className="w-4 h-4 rounded bg-gray-700 border-gray-600"
                    />
                    <label htmlFor="featured" className="text-gray-300">In evidenza</label>
                  </div>
                </div>
              )}

              {activeTab === 'tickets' && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold text-white">Categorie Biglietti</h3>
                    <button
                      onClick={addTicketCategory}
                      className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded-lg text-sm"
                    >
                      <Plus className="w-4 h-4" />
                      Aggiungi Categoria
                    </button>
                  </div>

                  {formData.ticket_categories.length === 0 ? (
                    <div className="text-center py-8 text-gray-400">
                      <Ticket className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <p>Nessuna categoria biglietti</p>
                      <p className="text-sm">Clicca "Aggiungi Categoria" per creare le fasce di prezzo</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {formData.ticket_categories.map((ticket, index) => (
                        <div key={ticket.id} className="bg-gray-700/50 rounded-lg p-4 border border-gray-600">
                          <div className="flex items-center justify-between mb-3">
                            <span className="text-white font-medium">Categoria {index + 1}</span>
                            <button
                              onClick={() => removeTicketCategory(index)}
                              className="text-red-400 hover:text-red-300"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div>
                              <label className="block text-xs text-gray-400 mb-1">Nome ({activeLang.toUpperCase()})</label>
                              <input
                                type="text"
                                value={ticket.name?.[activeLang] || ''}
                                onChange={(e) => updateTicketCategory(index, `name.${activeLang}`, e.target.value)}
                                className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-1.5 text-white text-sm"
                                placeholder="Es: Tribuna VIP"
                              />
                            </div>
                            <div>
                              <label className="block text-xs text-gray-400 mb-1">Posti disponibili</label>
                              <input
                                type="number"
                                value={ticket.available || 0}
                                onChange={(e) => updateTicketCategory(index, 'available', parseInt(e.target.value) || 0)}
                                className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-1.5 text-white text-sm"
                              />
                            </div>
                            <div>
                              <label className="block text-xs text-gray-400 mb-1">Prezzo Min (€)</label>
                              <input
                                type="number"
                                value={ticket.price_min || 0}
                                onChange={(e) => updateTicketCategory(index, 'price_min', parseFloat(e.target.value) || 0)}
                                className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-1.5 text-white text-sm"
                              />
                            </div>
                            <div>
                              <label className="block text-xs text-gray-400 mb-1">Prezzo Max (€)</label>
                              <input
                                type="number"
                                value={ticket.price_max || 0}
                                onChange={(e) => updateTicketCategory(index, 'price_max', parseFloat(e.target.value) || 0)}
                                className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-1.5 text-white text-sm"
                              />
                            </div>
                          </div>

                          <div className="mt-3">
                            <label className="block text-xs text-gray-400 mb-1">Note ({activeLang.toUpperCase()})</label>
                            <textarea
                              value={ticket.notes?.[activeLang] || ''}
                              onChange={(e) => updateTicketCategory(index, `notes.${activeLang}`, e.target.value)}
                              className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-1.5 text-white text-sm"
                              rows={2}
                              placeholder="Es: Accesso VIP, parcheggio incluso..."
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Content SEO Tab - Following exact prompt structure */}
              {activeTab === 'content' && (
                <div className="space-y-4">
                  <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 mb-4">
                    <p className="text-blue-400 text-sm">
                      <strong>Struttura SEO:</strong> Compila tutti i campi seguendo le linee guida. Testo unico per ogni evento.
                    </p>
                  </div>
                  
                  {/* 4) Intro - 100-130 parole */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      4) Intro ({activeLang.toUpperCase()}) - 100-130 parole, unica
                    </label>
                    <textarea
                      value={formData.seo_intro?.[activeLang] || ''}
                      onChange={(e) => updateMultiLang('seo_intro', e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      rows={5}
                      placeholder="Descrizione introduttiva unica dell'evento..."
                    />
                  </div>

                  {/* 5) Informazioni Evento (elenco) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      5) Informazioni Evento ({activeLang.toUpperCase()}) - Elenco puntato
                    </label>
                    <textarea
                      value={formData.seo_event_info?.[activeLang] || ''}
                      onChange={(e) => updateMultiLang('seo_event_info', e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      rows={4}
                      placeholder="• Data: 15 Marzo 2026&#10;• Orario: 20:45&#10;• Competizione: Serie A&#10;• Tipo: Derby"
                    />
                  </div>

                  {/* 6) Biglietti disponibili */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      6) Biglietti Disponibili ({activeLang.toUpperCase()})
                    </label>
                    <textarea
                      value={formData.seo_tickets_info?.[activeLang] || ''}
                      onChange={(e) => updateMultiLang('seo_tickets_info', e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      rows={3}
                      placeholder="Descrizione delle tipologie di biglietti disponibili..."
                    />
                  </div>

                  {/* 7) Settori consigliati (min 3, motivati) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      7) Settori Consigliati ({activeLang.toUpperCase()}) - Min 3, motivati - HTML supportato
                    </label>
                    <textarea
                      value={formData.seo_sectors?.[activeLang] || ''}
                      onChange={(e) => updateMultiLang('seo_sectors', e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      rows={6}
                      placeholder="<strong>Tribuna VIP:</strong> Vista panoramica ottimale...&#10;<strong>Primo Anello:</strong> Perfetto per famiglie...&#10;<strong>Curva:</strong> Atmosfera unica..."
                    />
                  </div>

                  {/* 8) Prezzi e domanda */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      8) Prezzi e Domanda ({activeLang.toUpperCase()})
                    </label>
                    <textarea
                      value={formData.seo_pricing?.[activeLang] || ''}
                      onChange={(e) => updateMultiLang('seo_pricing', e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      rows={3}
                      placeholder="Informazioni su prezzi, domanda e disponibilità..."
                    />
                  </div>

                  {/* 9) Venue personalizzata - 100-150 parole */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      9) Venue/Stadio ({activeLang.toUpperCase()}) - 100-150 parole
                    </label>
                    <textarea
                      value={formData.seo_venue?.[activeLang] || ''}
                      onChange={(e) => updateMultiLang('seo_venue', e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      rows={5}
                      placeholder="Descrizione personalizzata dello stadio..."
                    />
                  </div>

                  {/* 11) CTA finale */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      11) CTA Finale ({activeLang.toUpperCase()})
                    </label>
                    <textarea
                      value={formData.seo_cta?.[activeLang] || ''}
                      onChange={(e) => updateMultiLang('seo_cta', e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      rows={2}
                      placeholder="Non perdere questa partita! Acquista subito i tuoi biglietti..."
                    />
                  </div>
                </div>
              )}

              {/* FAQ Tab */}
              {activeTab === 'faq' && (
                <div className="space-y-6">
                  <p className="text-gray-400 text-sm mb-4">
                    FAQ personalizzate per questo evento. Se vuote, verranno mostrate le FAQ predefinite.
                  </p>
                  
                  {/* FAQ 1 */}
                  <div className="bg-gray-700/30 rounded-lg p-4 border border-gray-600">
                    <h4 className="text-white font-medium mb-3">FAQ 1</h4>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">Domanda ({activeLang.toUpperCase()})</label>
                        <input
                          type="text"
                          value={formData.faq_1_q?.[activeLang] || ''}
                          onChange={(e) => updateMultiLang('faq_1_q', e.target.value)}
                          className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white text-sm"
                          placeholder="Es: Come posso acquistare i biglietti?"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">Risposta ({activeLang.toUpperCase()})</label>
                        <textarea
                          value={formData.faq_1_a?.[activeLang] || ''}
                          onChange={(e) => updateMultiLang('faq_1_a', e.target.value)}
                          className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white text-sm"
                          rows={3}
                          placeholder="Risposta dettagliata..."
                        />
                      </div>
                    </div>
                  </div>

                  {/* FAQ 2 */}
                  <div className="bg-gray-700/30 rounded-lg p-4 border border-gray-600">
                    <h4 className="text-white font-medium mb-3">FAQ 2</h4>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">Domanda ({activeLang.toUpperCase()})</label>
                        <input
                          type="text"
                          value={formData.faq_2_q?.[activeLang] || ''}
                          onChange={(e) => updateMultiLang('faq_2_q', e.target.value)}
                          className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white text-sm"
                          placeholder="Es: Quando riceverò i biglietti?"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">Risposta ({activeLang.toUpperCase()})</label>
                        <textarea
                          value={formData.faq_2_a?.[activeLang] || ''}
                          onChange={(e) => updateMultiLang('faq_2_a', e.target.value)}
                          className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white text-sm"
                          rows={3}
                          placeholder="Risposta dettagliata..."
                        />
                      </div>
                    </div>
                  </div>

                  {/* FAQ 3 */}
                  <div className="bg-gray-700/30 rounded-lg p-4 border border-gray-600">
                    <h4 className="text-white font-medium mb-3">FAQ 3</h4>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">Domanda ({activeLang.toUpperCase()})</label>
                        <input
                          type="text"
                          value={formData.faq_3_q?.[activeLang] || ''}
                          onChange={(e) => updateMultiLang('faq_3_q', e.target.value)}
                          className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white text-sm"
                          placeholder="Es: Posso cancellare la prenotazione?"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-400 mb-1">Risposta ({activeLang.toUpperCase()})</label>
                        <textarea
                          value={formData.faq_3_a?.[activeLang] || ''}
                          onChange={(e) => updateMultiLang('faq_3_a', e.target.value)}
                          className="w-full bg-gray-600 border border-gray-500 rounded px-3 py-2 text-white text-sm"
                          rows={3}
                          placeholder="Risposta dettagliata..."
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'seo' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Left Column - Fields */}
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">SEO Title ({activeLang.toUpperCase()})</label>
                        <input
                          type="text"
                          value={formData.seo_title[activeLang] || ''}
                          onChange={(e) => updateMultiLang('seo_title', e.target.value)}
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                          placeholder="Biglietti Inter vs Milan - Acquista Online"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">SEO Description ({activeLang.toUpperCase()})</label>
                        <textarea
                          value={formData.seo_description[activeLang] || ''}
                          onChange={(e) => updateMultiLang('seo_description', e.target.value)}
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                          rows={3}
                          placeholder="Acquista i biglietti per Inter vs Milan. Prezzi da €50. Consegna garantita."
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-300 mb-1">URL Slug ({activeLang.toUpperCase()})</label>
                        <input
                          type="text"
                          value={formData.slug[activeLang] || ''}
                          onChange={(e) => updateMultiLang('slug', e.target.value)}
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                          placeholder="inter-vs-milan-serie-a"
                        />
                      </div>
                    </div>

                    {/* Right Column - Previews */}
                    <div className="space-y-6">
                      <GoogleSnippetPreview
                        title={formData.seo_title[activeLang] || formData.title[activeLang] || ''}
                        description={formData.seo_description[activeLang] || ''}
                        url={formData.slug[activeLang] ? `event/${formData.slug[activeLang]}` : ''}
                        lang={activeLang}
                        type="event"
                      />
                      
                      <SocialPreview
                        title={formData.seo_title[activeLang] || formData.title[activeLang] || ''}
                        description={formData.seo_description[activeLang] || ''}
                        image={formData.imageUrl}
                        platform="facebook"
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-4 border-t border-gray-700 flex justify-end gap-3">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
              >
                Annulla
              </button>
              <button
                onClick={handleSave}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                <Save className="w-4 h-4" />
                Salva
              </button>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  );
};

export default AdminEvents;
