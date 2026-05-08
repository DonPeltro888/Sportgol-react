import React, { useEffect, useMemo, useState } from 'react';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import { Link } from 'react-router-dom';
import {
  Activity, AlertTriangle, ArrowLeft, CheckCircle2, ChevronLeft, Clock, Code2,
  Copy, Download, FileText, Loader2, Play, RefreshCw, Search, Settings, Sparkles,
  Wrench, X, XCircle,
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const STATUS_META = {
  TODO:      { label: 'To do',     color: 'red',     icon: XCircle },
  GENERATED: { label: 'Patch ready', color: 'amber', icon: Clock },
  DONE:      { label: 'Applied',   color: 'emerald', icon: CheckCircle2 },
  OK:        { label: 'OK',        color: 'emerald', icon: CheckCircle2 },
};

const TIER_META = {
  P0: { label: 'P0', color: 'red' },
  P1: { label: 'P1', color: 'amber' },
  P2: { label: 'P2', color: 'blue' },
};

const Pill = ({ tone, children, testId }) => (
  <span data-testid={testId} className={`px-2 py-0.5 rounded text-[10px] font-semibold uppercase tracking-wide bg-${tone}-600/20 text-${tone}-300 border border-${tone}-700/40`}>{children}</span>
);

const ScoreRing = ({ score }) => {
  const color = score >= 90 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444';
  const offset = 339 - (339 * (score || 0)) / 100;
  return (
    <svg viewBox="0 0 120 120" className="w-32 h-32">
      <circle cx="60" cy="60" r="54" fill="none" stroke="#1f2937" strokeWidth="10" />
      <circle cx="60" cy="60" r="54" fill="none" stroke={color} strokeWidth="10"
        strokeDasharray="339" strokeDashoffset={offset} strokeLinecap="round"
        transform="rotate(-90 60 60)" style={{ transition: 'stroke-dashoffset 1s ease' }} />
      <text x="60" y="60" textAnchor="middle" dy="6" fill="white" fontSize="28" fontWeight="700">{score ?? '—'}</text>
      <text x="60" y="78" textAnchor="middle" fill="#9ca3af" fontSize="10">/ 100</text>
    </svg>
  );
};

const PatchModal = ({ patch, onClose }) => {
  if (!patch) return null;
  return (
    <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-gray-900 border border-gray-700 rounded-xl max-w-3xl w-full max-h-[85vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <div>
            <h3 className="text-white font-semibold">{patch.title}</h3>
            <code className="text-xs text-gray-400">{patch.filename}</code>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => { navigator.clipboard.writeText(patch.content); toast.success('Patch copiata'); }}
              data-testid="patch-copy-btn"
              className="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded text-sm inline-flex items-center gap-1"
            >
              <Copy className="w-3.5 h-3.5" /> Copia
            </button>
            <button
              onClick={() => {
                const blob = new Blob([patch.content], { type: 'text/plain' });
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = patch.filename;
                a.click();
              }}
              className="bg-gray-700 hover:bg-gray-600 text-white px-3 py-1.5 rounded text-sm inline-flex items-center gap-1"
            >
              <Download className="w-3.5 h-3.5" />
            </button>
            <button onClick={onClose} className="text-gray-400 hover:text-white"><X className="w-5 h-5" /></button>
          </div>
        </div>
        <pre className="flex-1 overflow-auto bg-black/40 text-emerald-200 text-sm p-4 font-mono whitespace-pre">{patch.content}</pre>
      </div>
    </div>
  );
};

const CwvCard = ({ item, action, onFix, onPatch, onMarkApplied, onReset, busy }) => {
  const status = action?.status || (item.detected ? 'TODO' : 'OK');
  const meta = STATUS_META[status] || STATUS_META.TODO;
  const StatusIcon = meta.icon;
  const tier = TIER_META[item.tier];
  const isAuto = item.kind === 'auto';

  return (
    <div data-testid={`cwv-card-${item.id}`}
      className={`rounded-xl border bg-gray-800/40 p-4 transition-all
        ${status === 'DONE' || status === 'OK' ? 'border-emerald-700/50' :
          status === 'GENERATED' ? 'border-amber-700/50' : 'border-red-800/40'}`}>
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-start gap-2 min-w-0 flex-1">
          <StatusIcon className={`w-5 h-5 flex-shrink-0 mt-0.5 text-${meta.color}-400`} />
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <Pill tone={tier.color}>{tier.label}</Pill>
              <Pill tone={isAuto ? 'blue' : 'violet'}>{isAuto ? 'Auto' : 'Manual'}</Pill>
              <span className="text-xs text-gray-500">{item.id}</span>
              <span className="text-xs text-gray-500">· {item.category}</span>
            </div>
            <h3 className="text-white font-semibold mt-0.5">{item.title}</h3>
          </div>
        </div>
      </div>

      <p className="text-xs text-gray-400 mb-3 ml-7">{item.detail || item.note || '—'}</p>

      {action?.applied_at && (
        <p className="text-[11px] text-emerald-400 mb-2 ml-7">
          ✓ Applied at {new Date(action.applied_at).toLocaleString('it-IT')}
        </p>
      )}
      {action?.generated_at && status === 'GENERATED' && (
        <p className="text-[11px] text-amber-300 mb-2 ml-7">
          ⏳ Patch generata {new Date(action.generated_at).toLocaleString('it-IT')} — in attesa di apply
        </p>
      )}

      <div className="flex flex-wrap gap-2 ml-7">
        {item.detected && status !== 'DONE' && status !== 'OK' && (
          <>
            {isAuto ? (
              <button
                onClick={() => onFix(item.id)}
                disabled={busy}
                data-testid={`cwv-fix-${item.id}`}
                className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-3 py-1.5 rounded text-xs inline-flex items-center gap-1"
              >
                {busy ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Wrench className="w-3.5 h-3.5" />} Fix Now
              </button>
            ) : (
              <>
                <button
                  onClick={() => onPatch(item.id)}
                  data-testid={`cwv-patch-${item.id}`}
                  className="bg-violet-600 hover:bg-violet-500 text-white px-3 py-1.5 rounded text-xs inline-flex items-center gap-1"
                >
                  <Code2 className="w-3.5 h-3.5" /> {status === 'GENERATED' ? 'Re-show patch' : 'Generate patch'}
                </button>
                {status === 'GENERATED' && (
                  <button
                    onClick={() => onMarkApplied(item.id)}
                    data-testid={`cwv-apply-${item.id}`}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1.5 rounded text-xs inline-flex items-center gap-1"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" /> Mark applied
                  </button>
                )}
              </>
            )}
          </>
        )}
        {status === 'DONE' && (
          <button onClick={() => onReset(item.id)}
            className="bg-gray-700 hover:bg-gray-600 text-gray-300 px-3 py-1.5 rounded text-xs inline-flex items-center gap-1">
            <RefreshCw className="w-3.5 h-3.5" /> Reset
          </button>
        )}
      </div>
    </div>
  );
};

const CwvAutomation = () => {
  const { authFetch } = useAdminAuth();
  const [targetUrl, setTargetUrl] = useState('https://golevents.com');
  const [scan, setScan] = useState(null);
  const [actions, setActions] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [patchModal, setPatchModal] = useState(null);
  const [busyId, setBusyId] = useState(null);
  const [history, setHistory] = useState([]);

  const loadActions = async (url = targetUrl) => {
    if (!url) return;
    const r = await authFetch(`${API_URL}/api/seo/cwv/actions?target_url=${encodeURIComponent(url)}`);
    if (r.ok) { const j = await r.json(); setActions(j.rows || []); }
    const h = await authFetch(`${API_URL}/api/seo/cwv/score-history?url=${encodeURIComponent(url)}&days=90`);
    if (h.ok) { const j = await h.json(); setHistory(j.rows || []); }
  };

  useEffect(() => { loadActions(); /* eslint-disable-next-line */ }, []);

  const runScan = async () => {
    if (!targetUrl) return;
    setScanning(true);
    setScan(null);
    try {
      const r = await authFetch(`${API_URL}/api/seo/cwv/scan`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: targetUrl }),
      });
      const j = await r.json();
      if (!j.ok) { toast.error(j.error || 'Scan failed'); return; }
      setScan(j);
      await loadActions(targetUrl);
      toast.success(`Scan completato — score ${j.score}/100`);
    } finally { setScanning(false); }
  };

  const handleFix = async (cwvId) => {
    setBusyId(cwvId);
    try {
      const r = await authFetch(`${API_URL}/api/seo/cwv/auto-fix/${cwvId}`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_url: targetUrl }),
      });
      const j = await r.json();
      if (j.ok) toast.success(j.message || `${cwvId} fixed`); else toast.error(j.error || 'Fix failed');
      await loadActions(targetUrl);
    } finally { setBusyId(null); }
  };

  const handleFixAll = async () => {
    if (!window.confirm('Eseguo tutti gli auto-fix sul tool? (CWV-1 hero images, CWV-5/6/11 conferme).')) return;
    setBusyId('ALL');
    try {
      const r = await authFetch(`${API_URL}/api/seo/cwv/auto-fix-all`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ target_url: targetUrl }),
      });
      const j = await r.json();
      if (j.ok) toast.success('Tutti gli auto-fix eseguiti');
      await loadActions(targetUrl);
    } finally { setBusyId(null); }
  };

  const handlePatch = async (cwvId) => {
    const r = await authFetch(`${API_URL}/api/seo/cwv/patch/${cwvId}?target_url=${encodeURIComponent(targetUrl)}`);
    const j = await r.json();
    if (!j.ok) { toast.error(j.error || 'Patch generation failed'); return; }
    setPatchModal(j);
    await loadActions(targetUrl);
  };

  const handleMarkApplied = async (cwvId) => {
    const r = await authFetch(`${API_URL}/api/seo/cwv/mark-applied`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_url: targetUrl, cwv_id: cwvId }),
    });
    const j = await r.json();
    if (j.ok) { toast.success(`${cwvId} marked as applied`); await loadActions(targetUrl); }
  };

  const handleReset = async (cwvId) => {
    const r = await authFetch(`${API_URL}/api/seo/cwv/reset-action`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_url: targetUrl, cwv_id: cwvId }),
    });
    if (r.ok) { toast.info(`${cwvId} reset`); await loadActions(targetUrl); }
  };

  const items = useMemo(() => {
    if (scan?.items) return scan.items;
    return actions.map((a) => ({
      id: a.cwv_id, title: a.title, kind: a.kind, tier: a.tier, category: a.category,
      detected: a.status !== 'OK',
      detail: '—',
    }));
  }, [scan, actions]);

  const actionsByCwv = useMemo(() => {
    const m = {};
    for (const a of actions) m[a.cwv_id] = a;
    return m;
  }, [actions]);

  const autoItems   = items.filter((i) => i.kind === 'auto');
  const manualItems = items.filter((i) => i.kind === 'manual');

  const doneCount = actions.filter((a) => a.status === 'DONE' || a.status === 'OK').length;
  const totalCount = actions.length || items.length;

  return (
    <AdminLayout>
      <PatchModal patch={patchModal} onClose={() => setPatchModal(null)} />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <Link to="/admin/seo" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
          <ChevronLeft className="w-4 h-4" /> Torna a SEO Dashboard
        </Link>

        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl text-white font-bold">CWV Automation Center</h1>
            <p className="text-sm text-gray-400">Analizza e applica i 12 fix Core Web Vitals su qualsiasi URL pubblico</p>
          </div>
        </div>

        {/* Scan bar */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6">
          <div className="flex flex-wrap gap-2 items-end">
            <div className="flex-1 min-w-[300px]">
              <label className="text-xs text-gray-400 block mb-1">Target URL</label>
              <input
                type="url"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="https://ticketgol.com"
                data-testid="cwv-target-url"
                className="w-full bg-gray-900 border border-gray-700 text-white rounded-lg px-3 py-2 text-sm"
              />
            </div>
            <button
              onClick={runScan}
              disabled={scanning || !targetUrl}
              data-testid="cwv-scan-btn"
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white px-5 py-2 rounded-lg text-sm inline-flex items-center gap-2"
            >
              {scanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />} Scan now
            </button>
            {scan && (
              <button
                onClick={handleFixAll}
                disabled={busyId === 'ALL'}
                data-testid="cwv-fix-all-btn"
                className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm inline-flex items-center gap-2"
              >
                {busyId === 'ALL' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />} Fix all auto
              </button>
            )}
          </div>
        </div>

        {/* Score ring + stats */}
        {scan && (
          <div className="grid lg:grid-cols-3 gap-5 mb-6">
            <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 flex items-center gap-5" data-testid="cwv-score-ring">
              <ScoreRing score={scan.score} />
              <div>
                <p className="text-xs text-gray-400 uppercase">CWV Score</p>
                <p className="text-2xl text-white font-semibold">
                  {scan.score >= 90 ? 'Eccellente' : scan.score >= 50 ? 'Da migliorare' : 'Critico'}
                </p>
                <p className="text-sm text-gray-400 mt-1">
                  {scan.detected_count} problemi su 12 + bonus
                </p>
                <p className="text-xs text-gray-500">Last scan: {scan.url}</p>
              </div>
            </div>
            <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
              <p className="text-xs text-gray-400 uppercase mb-2">Progress</p>
              <p className="text-3xl text-white font-semibold">{doneCount}/{totalCount}</p>
              <p className="text-sm text-gray-400">azioni completate</p>
              <div className="h-2 bg-gray-700 rounded-full mt-3 overflow-hidden">
                <div className="h-full bg-emerald-500 transition-all" style={{ width: `${totalCount ? (doneCount / totalCount) * 100 : 0}%` }} />
              </div>
            </div>
            <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
              <p className="text-xs text-gray-400 uppercase mb-2">Stats</p>
              <div className="grid grid-cols-3 gap-3 text-center">
                <div><p className="text-xl text-white font-semibold">{scan.total_imgs ?? 0}</p><p className="text-xs text-gray-500">img</p></div>
                <div><p className="text-xl text-white font-semibold">{scan.total_scripts ?? 0}</p><p className="text-xs text-gray-500">scripts</p></div>
                <div><p className="text-xl text-white font-semibold">{Math.round((scan.html_size ?? 0) / 1024)}</p><p className="text-xs text-gray-500">KB HTML</p></div>
              </div>
            </div>
          </div>
        )}

        {/* Auto-fix section */}
        <h2 className="text-lg text-white font-semibold mb-3 inline-flex items-center gap-2">
          <Wrench className="w-4 h-4 text-blue-400" /> Auto-Fix (eseguibili dal tool)
        </h2>
        <div className="grid md:grid-cols-2 gap-3 mb-8">
          {autoItems.length === 0 && (
            <p className="text-gray-500 text-sm">Esegui uno scan per popolare la lista.</p>
          )}
          {autoItems.map((it) => (
            <CwvCard key={it.id} item={it} action={actionsByCwv[it.id]}
              busy={busyId === it.id}
              onFix={handleFix} onPatch={handlePatch}
              onMarkApplied={handleMarkApplied} onReset={handleReset} />
          ))}
        </div>

        {/* Manual section */}
        <h2 className="text-lg text-white font-semibold mb-3 inline-flex items-center gap-2">
          <Code2 className="w-4 h-4 text-violet-400" /> Manual Patch (snippet pronti per il dev)
        </h2>
        <div className="grid md:grid-cols-2 gap-3 mb-8">
          {manualItems.length === 0 && (
            <p className="text-gray-500 text-sm">Esegui uno scan per popolare la lista.</p>
          )}
          {manualItems.map((it) => (
            <CwvCard key={it.id} item={it} action={actionsByCwv[it.id]}
              busy={busyId === it.id}
              onFix={handleFix} onPatch={handlePatch}
              onMarkApplied={handleMarkApplied} onReset={handleReset} />
          ))}
        </div>

        {/* Verification */}
        {history.length > 0 && (
          <>
            <h2 className="text-lg text-white font-semibold mb-3 inline-flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" /> Score history
            </h2>
            <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
              <div className="flex items-end gap-1 h-24" data-testid="cwv-score-history">
                {history.slice(-30).map((h, i) => {
                  const sc = h.score || 0;
                  const color = sc >= 90 ? 'bg-emerald-500' : sc >= 50 ? 'bg-amber-500' : 'bg-red-500';
                  return (
                    <div key={i} title={`${new Date(h.ts).toLocaleString('it-IT')} → ${sc}`}
                      className={`flex-1 rounded-t ${color} transition-all`}
                      style={{ height: `${(sc / 100) * 100}%`, minHeight: '4px' }} />
                  );
                })}
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                <span>{history[0] ? new Date(history[0].ts).toLocaleDateString('it-IT') : ''}</span>
                <span>{history.length} scans</span>
                <span>now</span>
              </div>
            </div>
          </>
        )}
      </div>
    </AdminLayout>
  );
};

export default CwvAutomation;
