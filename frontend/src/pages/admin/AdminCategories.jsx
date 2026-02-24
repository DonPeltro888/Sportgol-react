import React, { useState, useEffect } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { Plus, Pencil, Trash2, GripVertical, X, Save, ChevronUp, ChevronDown } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminCategories = () => {
  const { authFetch } = useAdminAuth();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [activeLang, setActiveLang] = useState('it');

  const defaultCategory = {
    name: { it: '', es: '', en: '' },
    slug: '',
    type: 'league',
    icon: '',
    country: '',
    flag: '',
    order: 0,
    visible_home: true,
    teams: []
  };

  const [formData, setFormData] = useState(defaultCategory);

  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    setLoading(true);
    try {
      const response = await authFetch(`${API_URL}/api/admin/menu-categories`);
      const data = await response.json();
      setCategories(data || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingCategory(null);
    setFormData({...defaultCategory, order: categories.length});
    setShowModal(true);
  };

  const handleEdit = (category) => {
    setEditingCategory(category);
    setFormData({
      name: typeof category.name === 'object' ? category.name : { it: category.name || '', es: '', en: '' },
      slug: category.slug || '',
      type: category.type || 'league',
      icon: category.icon || '',
      country: category.country || '',
      flag: category.flag || '',
      order: category.order || 0,
      visible_home: category.visible_home !== false,
      teams: category.teams || []
    });
    setShowModal(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Sei sicuro di voler eliminare questa categoria?')) return;
    
    try {
      await authFetch(`${API_URL}/api/admin/menu-categories/${id}`, { method: 'DELETE' });
      fetchCategories();
    } catch (error) {
      console.error('Error deleting category:', error);
    }
  };

  const handleSave = async () => {
    try {
      const method = editingCategory ? 'PUT' : 'POST';
      const url = editingCategory 
        ? `${API_URL}/api/admin/menu-categories/${editingCategory.id}`
        : `${API_URL}/api/admin/menu-categories`;
      
      await authFetch(url, {
        method,
        body: JSON.stringify(formData)
      });
      
      setShowModal(false);
      fetchCategories();
    } catch (error) {
      console.error('Error saving category:', error);
    }
  };

  const updateOrder = async (id, direction) => {
    const index = categories.findIndex(c => c.id === id);
    if ((direction === 'up' && index === 0) || (direction === 'down' && index === categories.length - 1)) return;

    const newIndex = direction === 'up' ? index - 1 : index + 1;
    const newCategories = [...categories];
    [newCategories[index], newCategories[newIndex]] = [newCategories[newIndex], newCategories[index]];

    // Update orders
    for (let i = 0; i < newCategories.length; i++) {
      await authFetch(`${API_URL}/api/admin/menu-categories/${newCategories[i].id}`, {
        method: 'PUT',
        body: JSON.stringify({ order: i })
      });
    }
    
    fetchCategories();
  };

  const getDisplayName = (category) => {
    if (typeof category.name === 'object') {
      return category.name.it || category.name.en || '-';
    }
    return category.name || '-';
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white">Categorie Menu</h1>
            <p className="text-gray-400">Gestisci i campionati, coppe e squadre nel menu</p>
          </div>
          <button
            onClick={handleCreate}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-5 h-5" />
            Nuova Categoria
          </button>
        </div>

        {/* Categories List */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-400">Caricamento...</div>
          ) : categories.length === 0 ? (
            <div className="p-8 text-center text-gray-400">Nessuna categoria. Crea la prima!</div>
          ) : (
            <div className="divide-y divide-gray-700">
              {categories.map((category, index) => (
                <div key={category.id} className="flex items-center gap-4 px-4 py-3 hover:bg-gray-700/30">
                  {/* Order Controls */}
                  <div className="flex flex-col gap-1">
                    <button 
                      onClick={() => updateOrder(category.id, 'up')}
                      disabled={index === 0}
                      className="text-gray-400 hover:text-white disabled:opacity-30"
                    >
                      <ChevronUp className="w-4 h-4" />
                    </button>
                    <button 
                      onClick={() => updateOrder(category.id, 'down')}
                      disabled={index === categories.length - 1}
                      className="text-gray-400 hover:text-white disabled:opacity-30"
                    >
                      <ChevronDown className="w-4 h-4" />
                    </button>
                  </div>

                  {/* Flag/Icon */}
                  <div className="w-10 h-10 bg-gray-700 rounded-lg flex items-center justify-center text-xl">
                    {category.flag || '🏆'}
                  </div>

                  {/* Info */}
                  <div className="flex-1">
                    <p className="text-white font-medium">{getDisplayName(category)}</p>
                    <p className="text-gray-400 text-sm">
                      {category.type === 'cup' ? 'Coppa' : 'Campionato'} • {category.teams?.length || 0} squadre
                    </p>
                  </div>

                  {/* Visibility */}
                  <div>
                    {category.visible_home ? (
                      <span className="px-2 py-1 bg-green-600/20 text-green-400 rounded text-xs">Visibile</span>
                    ) : (
                      <span className="px-2 py-1 bg-gray-600/20 text-gray-400 rounded text-xs">Nascosto</span>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleEdit(category)}
                      className="p-2 text-gray-400 hover:text-blue-400 transition-colors"
                    >
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(category.id)}
                      className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">
                {editingCategory ? 'Modifica Categoria' : 'Nuova Categoria'}
              </h2>
              <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-6 h-6" />
              </button>
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

            {/* Modal Body */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Nome ({activeLang.toUpperCase()})</label>
                <input
                  type="text"
                  value={formData.name[activeLang] || ''}
                  onChange={(e) => setFormData({...formData, name: {...formData.name, [activeLang]: e.target.value}})}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                  placeholder="Serie A"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Slug URL</label>
                  <input
                    type="text"
                    value={formData.slug}
                    onChange={(e) => setFormData({...formData, slug: e.target.value})}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    placeholder="serie-a"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Tipo</label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({...formData, type: e.target.value})}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                  >
                    <option value="league">Campionato</option>
                    <option value="cup">Coppa</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Paese</label>
                  <input
                    type="text"
                    value={formData.country}
                    onChange={(e) => setFormData({...formData, country: e.target.value})}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    placeholder="Italy"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1">Bandiera (emoji)</label>
                  <input
                    type="text"
                    value={formData.flag}
                    onChange={(e) => setFormData({...formData, flag: e.target.value})}
                    className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    placeholder="🇮🇹"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Squadre (una per riga)</label>
                <textarea
                  value={formData.teams.join('\n')}
                  onChange={(e) => setFormData({...formData, teams: e.target.value.split('\n').map(s => s.trim()).filter(Boolean)})}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                  rows={6}
                  placeholder="Inter&#10;Milan&#10;Juventus&#10;..."
                />
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="visible_home"
                  checked={formData.visible_home}
                  onChange={(e) => setFormData({...formData, visible_home: e.target.checked})}
                  className="w-4 h-4 rounded bg-gray-700 border-gray-600"
                />
                <label htmlFor="visible_home" className="text-gray-300">Visibile nel menu principale</label>
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

export default AdminCategories;
