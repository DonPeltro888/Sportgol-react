import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import AdminLayout from '../../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../../contexts/AdminAuthContext';
import {
  Network, Copy, Globe2, MessageCircleQuestion, FileCode2,
  ChevronRight, Sparkles, Loader2, AlertTriangle, ChevronLeft,
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const Stat = ({ icon: Icon, label, value, color = 'text-white' }) => (
  <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-3">
    <div className="flex items-center gap-2 text-gray-400 text-xs">
      <Icon className="w-3.5 h-3.5" /> {label}
    </div>
    <div className={`mt-1 text-2xl font-bold ${color}`}>{value}</div>
  </div>
);

const Card = ({ to, title, desc, icon: Icon, color, badge }) => (
  <Link to={to} className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 hover:border-emerald-500 hover:bg-gray-800/70 transition-all">
    <div className="flex items-center justify-between mb-3">
      <div className="flex items-center gap-3">
        <div className={`w-12 h-12 rounded-lg ${color}/20 flex items-center justify-center`}>
          <Icon className={`w-6 h-6 ${color.replace('bg-', 'text-')}`} />
        </div>
        <h3 className="text-white font-bold">{title}</h3>
      </div>
      {badge && (
        <span className="text-[10px] bg-red-600 text-white px-2 py-0.5 rounded-full font-bold">
          {badge}
        </span>
      )}
    </div>
    <p className="text-xs text-gray-400">{desc}</p>
    <div className="mt-3 text-xs text-emerald-400 inline-flex items-center gap-1 font-medium">
      Apri <ChevronRight className="w-3 h-3" />
    </div>
  </Link>
);

const SeoIntelligenceHub = () => {
  const { authFetch } = useAdminAuth();
  const [overview, setOverview] = useState(null);
  const [cannibalization, setCannibalization] = useState(null);
  const [hreflang, setHreflang] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [r1, r2, r3] = await Promise.all([
          authFetch(`${API_URL}/api/seo/intelligence/topic-cluster/overview`),
          authFetch(`${API_URL}/api/seo/intelligence/cannibalization/scan?threshold=90&limit=20`),
          authFetch(`${API_URL}/api/seo/intelligence/hreflang/scan?limit=20`),
        ]);
        if (r1.ok) setOverview(await r1.json());
        if (r2.ok) setCannibalization(await r2.json());
        if (r3.ok) setHreflang(await r3.json());
      } catch (e) { /* ignore */ }
      finally { setLoading(false); }
    })();
  }, [authFetch]);

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto">
        <Link to="/admin/seo" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
          <ChevronLeft className="w-4 h-4" /> Torna a SEO Dashboard
        </Link>

        <div className="mb-6">
          <h1 className="text-2xl lg:text-3xl font-bold text-white inline-flex items-center gap-2">
            <Sparkles className="w-7 h-7 text-emerald-400" /> SEO Intelligence Hub
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Topic Cluster, Cannibalization, Hreflang, FAQ AI Generator, Team Verifier, JSON-LD Validator.
            Powered by Claude + Gemini + Perplexity.
          </p>
        </div>

        {/* Overview stats */}
        {loading ? (
          <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-8 text-center mb-6">
            <Loader2 className="w-6 h-6 animate-spin text-gray-500 mx-auto" />
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-3 mb-6">
            <Stat icon={Network} label="Leagues hubs" value={overview?.total_leagues || 0} color="text-blue-300" />
            <Stat icon={Network} label="Team hubs" value={overview?.total_teams || 0} color="text-purple-300" />
            <Stat icon={Network} label="Event spokes" value={overview?.total_events_future || 0} color="text-emerald-300" />
            <Stat
              icon={Copy}
              label="Cannibalization"
              value={cannibalization?.issues_found || 0}
              color={cannibalization?.by_severity?.HIGH > 0 ? 'text-red-400' : 'text-amber-300'}
            />
            <Stat
              icon={Globe2}
              label="Hreflang invalid"
              value={hreflang?.total_invalid || 0}
              color={hreflang?.by_severity?.HIGH > 0 ? 'text-red-400' : 'text-amber-300'}
            />
          </div>
        )}

        {/* High-severity alerts */}
        {(cannibalization?.by_severity?.HIGH > 0 || hreflang?.by_severity?.HIGH > 0) && (
          <div className="rounded-xl border border-red-700/50 bg-red-900/20 p-4 mb-6 flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1 text-sm">
              <h3 className="text-red-200 font-bold">Issue HIGH severity da risolvere:</h3>
              <ul className="text-red-300/80 mt-1 list-disc list-inside text-xs space-y-0.5">
                {cannibalization?.by_severity?.HIGH > 0 && (
                  <li>{cannibalization.by_severity.HIGH} cannibalization HIGH (entrambe Published)</li>
                )}
                {hreflang?.by_severity?.HIGH > 0 && (
                  <li>{hreflang.by_severity.HIGH} hreflang errors HIGH (lingue obbligatorie mancanti)</li>
                )}
              </ul>
            </div>
          </div>
        )}

        {/* Tools grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card
            to="/admin/seo/intelligence/topic-cluster"
            title="🌐 Topic Cluster"
            desc="Hub-Spoke graph: League → Teams → Events. Auto-internal linking per ogni entità con anchor contestuale."
            icon={Network}
            color="bg-blue-600"
          />
          <Card
            to="/admin/seo/intelligence/cannibalization"
            title="🔁 Cannibalization Detector"
            desc="Trova entità che competono per la stessa keyword (rapidfuzz token_set_ratio ≥ 85%)."
            icon={Copy}
            color="bg-orange-600"
            badge={cannibalization?.by_severity?.HIGH > 0 ? `${cannibalization.by_severity.HIGH} HIGH` : null}
          />
          <Card
            to="/admin/seo/intelligence/hreflang"
            title="🌍 Hreflang Validator"
            desc="Valida lingue obbligatorie, x-default, URL pattern, codici ISO 639-1, reciprocità."
            icon={Globe2}
            color="bg-purple-600"
            badge={hreflang?.by_severity?.HIGH > 0 ? `${hreflang.by_severity.HIGH} HIGH` : null}
          />
          <Card
            to="/admin/seo/intelligence/faq"
            title="🤖 AI FAQ Generator"
            desc="Claude Sonnet 4.5 genera 6 FAQ ottimizzate per Google PAA + FAQPage rich snippet (it/en/es)."
            icon={MessageCircleQuestion}
            color="bg-emerald-600"
          />
          <Card
            to="/admin/seo/intelligence/jsonld-validator"
            title="📋 JSON-LD Validator"
            desc="Valida tutti gli schema.org packets generati: required props, ISO dates, URL validi, coerenza."
            icon={FileCode2}
            color="bg-pink-600"
          />
        </div>

        {/* Top hubs preview */}
        {overview?.league_hubs && (
          <div className="mt-8 rounded-xl border border-gray-700 bg-gray-800/40 p-5">
            <h2 className="text-lg font-bold text-white mb-3">🏆 Top League Hubs (graph density)</h2>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="text-xs text-gray-400 uppercase">
                  <tr>
                    <th className="text-left px-3 py-2">Lega</th>
                    <th className="text-left px-3 py-2">Country</th>
                    <th className="text-center px-3 py-2">Teams</th>
                    <th className="text-center px-3 py-2">Events futuri</th>
                  </tr>
                </thead>
                <tbody>
                  {overview.league_hubs.slice(0, 8).map((h) => (
                    <tr key={h.slug} className="border-t border-gray-700/50">
                      <td className="px-3 py-2 text-white font-medium">{h.name}</td>
                      <td className="px-3 py-2 text-gray-400 text-xs">{h.country}</td>
                      <td className="px-3 py-2 text-center text-blue-300 font-bold">{h.team_count}</td>
                      <td className="px-3 py-2 text-center text-emerald-300 font-bold">{h.future_events}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default SeoIntelligenceHub;
