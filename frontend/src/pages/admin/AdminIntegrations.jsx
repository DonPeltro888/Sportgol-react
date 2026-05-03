import React, { useState, useEffect } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { Key, CheckCircle2, XCircle, Loader2, Trash2, ExternalLink, Info } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminIntegrations = () => {
  const { authFetch } = useAdminAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [config, setConfig] = useState({
    provider: 'api_football',
    api_key: '',
    enabled: true,
  });
  const [currentStatus, setCurrentStatus] = useState({
    api_key_masked: '',
    api_key_set: false,
    enabled: false,
    last_test: null,
    last_test_result: null,
  });

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await authFetch(`${API_URL}/api/admin/integrations`);
      if (!response.ok) throw new Error('Fetch failed');
      const data = await response.json();
      const fa = data.football_api || {};
      setCurrentStatus(fa);
      setConfig((prev) => ({
        ...prev,
        provider: fa.provider || 'api_football',
        enabled: fa.enabled ?? true,
      }));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!config.api_key || config.api_key.trim().length < 10) {
      alert('Inserisci una API key valida (minimo 10 caratteri).');
      return;
    }
    setSaving(true);
    try {
      const response = await authFetch(`${API_URL}/api/admin/integrations/football-api`, {
        method: 'PUT',
        body: JSON.stringify(config),
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Save failed');
      }
      alert('✅ Configurazione salvata correttamente');
      setConfig((prev) => ({ ...prev, api_key: '' })); // clear form
      fetchStatus();
    } catch (err) {
      alert('❌ Errore: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    try {
      const response = await authFetch(`${API_URL}/api/admin/integrations/football-api/test`, {
        method: 'POST',
      });
      const data = await response.json();
      if (data.ok) {
        alert(`✅ Connessione riuscita!\n\nProvider: ${data.provider}\n${data.account_email ? 'Account: ' + data.account_email + '\n' : ''}${data.requests_today ? 'Richieste oggi: ' + data.requests_today + '\n' : ''}${data.plan ? 'Piano: ' + data.plan : ''}${data.sample_competition ? 'Test endpoint: ' + data.sample_competition : ''}${data.note ? '\n\n' + data.note : ''}`);
      } else {
        alert('❌ Test fallito:\n\n' + (data.error || 'Errore sconosciuto'));
      }
      fetchStatus();
    } catch (err) {
      alert('❌ Errore durante il test: ' + err.message);
    } finally {
      setTesting(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Sei sicuro di voler rimuovere la API key? Il sync con questo provider verrà disabilitato.')) return;
    try {
      await authFetch(`${API_URL}/api/admin/integrations/football-api`, { method: 'DELETE' });
      alert('✅ API key rimossa');
      fetchStatus();
    } catch (err) {
      alert('Errore: ' + err.message);
    }
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-96">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="p-6 max-w-4xl" data-testid="admin-integrations">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
            <Key className="w-8 h-8 text-blue-500" />
            Integrazioni API
          </h1>
          <p className="text-gray-400">
            Configura le integrazioni con provider esterni per il sync automatico degli eventi.
          </p>
        </div>

        {/* Football API Card */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-white mb-1">⚽ Football API</h2>
              <p className="text-sm text-gray-400">
                Usata come fallback o sorgente primaria per sincronizzare coppe mancanti (Europa League, Conference League, Coppa del Rey, ecc.).
              </p>
            </div>
            {currentStatus.api_key_set ? (
              <span className="px-3 py-1 bg-green-900/30 text-green-400 rounded-full text-sm flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4" /> Attiva
              </span>
            ) : (
              <span className="px-3 py-1 bg-gray-900/30 text-gray-400 rounded-full text-sm flex items-center gap-2">
                <XCircle className="w-4 h-4" /> Non configurata
              </span>
            )}
          </div>

          {/* Provider selector */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">Provider</label>
            <select
              data-testid="integration-provider-select"
              value={config.provider}
              onChange={(e) => setConfig({ ...config, provider: e.target.value })}
              className="w-full bg-gray-900 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-blue-500 focus:outline-none"
            >
              <option value="api_football">API-Football (RapidAPI) - 100 req/giorno gratis</option>
              <option value="football_data">Football-Data.org - 100 req/giorno, no carta richiesta</option>
            </select>
          </div>

          {/* API key input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              API Key
              {currentStatus.api_key_set && (
                <span className="ml-2 text-xs text-gray-500">
                  (attuale: {currentStatus.api_key_masked})
                </span>
              )}
            </label>
            <input
              data-testid="integration-api-key-input"
              type="password"
              placeholder={currentStatus.api_key_set ? 'Lascia vuoto per mantenere quella attuale' : 'Incolla qui la tua API key'}
              value={config.api_key}
              onChange={(e) => setConfig({ ...config, api_key: e.target.value })}
              className="w-full bg-gray-900 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-blue-500 focus:outline-none font-mono text-sm"
              autoComplete="off"
            />
            <p className="text-xs text-gray-500 mt-2">
              La chiave viene salvata in modo sicuro nel database. Non viene mai esposta al frontend (solo mascherata).
            </p>
          </div>

          {/* Enabled toggle */}
          <div className="mb-6">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                data-testid="integration-enabled-toggle"
                type="checkbox"
                checked={config.enabled}
                onChange={(e) => setConfig({ ...config, enabled: e.target.checked })}
                className="w-5 h-5 rounded bg-gray-900 border-gray-700 text-blue-500 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-300">
                Abilita questo provider per il sync automatico
              </span>
            </label>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            <button
              data-testid="integration-save-btn"
              onClick={handleSave}
              disabled={saving}
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition flex items-center gap-2"
            >
              {saving && <Loader2 className="w-4 h-4 animate-spin" />}
              💾 Salva configurazione
            </button>
            <button
              data-testid="integration-test-btn"
              onClick={handleTest}
              disabled={testing || !currentStatus.api_key_set}
              className="px-5 py-2.5 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition flex items-center gap-2"
            >
              {testing && <Loader2 className="w-4 h-4 animate-spin" />}
              🔗 Testa connessione
            </button>
            {currentStatus.api_key_set && (
              <button
                data-testid="integration-delete-btn"
                onClick={handleDelete}
                className="px-5 py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition flex items-center gap-2"
              >
                <Trash2 className="w-4 h-4" /> Rimuovi key
              </button>
            )}
          </div>

          {/* Last test result */}
          {currentStatus.last_test && (
            <div className="mt-6 p-4 bg-gray-900 rounded-lg border border-gray-700">
              <div className="flex items-center gap-2 mb-2">
                <Info className="w-4 h-4 text-blue-400" />
                <span className="text-sm font-medium text-gray-300">Ultimo test</span>
                <span className="text-xs text-gray-500">{new Date(currentStatus.last_test).toLocaleString('it-IT')}</span>
              </div>
              <pre className="text-xs text-gray-400 whitespace-pre-wrap overflow-x-auto">
                {JSON.stringify(currentStatus.last_test_result, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Info box */}
        <div className="bg-blue-900/20 border border-blue-800 rounded-xl p-5">
          <h3 className="text-blue-400 font-bold mb-3 flex items-center gap-2">
            <Info className="w-5 h-5" /> Come ottenere una API key
          </h3>
          <div className="text-sm text-gray-300 space-y-3">
            <div>
              <strong className="text-white">🎯 API-Football (RapidAPI)</strong> - consigliato per copertura completa
              <ol className="list-decimal list-inside mt-2 space-y-1 text-gray-400 ml-2">
                <li>Vai su <a href="https://rapidapi.com/api-sports/api/api-football" target="_blank" rel="noreferrer" className="text-blue-400 hover:underline inline-flex items-center gap-1">rapidapi.com/api-sports/api-football <ExternalLink className="w-3 h-3" /></a></li>
                <li>Sign up gratis (o login)</li>
                <li>Subscribe al piano <strong>Basic (FREE - 100 req/day)</strong></li>
                <li>Tab "Endpoints" → copia <code className="bg-gray-800 px-1 rounded">X-RapidAPI-Key</code></li>
                <li>Incollala qui sopra e salva</li>
              </ol>
            </div>
            <div className="pt-3 border-t border-gray-800">
              <strong className="text-white">🌟 Football-Data.org</strong> - alternativa senza carta richiesta
              <ol className="list-decimal list-inside mt-2 space-y-1 text-gray-400 ml-2">
                <li>Vai su <a href="https://www.football-data.org/client/register" target="_blank" rel="noreferrer" className="text-blue-400 hover:underline inline-flex items-center gap-1">football-data.org/client/register <ExternalLink className="w-3 h-3" /></a></li>
                <li>Registrati solo con email (niente carta)</li>
                <li>Ti arriva la key via email</li>
                <li>Copertura: 12 competizioni top (UCL, UEL, Serie A, Premier, La Liga, Bundesliga, ...)</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
};

export default AdminIntegrations;
