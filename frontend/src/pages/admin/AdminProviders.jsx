import React, { useState, useEffect } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { Database, CheckCircle2, XCircle, Loader2, ExternalLink, Info, Key, Trash2, Globe, Zap, RefreshCw, AlertCircle, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const STATUS_COLORS = {
  active: { bg: 'bg-green-900/30', border: 'border-green-700', text: 'text-green-400', icon: '🟢', label: 'Attiva' },
  dormant: { bg: 'bg-yellow-900/30', border: 'border-yellow-700', text: 'text-yellow-400', icon: '🟡', label: 'In pausa' },
  dead: { bg: 'bg-red-900/30', border: 'border-red-700', text: 'text-red-400', icon: '🔴', label: 'Stagione finita' },
};

const SOURCE_LABELS = {
  openfootball: { label: 'OpenFootball', color: 'bg-cyan-700' },
  matchesio: { label: 'matchesio', color: 'bg-blue-700' },
  apifootball: { label: 'APIfootball', color: 'bg-purple-700' },
  thesportsdb: { label: 'TheSportsDB', color: 'bg-pink-700' },
  football_data: { label: 'Football-Data', color: 'bg-indigo-700' },
  api_football: { label: 'API-Football', color: 'bg-emerald-700' },
};

const AdminProviders = () => {
  const { authFetch } = useAdminAuth();
  const [providers, setProviders] = useState([]);
  const [coverage, setCoverage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editingProvider, setEditingProvider] = useState(null);
  const [editKey, setEditKey] = useState('');
  const [testing, setTesting] = useState(null);
  const [running, setRunning] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const [pr, cv] = await Promise.all([
        authFetch(`${API_URL}/api/admin/providers`),
        authFetch(`${API_URL}/api/admin/providers/coverage-report`),
      ]);
      const prData = await pr.json();
      const cvData = await cv.json();
      setProviders(prData.providers || []);
      setCoverage(cvData);
    } catch (e) {
      toast.error('Errore caricamento: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleSaveKey = async (slug) => {
    if (!editKey || editKey.trim().length < 4) {
      toast.error('Key troppo corta');
      return;
    }
    try {
      const r = await authFetch(`${API_URL}/api/admin/providers/${slug}`, {
        method: 'PUT',
        body: JSON.stringify({ api_key: editKey.trim(), enabled: true }),
      });
      if (!r.ok) {
        const err = await r.json();
        throw new Error(err.detail || 'Save failed');
      }
      toast.success('Key salvata');
      setEditingProvider(null);
      setEditKey('');
      load();
    } catch (e) {
      toast.error(e.message);
    }
  };

  const handleTest = async (slug) => {
    setTesting(slug);
    try {
      const r = await authFetch(`${API_URL}/api/admin/providers/${slug}/test`, { method: 'POST' });
      const data = await r.json();
      if (data.ok) {
        toast.success(`✅ ${data.provider || slug}: ${JSON.stringify(data).slice(0, 200)}`);
      } else {
        toast.error(`❌ ${slug}: ${data.error || 'Test fallito'}`);
      }
      load();
    } catch (e) {
      toast.error(e.message);
    } finally {
      setTesting(null);
    }
  };

  const handleDelete = async (slug) => {
    if (!confirm(`Rimuovere la key di ${slug}?`)) return;
    try {
      await authFetch(`${API_URL}/api/admin/providers/${slug}`, { method: 'DELETE' });
      toast.success('Key rimossa');
      load();
    } catch (e) {
      toast.error(e.message);
    }
  };

  const handleToggle = async (provider) => {
    try {
      const r = await authFetch(`${API_URL}/api/admin/providers/${provider.slug}`, {
        method: 'PUT',
        body: JSON.stringify({ api_key: '__NOCHANGE__', enabled: !provider.enabled }),
      });
      if (!r.ok && provider.api_key_masked) {
        // backend richiede una key per il PUT, lo skippo se non c'è ma la key esiste
        toast.info('Stato aggiornato');
      }
      load();
    } catch (e) {
      toast.error(e.message);
    }
  };

  const handleRunMix = async () => {
    if (!confirm('Avviare il sync MIX completo (tutti i provider abilitati)? Può richiedere 1-2 minuti.')) return;
    setRunning(true);
    try {
      toast.info('MIX run avviato, attendere prego...');
      const r = await authFetch(`${API_URL}/api/admin/sync/run-mix`, { method: 'POST' });
      const text = await r.text();
      let data = {};
      try { data = text ? JSON.parse(text) : {}; } catch {
        throw new Error('Risposta non valida');
      }
      if (!r.ok) throw new Error(data.detail || 'Run failed');
      toast.success(`MIX completato: +${data.totals.inserted} nuovi, ${data.totals.updated} aggiornati, +${data.totals.logos} loghi (${data.total_in_db} totali nel DB)`);
      load();
    } catch (e) {
      toast.error(e.message);
    } finally {
      setRunning(false);
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
      <div className="p-6 space-y-6" data-testid="admin-providers">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white mb-1 flex items-center gap-3">
              <Database className="w-8 h-8 text-purple-500" />
              Provider Dati & Coverage
            </h1>
            <p className="text-gray-400 text-sm">
              Gestisci le API esterne e monitora la copertura per ogni competizione del sito.
            </p>
          </div>
          <button
            onClick={handleRunMix}
            disabled={running}
            data-testid="run-mix-btn"
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 text-white font-bold rounded-lg flex items-center gap-2"
          >
            {running ? <Loader2 className="w-5 h-5 animate-spin" /> : <Zap className="w-5 h-5" />}
            {running ? 'MIX in corso...' : 'Avvia MIX Sync ora'}
          </button>
        </div>

        {/* Coverage stats */}
        {coverage && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <div className="text-gray-400 text-xs uppercase">Totali</div>
              <div className="text-2xl font-bold text-white">{coverage.total_leagues}</div>
            </div>
            <div className="bg-green-900/20 border border-green-800 rounded-lg p-4">
              <div className="text-green-400 text-xs uppercase">🟢 Attive</div>
              <div className="text-2xl font-bold text-green-400">{coverage.active}</div>
            </div>
            <div className="bg-yellow-900/20 border border-yellow-800 rounded-lg p-4">
              <div className="text-yellow-400 text-xs uppercase">🟡 In pausa</div>
              <div className="text-2xl font-bold text-yellow-400">{coverage.dormant}</div>
            </div>
            <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
              <div className="text-red-400 text-xs uppercase">🔴 Finite</div>
              <div className="text-2xl font-bold text-red-400">{coverage.dead}</div>
            </div>
          </div>
        )}

        {/* PROVIDERS LIST */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Globe className="w-6 h-6" /> Fonti dati disponibili
          </h2>
          <div className="space-y-3">
            {providers.map((p) => (
              <div key={p.slug} className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <h3 className="text-white font-bold">{p.name}</h3>
                      {p.configured && p.enabled ? (
                        <span className="text-xs px-2 py-0.5 bg-green-700 text-green-100 rounded-full">Attivo</span>
                      ) : p.configured ? (
                        <span className="text-xs px-2 py-0.5 bg-yellow-700 text-yellow-100 rounded-full">Disabilitato</span>
                      ) : (
                        <span className="text-xs px-2 py-0.5 bg-gray-700 text-gray-300 rounded-full">Non configurato</span>
                      )}
                      {p.category === 'free' && <span className="text-xs px-2 py-0.5 bg-cyan-700 text-cyan-100 rounded-full">GRATIS</span>}
                      {p.free_tier && p.needs_key && <span className="text-xs px-2 py-0.5 bg-blue-700 text-blue-100 rounded-full">Free tier</span>}
                      {!p.free_tier && p.needs_key && <span className="text-xs px-2 py-0.5 bg-orange-700 text-orange-100 rounded-full">A pagamento</span>}
                    </div>
                    <p className="text-sm text-gray-400 mb-2">{p.description}</p>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {p.coverage.map((c) => (
                        <span key={c} className="text-xs px-2 py-0.5 bg-gray-800 text-gray-300 rounded">{c}</span>
                      ))}
                    </div>
                    <div className="flex flex-wrap gap-3 text-xs">
                      <a href={p.signup_url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline inline-flex items-center gap-1">
                        🔑 Ottieni key <ExternalLink className="w-3 h-3" />
                      </a>
                      <a href={p.docs_url} target="_blank" rel="noreferrer" className="text-blue-400 hover:underline inline-flex items-center gap-1">
                        📚 Documentazione <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                    {p.api_key_masked && (
                      <div className="text-xs text-gray-500 mt-2">
                        Key attuale: <code className="bg-gray-800 px-1 rounded font-mono">{p.api_key_masked}</code>
                      </div>
                    )}
                    {p.last_test_result && (
                      <div className={`text-xs mt-2 ${p.last_test_result.ok ? 'text-green-400' : 'text-red-400'}`}>
                        {p.last_test_result.ok ? '✅' : '❌'} Ultimo test: {p.last_test_result.error || JSON.stringify(p.last_test_result).slice(0, 120)}
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col gap-2 min-w-[160px]">
                    {editingProvider === p.slug ? (
                      <div className="flex flex-col gap-2 w-full">
                        <input
                          type="password"
                          placeholder="API key"
                          value={editKey}
                          onChange={(e) => setEditKey(e.target.value)}
                          className="bg-gray-800 text-white text-sm rounded px-3 py-2 border border-gray-700 font-mono"
                          autoFocus
                          data-testid={`edit-key-${p.slug}`}
                        />
                        <div className="flex gap-1">
                          <button
                            onClick={() => handleSaveKey(p.slug)}
                            className="flex-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded"
                          >
                            Salva
                          </button>
                          <button
                            onClick={() => { setEditingProvider(null); setEditKey(''); }}
                            className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-xs rounded"
                          >
                            X
                          </button>
                        </div>
                      </div>
                    ) : (
                      <>
                        {p.needs_key && (
                          <button
                            onClick={() => { setEditingProvider(p.slug); setEditKey(''); }}
                            data-testid={`set-key-btn-${p.slug}`}
                            className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded font-medium flex items-center gap-1"
                          >
                            <Key className="w-3 h-3" /> {p.configured ? 'Cambia key' : 'Imposta key'}
                          </button>
                        )}
                        <button
                          onClick={() => handleTest(p.slug)}
                          disabled={testing === p.slug}
                          data-testid={`test-btn-${p.slug}`}
                          className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white text-xs rounded font-medium flex items-center gap-1 disabled:opacity-50"
                        >
                          {testing === p.slug ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                          Testa
                        </button>
                        {p.configured && p.needs_key && (
                          <button
                            onClick={() => handleDelete(p.slug)}
                            className="px-3 py-1.5 bg-red-700 hover:bg-red-800 text-white text-xs rounded font-medium flex items-center gap-1"
                          >
                            <Trash2 className="w-3 h-3" /> Rimuovi
                          </button>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* COVERAGE TABLE */}
        {coverage && (
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
              <Database className="w-6 h-6" /> Coverage Report per Competizione
            </h2>
            <p className="text-gray-400 text-sm mb-4">
              Per ogni categoria del sito vedi quanti eventi futuri ha e da quale fonte arrivano.
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-900 text-gray-400 text-xs uppercase">
                  <tr>
                    <th className="px-3 py-2 text-left">Status</th>
                    <th className="px-3 py-2 text-left">Competizione</th>
                    <th className="px-3 py-2 text-left">Tipo</th>
                    <th className="px-3 py-2 text-right">Eventi futuri</th>
                    <th className="px-3 py-2 text-left">Fonti</th>
                    <th className="px-3 py-2 text-left">Ultimo evento</th>
                  </tr>
                </thead>
                <tbody>
                  {coverage.leagues.map((lg) => {
                    const sc = STATUS_COLORS[lg.status];
                    return (
                      <tr key={lg.slug} className="border-t border-gray-700 hover:bg-gray-900/50">
                        <td className={`px-3 py-2 ${sc.text}`}>{sc.icon} {sc.label}</td>
                        <td className="px-3 py-2 text-white font-medium">
                          {lg.name}
                          <span className="text-xs text-gray-500 block">{lg.country}</span>
                        </td>
                        <td className="px-3 py-2 text-gray-400">{lg.type}</td>
                        <td className={`px-3 py-2 text-right font-bold ${lg.future_events === 0 ? 'text-red-400' : lg.future_events > 30 ? 'text-green-400' : 'text-yellow-400'}`}>
                          {lg.future_events}
                        </td>
                        <td className="px-3 py-2">
                          <div className="flex flex-wrap gap-1">
                            {lg.sources.length === 0 && <span className="text-gray-600 text-xs italic">nessuna</span>}
                            {lg.sources.map((s) => {
                              const cfg = SOURCE_LABELS[s.source] || { label: s.source, color: 'bg-gray-700' };
                              return (
                                <span key={s.source} className={`text-xs px-2 py-0.5 rounded ${cfg.color} text-white`}>
                                  {cfg.label}: {s.count}
                                </span>
                              );
                            })}
                          </div>
                        </td>
                        <td className="px-3 py-2 text-gray-500 text-xs">
                          {lg.last_event_date || '—'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            {coverage.dead > 0 && (
              <div className="mt-4 p-3 bg-yellow-900/20 border border-yellow-800 rounded text-sm text-yellow-300 flex items-start gap-2">
                <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <div>
                  Le {coverage.dead} competizioni in stato 🔴 sono "morte" (stagione finita o non ancora iniziata). Considera di
                  disattivarle dal menu finché non riprendono. Lo trovi in <a href="/admin/leagues-teams" className="underline">Admin → Leghe & Squadre</a>.
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminProviders;
