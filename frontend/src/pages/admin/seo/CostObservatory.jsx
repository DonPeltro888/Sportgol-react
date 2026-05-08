import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import {
  DollarSign, Activity, TrendingUp, AlertTriangle, Zap, Clock, Database, Mail,
  ChevronLeft, RefreshCw, Download, Settings, Loader2, CheckCircle2, XCircle,
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SEVERITY_COLOR = {
  HIGH: 'bg-red-600 text-white',
  MEDIUM: 'bg-amber-600 text-white',
  LOW: 'bg-gray-600 text-gray-200',
};

const ALERT_ICON = {
  BUDGET_WARNING: TrendingUp,
  BUDGET_EXCEEDED: AlertTriangle,
  LOW_BALANCE: DollarSign,
  API_DOWN: XCircle,
  API_INTERMITTENT: Activity,
};

const Stat = ({ label, value, sub, icon: Icon, color = 'text-white', testid }) => (
  <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-3.5" data-testid={testid}>
    <div className="flex items-center gap-2 text-gray-400 text-xs">
      {Icon && <Icon className="w-3.5 h-3.5" />} {label}
    </div>
    <div className={`mt-1 text-2xl font-bold ${color}`}>{value}</div>
    {sub && <div className="text-[11px] text-gray-500 mt-0.5">{sub}</div>}
  </div>
);

const fmtUsd = (n) => `$${(n || 0).toFixed(n < 0.1 ? 4 : 2)}`;

const CostObservatory = () => {
  const { authFetch } = useAdminAuth();
  const [overview, setOverview] = useState(null);
  const [providers, setProviders] = useState([]);
  const [topEntities, setTopEntities] = useState([]);
  const [byType, setByType] = useState([]);
  const [chart, setChart] = useState([]);
  const [logs, setLogs] = useState({ items: [], total: 0 });
  const [alerts, setAlerts] = useState([]);
  const [latency, setLatency] = useState([]);
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [logFilter, setLogFilter] = useState({ provider: '', status: '' });
  const [showPricing, setShowPricing] = useState(false);
  const [showBudgets, setShowBudgets] = useState(false);
  const [showAlertConfig, setShowAlertConfig] = useState(false);

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [o, p, te, bt, c, a, lat] = await Promise.all([
        authFetch(`${API_URL}/api/seo/cost-observatory/overview`),
        authFetch(`${API_URL}/api/seo/cost-observatory/providers`),
        authFetch(`${API_URL}/api/seo/cost-observatory/entities/top?days=30&limit=10`),
        authFetch(`${API_URL}/api/seo/cost-observatory/entities/by-type?days=30`),
        authFetch(`${API_URL}/api/seo/cost-observatory/chart/daily?days=30`),
        authFetch(`${API_URL}/api/seo/cost-observatory/alerts/open`),
        authFetch(`${API_URL}/api/seo/cost-observatory/latency?days=7`),
      ]);
      if (o.ok) setOverview(await o.json());
      if (p.ok) setProviders((await p.json()).rows || []);
      if (te.ok) setTopEntities((await te.json()).rows || []);
      if (bt.ok) setByType((await bt.json()).rows || []);
      if (c.ok) setChart((await c.json()).rows || []);
      if (a.ok) setAlerts((await a.json()).items || []);
      if (lat.ok) setLatency((await lat.json()).rows || []);
    } finally { setLoading(false); }
  }, [authFetch]);

  const loadLogs = useCallback(async () => {
    const params = new URLSearchParams({ limit: '50' });
    if (logFilter.provider) params.set('provider', logFilter.provider);
    if (logFilter.status) params.set('status', logFilter.status);
    const r = await authFetch(`${API_URL}/api/seo/cost-observatory/logs?${params}`);
    if (r.ok) setLogs(await r.json());
  }, [authFetch, logFilter.provider, logFilter.status]);

  useEffect(() => { loadAll(); }, [loadAll]);
  useEffect(() => { loadLogs(); }, [loadLogs]);

  const runAlertChecks = async () => {
    toast.info('Lancio check alert in corso...');
    const r = await authFetch(`${API_URL}/api/seo/cost-observatory/alerts/run-checks`, { method: 'POST' });
    if (r.ok) {
      const d = await r.json();
      toast.success(`Check completato: ${d.new_alerts_count || 0} nuovi alert`);
      loadAll();
    }
  };

  const checkBalance = async () => {
    setBalance({ loading: true });
    const r = await authFetch(`${API_URL}/api/seo/cost-observatory/balance`);
    if (r.ok) setBalance(await r.json());
    else setBalance({ error: 'Errore' });
  };

  const ackAlert = async (id) => {
    await authFetch(`${API_URL}/api/seo/cost-observatory/alerts/${id}/ack`, { method: 'POST' });
    loadAll();
  };

  const exportCsv = () => {
    const params = new URLSearchParams({ days: '30' });
    if (logFilter.provider) params.set('provider', logFilter.provider);
    window.open(`${API_URL}/api/seo/cost-observatory/export?${params}&token=${localStorage.getItem('admin_token')}`, '_blank');
  };

  const backfill = async () => {
    if (!window.confirm('Ricostruisco i log dagli ultimi 30gg da seo_jobs?')) return;
    const r = await authFetch(`${API_URL}/api/seo/cost-observatory/backfill?days=30`, { method: 'POST' });
    const d = await r.json();
    if (r.ok) {
      toast.success(`Backfill OK: +${d.logs_inserted} log inseriti`);
      loadAll();
    }
  };

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto">
        <Link to="/admin/seo" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
          <ChevronLeft className="w-4 h-4" /> Torna a SEO Dashboard
        </Link>

        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3 mb-6">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-white inline-flex items-center gap-2">
              <DollarSign className="w-7 h-7 text-emerald-400" /> API Cost Observatory
            </h1>
            <p className="text-sm text-gray-400 mt-1">
              Spesa, last-used, latency, failure rate, budget alerts, top expensive entities. 17 metriche enterprise.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button onClick={loadAll} className="px-3 py-2 rounded bg-gray-700 hover:bg-gray-600 text-white text-xs inline-flex items-center gap-1">
              <RefreshCw className="w-3.5 h-3.5" /> Refresh
            </button>
            <button onClick={runAlertChecks} className="px-3 py-2 rounded bg-amber-600 hover:bg-amber-700 text-white text-xs inline-flex items-center gap-1" data-testid="cost-run-checks">
              <AlertTriangle className="w-3.5 h-3.5" /> Run alert check
            </button>
            <button onClick={checkBalance} className="px-3 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-xs inline-flex items-center gap-1" data-testid="cost-check-balance">
              <DollarSign className="w-3.5 h-3.5" /> Check balance
            </button>
            <button onClick={exportCsv} className="px-3 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white text-xs inline-flex items-center gap-1">
              <Download className="w-3.5 h-3.5" /> Export CSV
            </button>
            <button onClick={() => setShowAlertConfig(true)} className="px-3 py-2 rounded bg-pink-600 hover:bg-pink-700 text-white text-xs inline-flex items-center gap-1" data-testid="cost-alert-config">
              <Mail className="w-3.5 h-3.5" /> Email/SMTP
            </button>
            <button onClick={backfill} className="px-3 py-2 rounded bg-gray-700 hover:bg-gray-600 text-white text-xs inline-flex items-center gap-1">
              <Database className="w-3.5 h-3.5" /> Backfill 30g
            </button>
          </div>
        </div>

        {/* Stats overview */}
        {loading ? (
          <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-8 text-center">
            <Loader2 className="w-6 h-6 animate-spin text-gray-500 mx-auto" />
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-4 xl:grid-cols-8 gap-3 mb-6">
            <Stat label="Today" value={fmtUsd(overview?.today?.cost)} sub={`${overview?.today?.calls || 0} calls`} icon={Activity} color="text-emerald-300" testid="stat-today" />
            <Stat label="Week" value={fmtUsd(overview?.week?.cost)} sub={`${overview?.week?.calls || 0} calls`} icon={Activity} color="text-blue-300" />
            <Stat label="Month" value={fmtUsd(overview?.month?.cost)} sub={`${overview?.month?.calls || 0} calls`} icon={Activity} color="text-purple-300" testid="stat-month" />
            <Stat label="Forecast" value={fmtUsd(overview?.forecast_month_usd)} sub="run-rate × 30d" icon={TrendingUp} color="text-amber-300" testid="stat-forecast" />
            <Stat label="Calls today" value={(overview?.today?.calls || 0).toLocaleString()} icon={Zap} color="text-cyan-300" />
            <Stat label="Success rate" value={`${(overview?.month?.success_rate || 100).toFixed(1)}%`} sub={`${overview?.month?.fails || 0} fails / mo`} icon={CheckCircle2} color={(overview?.month?.success_rate || 100) > 95 ? 'text-emerald-300' : 'text-red-300'} />
            <Stat label="Avg latency" value={`${overview?.month?.avg_latency_ms || 0} ms`} icon={Clock} color="text-blue-300" />
            <Stat label="Top provider" value={overview?.top_provider || '—'} icon={DollarSign} color="text-pink-300" />
          </div>
        )}

        {/* Open alerts */}
        {alerts.length > 0 && (
          <div className="rounded-xl border border-red-700/50 bg-red-900/20 p-4 mb-6">
            <h2 className="text-base font-bold text-red-200 mb-2 inline-flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" /> {alerts.length} Alert aperti
            </h2>
            <div className="space-y-2 max-h-[280px] overflow-y-auto">
              {alerts.map((a, i) => {
                const Icon = ALERT_ICON[a.alert_type] || AlertTriangle;
                return (
                  <div key={i} className="flex items-start gap-2 p-2.5 rounded bg-gray-900/40 border border-red-700/30">
                    <Icon className={`w-4 h-4 mt-0.5 ${a.severity === 'HIGH' ? 'text-red-400' : 'text-amber-400'}`} />
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${SEVERITY_COLOR[a.severity]}`}>{a.severity}</span>
                        <span className="text-white font-semibold text-sm">{a.title}</span>
                        <span className="text-[10px] text-gray-500 ml-auto font-mono">{(a.ts || '').slice(0, 19).replace('T', ' ')}</span>
                      </div>
                      <div className="text-xs text-gray-300 mt-1">{a.message}</div>
                      {a.details?.last_error_code && (
                        <div className="text-[10px] text-red-300 mt-1 font-mono">
                          Errore: {a.details.last_error_code} — {a.details.last_error_msg?.slice(0, 100)}
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => a._id && ackAlert(a._id)}
                      className="text-[10px] px-2 py-0.5 rounded bg-gray-700 hover:bg-gray-600 text-white"
                    >
                      Ack
                    </button>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Providers table */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold text-white">📊 Per Provider (mese corrente)</h2>
            <div className="flex gap-2">
              <button onClick={() => setShowPricing(true)} className="text-xs px-3 py-1.5 rounded bg-gray-700 hover:bg-gray-600 text-white inline-flex items-center gap-1">
                <Settings className="w-3.5 h-3.5" /> Pricing
              </button>
              <button onClick={() => setShowBudgets(true)} className="text-xs px-3 py-1.5 rounded bg-gray-700 hover:bg-gray-600 text-white inline-flex items-center gap-1" data-testid="cost-budgets-btn">
                <DollarSign className="w-3.5 h-3.5" /> Budget
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-900/40 text-gray-400 text-xs uppercase">
                <tr>
                  <th className="text-left px-3 py-2">Provider</th>
                  <th className="text-right px-3 py-2">Cost mese</th>
                  <th className="text-center px-3 py-2">Budget</th>
                  <th className="text-center px-3 py-2">Calls</th>
                  <th className="text-center px-3 py-2">Success</th>
                  <th className="text-center px-3 py-2">Avg lat</th>
                  <th className="text-center px-3 py-2">Last used</th>
                </tr>
              </thead>
              <tbody>
                {providers.map((p) => (
                  <tr key={p.provider} className="border-t border-gray-700/50 hover:bg-gray-900/30">
                    <td className="px-3 py-2 text-white font-semibold">{p.provider}</td>
                    <td className="px-3 py-2 text-right font-mono text-emerald-300">{fmtUsd(p.cost_month_usd)}</td>
                    <td className="px-3 py-2 text-center">
                      {p.monthly_limit_usd ? (
                        <div>
                          <div className="text-[11px] text-gray-300">{fmtUsd(p.cost_month_usd)} / {fmtUsd(p.monthly_limit_usd)}</div>
                          <div className="w-24 h-1.5 bg-gray-800 rounded overflow-hidden mt-1 mx-auto">
                            <div className={`h-full ${p.budget_status === 'exceeded' ? 'bg-red-500' : p.budget_status === 'warning' ? 'bg-amber-500' : 'bg-emerald-500'}`} style={{ width: `${Math.min(p.budget_pct || 0, 100)}%` }} />
                          </div>
                          <div className="text-[10px] text-gray-500 mt-0.5">{(p.budget_pct || 0).toFixed(1)}%</div>
                        </div>
                      ) : <span className="text-[11px] text-gray-500">no limit</span>}
                    </td>
                    <td className="px-3 py-2 text-center text-blue-300">{p.calls_month}</td>
                    <td className="px-3 py-2 text-center">
                      <span className={p.success_rate_pct >= 95 ? 'text-emerald-300' : 'text-red-300'}>
                        {p.success_rate_pct.toFixed(1)}%
                      </span>
                      {p.fails_month > 0 && <span className="text-[10px] text-red-400 ml-1">({p.fails_month} fails)</span>}
                    </td>
                    <td className="px-3 py-2 text-center text-xs text-gray-400">{p.avg_latency_ms} ms</td>
                    <td className="px-3 py-2 text-center text-[11px] text-gray-500">
                      {p.last_used_at ? new Date(p.last_used_at).toLocaleString('it-IT', { hour: '2-digit', minute: '2-digit', day: '2-digit', month: '2-digit' }) : '—'}
                    </td>
                  </tr>
                ))}
                {providers.length === 0 && (
                  <tr><td colSpan={7} className="py-6 text-center text-gray-500">Nessun provider attivo</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Daily chart simple bar */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
            <h2 className="text-base font-bold text-white mb-3">📈 Spesa giornaliera (30gg)</h2>
            <div className="flex items-end gap-1 h-32">
              {chart.length === 0 && <div className="text-gray-500 text-sm">No data</div>}
              {chart.map((d) => {
                const max = Math.max(...chart.map(x => x.total || 0), 0.01);
                const h = ((d.total || 0) / max * 100);
                return (
                  <div key={d.day} className="flex-1 group relative">
                    <div
                      className="bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-t hover:from-emerald-500 hover:to-emerald-300 transition-colors"
                      style={{ height: `${Math.max(h, 1)}%` }}
                    />
                    <div className="absolute -top-7 left-1/2 -translate-x-1/2 hidden group-hover:block bg-black/90 text-white text-[10px] px-2 py-0.5 rounded whitespace-nowrap z-10">
                      {d.day}: {fmtUsd(d.total)}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="text-[10px] text-gray-500 mt-2 flex justify-between">
              <span>{chart[0]?.day || ''}</span>
              <span>{chart[chart.length - 1]?.day || ''}</span>
            </div>
          </div>

          {/* Latency p50/p95 */}
          <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
            <h2 className="text-base font-bold text-white mb-3">⏱️ Latency p50/p95 (7gg)</h2>
            <div className="space-y-2">
              {latency.map((l) => (
                <div key={l.provider} className="flex items-center gap-2 text-xs">
                  <span className="w-24 text-white font-mono truncate">{l.provider}</span>
                  <span className="text-emerald-300">p50: {l.p50_ms}ms</span>
                  <span className="text-amber-300">p95: {l.p95_ms}ms</span>
                  <span className="text-gray-500 ml-auto">({l.count})</span>
                </div>
              ))}
              {latency.length === 0 && <div className="text-gray-500 text-sm">No data</div>}
            </div>
          </div>
        </div>

        {/* Top entities + by type */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
          <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
            <h2 className="text-base font-bold text-white mb-3">💸 Top 10 entità più costose (30gg)</h2>
            <div className="space-y-1.5">
              {topEntities.map((e, i) => (
                <div key={i} className="flex items-center justify-between gap-2 text-sm py-1.5 border-b border-gray-700/30">
                  <div className="flex-1 min-w-0">
                    <span className="text-[10px] text-blue-300 mr-2">{e.entity_type}</span>
                    <span className="text-white font-mono truncate">{e.entity_slug}</span>
                  </div>
                  <span className="text-emerald-300 font-mono text-xs">{fmtUsd(e.cost_usd)}</span>
                  <span className="text-[10px] text-gray-500">{e.calls} calls</span>
                </div>
              ))}
              {topEntities.length === 0 && <div className="text-gray-500 text-sm py-4 text-center">Nessuna entità tracked</div>}
            </div>
          </div>

          <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
            <h2 className="text-base font-bold text-white mb-3">📂 Cost per tipo entità (30gg)</h2>
            <div className="space-y-2">
              {byType.map((t) => (
                <div key={t.entity_type} className="rounded bg-gray-900/40 p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-white font-semibold capitalize">{t.entity_type}</span>
                    <span className="text-emerald-300 font-mono">{fmtUsd(t.cost_usd)}</span>
                  </div>
                  <div className="text-[11px] text-gray-400 grid grid-cols-3 gap-2">
                    <span>{t.calls} calls</span>
                    <span>{t.unique_entities} entità</span>
                    <span>avg {fmtUsd(t.avg_cost_per_entity)}/entity</span>
                  </div>
                </div>
              ))}
              {byType.length === 0 && <div className="text-gray-500 text-sm py-4 text-center">No data</div>}
            </div>
          </div>
        </div>

        {/* Balance polling */}
        {balance && (
          <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6">
            <h2 className="text-base font-bold text-white mb-3 inline-flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-emerald-400" /> Balance status
            </h2>
            {balance.loading ? <Loader2 className="w-5 h-5 animate-spin text-gray-500" /> : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {balance.providers && Object.entries(balance.providers).map(([p, info]) => (
                  <div key={p} className="rounded bg-gray-900/40 p-3 text-xs">
                    <div className="text-white font-semibold mb-1.5">{p}</div>
                    {info.error ? <div className="text-red-300 text-[11px]">{info.error}</div> : (
                      <>
                        {info.real_polling && (
                          <div className="text-emerald-300 mb-1 text-[11px]">
                            🔌 Real: {info.real_polling.char_left != null ? `${info.real_polling.char_left.toLocaleString()} char left` : info.real_polling.note || JSON.stringify(info.real_polling).slice(0, 80)}
                          </div>
                        )}
                        <div className="text-gray-300">📊 Stimato: {fmtUsd(info.month_used_usd || 0)} usato</div>
                        {info.remaining_usd != null && <div className="text-gray-300">Rimasto: {fmtUsd(info.remaining_usd)} ({(info.pct_used || 0).toFixed(1)}%)</div>}
                        <div className="text-[10px] text-gray-500 mt-1">{info.calls_this_month || 0} calls / {info.failures_this_month || 0} fails</div>
                      </>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Logs drill-down */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6">
          <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
            <h2 className="text-base font-bold text-white">📋 Logs drill-down ({logs.total})</h2>
            <div className="flex gap-2">
              <select value={logFilter.provider} onChange={e => setLogFilter({ ...logFilter, provider: e.target.value })} className="px-2 py-1 bg-gray-900 border border-gray-700 rounded text-white text-xs">
                <option value="">Tutti i provider</option>
                {providers.map(p => <option key={p.provider} value={p.provider}>{p.provider}</option>)}
              </select>
              <select value={logFilter.status} onChange={e => setLogFilter({ ...logFilter, status: e.target.value })} className="px-2 py-1 bg-gray-900 border border-gray-700 rounded text-white text-xs">
                <option value="">Tutti</option>
                <option value="ok">OK</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>
          <div className="overflow-x-auto max-h-[420px]">
            <table className="w-full text-xs">
              <thead className="bg-gray-900/40 text-gray-400 uppercase sticky top-0">
                <tr>
                  <th className="text-left px-2 py-2">TS</th>
                  <th className="text-left px-2 py-2">Provider</th>
                  <th className="text-left px-2 py-2">Op</th>
                  <th className="text-center px-2 py-2">Status</th>
                  <th className="text-right px-2 py-2">Cost</th>
                  <th className="text-right px-2 py-2">Lat</th>
                  <th className="text-right px-2 py-2">Tokens</th>
                  <th className="text-left px-2 py-2">Entity</th>
                  <th className="text-left px-2 py-2">Error</th>
                </tr>
              </thead>
              <tbody>
                {logs.items.map((l, i) => (
                  <tr key={i} className="border-t border-gray-700/50 hover:bg-gray-900/30">
                    <td className="px-2 py-1.5 text-gray-400 font-mono">{(l.ts || '').slice(11, 19)}</td>
                    <td className="px-2 py-1.5 text-white">{l.provider}</td>
                    <td className="px-2 py-1.5 text-gray-400">{l.op_type}{l.sub_type ? `:${l.sub_type}` : ''}</td>
                    <td className="px-2 py-1.5 text-center">
                      {l.status === 'ok' ? <CheckCircle2 className="w-3 h-3 text-emerald-400 inline" /> : <XCircle className="w-3 h-3 text-red-400 inline" />}
                    </td>
                    <td className="px-2 py-1.5 text-right text-emerald-300 font-mono">{fmtUsd(l.cost_usd)}</td>
                    <td className="px-2 py-1.5 text-right text-gray-400">{l.latency_ms}ms</td>
                    <td className="px-2 py-1.5 text-right text-gray-400">{(l.tokens_in || 0) + (l.tokens_out || 0) || '—'}</td>
                    <td className="px-2 py-1.5 text-blue-300 truncate max-w-[140px]">{l.entity_slug || '—'}</td>
                    <td className="px-2 py-1.5 text-red-300 text-[10px] truncate max-w-[160px]" title={l.error_msg}>
                      {l.error_code ? `${l.error_code}: ${l.error_msg?.slice(0, 50) || ''}` : ''}
                    </td>
                  </tr>
                ))}
                {logs.items.length === 0 && (
                  <tr><td colSpan={9} className="py-6 text-center text-gray-500">Nessun log</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Modals */}
        {showBudgets && <BudgetsModal onClose={() => setShowBudgets(false)} authFetch={authFetch} onSaved={loadAll} />}
        {showPricing && <PricingModal onClose={() => setShowPricing(false)} authFetch={authFetch} />}
        {showAlertConfig && <AlertConfigModal onClose={() => setShowAlertConfig(false)} authFetch={authFetch} />}
      </div>
    </AdminLayout>
  );
};

// ============== MODALS ==============

const BudgetsModal = ({ onClose, authFetch, onSaved }) => {
  const [rows, setRows] = useState([]);
  const [editing, setEditing] = useState({ provider: '', monthly_limit_usd: 50, warning_pct: 80 });
  useEffect(() => {
    authFetch(`${API_URL}/api/seo/cost-observatory/budgets`).then(r => r.json()).then(d => setRows(d.rows || []));
  }, [authFetch]);
  const save = async () => {
    if (!editing.provider) return toast.error('Provider richiesto');
    const r = await authFetch(`${API_URL}/api/seo/cost-observatory/budgets/${editing.provider}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ monthly_limit_usd: parseFloat(editing.monthly_limit_usd), warning_pct: parseFloat(editing.warning_pct) }),
    });
    if (r.ok) { toast.success(`Budget ${editing.provider} salvato`); onSaved(); onClose(); }
    else toast.error('Errore salvataggio');
  };
  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-gray-900 rounded-xl border border-gray-700 max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <h2 className="text-lg font-bold text-white mb-4">💰 Budget per Provider</h2>
        <div className="space-y-2 mb-5 max-h-[300px] overflow-y-auto">
          {rows.map(r => (
            <div key={r.provider} className="flex justify-between p-2.5 bg-gray-800 rounded text-sm">
              <span className="text-white">{r.provider}</span>
              <span className="text-emerald-300">${r.monthly_limit_usd}/mo (warn @{r.warning_pct}%)</span>
            </div>
          ))}
        </div>
        <h3 className="text-sm font-semibold text-white mb-2">Aggiungi/Modifica</h3>
        <div className="grid grid-cols-3 gap-2 mb-3">
          <input placeholder="provider" value={editing.provider} onChange={e => setEditing({ ...editing, provider: e.target.value })} className="px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm" />
          <input type="number" placeholder="$ mensile" value={editing.monthly_limit_usd} onChange={e => setEditing({ ...editing, monthly_limit_usd: e.target.value })} className="px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm" />
          <input type="number" placeholder="warn %" value={editing.warning_pct} onChange={e => setEditing({ ...editing, warning_pct: e.target.value })} className="px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm" />
        </div>
        <div className="flex gap-2">
          <button onClick={save} className="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm">Salva</button>
          <button onClick={onClose} className="px-4 py-2 rounded bg-gray-700 hover:bg-gray-600 text-white text-sm">Chiudi</button>
        </div>
      </div>
    </div>
  );
};

const PricingModal = ({ onClose, authFetch }) => {
  const [rows, setRows] = useState([]);
  useEffect(() => {
    authFetch(`${API_URL}/api/seo/cost-observatory/pricing`).then(r => r.json()).then(d => setRows(d.rows || []));
  }, [authFetch]);
  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-gray-900 rounded-xl border border-gray-700 max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <h2 className="text-lg font-bold text-white mb-4">💵 Pricing config</h2>
        <div className="space-y-1 mb-5 max-h-[60vh] overflow-y-auto">
          {rows.map(r => (
            <div key={r.key} className="flex items-center justify-between p-2 rounded bg-gray-800 text-xs">
              <span className="font-mono text-white flex-1">{r.key}</span>
              <span className="text-emerald-300 mr-3">${r.cost_per_unit} / {r.unit}</span>
              {r.is_overridden && <span className="text-amber-300 text-[10px]">override</span>}
            </div>
          ))}
        </div>
        <button onClick={onClose} className="px-4 py-2 rounded bg-gray-700 hover:bg-gray-600 text-white text-sm">Chiudi</button>
      </div>
    </div>
  );
};

const AlertConfigModal = ({ onClose, authFetch }) => {
  const [cfg, setCfg] = useState({ email_enabled: true, from_email: '', to_email: '', smtp_host: '', smtp_port: 465, smtp_user: '', smtp_pass: '' });
  const [resendKeySet, setResendKeySet] = useState(false);

  useEffect(() => {
    authFetch(`${API_URL}/api/seo/cost-observatory/alert-config`).then(r => r.json()).then(d => {
      setCfg(prev => ({ ...prev, ...d, smtp_pass: '' }));
      setResendKeySet(d.resend_key_set);
    });
  }, [authFetch]);

  const save = async () => {
    const r = await authFetch(`${API_URL}/api/seo/cost-observatory/alert-config`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cfg),
    });
    if (r.ok) { toast.success('Config salvata'); onClose(); }
    else toast.error('Errore');
  };

  return (
    <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-gray-900 rounded-xl border border-gray-700 max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <h2 className="text-lg font-bold text-white mb-2">📧 Alert Email Config</h2>
        <p className="text-xs text-gray-400 mb-4">Resend API key: <span className={resendKeySet ? 'text-emerald-300' : 'text-amber-300'}>{resendKeySet ? '✅ configurata' : '⚠️ non configurata (vai a /admin/seo/api-tools)'}</span></p>

        <label className="flex items-center gap-2 mb-4 text-sm text-white">
          <input type="checkbox" checked={cfg.email_enabled} onChange={e => setCfg({ ...cfg, email_enabled: e.target.checked })} />
          Email notifications attive
        </label>

        <div className="grid grid-cols-2 gap-3 mb-4">
          <input placeholder="From email (alerts@...)" value={cfg.from_email || ''} onChange={e => setCfg({ ...cfg, from_email: e.target.value })} className="px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm" />
          <input placeholder="To email (destinatario)" value={cfg.to_email || ''} onChange={e => setCfg({ ...cfg, to_email: e.target.value })} className="px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm" />
        </div>

        <h3 className="text-sm font-bold text-white mb-2 mt-4">SMTP fallback (opzionale)</h3>
        <div className="grid grid-cols-2 gap-3 mb-4">
          <input placeholder="SMTP host" value={cfg.smtp_host || ''} onChange={e => setCfg({ ...cfg, smtp_host: e.target.value })} className="px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm" />
          <input placeholder="SMTP port (465)" type="number" value={cfg.smtp_port || 465} onChange={e => setCfg({ ...cfg, smtp_port: parseInt(e.target.value) })} className="px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm" />
          <input placeholder="SMTP user" value={cfg.smtp_user || ''} onChange={e => setCfg({ ...cfg, smtp_user: e.target.value })} className="px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm" />
          <input placeholder={cfg.smtp_pass_set ? 'SMTP pass (saved)' : 'SMTP pass'} type="password" value={cfg.smtp_pass || ''} onChange={e => setCfg({ ...cfg, smtp_pass: e.target.value })} className="px-3 py-2 bg-gray-800 border border-gray-700 rounded text-white text-sm" />
        </div>

        <h3 className="text-sm font-bold text-white mb-2 mt-4">Trigger</h3>
        <div className="grid grid-cols-2 gap-2 text-xs text-gray-200">
          {[
            ['email_on_budget_warning', '💰 Budget warning (80%)'],
            ['email_on_budget_exceeded', '🚨 Budget exceeded (100%)'],
            ['email_on_low_balance', '💳 Low balance'],
            ['email_on_api_down', '🔴 API down'],
            ['email_on_api_intermittent', '🟡 API intermittent'],
          ].map(([key, label]) => (
            <label key={key} className="inline-flex items-center gap-2">
              <input type="checkbox" checked={cfg[key] !== false} onChange={e => setCfg({ ...cfg, [key]: e.target.checked })} />
              {label}
            </label>
          ))}
        </div>

        <div className="flex gap-2 mt-5">
          <button onClick={save} className="px-4 py-2 rounded bg-emerald-600 hover:bg-emerald-700 text-white text-sm">Salva</button>
          <button onClick={onClose} className="px-4 py-2 rounded bg-gray-700 hover:bg-gray-600 text-white text-sm">Chiudi</button>
        </div>
      </div>
    </div>
  );
};

export default CostObservatory;
