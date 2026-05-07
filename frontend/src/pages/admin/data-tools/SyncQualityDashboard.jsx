import React, { useEffect, useState, useCallback } from 'react';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import { Loader2, RefreshCw, TrendingUp, Database, Image as ImageIcon, AlertTriangle, CheckCircle2, Wand2, Camera } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const StatCard = ({ icon: Icon, label, value, sub, color = 'blue', testId }) => (
  <div data-testid={testId} className={`rounded-xl border border-${color}-700/40 bg-${color}-900/10 p-4`}>
    <div className="flex items-center justify-between mb-2">
      <span className="text-xs uppercase text-gray-400 font-semibold">{label}</span>
      <Icon className={`w-4 h-4 text-${color}-400`} />
    </div>
    <div className="text-3xl font-bold text-white">{value}</div>
    {sub && <div className="text-[11px] text-gray-500 mt-1">{sub}</div>}
  </div>
);

const SeoSyncQuality = () => {
  const { authFetch } = useAdminAuth();
  const [stats, setStats] = useState(null);
  const [syncRuns, setSyncRuns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [snapshotting, setSnapshotting] = useState(false);
  const [fixingSlug, setFixingSlug] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [s, sr] = await Promise.all([
        authFetch(`${API_URL}/api/data-tools/sync-quality/stats`),
        authFetch(`${API_URL}/api/data-tools/sync-quality/sync-runs`),
      ]);
      if (s.ok) setStats(await s.json());
      if (sr.ok) setSyncRuns((await sr.json()).items || []);
    } catch (e) { /* ignore */ }
    finally { setLoading(false); }
  }, [authFetch]);

  useEffect(() => { load(); }, [load]);

  const takeSnapshot = async () => {
    setSnapshotting(true);
    try {
      const r = await authFetch(`${API_URL}/api/data-tools/sync-quality/snapshot`, { method: 'POST' });
      if (r.ok) { toast.success('Snapshot salvato'); load(); }
    } catch (e) { toast.error('Errore'); }
    finally { setSnapshotting(false); }
  };

  const fixOne = async (slug) => {
    setFixingSlug(slug);
    try {
      const r = await authFetch(`${API_URL}/api/data-tools/health/fix-team/${slug}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode: 'balanced' }),
      });
      const d = await r.json();
      if (r.ok && d.applied) toast.success(`${slug} fixato`);
      else if (r.ok) toast.info(`${slug}: nessun fix possibile`);
      else toast.error(d.error || 'Errore');
      load();
    } catch (e) { toast.error('Errore di rete'); }
    finally { setFixingSlug(null); }
  };

  const t = stats?.totals || {};
  const norm = stats?.normalize || {};
  const fixes = stats?.health_fixes || {};
  const lc = stats?.logo_coverage || {};
  const sp = stats?.seo_published || {};
  const trend = stats?.trend || [];

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-white inline-flex items-center gap-2">
              <TrendingUp className="w-7 h-7 text-cyan-400" /> Sync Quality Dashboard
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              Metriche real-time della qualità del DB: normalize, auto-fix, logo coverage, missing data, trend storico.
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={takeSnapshot}
              disabled={snapshotting}
              data-testid="snapshot-btn"
              className="px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-semibold inline-flex items-center gap-2 disabled:opacity-50"
            >
              {snapshotting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Camera className="w-4 h-4" />}
              Snapshot
            </button>
            <button
              onClick={load}
              className="px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white text-sm inline-flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" /> Aggiorna
            </button>
          </div>
        </div>

        {loading && !stats && (
          <div className="text-center text-gray-400 py-12 inline-flex items-center justify-center gap-2 w-full">
            <Loader2 className="w-5 h-5 animate-spin" /> Caricamento...
          </div>
        )}

        {stats && (
          <>
            {/* Top metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5">
              <StatCard icon={Database} label="Events" value={t.events || 0} sub={`${sp.events || 0} pubblicati SEO`} color="blue" testId="stat-events" />
              <StatCard icon={Database} label="Teams" value={t.teams || 0} sub={`${sp.teams || 0} pubblicati SEO`} color="emerald" testId="stat-teams" />
              <StatCard icon={Database} label="Leagues" value={t.leagues || 0} sub={`${sp.leagues || 0} pubblicate SEO`} color="purple" testId="stat-leagues" />
              <StatCard icon={ImageIcon} label="Logo Coverage" value={`${lc.coverage_pct || 0}%`} sub={`${lc.proxied_local || 0} locale + ${lc.external_url || 0} ext`} color="orange" testId="stat-logo" />
            </div>

            {/* Activity 24h/7d */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
              <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
                <h3 className="text-xs uppercase text-gray-400 font-semibold mb-3">Normalize ultime 24h</h3>
                <div className="grid grid-cols-3 gap-2">
                  <div><div className="text-2xl font-bold text-cyan-400">{norm.last_24h?.events || 0}</div><div className="text-[10px] text-gray-500">events</div></div>
                  <div><div className="text-2xl font-bold text-cyan-400">{norm.last_24h?.teams || 0}</div><div className="text-[10px] text-gray-500">teams</div></div>
                  <div><div className="text-2xl font-bold text-cyan-400">{norm.last_24h?.leagues || 0}</div><div className="text-[10px] text-gray-500">leagues</div></div>
                </div>
              </div>

              <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
                <h3 className="text-xs uppercase text-gray-400 font-semibold mb-3">AI Health Fixes (7gg)</h3>
                <div className="grid grid-cols-3 gap-2">
                  <div><div className="text-2xl font-bold text-purple-400">{fixes.last_7d || 0}</div><div className="text-[10px] text-gray-500">total</div></div>
                  <div><div className="text-2xl font-bold text-pink-400">{fixes.logo_added_7d || 0}</div><div className="text-[10px] text-gray-500">logo nuovi</div></div>
                  <div><div className="text-2xl font-bold text-orange-400">{fixes.logo_replaced_7d || 0}</div><div className="text-[10px] text-gray-500">logo sostituiti</div></div>
                </div>
              </div>

              <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
                <h3 className="text-xs uppercase text-gray-400 font-semibold mb-3">Logo Status</h3>
                <div className="grid grid-cols-3 gap-2">
                  <div><div className="text-2xl font-bold text-emerald-400">{lc.proxied_local || 0}</div><div className="text-[10px] text-gray-500">cached</div></div>
                  <div><div className="text-2xl font-bold text-blue-400">{lc.external_url || 0}</div><div className="text-[10px] text-gray-500">url ext</div></div>
                  <div><div className="text-2xl font-bold text-red-400">{lc.missing || 0}</div><div className="text-[10px] text-gray-500">mancanti</div></div>
                </div>
              </div>
            </div>

            {/* Trend chart (sparkline) */}
            {trend.length > 0 && (
              <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6">
                <h3 className="text-base font-bold text-white mb-3 inline-flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-cyan-400" /> Trend storico (ultimi {trend.length} snapshot)
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {[
                    { key: 'logo_proxied', label: 'Logo cached', color: 'emerald' },
                    { key: 'logo_missing', label: 'Logo mancanti', color: 'red' },
                    { key: 'fixes_24h', label: 'Fix automatici', color: 'purple' },
                    { key: 'teams_published', label: 'Team SEO pub.', color: 'blue' },
                  ].map(({ key, label, color }) => {
                    const max = Math.max(...trend.map(s => s[key] || 0), 1);
                    return (
                      <div key={key} className="bg-gray-900/40 rounded p-3">
                        <div className="text-[10px] text-gray-400 uppercase mb-2">{label}</div>
                        <div className="flex items-end gap-0.5 h-12">
                          {trend.map((s, i) => (
                            <div
                              key={i}
                              className={`flex-1 bg-${color}-500/60 rounded-t`}
                              style={{ height: `${((s[key] || 0) / max) * 100}%` }}
                              title={`${s.date}: ${s[key] || 0}`}
                            />
                          ))}
                        </div>
                        <div className="text-xs text-gray-300 mt-2 font-bold">{trend[trend.length - 1]?.[key] || 0}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Top Missing Data */}
            <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-base font-bold text-white inline-flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" /> Top 20 team con dati mancanti ({stats.missing_data_total || 0} totali)
                </h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left border-b border-gray-700 text-xs text-gray-400 uppercase">
                      <th className="py-2 px-2">#</th>
                      <th className="py-2 px-2">Team</th>
                      <th className="py-2 px-2">Slug</th>
                      <th className="py-2 px-2">Missing</th>
                      <th className="py-2 px-2 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(stats.missing_data_top || []).map((t, i) => (
                      <tr key={t.slug} className="border-b border-gray-800 text-gray-300 hover:bg-gray-900/30">
                        <td className="py-2 px-2 text-gray-500">{i + 1}</td>
                        <td className="py-2 px-2 font-semibold">{t.name}</td>
                        <td className="py-2 px-2 text-[11px] font-mono text-gray-400">{t.slug}</td>
                        <td className="py-2 px-2">
                          <div className="flex flex-wrap gap-1">
                            {t.missing.map(m => (
                              <span key={m} className="px-2 py-0.5 rounded bg-red-900/30 text-red-300 text-[10px] uppercase">{m}</span>
                            ))}
                          </div>
                        </td>
                        <td className="py-2 px-2 text-right">
                          <button
                            onClick={() => fixOne(t.slug)}
                            disabled={fixingSlug === t.slug}
                            className="px-3 py-1 rounded bg-purple-600 hover:bg-purple-700 text-white text-xs inline-flex items-center gap-1 disabled:opacity-50"
                          >
                            {fixingSlug === t.slug ? <Loader2 className="w-3 h-3 animate-spin" /> : <Wand2 className="w-3 h-3" />}
                            Fix AI
                          </button>
                        </td>
                      </tr>
                    ))}
                    {(stats.missing_data_top || []).length === 0 && (
                      <tr><td colSpan={5} className="py-6 text-center text-gray-500 inline-flex items-center justify-center gap-2 w-full">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Nessun dato mancante
                      </td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Recent sync runs */}
            {syncRuns.length > 0 && (
              <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
                <h3 className="text-base font-bold text-white mb-3">Ultimi sync runs (matchesio)</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left border-b border-gray-700 text-xs text-gray-400 uppercase">
                        <th className="py-2 px-2">Started</th>
                        <th className="py-2 px-2">Duration</th>
                        <th className="py-2 px-2">Inserted</th>
                        <th className="py-2 px-2">Updated</th>
                        <th className="py-2 px-2">Errors</th>
                      </tr>
                    </thead>
                    <tbody>
                      {syncRuns.map((r, i) => (
                        <tr key={i} className="border-b border-gray-800 text-gray-300">
                          <td className="py-2 px-2 text-[11px]">{r.started_at?.slice(0, 19).replace('T', ' ')}</td>
                          <td className="py-2 px-2">{r.duration_seconds ? `${Math.round(r.duration_seconds)}s` : '-'}</td>
                          <td className="py-2 px-2 text-emerald-300 font-mono">{r.total_inserted || 0}</td>
                          <td className="py-2 px-2 text-blue-300 font-mono">{r.total_updated || 0}</td>
                          <td className="py-2 px-2 text-red-300 font-mono">{r.total_errors || 0}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </AdminLayout>
  );
};

export default SeoSyncQuality;
