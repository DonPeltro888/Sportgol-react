import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import {
  AlertTriangle, RefreshCw, Loader2, Zap, Globe, Database, Bot, ChevronLeft,
  CheckCircle2, ListChecks,
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SourceBadge = ({ name, count }) => {
  const colors = {
    espn: 'bg-blue-600/30 text-blue-200 border border-blue-700/50',
    matchesio: 'bg-gray-600/30 text-gray-300 border border-gray-700/50',
    openfootball: 'bg-purple-600/30 text-purple-200 border border-purple-700/50',
    thesportsdb: 'bg-amber-600/30 text-amber-200 border border-amber-700/50',
    apifootball: 'bg-pink-600/30 text-pink-200 border border-pink-700/50',
    ai_perplexity: 'bg-emerald-600/30 text-emerald-200 border border-emerald-700/50',
  };
  return (
    <span className={`text-[10px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded ${colors[name] || 'bg-gray-700 text-gray-300'}`}>
      {name}: {count}
    </span>
  );
};

const DataRecoveryDashboard = () => {
  const { authFetch } = useAdminAuth();
  const [status, setStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(null); // 'espn'|'ai'|'openfootball'|'thesportsdb'| `league:slug`

  const loadStatus = useCallback(async () => {
    setLoading(true);
    try {
      const r = await authFetch(`${API_URL}/api/data-tools/data-recovery/sources-status`);
      if (r.ok) setStatus(await r.json());
    } catch (e) { /* ignore */ } finally { setLoading(false); }
  }, [authFetch]);

  const loadLogs = useCallback(async () => {
    try {
      const r = await authFetch(`${API_URL}/api/data-tools/data-recovery/logs?limit=15`);
      if (r.ok) {
        const d = await r.json();
        setLogs(d.items || []);
      }
    } catch (e) { /* ignore */ }
  }, [authFetch]);

  useEffect(() => { loadStatus(); loadLogs(); }, [loadStatus, loadLogs]);

  const runAction = async (path, label, key) => {
    if (!window.confirm(`Avvio "${label}"?\nLa procedura può richiedere 30-90 secondi.`)) return;
    setRunning(key);
    try {
      const r = await authFetch(`${API_URL}${path}`, { method: 'POST' });
      const d = await r.json();
      if (r.ok) {
        const inserted = d.total_inserted || d.inserted || 0;
        const updated = d.total_updated || 0;
        toast.success(`${label} OK: +${inserted} insert, ${updated} update`);
        loadStatus();
        loadLogs();
      } else toast.error(d.detail || `Errore ${label}`);
    } catch (e) { toast.error('Errore di rete'); }
    finally { setRunning(null); }
  };

  const runLeague = async (slug, name) => {
    if (!window.confirm(`Resync mirato di "${name}"?\nESPN + AI Gap Detector. ~30-60s.`)) return;
    setRunning(`league:${slug}`);
    try {
      const r = await authFetch(`${API_URL}/api/data-tools/data-recovery/run-league/${slug}`, { method: 'POST' });
      const d = await r.json();
      if (r.ok) {
        const espnIns = d.results?.espn?.inserted ?? 0;
        const aiIns = d.results?.ai_perplexity?.inserted ?? 0;
        toast.success(`${name}: ESPN +${espnIns} | AI +${aiIns}`);
        loadStatus();
      } else toast.error(d.detail || `Errore ${name}`);
    } catch (e) { toast.error('Errore di rete'); }
    finally { setRunning(null); }
  };

  const rows = status?.rows || [];
  const atRisk = rows.filter(r => r.is_at_risk);

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto">
        <Link to="/admin/data-tools" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
          <ChevronLeft className="w-4 h-4" /> Torna a Data Tools
        </Link>

        <div className="mb-6 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold text-white inline-flex items-center gap-2">
              <Database className="w-7 h-7 text-cyan-400" /> Data Recovery — Multi-Source Aggregator
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              Multi-fonte gratuita: <strong className="text-blue-300">ESPN</strong> (primary, no auth), OpenFootball, TheSportsDB, AI Gap Detector via Perplexity.
              Defense-in-depth: nessuna fonte può lasciarti a secco.
            </p>
          </div>
          <button
            onClick={() => { loadStatus(); loadLogs(); }}
            data-testid="dt-recovery-refresh"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-gray-700 hover:bg-gray-600 text-white text-sm font-semibold"
          >
            <RefreshCw className="w-4 h-4" /> Refresh
          </button>
        </div>

        {/* Bulk action buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
          <button
            onClick={() => runAction('/api/data-tools/data-recovery/run-espn', 'ESPN Sync', 'espn')}
            disabled={running !== null}
            data-testid="dt-recovery-run-espn"
            className="rounded-xl border border-blue-700/50 bg-blue-900/20 hover:bg-blue-900/40 p-4 text-left transition-all disabled:opacity-50"
          >
            <div className="flex items-center justify-between mb-2">
              <Globe className="w-5 h-5 text-blue-400" />
              {running === 'espn' && <Loader2 className="w-4 h-4 animate-spin text-blue-400" />}
            </div>
            <h3 className="text-white font-semibold text-sm">🌐 ESPN Sync</h3>
            <p className="text-[11px] text-gray-400 mt-1">Fonte primaria. Tutte le 30 competizioni, prossimi 90gg.</p>
          </button>

          <button
            onClick={() => runAction('/api/data-tools/data-recovery/run-openfootball', 'OpenFootball Sync', 'openfootball')}
            disabled={running !== null}
            data-testid="dt-recovery-run-openfootball"
            className="rounded-xl border border-purple-700/50 bg-purple-900/20 hover:bg-purple-900/40 p-4 text-left transition-all disabled:opacity-50"
          >
            <div className="flex items-center justify-between mb-2">
              <Database className="w-5 h-5 text-purple-400" />
              {running === 'openfootball' && <Loader2 className="w-4 h-4 animate-spin text-purple-400" />}
            </div>
            <h3 className="text-white font-semibold text-sm">📂 OpenFootball</h3>
            <p className="text-[11px] text-gray-400 mt-1">GitHub JSON stable. Top 5 leghe + CL/EL.</p>
          </button>

          <button
            onClick={() => runAction('/api/data-tools/data-recovery/run-thesportsdb', 'TheSportsDB Sync', 'thesportsdb')}
            disabled={running !== null}
            data-testid="dt-recovery-run-thesportsdb"
            className="rounded-xl border border-amber-700/50 bg-amber-900/20 hover:bg-amber-900/40 p-4 text-left transition-all disabled:opacity-50"
          >
            <div className="flex items-center justify-between mb-2">
              <ListChecks className="w-5 h-5 text-amber-400" />
              {running === 'thesportsdb' && <Loader2 className="w-4 h-4 animate-spin text-amber-400" />}
            </div>
            <h3 className="text-white font-semibold text-sm">🏆 TheSportsDB</h3>
            <p className="text-[11px] text-gray-400 mt-1">Fallback per coppe + loghi.</p>
          </button>

          <button
            onClick={() => runAction('/api/data-tools/data-recovery/run-ai-gap', 'AI Gap Detector', 'ai')}
            disabled={running !== null}
            data-testid="dt-recovery-run-ai"
            className="rounded-xl border border-emerald-700/50 bg-emerald-900/20 hover:bg-emerald-900/40 p-4 text-left transition-all disabled:opacity-50"
          >
            <div className="flex items-center justify-between mb-2">
              <Bot className="w-5 h-5 text-emerald-400" />
              {running === 'ai' && <Loader2 className="w-4 h-4 animate-spin text-emerald-400" />}
            </div>
            <h3 className="text-white font-semibold text-sm">🤖 AI Gap Detector</h3>
            <p className="text-[11px] text-gray-400 mt-1">Perplexity Sonar Pro: trova match mancanti residui.</p>
          </button>
        </div>

        {/* At-risk leagues alert */}
        {!loading && atRisk.length > 0 && (
          <div className="rounded-xl border border-red-700/50 bg-red-900/20 p-4 mb-6 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-red-200 font-bold text-sm">⚠️ {atRisk.length} leghe a rischio (&lt; 3 eventi futuri)</h3>
              <p className="text-xs text-red-300/80 mt-1">
                {atRisk.slice(0, 5).map(r => r.league).join(', ')}{atRisk.length > 5 ? ` +${atRisk.length - 5}…` : ''}
              </p>
            </div>
          </div>
        )}

        {/* Sources matrix */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6">
          <h2 className="text-lg font-bold text-white mb-3 inline-flex items-center gap-2">
            <Database className="w-5 h-5 text-cyan-400" /> Stato Fonti per Lega ({rows.length})
          </h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-900/40 text-gray-400 text-xs uppercase">
                <tr>
                  <th className="text-left px-3 py-2">Lega</th>
                  <th className="text-left px-3 py-2 hidden md:table-cell">Country</th>
                  <th className="text-center px-3 py-2">Eventi futuri</th>
                  <th className="text-left px-3 py-2">Fonti</th>
                  <th className="text-right px-3 py-2">Azione</th>
                </tr>
              </thead>
              <tbody>
                {loading && (
                  <tr><td colSpan={5} className="py-12 text-center text-gray-500"><Loader2 className="w-5 h-5 animate-spin mx-auto" /></td></tr>
                )}
                {!loading && rows.map(r => {
                  const slug = r.slug;
                  const sources = Object.entries(r.by_source || {});
                  return (
                    <tr key={r.league} className={`border-t border-gray-700/50 ${r.is_at_risk ? 'bg-red-900/10' : 'hover:bg-gray-900/30'}`}>
                      <td className="px-3 py-2 text-white">
                        <span className="font-medium">{r.league}</span>
                        {r.type === 'cup' && <span className="ml-2 text-[10px] text-amber-300 uppercase">cup</span>}
                      </td>
                      <td className="px-3 py-2 text-gray-400 text-xs hidden md:table-cell">{r.country}</td>
                      <td className="px-3 py-2 text-center">
                        <span className={`text-base font-bold ${r.is_at_risk ? 'text-red-300' : 'text-emerald-300'}`}>
                          {r.total_future}
                        </span>
                      </td>
                      <td className="px-3 py-2">
                        <div className="flex flex-wrap gap-1">
                          {sources.map(([s, c]) => <SourceBadge key={s} name={s} count={c} />)}
                          {sources.length === 0 && <span className="text-gray-500 text-xs">—</span>}
                        </div>
                      </td>
                      <td className="px-3 py-2 text-right">
                        <button
                          onClick={() => runLeague(slug, r.league)}
                          disabled={running !== null || !slug}
                          data-testid={`dt-recovery-resync-${slug}`}
                          className="text-[11px] px-2.5 py-1 rounded bg-cyan-600 hover:bg-cyan-700 text-white inline-flex items-center gap-1 disabled:opacity-30"
                        >
                          {running === `league:${slug}` ? <Loader2 className="w-3 h-3 animate-spin" /> : <Zap className="w-3 h-3" />}
                          Resync
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {!loading && rows.length === 0 && (
                  <tr><td colSpan={5} className="py-12 text-center text-gray-500">Nessuna lega con eventi futuri (DB vuoto)</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Logs */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
          <h2 className="text-lg font-bold text-white mb-3 inline-flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Ultimi sync log
          </h2>
          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {logs.map((l, i) => (
              <div key={i} className="rounded border border-gray-700/50 bg-gray-900/40 p-3 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white uppercase tracking-wide">{l.source}</span>
                  <span className="text-gray-500 font-mono">{l.log_at?.slice(0, 19).replace('T', ' ')}</span>
                </div>
                <div className="mt-1.5 grid grid-cols-2 md:grid-cols-4 gap-2 text-gray-300">
                  {l.total_inserted != null && <span>+{l.total_inserted} inserted</span>}
                  {l.total_updated != null && l.total_updated > 0 && <span>~{l.total_updated} updated</span>}
                  {l.leagues_empty > 0 && <span className="text-amber-300">{l.leagues_empty} leghe vuote</span>}
                  {l.leagues_with_gaps != null && <span className="text-emerald-300">{l.leagues_with_gaps}/{l.leagues_checked} con gap</span>}
                  {l.total_missing != null && l.total_missing > 0 && <span className="text-amber-300">{l.total_missing} match recuperati</span>}
                </div>
                {l.errors?.length > 0 && (
                  <div className="mt-2 text-red-400 text-[10px]">
                    {l.errors.length} errori: {l.errors[0]}
                  </div>
                )}
              </div>
            ))}
            {logs.length === 0 && <div className="text-gray-500 text-sm py-8 text-center">Nessun log</div>}
          </div>
        </div>
      </div>
    </AdminLayout>
  );
};

export default DataRecoveryDashboard;
