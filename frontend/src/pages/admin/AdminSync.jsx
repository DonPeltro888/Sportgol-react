import React, { useState, useEffect } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { RefreshCw, Clock, CheckCircle, AlertCircle, Database, Globe, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminSync = () => {
  const { authFetch } = useAdminAuth();
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [replaceAll, setReplaceAll] = useState(false);

  const [logosLoading, setLogosLoading] = useState(false);
  const [apiSyncing, setApiSyncing] = useState(false);

  const runApiFootballSync = async () => {
    if (!confirm('Avviare sync via API-Football (provider primario)? Verranno recuperati eventi e loghi per tutte le competizioni configurate.')) return;
    try {
      setApiSyncing(true);
      toast.info('Sync API-Football avviata, attendere prego (~10-30s)...');
      const r = await authFetch(`${API_URL}/api/admin/sync/football-api`, { method: 'POST' });
      const data = await r.json();
      if (!r.ok || data.success === false) {
        throw new Error(data.detail || data.error || `HTTP ${r.status}`);
      }
      toast.success(
        `Sync API-Football OK: ${data.total_inserted} nuovi, ${data.total_updated} aggiornati, ${data.logos_added} loghi nuovi, ${data.leagues_synced} leghe`
      );
      fetchLogs();
    } catch (e) {
      toast.error(`Errore: ${e.message}. Hai configurato la API key in /admin/integrations?`);
    } finally {
      setApiSyncing(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const r = await authFetch(`${API_URL}/api/admin/sync/logs?limit=10`);
      const data = await r.json();
      setLogs(data.logs || []);
    } catch (error) {
      console.error('Errore caricamento log:', error);
    } finally {
      setLoading(false);
    }
  };

  const runSync = async () => {
    if (!confirm(replaceAll
      ? 'Confermi sync completa? Tutti gli eventi importati da matchesio verranno SOSTITUITI. Eventi custom dell\'admin saranno preservati.'
      : 'Confermi sync incrementale? Verranno aggiornati gli eventi esistenti e aggiunti i nuovi.')) {
      return;
    }

    try {
      setSyncing(true);
      toast.info('Sync avviata, attendere prego...');
      const r = await authFetch(
        `${API_URL}/api/admin/sync/matchesio?replace_all=${replaceAll}`,
        { method: 'POST' }
      );

      if (!r.ok) {
        throw new Error(`HTTP ${r.status}`);
      }

      const data = await r.json();
      toast.success(
        `Sync completata! ${data.stats.total_inserted} inseriti, ${data.stats.total_in_db} totali in DB`
      );
      fetchLogs();
    } catch (error) {
      console.error('Errore sync:', error);
      toast.error(`Errore: ${error.message}`);
    } finally {
      setSyncing(false);
    }
  };

  const runLogosSync = async () => {
    if (!confirm('Avvia popolamento loghi? Limit 50 team per chiamata (rate limit TheSportsDB ~30/min).\nLanciare più volte per popolare tutti i ~400 team.')) return;
    try {
      setLogosLoading(true);
      toast.info('Popolamento loghi in corso (~2 min)...');
      const r = await authFetch(
        `${API_URL}/api/admin/sync/logos?refresh_existing=false&team_batch=50`,
        { method: 'POST' }
      );
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      const ts = data.stats?.teams || {};
      const ls = data.stats?.leagues || {};
      toast.success(
        `Loghi: leghe agg.=${ls.updated}, nuovi team=${ts.created}, agg=${ts.updated_logo}, restanti=${ts.remaining || 0}`
      );
    } catch (e) {
      toast.error(`Errore: ${e.message}`);
    } finally {
      setLogosLoading(false);
    }
  };

  const fmtDate = (iso) => {
    if (!iso) return '-';
    try {
      return new Date(iso).toLocaleString('it-IT');
    } catch {
      return iso;
    }
  };

  return (
    <AdminLayout>
      <div className="space-y-6" data-testid="admin-sync-page">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <RefreshCw className="w-6 h-6 text-blue-400" /> Sincronizzazione Eventi
          </h1>
          <p className="text-gray-400">
            API-Football è il provider primario. matchesio.com e TheSportsDB restano disponibili come fallback manuali.
          </p>
        </div>

        {/* API-Football Card (PRIMARIO) */}
        <div className="bg-gradient-to-r from-green-900/40 to-emerald-900/40 border border-green-700 rounded-xl p-6">
          <div className="flex items-start justify-between gap-4 mb-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-white font-bold mb-1 flex items-center gap-2">
                  ⭐ API-Football <span className="text-xs bg-green-600 text-white px-2 py-0.5 rounded-full">PRIMARIO</span>
                </h3>
                <p className="text-gray-300 text-sm mb-2">
                  31 competizioni con dati ufficiali, loghi inclusi, aggiornamento real-time. Copertura completa: Champions, Europa League, Conference, World Cup, tutte le coppe nazionali.
                </p>
                <p className="text-gray-400 text-xs">
                  <Clock className="w-3 h-3 inline mr-1" />
                  Sync auto: <strong>06:00</strong> e <strong>21:00</strong> Italia (cattura annunci serali UEFA/Lega).
                  <br />
                  📊 Configurazione API key: <a href="/admin/integrations" className="text-blue-400 hover:underline">Admin → Integrazioni API</a>
                </p>
              </div>
            </div>
          </div>
          <button
            onClick={runApiFootballSync}
            disabled={apiSyncing}
            data-testid="run-api-football-sync-btn"
            className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-lg flex items-center gap-2 transition-all"
          >
            {apiSyncing ? (
              <><Loader2 className="w-5 h-5 animate-spin" /> Sync API-Football in corso...</>
            ) : (
              <><RefreshCw className="w-5 h-5" /> Avvia sync API-Football ora</>
            )}
          </button>
        </div>

        {/* Info Card matchesio (FALLBACK) */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <div className="flex items-start gap-3">
            <Globe className="w-6 h-6 text-gray-400 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-white font-bold mb-1 flex items-center gap-2">
                matchesio.com <span className="text-xs bg-yellow-600 text-white px-2 py-0.5 rounded-full">FALLBACK</span>
              </h3>
              <p className="text-gray-300 text-sm mb-2">
                Usato automaticamente se API-Football non è disponibile o non configurata. Mantienilo come safety net.
              </p>
              <p className="text-gray-400 text-xs">
                <AlertCircle className="w-3 h-3 inline mr-1" />
                Limite noto: alcune coppe (Europa League, Conference, Copa del Rey) non disponibili (server matchesio errore 500).
              </p>
            </div>
          </div>
        </div>

        {/* Controls matchesio (fallback manuale) */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <h2 className="text-white font-bold text-lg mb-4">Sync Manuale matchesio.com (fallback)</h2>

          <div className="space-y-4">
            <label className="flex items-start gap-3 cursor-pointer p-3 bg-gray-900 rounded-lg border border-gray-700">
              <input
                type="radio"
                name="mode"
                checked={!replaceAll}
                onChange={() => setReplaceAll(false)}
                className="mt-1"
                data-testid="sync-mode-upsert"
              />
              <div>
                <div className="text-white font-medium">Sync incrementale (upsert) — RACCOMANDATO</div>
                <div className="text-gray-400 text-xs mt-0.5">
                  Aggiorna eventi esistenti e aggiunge nuovi. Preserva eventi custom dell'admin.
                </div>
              </div>
            </label>

            <label className="flex items-start gap-3 cursor-pointer p-3 bg-gray-900 rounded-lg border border-gray-700">
              <input
                type="radio"
                name="mode"
                checked={replaceAll}
                onChange={() => setReplaceAll(true)}
                className="mt-1"
                data-testid="sync-mode-replace"
              />
              <div>
                <div className="text-white font-medium">Sostituzione completa (replace_all)</div>
                <div className="text-gray-400 text-xs mt-0.5">
                  Cancella tutti gli eventi matchesio e re-importa da zero. Eventi custom preservati.
                </div>
              </div>
            </label>

            <button
              onClick={runSync}
              disabled={syncing}
              data-testid="run-sync-btn"
              className="w-full md:w-auto px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold rounded-lg flex items-center justify-center gap-2 transition-all"
            >
              {syncing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" /> Sincronizzazione in corso...
                </>
              ) : (
                <>
                  <RefreshCw className="w-5 h-5" /> Avvia Sync Manuale
                </>
              )}
            </button>
          </div>
        </div>

        {/* Logos sync (TheSportsDB fallback) */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <h2 className="text-white font-bold text-lg mb-2">Loghi via TheSportsDB (fallback)</h2>
          <p className="text-gray-400 text-sm mb-4">
            Usa solo se i loghi non vengono dall'API-Football. Recupera loghi delle leghe e badge delle squadre da
            <a href="https://www.thesportsdb.com" target="_blank" rel="noreferrer" className="text-blue-400 hover:underline ml-1">TheSportsDB</a>
            (gratis, rate limit ~30 req/min).
          </p>
          <button
            onClick={runLogosSync}
            disabled={logosLoading}
            data-testid="run-logos-sync-btn"
            className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 text-white font-bold rounded-lg flex items-center gap-2 transition-all"
          >
            {logosLoading ? (
              <><Loader2 className="w-5 h-5 animate-spin" /> Recupero loghi...</>
            ) : (
              <><Globe className="w-5 h-5" /> Popola Loghi (50 team batch)</>
            )}
          </button>
        </div>

        {/* Logs */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-white font-bold text-lg flex items-center gap-2">
              <Database className="w-5 h-5" /> Storico Sync (ultimi 10)
            </h2>
            <button
              onClick={fetchLogs}
              data-testid="refresh-logs-btn"
              className="text-gray-400 hover:text-white text-sm"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
            </div>
          ) : logs.length === 0 ? (
            <div className="text-gray-500 text-sm text-center py-8">
              Nessuna sync eseguita ancora. Clicca "Avvia Sync Manuale" per iniziare.
            </div>
          ) : (
            <div className="space-y-3" data-testid="sync-logs-list">
              {logs.map((log, idx) => {
                const hasErrors = log.errors && log.errors.length > 0;
                return (
                  <div
                    key={idx}
                    className={`bg-gray-900 border rounded-lg p-4 ${
                      hasErrors ? 'border-yellow-700' : 'border-gray-700'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {hasErrors ? (
                          <AlertCircle className="w-4 h-4 text-yellow-500" />
                        ) : (
                          <CheckCircle className="w-4 h-4 text-green-500" />
                        )}
                        <span className="text-white font-medium text-sm">
                          {fmtDate(log.log_at || log.finished_at)}
                        </span>
                      </div>
                      <span className="text-gray-400 text-xs">
                        {log.total_in_db || 0} eventi totali
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs mt-3">
                      <div>
                        <div className="text-gray-500">Inseriti</div>
                        <div className="text-green-400 font-bold">{log.total_inserted || 0}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Aggiornati</div>
                        <div className="text-blue-400 font-bold">{log.total_updated || 0}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Cancellati</div>
                        <div className="text-orange-400 font-bold">{log.total_deleted_past || 0}</div>
                      </div>
                      <div>
                        <div className="text-gray-500">Errori</div>
                        <div className={hasErrors ? 'text-yellow-400 font-bold' : 'text-gray-400'}>
                          {(log.errors || []).length}
                        </div>
                      </div>
                    </div>
                    {log.per_league && Object.keys(log.per_league).length > 0 && (
                      <details className="mt-3">
                        <summary className="text-gray-500 text-xs cursor-pointer hover:text-gray-400">
                          Dettagli per lega
                        </summary>
                        <div className="mt-2 grid grid-cols-2 md:grid-cols-3 gap-1 text-xs">
                          {Object.entries(log.per_league).map(([league, count]) => (
                            <div key={league} className="text-gray-400">
                              {league}: <span className="text-white">{count}</span>
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
                    {hasErrors && (
                      <details className="mt-2">
                        <summary className="text-yellow-500 text-xs cursor-pointer">
                          Vedi errori ({log.errors.length})
                        </summary>
                        <ul className="mt-2 text-yellow-400 text-xs space-y-1">
                          {log.errors.map((err, i) => (
                            <li key={i}>• {err}</li>
                          ))}
                        </ul>
                      </details>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </AdminLayout>
  );
};

export default AdminSync;
