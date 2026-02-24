import React, { useState, useEffect } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { Plus, Pencil, Trash2, Search, X, Save, Filter } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminTranslations = () => {
  const { authFetch } = useAdminAuth();
  const [translations, setTranslations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingKey, setEditingKey] = useState(null);

  const categories = ['general', 'menu', 'buttons', 'messages', 'labels', 'errors', 'pages'];

  const defaultTranslation = {
    key: '',
    it: '',
    es: '',
    en: '',
    category: 'general'
  };

  const [formData, setFormData] = useState(defaultTranslation);

  useEffect(() => {
    fetchTranslations();
  }, [categoryFilter]);

  const fetchTranslations = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (categoryFilter) params.append('category', categoryFilter);
      
      const response = await authFetch(`${API_URL}/api/admin/translations?${params}`);
      const data = await response.json();
      setTranslations(data || []);
    } catch (error) {
      console.error('Error fetching translations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingKey(null);
    setFormData(defaultTranslation);
    setShowModal(true);
  };

  const handleEdit = (translation) => {
    setEditingKey(translation.key);
    setFormData({
      key: translation.key,
      it: translation.it || '',
      es: translation.es || '',
      en: translation.en || '',
      category: translation.category || 'general'
    });
    setShowModal(true);
  };

  const handleDelete = async (key) => {
    if (!window.confirm('Sei sicuro di voler eliminare questa traduzione?')) return;
    
    try {
      await authFetch(`${API_URL}/api/admin/translations/${encodeURIComponent(key)}`, { method: 'DELETE' });
      fetchTranslations();
    } catch (error) {
      console.error('Error deleting translation:', error);
    }
  };

  const handleSave = async () => {
    try {
      const method = editingKey ? 'PUT' : 'POST';
      const url = editingKey 
        ? `${API_URL}/api/admin/translations/${encodeURIComponent(editingKey)}`
        : `${API_URL}/api/admin/translations`;
      
      await authFetch(url, {
        method,
        body: JSON.stringify(formData)
      });
      
      setShowModal(false);
      fetchTranslations();
    } catch (error) {
      console.error('Error saving translation:', error);
      alert('Errore: la chiave potrebbe già esistere');
    }
  };

  const filteredTranslations = translations.filter(t => 
    !search || 
    t.key.toLowerCase().includes(search.toLowerCase()) ||
    t.it?.toLowerCase().includes(search.toLowerCase()) ||
    t.es?.toLowerCase().includes(search.toLowerCase()) ||
    t.en?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white">Traduzioni</h1>
            <p className="text-gray-400">Gestisci i testi multilingua (IT, ES, EN)</p>
          </div>
          <button
            onClick={handleCreate}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            Nuova Traduzione
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Cerca per chiave o testo..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Tutte le categorie</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        {/* Translations Table */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-900/50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Chiave</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">IT 🇮🇹</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">ES 🇪🇸</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">EN 🇬🇧</th>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Categoria</th>
                  <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase">Azioni</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-gray-400">
                      Caricamento...
                    </td>
                  </tr>
                ) : filteredTranslations.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-gray-400">
                      Nessuna traduzione trovata
                    </td>
                  </tr>
                ) : filteredTranslations.map((t) => (
                  <tr key={t.key} className="hover:bg-gray-700/30">
                    <td className="px-4 py-3">
                      <code className="text-blue-400 text-sm bg-blue-900/30 px-2 py-1 rounded">{t.key}</code>
                    </td>
                    <td className="px-4 py-3 text-gray-300 text-sm max-w-[200px] truncate">{t.it || '-'}</td>
                    <td className="px-4 py-3 text-gray-300 text-sm max-w-[200px] truncate">{t.es || '-'}</td>
                    <td className="px-4 py-3 text-gray-300 text-sm max-w-[200px] truncate">{t.en || '-'}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-1 bg-purple-600/20 text-purple-400 rounded text-xs">
                        {t.category}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleEdit(t)}
                          className="p-2 text-gray-400 hover:text-blue-400 transition-colors"
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(t.key)}
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
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">
                {editingKey ? 'Modifica Traduzione' : 'Nuova Traduzione'}
              </h2>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Chiave</label>
                  <input
                    type="text"
                    value={formData.key}
                    onChange={(e) => setFormData({...formData, key: e.target.value})}
                    disabled={!!editingKey}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white disabled:opacity-50"
                    placeholder="hero.title"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Categoria</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({...formData, category: e.target.value})}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                  >
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Italiano 🇮🇹</label>
                <textarea
                  value={formData.it}
                  onChange={(e) => setFormData({...formData, it: e.target.value})}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                  rows={2}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Spagnolo 🇪🇸</label>
                <textarea
                  value={formData.es}
                  onChange={(e) => setFormData({...formData, es: e.target.value})}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                  rows={2}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Inglese 🇬🇧</label>
                <textarea
                  value={formData.en}
                  onChange={(e) => setFormData({...formData, en: e.target.value})}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                  rows={2}
                />
              </div>
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

export default AdminTranslations;
