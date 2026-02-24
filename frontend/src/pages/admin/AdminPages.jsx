import React, { useState, useEffect } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { Plus, Pencil, Trash2, Search, X, Save, Globe, FileText } from 'lucide-react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import GoogleSnippetPreview, { SocialPreview } from '../../components/admin/GoogleSnippetPreview';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminPages = () => {
  const { authFetch } = useAdminAuth();
  const [content, setContent] = useState([]);
  const [seoSettings, setSeoSettings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('content');
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [modalType, setModalType] = useState('content'); // 'content' or 'seo'
  const [activeLang, setActiveLang] = useState('it');

  const pageKeys = ['home', 'about', 'contact', 'event_detail', 'team', 'league', 'faq'];

  const defaultContent = {
    page_key: 'home',
    section_key: '',
    content: { it: '', es: '', en: '' },
    content_type: 'html'
  };

  const defaultSeo = {
    page_key: 'home',
    title: { it: '', es: '', en: '' },
    description: { it: '', es: '', en: '' },
    keywords: { it: '', es: '', en: '' },
    og_image: '',
    canonical_url: ''
  };

  const [formData, setFormData] = useState(defaultContent);

  useEffect(() => {
    fetchContent();
    fetchSeo();
  }, []);

  const fetchContent = async () => {
    try {
      const response = await authFetch(`${API_URL}/api/admin/page-content`);
      const data = await response.json();
      setContent(data || []);
    } catch (error) {
      console.error('Error fetching content:', error);
    }
  };

  const fetchSeo = async () => {
    try {
      const response = await authFetch(`${API_URL}/api/admin/seo`);
      const data = await response.json();
      setSeoSettings(data || []);
    } catch (error) {
      console.error('Error fetching SEO:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateContent = () => {
    setEditingItem(null);
    setModalType('content');
    setFormData(defaultContent);
    setShowModal(true);
  };

  const handleCreateSeo = () => {
    setEditingItem(null);
    setModalType('seo');
    setFormData(defaultSeo);
    setShowModal(true);
  };

  const handleEditContent = (item) => {
    setEditingItem(item);
    setModalType('content');
    setFormData({
      page_key: item.page_key,
      section_key: item.section_key,
      content: typeof item.content === 'object' ? item.content : { it: item.content || '', es: '', en: '' },
      content_type: item.content_type || 'html'
    });
    setShowModal(true);
  };

  const handleEditSeo = (item) => {
    setEditingItem(item);
    setModalType('seo');
    setFormData({
      page_key: item.page_key,
      title: typeof item.title === 'object' ? item.title : { it: item.title || '', es: '', en: '' },
      description: typeof item.description === 'object' ? item.description : { it: item.description || '', es: '', en: '' },
      keywords: typeof item.keywords === 'object' ? item.keywords : { it: item.keywords || '', es: '', en: '' },
      og_image: item.og_image || '',
      canonical_url: item.canonical_url || ''
    });
    setShowModal(true);
  };

  const handleDeleteContent = async (id) => {
    if (!window.confirm('Sei sicuro?')) return;
    try {
      await authFetch(`${API_URL}/api/admin/page-content/${id}`, { method: 'DELETE' });
      fetchContent();
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleSave = async () => {
    try {
      if (modalType === 'content') {
        const method = editingItem ? 'PUT' : 'POST';
        const url = editingItem 
          ? `${API_URL}/api/admin/page-content/${editingItem.id}`
          : `${API_URL}/api/admin/page-content`;
        
        await authFetch(url, { method, body: JSON.stringify(formData) });
        fetchContent();
      } else {
        const method = editingItem ? 'PUT' : 'POST';
        const url = editingItem 
          ? `${API_URL}/api/admin/seo/${formData.page_key}`
          : `${API_URL}/api/admin/seo`;
        
        await authFetch(url, { method, body: JSON.stringify(formData) });
        fetchSeo();
      }
      setShowModal(false);
    } catch (error) {
      console.error('Error:', error);
      alert('Errore nel salvataggio');
    }
  };

  const updateMultiLang = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: { ...prev[field], [activeLang]: value }
    }));
  };

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-white">Pagine & Testi</h1>
          <p className="text-gray-400">Gestisci i contenuti delle pagine e le impostazioni SEO</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 border-b border-gray-700 pb-2">
          <button
            onClick={() => setActiveTab('content')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'content' 
                ? 'bg-blue-600 text-white' 
                : 'text-gray-400 hover:text-white hover:bg-gray-700'
            }`}
          >
            <FileText className="w-4 h-4" />
            Contenuti Pagine
          </button>
          <button
            onClick={() => setActiveTab('seo')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'seo' 
                ? 'bg-blue-600 text-white' 
                : 'text-gray-400 hover:text-white hover:bg-gray-700'
            }`}
          >
            <Globe className="w-4 h-4" />
            Impostazioni SEO
          </button>
        </div>

        {/* Content Tab */}
        {activeTab === 'content' && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                onClick={handleCreateContent}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Plus className="w-5 h-5" />
                Nuovo Contenuto
              </button>
            </div>

            <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-900/50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Pagina</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Sezione</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Tipo</th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Anteprima IT</th>
                    <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase">Azioni</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {loading ? (
                    <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">Caricamento...</td></tr>
                  ) : content.length === 0 ? (
                    <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">Nessun contenuto</td></tr>
                  ) : content.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-700/30">
                      <td className="px-4 py-3">
                        <span className="px-2 py-1 bg-blue-600/20 text-blue-400 rounded text-xs">{item.page_key}</span>
                      </td>
                      <td className="px-4 py-3 text-gray-300">{item.section_key}</td>
                      <td className="px-4 py-3 text-gray-400 text-sm">{item.content_type}</td>
                      <td className="px-4 py-3 text-gray-300 text-sm max-w-[200px] truncate">
                        {typeof item.content === 'object' ? item.content.it?.substring(0, 50) : item.content?.substring(0, 50)}...
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-2">
                          <button onClick={() => handleEditContent(item)} className="p-2 text-gray-400 hover:text-blue-400">
                            <Pencil className="w-4 h-4" />
                          </button>
                          <button onClick={() => handleDeleteContent(item.id)} className="p-2 text-gray-400 hover:text-red-400">
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
        )}

        {/* SEO Tab */}
        {activeTab === 'seo' && (
          <div className="space-y-4">
            <div className="flex justify-end">
              <button
                onClick={handleCreateSeo}
                className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Plus className="w-5 h-5" />
                Nuova Pagina SEO
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {seoSettings.map((seo) => (
                <div key={seo.id} className="bg-gray-800 rounded-xl border border-gray-700 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="px-2 py-1 bg-purple-600/20 text-purple-400 rounded text-sm font-medium">
                      {seo.page_key}
                    </span>
                    <button onClick={() => handleEditSeo(seo)} className="text-gray-400 hover:text-blue-400">
                      <Pencil className="w-4 h-4" />
                    </button>
                  </div>
                  <h3 className="text-white font-medium mb-1 truncate">
                    {typeof seo.title === 'object' ? seo.title.it : seo.title || 'Nessun titolo'}
                  </h3>
                  <p className="text-gray-400 text-sm line-clamp-2">
                    {typeof seo.description === 'object' ? seo.description.it : seo.description || 'Nessuna descrizione'}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
              <h2 className="text-xl font-bold text-white">
                {modalType === 'content' ? 'Contenuto Pagina' : 'Impostazioni SEO'}
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
                  className={`px-4 py-2 rounded-lg text-sm font-medium ${
                    activeLang === lang ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
                  }`}
                >
                  {lang.toUpperCase()}
                </button>
              ))}
            </div>

            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {modalType === 'content' ? (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-1">Pagina</label>
                      <select
                        value={formData.page_key}
                        onChange={(e) => setFormData({...formData, page_key: e.target.value})}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      >
                        {pageKeys.map(key => <option key={key} value={key}>{key}</option>)}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-1">Sezione</label>
                      <input
                        type="text"
                        value={formData.section_key}
                        onChange={(e) => setFormData({...formData, section_key: e.target.value})}
                        className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        placeholder="hero_title, faq_1, about_text..."
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Contenuto ({activeLang.toUpperCase()})</label>
                    <div className="bg-white rounded-lg">
                      <ReactQuill
                        theme="snow"
                        value={formData.content[activeLang] || ''}
                        onChange={(value) => updateMultiLang('content', value)}
                        className="text-black"
                        style={{ minHeight: '200px' }}
                      />
                    </div>
                  </div>
                </>
              ) : (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Pagina</label>
                    <select
                      value={formData.page_key}
                      onChange={(e) => setFormData({...formData, page_key: e.target.value})}
                      disabled={!!editingItem}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white disabled:opacity-50"
                    >
                      {pageKeys.map(key => <option key={key} value={key}>{key}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Title ({activeLang.toUpperCase()})</label>
                    <input
                      type="text"
                      value={formData.title[activeLang] || ''}
                      onChange={(e) => updateMultiLang('title', e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Description ({activeLang.toUpperCase()})</label>
                    <textarea
                      value={formData.description[activeLang] || ''}
                      onChange={(e) => updateMultiLang('description', e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      rows={3}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">Keywords ({activeLang.toUpperCase()})</label>
                    <input
                      type="text"
                      value={formData.keywords[activeLang] || ''}
                      onChange={(e) => updateMultiLang('keywords', e.target.value)}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                      placeholder="biglietti, calcio, serie a..."
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">OG Image URL</label>
                    <input
                      type="text"
                      value={formData.og_image}
                      onChange={(e) => setFormData({...formData, og_image: e.target.value})}
                      className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                    />
                  </div>
                </>
              )}
            </div>

            <div className="px-6 py-4 border-t border-gray-700 flex justify-end gap-3">
              <button onClick={() => setShowModal(false)} className="px-4 py-2 bg-gray-700 text-white rounded-lg">
                Annulla
              </button>
              <button onClick={handleSave} className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg">
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

export default AdminPages;
