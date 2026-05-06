import React, { useEffect, useState } from 'react';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, Sparkles, Lock, Unlock, Save, Trash2, Loader2, CheckCircle2,
  Languages, FileCode, AlertCircle, Wand2, Eye
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const LANGS = ['it', 'en', 'es'];
const FIELDS = [
  { key: 'meta_title', label: 'Meta Title', max: 60 },
  { key: 'meta_description', label: 'Meta Description', max: 160 },
  { key: 'h1', label: 'H1' },
  { key: 'intro_text', label: 'Intro', textarea: true },
  { key: 'cta_text', label: 'CTA' },
  { key: 'open_graph_title', label: 'OG Title' },
  { key: 'open_graph_description', label: 'OG Description', textarea: true },
];

const FieldRow = ({ lang, field, value, locked, onChange, onLock }) => {
  const [v, setV] = useState(value || '');
  useEffect(() => { setV(value || ''); }, [value]);
  const tooLong = field.max && v && v.length > field.max;
  const tooShort = field.max && v && v.length < field.max * 0.4;

  return (
    <div className={`rounded-lg border ${locked ? 'border-amber-700/40 bg-amber-900/10' : 'border-gray-700 bg-gray-900/40'} p-3 mb-2`}>
      <div className="flex items-center justify-between mb-1.5">
        <label className="text-xs font-semibold text-gray-300 flex items-center gap-2">
          <span className="px-1.5 py-0.5 rounded bg-gray-700 text-[10px] uppercase">{lang}</span>
          {field.label}
          {field.max && <span className={`text-[10px] ${tooLong ? 'text-red-400' : tooShort ? 'text-amber-400' : 'text-gray-500'}`}>
            {v.length}/{field.max}
          </span>}
        </label>
        <div className="flex gap-1">
          <button
            onClick={() => onLock(!locked)}
            data-testid={`seo-field-lock-${lang}-${field.key}`}
            className={`text-xs px-2 py-1 rounded inline-flex items-center gap-1 ${
              locked ? 'bg-amber-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {locked ? <Lock className="w-3 h-3" /> : <Unlock className="w-3 h-3" />}
            {locked ? 'Lock' : 'Unlock'}
          </button>
          <button
            onClick={() => onChange(v)}
            data-testid={`seo-field-save-${lang}-${field.key}`}
            className="text-xs px-2 py-1 rounded bg-blue-600 hover:bg-blue-700 text-white inline-flex items-center gap-1"
          >
            <Save className="w-3 h-3" /> Save
          </button>
        </div>
      </div>
      {field.textarea ? (
        <textarea
          value={v}
          onChange={e => setV(e.target.value)}
          disabled={locked}
          rows={3}
          data-testid={`seo-field-${lang}-${field.key}`}
          className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm resize-y disabled:opacity-60 focus:border-blue-500 focus:outline-none"
        />
      ) : (
        <input
          value={v}
          onChange={e => setV(e.target.value)}
          disabled={locked}
          data-testid={`seo-field-${lang}-${field.key}`}
          className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm disabled:opacity-60 focus:border-blue-500 focus:outline-none"
        />
      )}
    </div>
  );
};

const SeoTargetEditor = () => {
  const { type, id } = useParams();
  const { authFetch } = useAdminAuth();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [tab, setTab] = useState('it');
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [view, setView] = useState('meta'); // 'meta' = pubblicato, 'draft' = generato

  const load = async () => {
    setLoading(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/targets/${type}/${id}`);
      if (r.ok) setData((await r.json()).data);
      else toast.error('Errore caricamento');
    } catch (e) {
      toast.error('Errore di rete');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, [type, id]);

  const generate = async () => {
    setGenerating(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/targets/${type}/${id}/generate`, { method: 'POST' });
      const d = await r.json();
      if (r.ok) {
        toast.success(d.note || 'Draft generato');
        setView('draft');
        load();
      } else toast.error(d.detail || 'Errore generazione');
    } catch (e) {
      toast.error('Errore di rete');
    } finally {
      setGenerating(false);
    }
  };

  const publish = async () => {
    if (!window.confirm('Pubblichi il draft sui campi reali della pagina? Verranno sovrascritti i campi NON lockati.')) return;
    setPublishing(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/targets/${type}/${id}/publish`, { method: 'POST' });
      const d = await r.json();
      if (r.ok) {
        toast.success(`Pubblicato! ${d.applied} campi applicati, ${d.skipped_locked} saltati (locked)`);
        setView('meta');
        load();
      } else toast.error(d.detail || 'Errore pubblicazione');
    } catch (e) {
      toast.error('Errore di rete');
    } finally {
      setPublishing(false);
    }
  };

  const discard = async () => {
    if (!window.confirm('Elimini il draft generato?')) return;
    try {
      const r = await authFetch(`${API_URL}/api/seo/targets/${type}/${id}/draft`, { method: 'DELETE' });
      if (r.ok) { toast.success('Draft eliminato'); load(); }
      else toast.error('Errore');
    } catch (e) { toast.error('Errore di rete'); }
  };

  const saveField = async (lang, fieldKey, value) => {
    try {
      const r = await authFetch(`${API_URL}/api/seo/targets/${type}/${id}/field`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field_path: `${lang}.${fieldKey}`, value }),
      });
      if (r.ok) { toast.success('Salvato'); load(); }
      else toast.error('Errore');
    } catch (e) { toast.error('Errore di rete'); }
  };

  const toggleLock = async (lang, fieldKey, locked) => {
    try {
      const r = await authFetch(`${API_URL}/api/seo/targets/${type}/${id}/lock`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ field_path: `${lang}.${fieldKey}`, locked }),
      });
      if (r.ok) { toast.success(locked ? 'Field locked' : 'Unlocked'); load(); }
      else toast.error('Errore');
    } catch (e) { toast.error('Errore di rete'); }
  };

  if (loading) return (
    <AdminLayout>
      <div className="p-12 text-center text-gray-400"><Loader2 className="w-8 h-8 animate-spin mx-auto" /></div>
    </AdminLayout>
  );
  if (!data) return (
    <AdminLayout>
      <div className="p-12 text-center text-red-400">Entity non trovata</div>
    </AdminLayout>
  );

  const title = data.title || data.name || data.slug || '?';
  const matchTitle = (type === 'event' && data.home_team && data.away_team)
    ? `${data.home_team} vs ${data.away_team}` : title;
  const meta = data.seo_meta || { it: {}, en: {}, es: {} };
  const draft = data.seo_draft || {};
  const locks = data.seo_locks || {};
  const showing = view === 'draft' ? draft : meta;
  const hasDraft = Object.keys(draft).length > 0;

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-6xl mx-auto">
        <Link to="/admin/seo/pages" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
          <ArrowLeft className="w-4 h-4" /> Torna alla lista
        </Link>

        {/* Header */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/50 p-5 mb-5">
          <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-3">
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-wide font-semibold mb-1">
                {type === 'event' ? 'Match' : type === 'league' ? 'Lega' : 'Squadra'}
                {data.slug && <span className="ml-2 text-gray-600">/{data.slug}</span>}
              </div>
              <h1 className="text-2xl font-bold text-white" data-testid="seo-target-title">{matchTitle}</h1>
              <div className="mt-2 flex flex-wrap gap-2 text-xs">
                <span className="px-2 py-1 rounded bg-gray-700 text-gray-300">Stato: <strong>{data.seo_status || 'Draft'}</strong></span>
                {data.seo_published_at && <span className="px-2 py-1 rounded bg-purple-900/30 text-purple-300">Pubblicato: {new Date(data.seo_published_at).toLocaleString('it-IT')}</span>}
                {hasDraft && <span className="px-2 py-1 rounded bg-blue-900/40 text-blue-300">Draft pronto</span>}
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <button
                onClick={generate}
                disabled={generating}
                data-testid="seo-target-generate-btn"
                className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold inline-flex items-center gap-2 disabled:opacity-50"
              >
                {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                Genera SEO con AI
              </button>
              {hasDraft && (
                <>
                  <button
                    onClick={publish}
                    disabled={publishing}
                    data-testid="seo-target-publish-btn"
                    className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold inline-flex items-center gap-2 disabled:opacity-50"
                  >
                    {publishing ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                    Pubblica draft
                  </button>
                  <button
                    onClick={discard}
                    data-testid="seo-target-discard-btn"
                    className="px-3 py-2 rounded-lg bg-red-900/40 hover:bg-red-900/70 text-red-300 text-sm inline-flex items-center gap-1"
                  >
                    <Trash2 className="w-4 h-4" /> Elimina draft
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Notice MOCK */}
        <div className="mb-4 rounded-lg border border-amber-700/40 bg-amber-900/10 p-3 text-xs text-amber-200 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <div>
            <strong>P1 – Pipeline mock attiva.</strong> Il bottone "Genera SEO" produce un draft realistico ma non chiama ancora i provider.
            FASE 2 collegherà Claude (copy IT), Gemini (schema), Perplexity (FAQ PAA), DataForSEO (keywords), DeepL (EN+ES). Tutte le 4 chiavi sono già live.
          </div>
        </div>

        {/* View toggle (Draft vs Published) */}
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setView('meta')}
            className={`px-3 py-1.5 rounded text-xs inline-flex items-center gap-1 ${view === 'meta' ? 'bg-purple-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}
          >
            <Eye className="w-3 h-3" /> Pubblicato (live)
          </button>
          <button
            onClick={() => setView('draft')}
            disabled={!hasDraft}
            className={`px-3 py-1.5 rounded text-xs inline-flex items-center gap-1 disabled:opacity-40 ${view === 'draft' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}`}
          >
            <Wand2 className="w-3 h-3" /> Draft (da approvare)
          </button>
        </div>

        {/* Lang tabs */}
        <div className="flex gap-2 mb-4 border-b border-gray-700">
          {LANGS.map(l => (
            <button
              key={l}
              onClick={() => setTab(l)}
              data-testid={`seo-lang-tab-${l}`}
              className={`px-4 py-2 text-sm font-semibold border-b-2 transition-colors inline-flex items-center gap-2 ${
                tab === l ? 'border-blue-500 text-white' : 'border-transparent text-gray-400 hover:text-white'
              }`}
            >
              <Languages className="w-4 h-4" /> {l.toUpperCase()}
            </button>
          ))}
        </div>

        {/* Fields */}
        <div className="space-y-1">
          {FIELDS.map(field => {
            const value = (showing[tab] || {})[field.key];
            const isLocked = !!locks[`${tab}.${field.key}`];
            return (
              <FieldRow
                key={`${tab}-${field.key}`}
                lang={tab}
                field={field}
                value={value}
                locked={isLocked}
                onChange={(v) => saveField(tab, field.key, v)}
                onLock={(l) => toggleLock(tab, field.key, l)}
              />
            );
          })}
        </div>

        {/* Schema preview */}
        {(data.seo_meta_schema_jsonld || data.seo_draft_schema_jsonld) && (
          <details className="mt-6 rounded-lg border border-gray-700 bg-gray-900/40 p-4">
            <summary className="cursor-pointer text-sm font-semibold text-white inline-flex items-center gap-2">
              <FileCode className="w-4 h-4" /> JSON-LD Schema ({view === 'draft' ? 'draft' : 'pubblicato'})
            </summary>
            <pre className="mt-3 text-xs text-gray-300 overflow-auto bg-black/30 p-3 rounded max-h-96">
              {JSON.stringify(view === 'draft' ? data.seo_draft_schema_jsonld : data.seo_meta_schema_jsonld, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </AdminLayout>
  );
};

export default SeoTargetEditor;
