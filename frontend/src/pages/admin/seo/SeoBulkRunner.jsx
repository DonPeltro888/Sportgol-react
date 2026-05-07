import React, { useEffect, useState, useCallback } from 'react';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import { Loader2, Play, Download, RefreshCw, CheckCircle2, XCircle, Clock } from 'lucide-react';
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
  const [leagues, setLeagues] = useState([]);
  const [selectedLeague, setSelectedLeague] = useState('serie-a');
  const [bulkType, setBulkType] = useState('team');
  const [onlyPending, setOnlyPending] = useState(true);
  const [bulkLimit, setBulkLimit] = useState(20);
  const [launching, setLaunching] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const loadLeagues = async () => {
    try {
      const r = await fetch(`${API_URL}/api/leagues/active-slugs`);
      if (r.ok) {
        const d = await r.json();
        setLeagues(d.slugs || d.leagues || []);
      }
    } catch (e) { /* ignore */ }
  };

  const loadJobs = useCallback(async () => {
    try {
      const r = await authFetch(`${API_URL}/api/seo/jobs?limit=50`);
      if (r.ok) {
        const d = await r.json();
        setJobs(d.items || []);
      }
    } catch (e) { /* ignore */ }
  }, [authFetch]);

  useEffect(() => {
    loadLeagues();
    loadJobs();
    /* eslint-disable-next-line react-hooks/exhaustive-deps */
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;
    const t = setInterval(loadJobs, 4000);
    return () => clearInterval(t);
  }, [autoRefresh, loadJobs]);

  const launchBulk = async () => {
    if (!selectedLeague) return toast.error('Scegli una lega');
    if (!window.confirm(`Avvio generazione SEO bulk per ${bulkType === 'team' ? 'tutte le squadre' : 'tutti gli eventi'} di ${selectedLeague}? Ogni entity richiede ~60-90s.`)) return;
    setLaunching(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/targets/bulk-generate-league`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          league_slug: selectedLeague,
          type: bulkType,
          only_pending: onlyPending,
          limit: parseInt(bulkLimit, 10) || 20,
        }),
      });
      const d = await r.json();
      if (r.ok) {
        toast.success(`Avviati ${d.queued} job in parallelo`);
        loadJobs();
      } else toast.error(d.detail || 'Errore avvio');
    } catch (e) { toast.error('Errore di rete'); }
    finally { setLaunching(false); }
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

  // Stats
  const stats = jobs.reduce((acc, j) => {
    acc[j.status] = (acc[j.status] || 0) + 1;
    return acc;
  }, {});

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white">SEO Bulk Runner & Export</h1>
          <p className="text-sm text-gray-400 mt-1">
            Avvia la pipeline AI in batch su intere leghe e scarica i payload SEO per backup/migrazione.
          </p>
        </div>

        {/* Bulk Generate */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5 mb-6">
          <h2 className="text-lg font-bold text-white mb-3 inline-flex items-center gap-2">
            <Play className="w-5 h-5 text-blue-400" /> Bulk Generate
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
            <div className="md:col-span-2">
              <label className="text-xs text-gray-400 mb-1 block">Lega (slug)</label>
              <input
                value={selectedLeague}
                onChange={e => setSelectedLeague(e.target.value)}
                list="leagues-list"
                placeholder="es. serie-a"
                data-testid="bulk-league-input"
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm focus:border-blue-500 focus:outline-none"
              />
              <datalist id="leagues-list">
                {leagues.map(s => <option key={s} value={s} />)}
              </datalist>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Tipo</label>
              <select
                value={bulkType}
                onChange={e => setBulkType(e.target.value)}
                data-testid="bulk-type-select"
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm focus:border-blue-500 focus:outline-none"
              >
                <option value="team">Squadre</option>
                <option value="event">Eventi</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-400 mb-1 block">Limit</label>
              <input
                type="number"
                value={bulkLimit}
                onChange={e => setBulkLimit(e.target.value)}
                min="1"
                max="50"
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm focus:border-blue-500 focus:outline-none"
              />
            </div>
            <div className="flex items-end">
              <label className="text-xs text-gray-300 inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={onlyPending}
                  onChange={e => setOnlyPending(e.target.checked)}
                  className="w-4 h-4"
                />
                Solo non pubblicati
              </label>
            </div>
          </div>
          <button
            onClick={launchBulk}
            disabled={launching}
            data-testid="bulk-launch-btn"
            className="mt-4 px-5 py-2.5 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-sm font-semibold inline-flex items-center gap-2 disabled:opacity-50"
          >
            {launching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
            Avvia Bulk Generation
          </button>
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
            <button
              onClick={() => downloadExport('json')}
              data-testid="export-json-btn"
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold inline-flex items-center gap-2"
            >
              <Download className="w-4 h-4" /> JSON
            </button>
            <button
              onClick={() => downloadExport('csv')}
              data-testid="export-csv-btn"
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold inline-flex items-center gap-2"
            >
              <Download className="w-4 h-4" /> CSV
            </button>
            <button
              onClick={() => downloadExport('ndjson')}
              data-testid="export-ndjson-btn"
              className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold inline-flex items-center gap-2"
            >
              <Download className="w-4 h-4" /> NDJSON
            </button>
          </div>
        </div>

        {/* Jobs Table */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold text-white">Jobs ({jobs.length})</h2>
            <div className="flex items-center gap-3">
              <label className="text-xs text-gray-300 inline-flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={e => setAutoRefresh(e.target.checked)}
                  className="w-4 h-4"
                />
                Auto-refresh
              </label>
              <button
                onClick={loadJobs}
                className="px-3 py-1.5 rounded bg-gray-700 hover:bg-gray-600 text-xs text-white inline-flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" /> Refresh
              </button>
            </div>
          </div>

          {/* Stats */}
          <div className="flex flex-wrap gap-2 mb-4">
            {Object.entries(stats).map(([k, v]) => (
              <span key={k} className={`px-3 py-1 rounded text-xs font-bold ${STATUS_BADGE[k]}`}>
                {k}: {v}
              </span>
            ))}
          </div>

          {/* Table */}
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
                      <a
                        href={`/admin/seo/targets/${j.target_type}/${j.target_id}`}
                        className="text-blue-400 hover:text-blue-300"
                      >
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
