import React, { useEffect, useState, useCallback } from 'react';
import AdminLayout from '../../../components/admin/AdminLayout';
import SeoTargetSelector from '../../../components/admin/SeoTargetSelector';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import { Loader2, Play, Download, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const STATUS_BADGE = {
  queued: 'bg-gray-700 text-gray-300',
  running: 'bg-blue-600 text-white',
  succeeded: 'bg-emerald-600 text-white',
  failed: 'bg-red-600 text-white',
};

const StatusBadge = ({ status }) => (
  <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${STATUS_BADGE[status] || 'bg-gray-700 text-gray-300'}`}>
    {status}
  </span>
);

const SeoBulkRunner = () => {
  const { authFetch } = useAdminAuth();
  const [target, setTarget] = useState({ leagueSlug: '', teamSlug: '', eventSlug: '' });
  // scope = "teams_of_league" | "events_of_league" | "events_of_team" | "single_event" | "single_team" | "single_league"
  const [scope, setScope] = useState('teams_of_league');
  const [onlyPending, setOnlyPending] = useState(true);
  const [bulkLimit, setBulkLimit] = useState(50);
  const [launching, setLaunching] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Auto-suggest scope based on selection
  useEffect(() => {
    if (target.eventSlug) setScope('single_event');
    else if (target.teamSlug) setScope('events_of_team');
    else if (target.leagueSlug) setScope(s => (s === 'events_of_league' ? 'events_of_league' : 'teams_of_league'));
    else setScope('teams_of_league');
  }, [target.leagueSlug, target.teamSlug, target.eventSlug]);

  const loadJobs = useCallback(async () => {
    try {
      const r = await authFetch(`${API_URL}/api/seo/jobs?limit=50`);
      if (r.ok) {
        const d = await r.json();
        setJobs(d.items || []);
      }
    } catch (e) { /* ignore */ }
  }, [authFetch]);

  useEffect(() => { loadJobs(); /* eslint-disable-next-line */ }, []);
  useEffect(() => {
    if (!autoRefresh) return;
    const t = setInterval(loadJobs, 4000);
    return () => clearInterval(t);
  }, [autoRefresh, loadJobs]);

  const launchSingle = async (type, id) => {
    const r = await authFetch(`${API_URL}/api/seo/targets/${type}/${id}/generate`, { method: 'POST' });
    const d = await r.json().catch(() => ({}));
    if (r.ok) {
      toast.success(`Job avviato: ${d.job_id?.slice(0, 8)}`);
      loadJobs();
    } else toast.error(d.detail || 'Errore avvio');
  };

  const launchBulkLeague = async (type, extra = {}) => {
    if (!target.leagueSlug) return toast.error('Seleziona una lega');
    const r = await authFetch(`${API_URL}/api/seo/targets/bulk-generate-league`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        league_slug: target.leagueSlug,
        type,
        only_pending: onlyPending,
        limit: parseInt(bulkLimit, 10) || 50,
        ...extra,
      }),
    });
    const d = await r.json().catch(() => ({}));
    if (r.ok) {
      toast.success(`Avviati ${d.queued} job in parallelo`);
      loadJobs();
    } else toast.error(d.detail || 'Errore avvio');
  };

  const launch = async () => {
    setLaunching(true);
    try {
      if (scope === 'single_event' && target.eventSlug) {
        await launchSingle('event', target.eventSlug);
      } else if (scope === 'single_team' && target.teamSlug) {
        await launchSingle('team', target.teamSlug);
      } else if (scope === 'single_league' && target.leagueSlug) {
        await launchSingle('league', target.leagueSlug);
      } else if (scope === 'events_of_team' && target.leagueSlug && target.teamSlug) {
        if (!window.confirm(`Avvio generazione SEO per tutti gli eventi di "${target.teamSlug}" (max ${bulkLimit})?`)) return;
        await launchBulkLeague('event', { team_slug: target.teamSlug });
      } else if (scope === 'events_of_league' && target.leagueSlug) {
        if (!window.confirm(`Avvio generazione SEO per tutti gli eventi di "${target.leagueSlug}" (max ${bulkLimit})?`)) return;
        await launchBulkLeague('event');
      } else if (scope === 'teams_of_league' && target.leagueSlug) {
        if (!window.confirm(`Avvio generazione SEO per tutte le squadre di "${target.leagueSlug}" (max ${bulkLimit})?`)) return;
        await launchBulkLeague('team');
      } else {
        toast.error('Selezione incompleta per lo scope scelto');
      }
    } finally { setLaunching(false); }
  };

  const downloadExport = async (format) => {
    try {
      const r = await authFetch(`${API_URL}/api/seo/export?type=all&format=${format}&only_published=true`);
      if (!r.ok) return toast.error('Errore export');
      const blob = await r.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const ts = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
      a.download = `seo-export-${ts}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Export ${format.toUpperCase()} scaricato`);
    } catch (e) { toast.error('Errore download'); }
  };

  const stats = jobs.reduce((acc, j) => { acc[j.status] = (acc[j.status] || 0) + 1; return acc; }, {});

  // Available scope options based on current selection
  const scopeOptions = [];
  if (target.leagueSlug) {
    scopeOptions.push({ value: 'teams_of_league', label: '🏟️ Tutte le squadre della lega' });
    scopeOptions.push({ value: 'events_of_league', label: '📅 Tutti gli eventi della lega' });
    scopeOptions.push({ value: 'single_league', label: '🏆 Solo la lega' });
  }
  if (target.teamSlug) {
    scopeOptions.push({ value: 'events_of_team', label: '📅 Tutti gli eventi della squadra' });
    scopeOptions.push({ value: 'single_team', label: '👥 Solo la squadra' });
  }
  if (target.eventSlug) {
    scopeOptions.push({ value: 'single_event', label: '🎯 Solo questo evento' });
  }

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">SEO Bulk Runner & Export</h1>
          <p className="text-sm text-gray-400 mt-1">
            Filtra a cascata Lega → Squadra → Evento e scegli lo scope di generazione AI.
          </p>
        </div>

        {/* Bulk Generate */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5 mb-6">
          <h2 className="text-lg font-bold text-white mb-3 inline-flex items-center gap-2">
            <Play className="w-5 h-5 text-blue-400" /> Bulk Generate
          </h2>

          <SeoTargetSelector value={target} onChange={setTarget} />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
            <div className="md:col-span-2">
              <label className="text-xs text-gray-400 mb-1 block">Cosa generare</label>
              <select
                value={scope}
                onChange={e => setScope(e.target.value)}
                data-testid="bulk-scope-select"
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm focus:border-blue-500 focus:outline-none"
                disabled={!target.leagueSlug}
              >
                {scopeOptions.length === 0 && <option value="">Seleziona almeno una lega…</option>}
                {scopeOptions.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Limit</label>
              <input
                type="number"
                value={bulkLimit}
                onChange={e => setBulkLimit(e.target.value)}
                min="1"
                max="200"
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3 mt-4">
            <label className="text-xs text-gray-300 inline-flex items-center gap-2">
              <input type="checkbox" checked={onlyPending} onChange={e => setOnlyPending(e.target.checked)} className="w-4 h-4" />
              Solo non pubblicati
            </label>
            <button
              onClick={launch}
              disabled={launching || !target.leagueSlug}
              data-testid="bulk-launch-btn"
              className="px-5 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-sm font-semibold inline-flex items-center gap-2 disabled:opacity-50"
            >
              {launching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
              Avvia Generazione
            </button>
          </div>
        </div>

        {/* Export */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5 mb-6">
          <h2 className="text-lg font-bold text-white mb-3 inline-flex items-center gap-2">
            <Download className="w-5 h-5 text-emerald-400" /> Export Module
          </h2>
          <p className="text-xs text-gray-400 mb-3">
            Scarica i dati SEO di tutte le entity pubblicate (events + leagues + teams) per backup o migrazione.
          </p>
          <div className="flex flex-wrap gap-2">
            {['json', 'csv', 'ndjson'].map(fmt => (
              <button
                key={fmt}
                onClick={() => downloadExport(fmt)}
                data-testid={`export-${fmt}-btn`}
                className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold inline-flex items-center gap-2"
              >
                <Download className="w-4 h-4" /> {fmt.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Jobs Table */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold text-white">Jobs ({jobs.length})</h2>
            <div className="flex items-center gap-3">
              <label className="text-xs text-gray-300 inline-flex items-center gap-2">
                <input type="checkbox" checked={autoRefresh} onChange={e => setAutoRefresh(e.target.checked)} className="w-4 h-4" />
                Auto-refresh
              </label>
              <button onClick={loadJobs} className="px-3 py-1.5 rounded bg-gray-700 hover:bg-gray-600 text-xs text-white inline-flex items-center gap-1">
                <RefreshCw className="w-3 h-3" /> Refresh
              </button>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 mb-4">
            {Object.entries(stats).map(([k, v]) => (
              <span key={k} className={`px-3 py-1 rounded text-xs font-bold ${STATUS_BADGE[k]}`}>{k}: {v}</span>
            ))}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b border-gray-700 text-xs text-gray-400 uppercase">
                  <th className="py-2 px-2">Job</th>
                  <th className="py-2 px-2">Tipo</th>
                  <th className="py-2 px-2">Target</th>
                  <th className="py-2 px-2">Status</th>
                  <th className="py-2 px-2">Step</th>
                  <th className="py-2 px-2">Progress</th>
                  <th className="py-2 px-2">Score</th>
                  <th className="py-2 px-2">Created</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map(j => (
                  <tr key={j._id} className="border-b border-gray-800 text-gray-300 hover:bg-gray-900/30">
                    <td className="py-2 px-2 font-mono text-[11px]">{(j._id || '').slice(0, 8)}</td>
                    <td className="py-2 px-2">{j.target_type}</td>
                    <td className="py-2 px-2">
                      <a href={`/admin/seo/targets/${j.target_type}/${j.target_id}`} className="text-blue-400 hover:text-blue-300">
                        {j.target_id}
                      </a>
                    </td>
                    <td className="py-2 px-2"><StatusBadge status={j.status} /></td>
                    <td className="py-2 px-2 text-xs">{j.step}</td>
                    <td className="py-2 px-2">
                      <div className="w-24 h-1.5 bg-gray-800 rounded overflow-hidden">
                        <div
                          className={`h-full transition-all ${
                            j.status === 'failed' ? 'bg-red-500' :
                            j.status === 'succeeded' ? 'bg-emerald-500' :
                            'bg-blue-500'
                          }`}
                          style={{ width: `${j.progress || 0}%` }}
                        />
                      </div>
                      <span className="text-[10px] text-gray-500 mt-0.5 block">{j.progress || 0}%</span>
                    </td>
                    <td className="py-2 px-2 text-xs">
                      {j.seo_score ? <span className="font-bold text-emerald-300">{j.seo_score}</span> : '-'}
                    </td>
                    <td className="py-2 px-2 text-[11px] text-gray-500">
                      {j.created_at ? new Date(j.created_at).toLocaleString('it-IT', { hour: '2-digit', minute: '2-digit', second: '2-digit', day: '2-digit', month: '2-digit' }) : '-'}
                    </td>
                  </tr>
                ))}
                {jobs.length === 0 && (
                  <tr><td colSpan={8} className="py-8 text-center text-gray-500">Nessun job</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AdminLayout>
  );
};

export default SeoBulkRunner;
