import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminLayout from '../../components/admin/AdminLayout';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Loader2, Search, Filter, ChevronDown, ChevronUp, Plus, Trash2, 
  Save, Copy, CheckCircle, XCircle, Edit2, RotateCcw, Layers
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const DEFAULT_SECTORS = [
  { name: "Cat 1 Premium", price: 0, available: true, notes: "" },
  { name: "Cat 1 Normal", price: 0, available: true, notes: "" },
  { name: "Cat 2 Short Side Lower", price: 0, available: true, notes: "" },
  { name: "Cat 2 Long Side Upper", price: 0, available: true, notes: "" },
  { name: "Cat 3 Short Side", price: 0, available: true, notes: "" },
  { name: "Best Available", price: 0, available: true, notes: "" },
];

const AdminSectors = () => {
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all'); // all, with-sectors, without-sectors
  const [expandedEvent, setExpandedEvent] = useState(null);
  const [editingSectors, setEditingSectors] = useState({});
  const [selectedEvents, setSelectedEvents] = useState([]);
  const [bulkMode, setBulkMode] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/admin/sectors/events`);
      const data = await response.json();
      setEvents(data.events || []);
    } catch (error) {
      console.error('Error fetching events:', error);
      toast.error('Errore nel caricamento eventi');
    } finally {
      setLoading(false);
    }
  };

  const handleExpandEvent = (eventId) => {
    if (expandedEvent === eventId) {
      setExpandedEvent(null);
    } else {
      setExpandedEvent(eventId);
      const event = events.find(e => e.id === eventId);
      if (event) {
        setEditingSectors({
          ...editingSectors,
          [eventId]: event.sectors.length > 0 ? [...event.sectors] : [...DEFAULT_SECTORS]
        });
      }
    }
  };

  const handleSectorChange = (eventId, index, field, value) => {
    const updated = [...(editingSectors[eventId] || [])];
    updated[index] = { ...updated[index], [field]: value };
    setEditingSectors({ ...editingSectors, [eventId]: updated });
  };

  const handleAddSector = (eventId) => {
    const updated = [...(editingSectors[eventId] || [])];
    updated.push({ name: "", price: 0, available: true, notes: "" });
    setEditingSectors({ ...editingSectors, [eventId]: updated });
  };

  const handleRemoveSector = (eventId, index) => {
    const updated = [...(editingSectors[eventId] || [])];
    updated.splice(index, 1);
    setEditingSectors({ ...editingSectors, [eventId]: updated });
  };

  const handleResetToDefaults = (eventId) => {
    setEditingSectors({ ...editingSectors, [eventId]: [...DEFAULT_SECTORS] });
    toast.info('Settori resettati ai valori di default');
  };

  const handleSaveSectors = async (eventId) => {
    try {
      setSaving(true);
      const sectors = editingSectors[eventId] || [];
      
      const response = await fetch(`${API_URL}/api/admin/sectors/event/${eventId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sectors })
      });
      
      if (!response.ok) throw new Error('Failed to save');
      
      toast.success('Settori salvati con successo');
      fetchEvents();
    } catch (error) {
      console.error('Error saving sectors:', error);
      toast.error('Errore nel salvataggio');
    } finally {
      setSaving(false);
    }
  };

  const handleBulkAddDefaults = async () => {
    if (selectedEvents.length === 0) {
      toast.warning('Seleziona almeno un evento');
      return;
    }
    
    try {
      setSaving(true);
      const response = await fetch(`${API_URL}/api/admin/sectors/bulk-defaults`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(selectedEvents)
      });
      
      const data = await response.json();
      toast.success(`Settori default aggiunti a ${data.updated_count} eventi`);
      setSelectedEvents([]);
      setBulkMode(false);
      fetchEvents();
    } catch (error) {
      console.error('Error bulk adding defaults:', error);
      toast.error('Errore nell\'operazione bulk');
    } finally {
      setSaving(false);
    }
  };

  const handleSelectAll = () => {
    if (selectedEvents.length === filteredEvents.length) {
      setSelectedEvents([]);
    } else {
      setSelectedEvents(filteredEvents.map(e => e.id));
    }
  };

  const handleToggleSelect = (eventId) => {
    if (selectedEvents.includes(eventId)) {
      setSelectedEvents(selectedEvents.filter(id => id !== eventId));
    } else {
      setSelectedEvents([...selectedEvents, eventId]);
    }
  };

  // Filter events
  const filteredEvents = events.filter(event => {
    const matchesSearch = event.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         event.stadium?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         event.league?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesFilter = filterStatus === 'all' ||
                         (filterStatus === 'with-sectors' && event.has_sectors) ||
                         (filterStatus === 'without-sectors' && !event.has_sectors);
    
    return matchesSearch && matchesFilter;
  });

  const eventsWithSectors = events.filter(e => e.has_sectors).length;
  const eventsWithoutSectors = events.filter(e => !e.has_sectors).length;

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Gestione Settori</h1>
            <p className="text-gray-500 text-sm mt-1">
              Configura i settori e prezzi per ogni evento
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant={bulkMode ? "default" : "outline"}
              onClick={() => {
                setBulkMode(!bulkMode);
                setSelectedEvents([]);
              }}
              className="gap-2"
            >
              <Layers className="w-4 h-4" />
              {bulkMode ? 'Esci da Bulk' : 'Modalità Bulk'}
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="text-2xl font-bold text-gray-900">{events.length}</div>
            <div className="text-sm text-gray-500">Totale Eventi</div>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="text-2xl font-bold text-green-600">{eventsWithSectors}</div>
            <div className="text-sm text-gray-500">Con Settori Configurati</div>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="text-2xl font-bold text-orange-500">{eventsWithoutSectors}</div>
            <div className="text-sm text-gray-500">Senza Settori</div>
          </div>
        </div>

        {/* Bulk Actions */}
        {bulkMode && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <input
                  type="checkbox"
                  checked={selectedEvents.length === filteredEvents.length && filteredEvents.length > 0}
                  onChange={handleSelectAll}
                  className="w-5 h-5 rounded border-gray-300"
                />
                <span className="text-sm font-medium text-blue-800">
                  {selectedEvents.length} eventi selezionati
                </span>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  onClick={handleBulkAddDefaults}
                  disabled={selectedEvents.length === 0 || saving}
                  className="gap-2 bg-blue-600 hover:bg-blue-700"
                >
                  {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                  Aggiungi Settori Default
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <Input
                placeholder="Cerca evento, stadio, lega..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-gray-400" />
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="border border-gray-200 rounded-lg px-3 py-2 text-sm"
              >
                <option value="all">Tutti ({events.length})</option>
                <option value="with-sectors">Con settori ({eventsWithSectors})</option>
                <option value="without-sectors">Senza settori ({eventsWithoutSectors})</option>
              </select>
            </div>
          </div>
        </div>

        {/* Events List */}
        <div className="space-y-3">
          {filteredEvents.map((event) => (
            <div key={event.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
              {/* Event Header */}
              <div 
                className={`p-4 flex items-center gap-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                  expandedEvent === event.id ? 'bg-gray-50 border-b border-gray-200' : ''
                }`}
                onClick={() => !bulkMode && handleExpandEvent(event.id)}
              >
                {bulkMode && (
                  <input
                    type="checkbox"
                    checked={selectedEvents.includes(event.id)}
                    onChange={(e) => {
                      e.stopPropagation();
                      handleToggleSelect(event.id);
                    }}
                    className="w-5 h-5 rounded border-gray-300"
                  />
                )}
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-gray-900 truncate">{event.title}</h3>
                    {event.has_sectors ? (
                      <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded-full flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" />
                        {event.sectors.length} settori
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 bg-orange-100 text-orange-700 text-xs font-medium rounded-full flex items-center gap-1">
                        <XCircle className="w-3 h-3" />
                        Nessun settore
                      </span>
                    )}
                  </div>
                  <div className="text-sm text-gray-500 mt-1">
                    {event.date} • {event.stadium} • {event.location}
                    {event.price_range?.min > 0 && (
                      <span className="ml-2 text-green-600 font-medium">
                        €{event.price_range.min} - €{event.price_range.max}
                      </span>
                    )}
                  </div>
                </div>
                
                {!bulkMode && (
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                      {event.league}
                    </span>
                    {expandedEvent === event.id ? (
                      <ChevronUp className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                )}
              </div>

              {/* Expanded Sectors Editor */}
              {expandedEvent === event.id && !bulkMode && (
                <div className="p-4 bg-gray-50">
                  {/* Toolbar */}
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium text-gray-700">Configura Settori</h4>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleResetToDefaults(event.id)}
                        className="gap-1 text-xs"
                      >
                        <RotateCcw className="w-3 h-3" />
                        Reset Default
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleAddSector(event.id)}
                        className="gap-1 text-xs"
                      >
                        <Plus className="w-3 h-3" />
                        Aggiungi
                      </Button>
                    </div>
                  </div>

                  {/* Sectors Grid */}
                  <div className="space-y-2">
                    {(editingSectors[event.id] || []).map((sector, index) => (
                      <div key={index} className="flex items-center gap-3 bg-white p-3 rounded-lg border border-gray-200">
                        <div className="flex-1">
                          <Input
                            value={sector.name}
                            onChange={(e) => handleSectorChange(event.id, index, 'name', e.target.value)}
                            placeholder="Nome settore"
                            className="text-sm"
                          />
                        </div>
                        <div className="w-28">
                          <div className="relative">
                            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">€</span>
                            <Input
                              type="number"
                              value={sector.price}
                              onChange={(e) => handleSectorChange(event.id, index, 'price', parseFloat(e.target.value) || 0)}
                              className="pl-7 text-sm"
                              placeholder="Prezzo"
                            />
                          </div>
                        </div>
                        <div className="w-24">
                          <select
                            value={sector.available ? 'available' : 'unavailable'}
                            onChange={(e) => handleSectorChange(event.id, index, 'available', e.target.value === 'available')}
                            className="w-full border border-gray-200 rounded-md px-2 py-2 text-sm"
                          >
                            <option value="available">Disponibile</option>
                            <option value="unavailable">Esaurito</option>
                          </select>
                        </div>
                        <div className="flex-1">
                          <Input
                            value={sector.notes || ''}
                            onChange={(e) => handleSectorChange(event.id, index, 'notes', e.target.value)}
                            placeholder="Note (opzionale)"
                            className="text-sm"
                          />
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveSector(event.id, index)}
                          className="text-red-500 hover:text-red-700 hover:bg-red-50"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>

                  {/* Save Button */}
                  <div className="flex justify-end mt-4">
                    <Button
                      onClick={() => handleSaveSectors(event.id)}
                      disabled={saving}
                      className="gap-2 bg-green-600 hover:bg-green-700"
                    >
                      {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                      Salva Settori
                    </Button>
                  </div>
                </div>
              )}
            </div>
          ))}

          {filteredEvents.length === 0 && (
            <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
              <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">Nessun evento trovato</p>
            </div>
          )}
        </div>
      </div>
    </AdminLayout>
  );
};

export default AdminSectors;
