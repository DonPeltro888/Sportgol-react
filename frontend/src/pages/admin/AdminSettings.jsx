import React, { useState, useEffect } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { Save, Globe, Mail, Phone, MapPin, Share2 } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminSettings = () => {
  const { authFetch } = useAdminAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeLang, setActiveLang] = useState('it');

  const [settings, setSettings] = useState({
    logo_url: '',
    site_name: { it: '', es: '', en: '' },
    site_description: { it: '', es: '', en: '' },
    contact_email: '',
    phone: '',
    address: { it: '', es: '', en: '' },
    social_facebook: '',
    social_instagram: '',
    social_twitter: '',
    footer_text: { it: '', es: '', en: '' }
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await authFetch(`${API_URL}/api/admin/settings`);
      const data = await response.json();
      setSettings(prev => ({...prev, ...data}));
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await authFetch(`${API_URL}/api/admin/settings`, {
        method: 'PUT',
        body: JSON.stringify(settings)
      });
      alert('Impostazioni salvate!');
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Errore nel salvataggio');
    } finally {
      setSaving(false);
    }
  };

  const updateMultiLang = (field, value) => {
    setSettings(prev => ({
      ...prev,
      [field]: { ...prev[field], [activeLang]: value }
    }));
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6 max-w-4xl">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">Impostazioni Sito</h1>
            <p className="text-gray-400">Configura le informazioni generali del sito</p>
          </div>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            <Save className="w-5 h-5" />
            {saving ? 'Salvataggio...' : 'Salva Tutto'}
          </button>
        </div>

        {/* Language Tabs */}
        <div className="flex gap-2">
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

        {/* Branding */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Globe className="w-5 h-5 text-blue-400" />
            Branding
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">URL Logo</label>
              <input
                type="text"
                value={settings.logo_url}
                onChange={(e) => setSettings({...settings, logo_url: e.target.value})}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                placeholder="https://..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Nome Sito ({activeLang.toUpperCase()})</label>
              <input
                type="text"
                value={settings.site_name[activeLang] || ''}
                onChange={(e) => updateMultiLang('site_name', e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                placeholder="GOLEVENTS"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Descrizione Sito ({activeLang.toUpperCase()})</label>
              <textarea
                value={settings.site_description[activeLang] || ''}
                onChange={(e) => updateMultiLang('site_description', e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                rows={2}
                placeholder="La tua piattaforma per biglietti sportivi..."
              />
            </div>
          </div>
        </div>

        {/* Contact Info */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Mail className="w-5 h-5 text-green-400" />
            Informazioni di Contatto
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="email"
                  value={settings.contact_email}
                  onChange={(e) => setSettings({...settings, contact_email: e.target.value})}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-white"
                  placeholder="info@golevents.com"
                />
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Telefono</label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={settings.phone}
                  onChange={(e) => setSettings({...settings, phone: e.target.value})}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-white"
                  placeholder="+39 02 1234567"
                />
              </div>
            </div>
          </div>
          
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-300 mb-1">Indirizzo ({activeLang.toUpperCase()})</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
              <textarea
                value={settings.address[activeLang] || ''}
                onChange={(e) => updateMultiLang('address', e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-white"
                rows={2}
                placeholder="Via Roma 123, Milano, Italia"
              />
            </div>
          </div>
        </div>

        {/* Social Media */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Share2 className="w-5 h-5 text-purple-400" />
            Social Media
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Facebook</label>
              <input
                type="text"
                value={settings.social_facebook}
                onChange={(e) => setSettings({...settings, social_facebook: e.target.value})}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                placeholder="https://facebook.com/..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Instagram</label>
              <input
                type="text"
                value={settings.social_instagram}
                onChange={(e) => setSettings({...settings, social_instagram: e.target.value})}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                placeholder="https://instagram.com/..."
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Twitter/X</label>
              <input
                type="text"
                value={settings.social_twitter}
                onChange={(e) => setSettings({...settings, social_twitter: e.target.value})}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                placeholder="https://twitter.com/..."
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Footer</h2>
          
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Testo Footer ({activeLang.toUpperCase()})</label>
            <textarea
              value={settings.footer_text[activeLang] || ''}
              onChange={(e) => updateMultiLang('footer_text', e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
              rows={3}
              placeholder="© 2024 GOLEVENTS. Tutti i diritti riservati."
            />
          </div>
        </div>
      </div>
    </AdminLayout>
  );
};

export default AdminSettings;
