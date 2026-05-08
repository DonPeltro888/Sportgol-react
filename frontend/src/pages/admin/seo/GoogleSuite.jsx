import React, { useEffect, useState } from 'react';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import { Link } from 'react-router-dom';
import {
  ChevronLeft, Search, Send, BarChart3, Gauge, Loader2, AlertTriangle,
  ExternalLink, Copy, CheckCircle2, XCircle, RefreshCw, TrendingUp,
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TabBtn = ({ active, onClick, icon: Icon, label, testId }) => (
  <button
    onClick={onClick}
    data-testid={testId}
    className={`px-4 py-2 rounded-lg text-sm font-medium inline-flex items-center gap-2 transition-all ${
      active
        ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
        : 'bg-gray-800 text-gray-400 hover:text-white hover:bg-gray-700'
    }`}
  >
    <Icon className="w-4 h-4" /> {label}
  </button>
);

const Stat = ({ label, value, sub, testId }) => (
  <div data-testid={testId} className="rounded-xl border border-gray-700 bg-gray-800/40 p-4">
    <div className="text-xs text-gray-400 uppercase tracking-wide">{label}</div>
    <div className="mt-1 text-2xl font-semibold text-white">{value ?? '—'}</div>
    {sub && <div className="text-xs text-gray-500 mt-1">{sub}</div>}
  </div>
);

const StatusBanner = ({ status, sa }) => {
  if (!status) return null;
  return (
    <div className="rounded-xl border border-blue-700/40 bg-blue-900/20 p-4 mb-6">
      <div className="flex items-start gap-3">
        <CheckCircle2 className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
        <div className="flex-1">
          <div className="text-sm text-white font-semibold">Service account configurato</div>
          <div className="text-xs text-blue-200 mt-1 inline-flex items-center gap-2 break-all">
            <code className="text-blue-300">{sa}</code>
            <button
              onClick={() => { navigator.clipboard.writeText(sa); toast.success('Email copiata'); }}
              className="text-blue-400 hover:text-white"
            >
              <Copy className="w-3.5 h-3.5" />
            </button>
          </div>
          <div className="text-xs text-gray-400 mt-2">
            Per attivare le 4 API, aggiungi questa email come <strong>Owner</strong> in Search Console
            (per Search Console + Indexing) e come <strong>Viewer</strong> in Google Analytics 4.
          </div>
        </div>
      </div>
    </div>
  );
};

// ============================ Search Console Tab ============================
const SearchConsoleTab = ({ authFetch }) => {
  const [sites, setSites] = useState([]);
  const [siteUrl, setSiteUrl] = useState('');
  const [days, setDays] = useState(28);
  const [tab, setTab] = useState('queries'); // queries | pages | opportunities
  const [data, setData] = useState({ rows: [] });
  const [loading, setLoading] = useState(false);

  useEffect(() => { (async () => {
    const r = await authFetch(`${API_URL}/api/google/search-console/sites`);
    if (r.ok) {
      const j = await r.json();
      setSites(j.sites || []);
      if (j.sites?.length) setSiteUrl(j.sites[0].siteUrl);
    }
  })(); /* eslint-disable-next-line */ }, []);

  const load = async () => {
    if (!siteUrl) return;
    setLoading(true);
    try {
      const r = await authFetch(
        `${API_URL}/api/google/search-console/${tab}?site_url=${encodeURIComponent(siteUrl)}&days=${days}&limit=100`
      );
      const j = await r.json();
      setData(j);
    } finally { setLoading(false); }
  };

  useEffect(() => { if (siteUrl) load(); /* eslint-disable-next-line */ }, [siteUrl, days, tab]);

  if (!sites.length) {
    return (
      <div className="rounded-xl border border-amber-600/30 bg-amber-900/10 p-6">
        <AlertTriangle className="w-5 h-5 text-amber-400 inline mr-2" />
        <span className="text-amber-200">
          Nessun sito accessibile. Aggiungi il service account come <strong>Owner</strong> su Google
          Search Console (<a className="underline" href="https://search.google.com/search-console" target="_blank" rel="noreferrer">apri</a>).
        </span>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap gap-3 items-end">
        <div>
          <label className="text-xs text-gray-400 block mb-1">Sito</label>
          <select
            value={siteUrl}
            onChange={(e) => setSiteUrl(e.target.value)}
            data-testid="gsc-site-select"
            className="bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm"
          >
            {sites.map((s) => <option key={s.siteUrl} value={s.siteUrl}>{s.siteUrl}</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-400 block mb-1">Ultimi giorni</label>
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm"
          >
            {[7, 14, 28, 90].map((d) => <option key={d} value={d}>{d}g</option>)}
          </select>
        </div>
        <div className="flex gap-2 ml-auto">
          <TabBtn active={tab === 'queries'} onClick={() => setTab('queries')} icon={Search} label="Top Keyword" testId="gsc-tab-queries" />
          <TabBtn active={tab === 'pages'} onClick={() => setTab('pages')} icon={BarChart3} label="Top Pagine" testId="gsc-tab-pages" />
          <TabBtn active={tab === 'opportunities'} onClick={() => setTab('opportunities')} icon={TrendingUp} label="Opportunità (pos 11-20)" testId="gsc-tab-opportunities" />
        </div>
      </div>

      <div className="rounded-xl border border-gray-700 bg-gray-800/40 overflow-hidden">
        {loading && <div className="p-6 text-center text-gray-400"><Loader2 className="w-5 h-5 animate-spin inline mr-2" /> Caricamento…</div>}
        {!loading && data.error && <div className="p-6 text-amber-200"><AlertTriangle className="inline w-4 h-4 mr-2" />{data.error}</div>}
        {!loading && !data.error && (
          <table className="w-full text-sm" data-testid="gsc-table">
            <thead className="bg-gray-900/60 text-xs uppercase text-gray-400">
              <tr>
                <th className="text-left px-4 py-2">{tab === 'pages' ? 'Pagina' : 'Keyword'}</th>
                <th className="text-right px-4 py-2">Click</th>
                <th className="text-right px-4 py-2">Impressioni</th>
                <th className="text-right px-4 py-2">CTR</th>
                <th className="text-right px-4 py-2">Posizione</th>
                {tab === 'opportunities' && <th className="text-right px-4 py-2">Click pot.</th>}
              </tr>
            </thead>
            <tbody>
              {(data.rows || []).map((r, i) => (
                <tr key={i} className="border-t border-gray-700 hover:bg-gray-700/20">
                  <td className="px-4 py-2 text-white">
                    {tab === 'opportunities' ? r.query : (r.keys?.[0] || r.query || '—')}
                  </td>
                  <td className="px-4 py-2 text-right text-gray-300">
                    {tab === 'opportunities' ? r.clicks : (r.clicks ?? 0)}
                  </td>
                  <td className="px-4 py-2 text-right text-gray-300">
                    {tab === 'opportunities' ? r.impressions : (r.impressions ?? 0)}
                  </td>
                  <td className="px-4 py-2 text-right text-gray-300">
                    {tab === 'opportunities' ? `${r.ctr}%` : `${((r.ctr ?? 0) * 100).toFixed(2)}%`}
                  </td>
                  <td className="px-4 py-2 text-right text-gray-300">
                    {tab === 'opportunities' ? r.position : (r.position ?? 0).toFixed(1)}
                  </td>
                  {tab === 'opportunities' && (
                    <td className="px-4 py-2 text-right text-emerald-300 font-semibold">
                      +{r.potential_clicks ?? 0}
                    </td>
                  )}
                </tr>
              ))}
              {(!data.rows || data.rows.length === 0) && (
                <tr><td colSpan={tab === 'opportunities' ? 6 : 5} className="px-4 py-6 text-center text-gray-500">Nessun dato per il periodo selezionato.</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

// =============================== Indexing Tab ===============================
const IndexingTab = ({ authFetch }) => {
  const [url, setUrl] = useState('');
  const [bulkUrls, setBulkUrls] = useState('');
  const [running, setRunning] = useState(false);
  const [history, setHistory] = useState([]);

  const loadHistory = async () => {
    const r = await authFetch(`${API_URL}/api/google/indexing/history?limit=50`);
    if (r.ok) { const j = await r.json(); setHistory(j.rows || []); }
  };
  useEffect(() => { loadHistory(); /* eslint-disable-next-line */ }, []);

  const submitOne = async () => {
    if (!url.trim()) return;
    setRunning(true);
    try {
      const r = await authFetch(`${API_URL}/api/google/indexing/submit`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim(), action: 'URL_UPDATED' }),
      });
      const j = await r.json();
      if (j.ok) toast.success('URL submitted to Google Indexing'); else toast.error(j.error || 'Errore');
      setUrl(''); loadHistory();
    } finally { setRunning(false); }
  };

  const submitBatch = async () => {
    const list = bulkUrls.split('\n').map((s) => s.trim()).filter(Boolean);
    if (!list.length) return;
    if (!window.confirm(`Submit ${list.length} URLs? (max 200/giorno per progetto Google)`)) return;
    setRunning(true);
    try {
      const r = await authFetch(`${API_URL}/api/google/indexing/submit-batch`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ urls: list, action: 'URL_UPDATED' }),
      });
      const j = await r.json();
      toast.success(`Submitted: ${j.submitted_count}, Failed: ${j.failed_count}`);
      setBulkUrls(''); loadHistory();
    } finally { setRunning(false); }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
        <h3 className="text-white font-semibold mb-3">Submit singolo URL</h3>
        <div className="flex gap-2">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://golevents.com/biglietti-..."
            data-testid="indexing-url-input"
            className="flex-1 bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm"
          />
          <button
            onClick={submitOne}
            disabled={running || !url.trim()}
            data-testid="indexing-submit-btn"
            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm inline-flex items-center gap-2"
          >
            {running ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />} Indexa
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
        <h3 className="text-white font-semibold mb-3">Submit batch (max 100, uno per riga)</h3>
        <textarea
          rows={5}
          value={bulkUrls}
          onChange={(e) => setBulkUrls(e.target.value)}
          placeholder={`https://golevents.com/biglietti-inter-vs-juventus\nhttps://golevents.com/biglietti-milan-vs-roma`}
          data-testid="indexing-batch-textarea"
          className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm font-mono"
        />
        <div className="flex justify-between mt-2">
          <span className="text-xs text-gray-500">{bulkUrls.split('\n').filter(Boolean).length} URL nella lista</span>
          <button
            onClick={submitBatch}
            disabled={running || !bulkUrls.trim()}
            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm inline-flex items-center gap-2"
          >
            {running ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />} Submit batch
          </button>
        </div>
      </div>

      <div className="rounded-xl border border-gray-700 bg-gray-800/40 overflow-hidden">
        <div className="px-5 py-3 flex items-center justify-between border-b border-gray-700">
          <h3 className="text-white font-semibold">Storico submission</h3>
          <button onClick={loadHistory} className="text-xs text-gray-400 hover:text-white inline-flex items-center gap-1">
            <RefreshCw className="w-3.5 h-3.5" /> Aggiorna
          </button>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-900/60 text-xs uppercase text-gray-400">
            <tr>
              <th className="text-left px-4 py-2">URL</th>
              <th className="text-left px-4 py-2 w-32">Action</th>
              <th className="text-left px-4 py-2 w-24">Esito</th>
              <th className="text-left px-4 py-2 w-44">Data</th>
            </tr>
          </thead>
          <tbody>
            {history.map((r, i) => (
              <tr key={i} className="border-t border-gray-700">
                <td className="px-4 py-2 text-white truncate max-w-md"><a href={r.url} target="_blank" rel="noreferrer" className="hover:underline inline-flex items-center gap-1">{r.url}<ExternalLink className="w-3 h-3 inline" /></a></td>
                <td className="px-4 py-2 text-gray-300 text-xs">{r.action}</td>
                <td className="px-4 py-2">
                  {r.error
                    ? <XCircle className="w-4 h-4 text-red-400 inline" />
                    : <CheckCircle2 className="w-4 h-4 text-emerald-400 inline" />}
                </td>
                <td className="px-4 py-2 text-gray-400 text-xs">{(r.ts || '').slice(0, 19).replace('T', ' ')}</td>
              </tr>
            ))}
            {!history.length && (
              <tr><td colSpan={4} className="px-4 py-6 text-center text-gray-500">Nessuna submission ancora.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// =============================== Analytics Tab ==============================
const AnalyticsTab = ({ authFetch }) => {
  const [props, setProps] = useState([]);
  const [propId, setPropId] = useState('');
  const [days, setDays] = useState(7);
  const [overview, setOverview] = useState(null);
  const [pages, setPages] = useState([]);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { (async () => {
    const r = await authFetch(`${API_URL}/api/google/analytics/properties`);
    if (r.ok) {
      const j = await r.json();
      setProps(j.properties || []);
      if (j.properties?.length) setPropId(j.properties[0].property_id);
    }
  })(); /* eslint-disable-next-line */ }, []);

  const load = async () => {
    if (!propId) return;
    setLoading(true);
    try {
      const [o, p, s] = await Promise.all([
        authFetch(`${API_URL}/api/google/analytics/overview?property_id=${encodeURIComponent(propId)}&days=${days}`).then((r) => r.json()),
        authFetch(`${API_URL}/api/google/analytics/top-pages?property_id=${encodeURIComponent(propId)}&days=${days}&limit=20`).then((r) => r.json()),
        authFetch(`${API_URL}/api/google/analytics/sources?property_id=${encodeURIComponent(propId)}&days=${days}&limit=10`).then((r) => r.json()),
      ]);
      setOverview(o); setPages(p.rows || []); setSources(s.rows || []);
    } finally { setLoading(false); }
  };
  useEffect(() => { if (propId) load(); /* eslint-disable-next-line */ }, [propId, days]);

  if (!props.length) {
    return (
      <div className="rounded-xl border border-amber-600/30 bg-amber-900/10 p-6">
        <AlertTriangle className="w-5 h-5 text-amber-400 inline mr-2" />
        <span className="text-amber-200">
          Nessuna property GA4. Aggiungi il service account come <strong>Viewer</strong> in
          Google Analytics → Admin → Property → Property access management
          (<a className="underline" href="https://analytics.google.com" target="_blank" rel="noreferrer">apri</a>).
        </span>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap gap-3 items-end">
        <div>
          <label className="text-xs text-gray-400 block mb-1">Property GA4</label>
          <select
            value={propId}
            onChange={(e) => setPropId(e.target.value)}
            data-testid="ga-property-select"
            className="bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm"
          >
            {props.map((p) => <option key={p.property_id} value={p.property_id}>{p.property_name} ({p.property_short_id})</option>)}
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-400 block mb-1">Periodo</label>
          <select value={days} onChange={(e) => setDays(Number(e.target.value))}
            className="bg-gray-800 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm">
            {[1, 7, 14, 28, 90].map((d) => <option key={d} value={d}>{d}g</option>)}
          </select>
        </div>
      </div>

      {loading && <div className="text-gray-400 text-center py-6"><Loader2 className="w-5 h-5 animate-spin inline mr-2" /> Caricamento…</div>}

      {overview && !overview.error && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <Stat testId="ga-stat-users" label="Utenti" value={overview.users?.toLocaleString()} />
          <Stat testId="ga-stat-sessions" label="Sessioni" value={overview.sessions?.toLocaleString()} />
          <Stat testId="ga-stat-pviews" label="Pageviews" value={overview.page_views?.toLocaleString()} />
          <Stat testId="ga-stat-duration" label="Durata media" value={`${overview.avg_session_duration}s`} />
          <Stat testId="ga-stat-bounce" label="Bounce" value={`${overview.bounce_rate}%`} />
          <Stat testId="ga-stat-conv" label="Conversioni" value={overview.conversions?.toLocaleString()} />
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-5">
        <div className="rounded-xl border border-gray-700 bg-gray-800/40 overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-700"><h3 className="text-white font-semibold">Top pagine</h3></div>
          <table className="w-full text-sm">
            <thead className="text-xs uppercase text-gray-400"><tr><th className="text-left px-4 py-2">Path</th><th className="text-right px-4 py-2">Views</th><th className="text-right px-4 py-2">Users</th></tr></thead>
            <tbody>
              {pages.map((p, i) => (
                <tr key={i} className="border-t border-gray-700">
                  <td className="px-4 py-2 text-white truncate max-w-xs">{p.path}</td>
                  <td className="px-4 py-2 text-right text-gray-300">{p.page_views.toLocaleString()}</td>
                  <td className="px-4 py-2 text-right text-gray-300">{p.users.toLocaleString()}</td>
                </tr>
              ))}
              {!pages.length && <tr><td colSpan={3} className="text-center px-4 py-6 text-gray-500">Nessuna pagina.</td></tr>}
            </tbody>
          </table>
        </div>

        <div className="rounded-xl border border-gray-700 bg-gray-800/40 overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-700"><h3 className="text-white font-semibold">Fonti traffico</h3></div>
          <table className="w-full text-sm">
            <thead className="text-xs uppercase text-gray-400"><tr><th className="text-left px-4 py-2">Channel / Source</th><th className="text-right px-4 py-2">Sessioni</th><th className="text-right px-4 py-2">Users</th></tr></thead>
            <tbody>
              {sources.map((s, i) => (
                <tr key={i} className="border-t border-gray-700">
                  <td className="px-4 py-2 text-white"><span className="text-gray-400 text-xs">{s.channel}</span> · {s.source}</td>
                  <td className="px-4 py-2 text-right text-gray-300">{s.sessions.toLocaleString()}</td>
                  <td className="px-4 py-2 text-right text-gray-300">{s.users.toLocaleString()}</td>
                </tr>
              ))}
              {!sources.length && <tr><td colSpan={3} className="text-center px-4 py-6 text-gray-500">Nessuna fonte.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// =============================== PageSpeed Tab ==============================
const PageSpeedTab = ({ authFetch }) => {
  const [url, setUrl] = useState('https://golevents.com');
  const [strategy, setStrategy] = useState('mobile');
  const [running, setRunning] = useState(false);
  const [latest, setLatest] = useState(null);
  const [dashboard, setDashboard] = useState([]);

  const loadDash = async () => {
    const r = await authFetch(`${API_URL}/api/google/pagespeed/dashboard?limit=20`);
    if (r.ok) { const j = await r.json(); setDashboard(j.rows || []); }
  };
  useEffect(() => { loadDash(); /* eslint-disable-next-line */ }, []);

  const runScan = async () => {
    if (!url) return;
    setRunning(true); setLatest(null);
    try {
      const r = await authFetch(`${API_URL}/api/google/pagespeed/scan`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, strategy }),
      });
      const j = await r.json();
      setLatest(j);
      if (j.ok) toast.success(`Scan ok — Performance: ${j.performance_score}/100`); else toast.error(j.error || 'Errore scan');
      loadDash();
    } finally { setRunning(false); }
  };

  const ScoreBar = ({ score, label }) => {
    const color = score >= 90 ? 'bg-emerald-500' : score >= 50 ? 'bg-amber-500' : 'bg-red-500';
    return (
      <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-4">
        <div className="text-xs text-gray-400 uppercase">{label}</div>
        <div className="text-3xl font-semibold text-white mt-1">{score ?? '—'}</div>
        <div className="h-1.5 bg-gray-700 rounded-full mt-2 overflow-hidden"><div className={`h-full ${color}`} style={{ width: `${score || 0}%` }} /></div>
      </div>
    );
  };

  return (
    <div className="space-y-5">
      <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
        <h3 className="text-white font-semibold mb-3">Nuovo scan</h3>
        <div className="flex flex-wrap gap-2">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://golevents.com/..."
            data-testid="ps-url-input"
            className="flex-1 min-w-[300px] bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm"
          />
          <select value={strategy} onChange={(e) => setStrategy(e.target.value)}
            className="bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm">
            <option value="mobile">Mobile</option>
            <option value="desktop">Desktop</option>
          </select>
          <button
            onClick={runScan}
            disabled={running || !url}
            data-testid="ps-scan-btn"
            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm inline-flex items-center gap-2"
          >
            {running ? <Loader2 className="w-4 h-4 animate-spin" /> : <Gauge className="w-4 h-4" />} Scansiona
          </button>
        </div>
        {running && <p className="text-xs text-gray-500 mt-2">Lo scan può richiedere 30-60 secondi…</p>}
      </div>

      {latest && latest.ok && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <ScoreBar score={latest.performance_score} label="Performance" />
          <ScoreBar score={latest.seo_score} label="SEO" />
          <ScoreBar score={latest.accessibility_score} label="A11y" />
          <ScoreBar score={latest.best_practices_score} label="Best Practices" />
        </div>
      )}
      {latest && !latest.ok && (
        <div className="rounded-xl border border-red-700/50 bg-red-900/20 p-4 text-red-200">
          <AlertTriangle className="w-4 h-4 inline mr-2" />{latest.error}
          {latest.status_code === 429 && (
            <div className="text-xs text-red-300 mt-1">
              Quota giornaliera del progetto GCP esaurita. Resetta a mezzanotte UTC, oppure aggiungi
              <code className="bg-black/40 px-1 rounded ml-1">PAGESPEED_API_KEY</code> in <code>backend/.env</code>.
            </div>
          )}
        </div>
      )}
      {latest && latest.ok && (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
          <Stat label="LCP" value={latest.lcp?.display} sub="Largest Contentful Paint" />
          <Stat label="CLS" value={latest.cls?.display} sub="Cumulative Layout Shift" />
          <Stat label="TBT" value={latest.tbt?.display} sub="Total Blocking Time" />
          <Stat label="FCP" value={latest.fcp?.display} sub="First Contentful Paint" />
          <Stat label="Speed Index" value={latest.speed_index?.display} sub="visibility ramp-up" />
          <Stat label="TTI" value={latest.tti?.display} sub="Time to Interactive" />
        </div>
      )}

      <div className="rounded-xl border border-gray-700 bg-gray-800/40 overflow-hidden">
        <div className="px-5 py-3 flex items-center justify-between border-b border-gray-700">
          <h3 className="text-white font-semibold">Ultimi scan (worst-first)</h3>
          <button onClick={loadDash} className="text-xs text-gray-400 hover:text-white inline-flex items-center gap-1">
            <RefreshCw className="w-3.5 h-3.5" /> Aggiorna
          </button>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-900/60 text-xs uppercase text-gray-400">
            <tr>
              <th className="text-left px-4 py-2">URL</th>
              <th className="text-left px-4 py-2 w-24">Strategy</th>
              <th className="text-right px-4 py-2 w-20">Perf</th>
              <th className="text-right px-4 py-2 w-24">LCP</th>
              <th className="text-right px-4 py-2 w-20">CLS</th>
              <th className="text-left px-4 py-2 w-44">Scansionato</th>
            </tr>
          </thead>
          <tbody>
            {dashboard.map((r, i) => (
              <tr key={i} className="border-t border-gray-700">
                <td className="px-4 py-2 text-white truncate max-w-xs"><a href={r.url} target="_blank" rel="noreferrer" className="hover:underline">{r.url}</a></td>
                <td className="px-4 py-2 text-gray-300">{r.strategy}</td>
                <td className={`px-4 py-2 text-right font-semibold ${r.performance_score >= 90 ? 'text-emerald-300' : r.performance_score >= 50 ? 'text-amber-300' : 'text-red-300'}`}>{r.performance_score ?? '—'}</td>
                <td className="px-4 py-2 text-right text-gray-300">{r.lcp?.display || '—'}</td>
                <td className="px-4 py-2 text-right text-gray-300">{r.cls?.display || '—'}</td>
                <td className="px-4 py-2 text-gray-400 text-xs">{(r.scanned_at || '').slice(0, 19).replace('T', ' ')}</td>
              </tr>
            ))}
            {!dashboard.length && <tr><td colSpan={6} className="px-4 py-6 text-center text-gray-500">Nessuno scan ancora.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// =============================== Main Page ==============================
const GoogleSuite = () => {
  const { authFetch } = useAdminAuth();
  const [activeTab, setActiveTab] = useState('search-console');
  const [status, setStatus] = useState(null);

  useEffect(() => { (async () => {
    const r = await authFetch(`${API_URL}/api/google/status`);
    if (r.ok) setStatus(await r.json());
  })(); /* eslint-disable-next-line */ }, []);

  return (
    <AdminLayout>
      <div className="max-w-7xl mx-auto px-4 py-8">
        <Link to="/admin/seo" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
          <ChevronLeft className="w-4 h-4" /> Torna a SEO Dashboard
        </Link>

        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
            <Search className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl text-white font-bold">Google Suite</h1>
            <p className="text-sm text-gray-400">Search Console, Indexing, Analytics 4, PageSpeed Insights — tutto in un posto</p>
          </div>
        </div>

        {status?.configured && <StatusBanner status={status} sa={status.service_account_email} />}

        <div className="flex flex-wrap gap-2 mb-6 border-b border-gray-800 pb-3" data-testid="google-suite-tabs">
          <TabBtn active={activeTab === 'search-console'} onClick={() => setActiveTab('search-console')} icon={Search} label="Search Console" testId="tab-search-console" />
          <TabBtn active={activeTab === 'indexing'} onClick={() => setActiveTab('indexing')} icon={Send} label="Indexing API" testId="tab-indexing" />
          <TabBtn active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')} icon={BarChart3} label="Analytics 4" testId="tab-analytics" />
          <TabBtn active={activeTab === 'pagespeed'} onClick={() => setActiveTab('pagespeed')} icon={Gauge} label="PageSpeed" testId="tab-pagespeed" />
        </div>

        {activeTab === 'search-console' && <SearchConsoleTab authFetch={authFetch} />}
        {activeTab === 'indexing' && <IndexingTab authFetch={authFetch} />}
        {activeTab === 'analytics' && <AnalyticsTab authFetch={authFetch} />}
        {activeTab === 'pagespeed' && <PageSpeedTab authFetch={authFetch} />}
      </div>
    </AdminLayout>
  );
};

export default GoogleSuite;
