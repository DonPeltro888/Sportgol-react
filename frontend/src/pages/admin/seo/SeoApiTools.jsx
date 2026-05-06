import React, { useEffect, useState } from 'react';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import { Link } from 'react-router-dom';
import {
  KeyRound, CheckCircle2, XCircle, ExternalLink, Loader2, Save, Zap, Eye, EyeOff,
  Info, ArrowLeft, Sparkles, Bot, Languages, Search, Image as ImageIcon, Wand2
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const CATEGORY_META = {
  ai_llm: { label: 'AI / LLM', icon: Bot, color: 'text-blue-300', accent: 'border-blue-700/40 bg-blue-900/10' },
  research: { label: 'Web Research', icon: Search, color: 'text-purple-300', accent: 'border-purple-700/40 bg-purple-900/10' },
  seo_data: { label: 'SEO Data', icon: Sparkles, color: 'text-emerald-300', accent: 'border-emerald-700/40 bg-emerald-900/10' },
  translation: { label: 'Translation', icon: Languages, color: 'text-amber-300', accent: 'border-amber-700/40 bg-amber-900/10' },
  humanize: { label: 'Humanization', icon: Wand2, color: 'text-pink-300', accent: 'border-pink-700/40 bg-pink-900/10' },
  image: { label: 'Image SEO', icon: ImageIcon, color: 'text-indigo-300', accent: 'border-indigo-700/40 bg-indigo-900/10' },
};

const ToolCard = ({ tool, onSaved }) => {
  const { authFetch } = useAdminAuth();
  const [open, setOpen] = useState(false);
  const [keyInput, setKeyInput] = useState('');
  const [loginInput, setLoginInput] = useState(tool.api_login || '');
  const [showKey, setShowKey] = useState(false);
  const [active, setActive] = useState(tool.active);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);

  const meta = CATEGORY_META[tool.category] || CATEGORY_META.ai_llm;
  const Icon = meta.icon;

  const save = async () => {
    setSaving(true);
    try {
      const body = { active };
      if (keyInput !== '') body.api_key = keyInput;
      if (tool.requires_login && loginInput !== tool.api_login) body.api_login = loginInput;
      const r = await authFetch(`${API_URL}/api/seo/tools/${tool.slug}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (r.ok) {
        toast.success(`${tool.name} salvato`);
        setKeyInput('');
        setOpen(false);
        onSaved?.();
      } else {
        toast.error('Errore salvataggio');
      }
    } catch (e) {
      toast.error('Errore di rete');
    } finally {
      setSaving(false);
    }
  };

  const test = async () => {
    setTesting(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/tools/${tool.slug}/test`, { method: 'POST' });
      const d = await r.json();
      if (d.ok) toast.success(`✓ ${tool.name}: ${d.info || 'OK'} (${d.elapsed_ms}ms)`);
      else toast.error(`✗ ${tool.name}: ${d.error || 'fallito'}`);
      onSaved?.();
    } catch (e) {
      toast.error('Errore test');
    } finally {
      setTesting(false);
    }
  };

  const statusBadge = () => {
    if (!tool.has_key) return <span className="text-xs px-2 py-1 rounded bg-gray-700 text-gray-300">No key</span>;
    if (tool.last_test_status === 'ok') return <span className="text-xs px-2 py-1 rounded bg-emerald-900/40 text-emerald-300 border border-emerald-700">✓ Live</span>;
    if (tool.last_test_status === 'fail') return <span className="text-xs px-2 py-1 rounded bg-red-900/40 text-red-300 border border-red-700">✗ Fail</span>;
    return <span className="text-xs px-2 py-1 rounded bg-blue-900/40 text-blue-300 border border-blue-700">Configured</span>;
  };

  return (
    <div className={`rounded-xl border ${meta.accent} p-5 transition-all hover:bg-gray-800/40`} data-testid={`seo-tool-card-${tool.slug}`}>
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-10 h-10 rounded-lg bg-gray-800 border border-gray-700 flex items-center justify-center flex-shrink-0">
            <Icon className={`w-5 h-5 ${meta.color}`} />
          </div>
          <div className="min-w-0">
            <h3 className="text-white font-semibold truncate">{tool.name}</h3>
            <p className="text-[11px] text-gray-500 uppercase tracking-wide">{meta.label} · {tool.cost_type}</p>
          </div>
        </div>
        {statusBadge()}
      </div>

      <p className="text-xs text-gray-400 mb-3 line-clamp-2">{tool.description}</p>

      {/* Use cases */}
      {tool.use_cases?.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {tool.use_cases.slice(0, 3).map(uc => (
            <span key={uc} className="text-[10px] px-2 py-0.5 rounded bg-gray-800 text-gray-400 border border-gray-700">{uc}</span>
          ))}
          {tool.use_cases.length > 3 && (
            <span className="text-[10px] px-2 py-0.5 text-gray-500">+{tool.use_cases.length - 3}</span>
          )}
        </div>
      )}

      {/* Key info */}
      {tool.has_key && !open && (
        <div className="text-xs bg-gray-900/50 rounded p-2 mb-3 border border-gray-700">
          {tool.requires_login && tool.api_login && (
            <div className="text-gray-400">Login: <span className="text-gray-200">{tool.api_login}</span></div>
          )}
          <div className="text-gray-400">Key: <span className="font-mono text-gray-200">{tool.api_key_masked || '—'}</span></div>
          {tool.last_test_info && <div className="text-emerald-400 mt-1">{tool.last_test_info}</div>}
          {tool.last_test_error && <div className="text-red-400 mt-1 truncate">{tool.last_test_error}</div>}
        </div>
      )}

      {/* Edit form */}
      {open && (
        <div className="space-y-2 mb-3">
          {tool.requires_login && (
            <input
              type="text"
              value={loginInput}
              onChange={e => setLoginInput(e.target.value)}
              placeholder="Login (email)"
              data-testid={`seo-tool-login-${tool.slug}`}
              className="w-full px-3 py-2 rounded bg-gray-900 border border-gray-700 text-white text-sm focus:border-blue-500 focus:outline-none"
            />
          )}
          <div className="relative">
            <input
              type={showKey ? 'text' : 'password'}
              value={keyInput}
              onChange={e => setKeyInput(e.target.value)}
              placeholder={tool.has_key ? '(invariata)' : 'Inserisci API key'}
              data-testid={`seo-tool-key-${tool.slug}`}
              className="w-full px-3 py-2 pr-9 rounded bg-gray-900 border border-gray-700 text-white text-sm focus:border-blue-500 focus:outline-none font-mono"
            />
            <button onClick={() => setShowKey(v => !v)} className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white">
              {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          <label className="flex items-center gap-2 text-xs text-gray-300">
            <input type="checkbox" checked={active} onChange={e => setActive(e.target.checked)} data-testid={`seo-tool-active-${tool.slug}`} />
            Attivo
          </label>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap items-center gap-2">
        {!open && (
          <button
            onClick={() => { setOpen(true); setKeyInput(''); }}
            data-testid={`seo-tool-edit-${tool.slug}`}
            className="text-xs px-3 py-1.5 rounded bg-gray-700 hover:bg-gray-600 text-white inline-flex items-center gap-1"
          >
            <KeyRound className="w-3 h-3" /> {tool.has_key ? 'Cambia' : 'Configura'}
          </button>
        )}
        {open && (
          <>
            <button
              onClick={save}
              disabled={saving}
              data-testid={`seo-tool-save-${tool.slug}`}
              className="text-xs px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white inline-flex items-center gap-1 disabled:opacity-50"
            >
              {saving ? <Loader2 className="w-3 h-3 animate-spin" /> : <Save className="w-3 h-3" />}
              Salva
            </button>
            <button
              onClick={() => { setOpen(false); setKeyInput(''); }}
              className="text-xs px-3 py-1.5 rounded bg-gray-700 hover:bg-gray-600 text-gray-300"
            >
              Annulla
            </button>
          </>
        )}
        {tool.has_key && !open && !tool.p1_only && (
          <button
            onClick={test}
            disabled={testing}
            data-testid={`seo-tool-test-${tool.slug}`}
            className="text-xs px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-700 text-white inline-flex items-center gap-1 disabled:opacity-50"
          >
            {testing ? <Loader2 className="w-3 h-3 animate-spin" /> : <Zap className="w-3 h-3" />}
            Test
          </button>
        )}
        <a
          href={tool.website}
          target="_blank"
          rel="noopener noreferrer"
          className="ml-auto text-xs text-gray-400 hover:text-blue-400 inline-flex items-center gap-1"
        >
          Docs <ExternalLink className="w-3 h-3" />
        </a>
      </div>

      {tool.p1_only && (
        <div className="mt-3 text-[11px] text-amber-400 border border-amber-700/40 bg-amber-900/10 rounded p-2">
          ⏳ Disponibile in P1
        </div>
      )}
    </div>
  );
};

const SeoApiTools = () => {
  const { authFetch } = useAdminAuth();
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/tools`);
      if (r.ok) setTools(await r.json());
    } catch (e) {
      toast.error('Errore caricamento tool');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  // Group by category
  const grouped = tools.reduce((acc, t) => {
    if (!acc[t.category]) acc[t.category] = [];
    acc[t.category].push(t);
    return acc;
  }, {});

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <Link to="/admin/seo" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
            <ArrowLeft className="w-4 h-4" /> Torna a SEO Dashboard
          </Link>
          <h1 className="text-2xl lg:text-3xl font-bold text-white flex items-center gap-3" data-testid="seo-tools-title">
            <KeyRound className="w-7 h-7 text-blue-400" />
            API & Tools Settings
          </h1>
          <p className="mt-2 text-sm text-gray-400">
            Gestisci le chiavi API per ogni provider della pipeline. Le chiavi sono cifrate (Fernet AES) e non vengono mai esposte.
          </p>
        </div>

        {/* Info banner */}
        <div className="mb-6 rounded-lg border border-blue-700/40 bg-blue-900/10 p-4 text-xs text-blue-200 flex items-start gap-3">
          <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <div>
            Click <strong>Test</strong> per verificare ogni chiave in tempo reale. I tool con badge <span className="px-1 rounded bg-emerald-900/40 text-emerald-300 border border-emerald-700">✓ Live</span> sono pronti per la pipeline.
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-400">
            <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2" />
            Caricamento tools…
          </div>
        ) : (
          <div className="space-y-8">
            {['ai_llm', 'research', 'seo_data', 'translation', 'humanize', 'image'].map(cat => {
              const list = grouped[cat];
              if (!list?.length) return null;
              const meta = CATEGORY_META[cat];
              const Icon = meta?.icon || Sparkles;
              return (
                <div key={cat}>
                  <h2 className="text-sm uppercase tracking-wide text-gray-400 font-semibold mb-3 flex items-center gap-2">
                    <Icon className={`w-4 h-4 ${meta?.color}`} />
                    {meta?.label || cat}
                    <span className="text-gray-600">·</span>
                    <span className="text-gray-500 normal-case font-normal">{list.length} tool{list.length > 1 ? 's' : ''}</span>
                  </h2>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    {list.map(t => <ToolCard key={t.slug} tool={t} onSaved={load} />)}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default SeoApiTools;
