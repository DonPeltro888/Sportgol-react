import React, { useEffect, useState, useCallback } from 'react';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import { Loader2, Activity, Wand2, Download, RefreshCw, AlertTriangle, CheckCircle2, ShieldCheck } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SEVERITY = {
  high: 'bg-red-600 text-white',
  medium: 'bg-amber-600 text-white',
  low: 'bg-gray-600 text-white',
};

const CATEGORY_LABELS = {
  missing_data: '📋 Dati mancanti',
  logo_collision: '🖼️ Logo collision',
  name_confusion: '⚠️ Name confusion',
  fuzzy_duplicate: '🔁 Possibile duplicato',
  duplicate_slug: '🔁 Slug duplicato',
  orphan_event_team: '👻 Team orfano (event)',
  event_missing_data: '📋 Event dati mancanti',
  league_missing_data: '📋 League dati mancanti',
};

const SeoHealthDashboard = () => {
  const { authFetch } = useAdminAuth();
  const [report, setReport] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [filter, setFilter] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [job, setJob] = useState(null);
  const [bulkLaunching, setBulkLaunching] = useState(false);
  const [fixingSlug, setFixingSlug] = useState(null);

  const loadLatest = useCallback(async () => {
    try {
      const r = await authFetch(`${API_URL}/api/seo/health/report/latest`);
      if (r.ok) {
        const d = await r.json();
        if (!d.error) setReport(d);
      }
    } catch (e) {/* ignore */}
  }, [authFetch]);

  useEffect(() => { loadLatest(); }, [loadLatest]);

  const runScan = async () => {
    setScanning(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/health/run`, { method: 'POST' });
      if (r.ok) {
        const d = await r.json();
        toast.success(`Scan completato: ${d.summary.total_issues} issue trovati`);
        await loadLatest();
      } else toast.error('Errore scan');
    } catch (e) { toast.error('Errore di rete'); }
    finally { setScanning(false); }
  };

  const downloadExport = async (format) => {
    try {
      const r = await authFetch(`${API_URL}/api/seo/health/export?format=${format}`);
      if (!r.ok) return toast.error('Errore export (esegui prima scan)');
      const blob = await r.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const ts = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-');
      a.download = `health-report-${ts}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Report ${format.toUpperCase()} scaricato`);
    } catch (e) { toast.error('Errore download'); }
  };

  const fixOne = async (slug) => {
    setFixingSlug(slug);
    try {
      const r = await authFetch(`${API_URL}/api/seo/health/fix-team/${slug}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'balanced' }),
      });
      const d = await r.json();
      if (r.ok && d.applied) {
        toast.success(`${slug} fixato: ${d.actions.join(', ')}`);
      } else if (r.ok && !d.applied) {
        toast.info(`${slug}: nessun fix necessario`);
      } else toast.error(d.error || 'Errore fix');
    } catch (e) { toast.error('Errore di rete'); }
    finally { setFixingSlug(null); }
  };

  const launchBulkFix = async (categories) => {
    if (!window.confirm(`Avviare bulk fix con AI Vision?\nVerranno processati i team con issue nelle categorie: ${categories.join(', ')}.\nUsa Perplexity (metadati) + Gemini Vision (loghi).`)) return;
    setBulkLaunching(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/health/fix-bulk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'balanced', only_categories: categories, limit: 100 }),
      });
      const d = await r.json();
      if (r.ok && d.job_id) {
        toast.info(`Bulk fix avviato: ${d.queued} team in coda`);
        pollJob(d.job_id);
      } else toast.error('Errore avvio');
    } catch (e) { toast.error('Errore di rete'); }
    finally { setBulkLaunching(false); }
  };

  const pollJob = async (jobId) => {
    for (let i = 0; i < 200; i++) {
      await new Promise(r => setTimeout(r, 4000));
      try {
        const r = await authFetch(`${API_URL}/api/seo/health/fix-jobs/${jobId}`);
        if (r.ok) {
          const d = await r.json();
          setJob(d);
          if (d.status === 'succeeded' || d.status === 'failed') {
            toast.success(`Bulk fix terminato: ${d.fixed}/${d.total} team aggiornati`);
            await loadLatest();
            return;
          }
        }
      } catch (e) { /* ignore */ }
    }
  };

  // Aggregate issues
  const allIssues = report ? [
    ...(report.teams?.issues || []),
    ...(report.events?.issues || []),
    ...(report.leagues?.issues || []),
  ] : [];

  const filtered = allIssues.filter(it => {
    if (filter !== 'all' && it.category !== filter) return false;
    if (filterSeverity !== 'all' && it.severity !== filterSeverity) return false;
    return true;
  });

  const summary = report?.summary || {};

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white inline-flex items-center gap-2">
            <ShieldCheck className="w-7 h-7 text-emerald-400" /> SEO Data Health Check
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Diagnosi e correzione automatica con AI: Perplexity (metadata) + Gemini Vision (loghi).
          </p>
        </div>

        {/* Action Bar */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5 mb-6 flex flex-wrap gap-3 items-center">
          <button
            onClick={runScan}
            disabled={scanning}
            data-testid="health-scan-btn"
            className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold inline-flex items-center gap-2 disabled:opacity-50"
          >
            {scanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            Esegui Scan
          </button>

          <button
            onClick={() => launchBulkFix(['missing_data', 'logo_collision'])}
            disabled={bulkLaunching || !report}
            data-testid="health-fix-bulk-btn"
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white text-sm font-semibold inline-flex items-center gap-2 disabled:opacity-50"
          >
            {bulkLaunching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
            Fix Auto (missing + loghi)
          </button>

          <div className="ml-auto flex gap-2">
            <button
              onClick={() => downloadExport('json')}
              className="px-3 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white text-sm inline-flex items-center gap-1"
            >
              <Download className="w-4 h-4" /> JSON
            </button>
            <button
              onClick={() => downloadExport('csv')}
              className="px-3 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-800 text-white text-sm inline-flex items-center gap-1"
            >
              <Download className="w-4 h-4" /> CSV
            </button>
          </div>
        </div>

        {/* Job progress */}
        {job && job.status !== 'succeeded' && job.status !== 'failed' && (
          <div className="rounded-xl border border-blue-700/40 bg-blue-900/10 p-4 mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-blue-200 inline-flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                Bulk Fix in corso: {job.processed}/{job.total} ({job.fixed} fixed)
              </span>
              <span className="text-xs text-blue-300 font-mono">{Math.round((job.processed / Math.max(1, job.total)) * 100)}%</span>
            </div>
            <div className="w-full h-2 bg-gray-800 rounded overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all"
                style={{ width: `${(job.processed / Math.max(1, job.total)) * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* Summary cards */}
        {report && (
          <>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
              <div className="rounded-lg border border-gray-700 bg-gray-800/40 p-4">
                <div className="text-xs text-gray-400 uppercase">Total Issues</div>
                <div className="text-3xl font-bold text-white mt-1">{summary.total_issues || 0}</div>
              </div>
              <div className="rounded-lg border border-red-700/40 bg-red-900/10 p-4">
                <div className="text-xs text-red-300 uppercase">High</div>
                <div className="text-3xl font-bold text-red-400 mt-1">{summary.by_severity?.high || 0}</div>
              </div>
              <div className="rounded-lg border border-amber-700/40 bg-amber-900/10 p-4">
                <div className="text-xs text-amber-300 uppercase">Medium</div>
                <div className="text-3xl font-bold text-amber-400 mt-1">{summary.by_severity?.medium || 0}</div>
              </div>
              <div className="rounded-lg border border-gray-700 bg-gray-800/40 p-4">
                <div className="text-xs text-gray-400 uppercase">Low</div>
                <div className="text-3xl font-bold text-gray-400 mt-1">{summary.by_severity?.low || 0}</div>
              </div>
            </div>

            {/* Category filters */}
            <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-4 mb-3">
              <div className="text-xs text-gray-400 mb-2 uppercase font-semibold">Filtra per categoria</div>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setFilter('all')}
                  className={`px-3 py-1.5 rounded text-xs ${filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                >
                  Tutte ({summary.total_issues || 0})
                </button>
                {Object.entries(summary.by_category || {}).sort((a, b) => b[1] - a[1]).map(([cat, count]) => (
                  <button
                    key={cat}
                    onClick={() => setFilter(cat)}
                    className={`px-3 py-1.5 rounded text-xs ${filter === cat ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'}`}
                  >
                    {CATEGORY_LABELS[cat] || cat} ({count})
                  </button>
                ))}
              </div>
              <div className="mt-3 flex gap-2">
                <span className="text-xs text-gray-400 self-center">Severity:</span>
                {['all', 'high', 'medium', 'low'].map(s => (
                  <button
                    key={s}
                    onClick={() => setFilterSeverity(s)}
                    className={`px-2.5 py-1 rounded text-[10px] uppercase ${filterSeverity === s ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'}`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {/* Issues list */}
            <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-base font-bold text-white">Issues ({filtered.length})</h3>
              </div>
              <div className="space-y-1.5 max-h-[600px] overflow-y-auto">
                {filtered.slice(0, 200).map((it, i) => (
                  <div key={i} className="flex items-start gap-2 text-xs border border-gray-700 rounded p-2 hover:bg-gray-900/30">
                    <span className={`px-2 py-0.5 rounded text-[9px] uppercase font-bold ${SEVERITY[it.severity || 'low']}`}>
                      {it.severity}
                    </span>
                    <span className="text-gray-300 font-semibold whitespace-nowrap">
                      {CATEGORY_LABELS[it.category] || it.category}
                    </span>
                    <span className="text-gray-400 flex-1 break-words">
                      {(() => {
                        const { category, severity, ...rest } = it;
                        return JSON.stringify(rest, null, 0).slice(0, 220);
                      })()}
                    </span>
                    {it.team_slug && (
                      <button
                        onClick={() => fixOne(it.team_slug)}
                        disabled={fixingSlug === it.team_slug}
                        className="px-2 py-0.5 rounded bg-purple-600 hover:bg-purple-700 text-white text-[10px] inline-flex items-center gap-1 disabled:opacity-50 whitespace-nowrap"
                      >
                        {fixingSlug === it.team_slug ? <Loader2 className="w-3 h-3 animate-spin" /> : <Wand2 className="w-3 h-3" />}
                        Fix
                      </button>
                    )}
                  </div>
                ))}
                {filtered.length === 0 && (
                  <div className="py-8 text-center text-gray-500 text-sm inline-flex items-center justify-center gap-2 w-full">
                    <CheckCircle2 className="w-5 h-5 text-emerald-500" /> Nessun issue
                  </div>
                )}
                {filtered.length > 200 && (
                  <div className="py-2 text-center text-gray-500 text-xs">
                    +{filtered.length - 200} altri (visibili tramite Export CSV/JSON)
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {!report && !scanning && (
          <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-8 text-center">
            <Activity className="w-12 h-12 text-gray-600 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-white mb-2">Nessun report disponibile</h3>
            <p className="text-sm text-gray-400 mb-4">Avvia il primo scan per vedere lo stato dei dati nel DB.</p>
            <button
              onClick={runScan}
              className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold inline-flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" /> Esegui Primo Scan
            </button>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default SeoHealthDashboard;
