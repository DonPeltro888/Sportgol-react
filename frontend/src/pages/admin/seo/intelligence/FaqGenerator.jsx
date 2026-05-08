import React, { useState } from 'react';
import AdminLayout from '../../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../../contexts/AdminAuthContext';
import SeoTargetSelector from '../../../../components/admin/SeoTargetSelector';
import { Link } from 'react-router-dom';
import { Loader2, MessageCircleQuestion, ChevronLeft, Sparkles } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const FaqGenerator = () => {
  const { authFetch } = useAdminAuth();
  const [target, setTarget] = useState({ leagueSlug: '', teamSlug: '', eventSlug: '' });
  const [type, setType] = useState('event');
  const [langs, setLangs] = useState({ it: true, en: true, es: true });
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState(null);
  const [previewLang, setPreviewLang] = useState('it');

  React.useEffect(() => {
    if (target.eventSlug) setType('event');
    else if (target.teamSlug) setType('team');
    else if (target.leagueSlug) setType('league');
  }, [target.leagueSlug, target.teamSlug, target.eventSlug]);

  const generate = async () => {
    let slug = '';
    if (type === 'event') slug = target.eventSlug;
    else if (type === 'team') slug = target.teamSlug;
    else slug = target.leagueSlug;
    if (!slug) return toast.error('Seleziona un\'entità');
    const langsCsv = Object.keys(langs).filter(k => langs[k]).join(',');
    if (!langsCsv) return toast.error('Seleziona almeno una lingua');

    setGenerating(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/intelligence/faq/${type}/${slug}/generate?langs=${langsCsv}`, {
        method: 'POST',
      });
      const d = await r.json();
      if (r.ok && d.ok) {
        toast.success(`FAQ generate: ${Object.entries(d.faq_counts || {}).map(([l, n]) => `${l}=${n}`).join(', ')}`);
        // load preview
        const r2 = await authFetch(`${API_URL}/api/seo/intelligence/faq/${type}/${slug}?lang=${previewLang}`);
        if (r2.ok) setResult(await r2.json());
      } else toast.error(d.error || 'Errore generation');
    } catch (e) { toast.error('Errore di rete'); }
    finally { setGenerating(false); }
  };

  const loadPreview = async (lang) => {
    let slug = '';
    if (type === 'event') slug = target.eventSlug;
    else if (type === 'team') slug = target.teamSlug;
    else slug = target.leagueSlug;
    if (!slug) return;
    setPreviewLang(lang);
    const r = await authFetch(`${API_URL}/api/seo/intelligence/faq/${type}/${slug}?lang=${lang}`);
    if (r.ok) setResult(await r.json());
  };

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-5xl mx-auto">
        <Link to="/admin/seo/intelligence" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
          <ChevronLeft className="w-4 h-4" /> Torna a Intelligence Hub
        </Link>
        <h1 className="text-2xl font-bold text-white inline-flex items-center gap-2">
          <MessageCircleQuestion className="w-7 h-7 text-emerald-400" /> AI FAQ Generator (FAQPage Schema)
        </h1>
        <p className="text-sm text-gray-400 mt-1 mb-5">
          Claude Sonnet 4.5 genera 6 FAQ ottimizzate per Google "People Also Ask" + FAQPage rich snippet.
          Le FAQ vengono salvate in <code className="text-emerald-300">seo_meta.{'{lang}'}.faq</code> e
          iniettate automaticamente come schema.org/FAQPage nelle pagine pubbliche.
        </p>

        <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6">
          <h2 className="text-base font-bold text-white mb-3">Seleziona entità</h2>
          <SeoTargetSelector value={target} onChange={setTarget} compact />

          <div className="mt-4 flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400">Lingue:</span>
              {['it', 'en', 'es'].map(l => (
                <label key={l} className="text-xs text-gray-200 inline-flex items-center gap-1">
                  <input
                    type="checkbox"
                    checked={langs[l]}
                    onChange={e => setLangs(prev => ({ ...prev, [l]: e.target.checked }))}
                    className="w-3.5 h-3.5"
                  />
                  {l.toUpperCase()}
                </label>
              ))}
            </div>
            <button
              onClick={generate}
              disabled={generating}
              data-testid="faq-generate-btn"
              className="ml-auto px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold inline-flex items-center gap-2 disabled:opacity-50"
            >
              {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              Genera FAQ
            </button>
          </div>
        </div>

        {result?.faq?.length > 0 && (
          <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-bold text-white">
                FAQ ({result.faq.length}) — {result.entity_type}/{result.slug}
              </h2>
              <div className="flex gap-1 bg-gray-900 rounded p-0.5">
                {['it', 'en', 'es'].map(l => (
                  <button
                    key={l}
                    onClick={() => loadPreview(l)}
                    className={`px-2.5 py-0.5 text-xs rounded ${previewLang === l ? 'bg-emerald-600 text-white' : 'text-gray-400'}`}
                  >
                    {l.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
            <div className="space-y-3">
              {result.faq.map((f, i) => (
                <div key={i} className="rounded border border-gray-700 bg-gray-900/40 p-3">
                  <div className="text-sm text-emerald-300 font-semibold mb-1">Q: {f.q}</div>
                  <div className="text-sm text-gray-200 leading-relaxed">A: {f.a}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default FaqGenerator;
