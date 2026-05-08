import React, { useEffect, useState } from 'react';
import AdminLayout from '../../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../../contexts/AdminAuthContext';
import { Link } from 'react-router-dom';
import { Loader2, Network, ChevronLeft } from 'lucide-react';
import SeoTargetSelector from '../../../../components/admin/SeoTargetSelector';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TopicCluster = () => {
  const { authFetch } = useAdminAuth();
  const [overview, setOverview] = useState(null);
  const [target, setTarget] = useState({ leagueSlug: '', teamSlug: '', eventSlug: '' });
  const [type, setType] = useState('league');
  const [links, setLinks] = useState(null);
  const [loadingLinks, setLoadingLinks] = useState(false);

  useEffect(() => {
    (async () => {
      const r = await authFetch(`${API_URL}/api/seo/intelligence/topic-cluster/overview`);
      if (r.ok) setOverview(await r.json());
    })();
  }, [authFetch]);

  // Auto-update type
  useEffect(() => {
    if (target.eventSlug) setType('event');
    else if (target.teamSlug) setType('team');
    else if (target.leagueSlug) setType('league');
  }, [target.leagueSlug, target.teamSlug, target.eventSlug]);

  const loadLinks = async () => {
    let slug = '';
    if (type === 'event') slug = target.eventSlug;
    else if (type === 'team') slug = target.teamSlug;
    else slug = target.leagueSlug;
    if (!slug) return;
    setLoadingLinks(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/intelligence/topic-cluster/${type}/${slug}`);
      if (r.ok) setLinks(await r.json());
    } finally { setLoadingLinks(false); }
  };

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-6xl mx-auto">
        <Link to="/admin/seo/intelligence" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
          <ChevronLeft className="w-4 h-4" /> Torna a Intelligence Hub
        </Link>
        <h1 className="text-2xl font-bold text-white inline-flex items-center gap-2">
          <Network className="w-7 h-7 text-blue-400" /> Topic Cluster Hub-Spoke
        </h1>
        <p className="text-sm text-gray-400 mt-1 mb-5">
          Internal linking automatico League → Teams → Events. Anchor text contestuali per ogni entità.
        </p>

        {overview && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-3">
              <div className="text-xs text-gray-400">League hubs</div>
              <div className="text-2xl font-bold text-blue-300">{overview.total_leagues}</div>
            </div>
            <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-3">
              <div className="text-xs text-gray-400">Team hubs</div>
              <div className="text-2xl font-bold text-purple-300">{overview.total_teams}</div>
            </div>
            <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-3">
              <div className="text-xs text-gray-400">Event spokes</div>
              <div className="text-2xl font-bold text-emerald-300">{overview.total_events_future}</div>
            </div>
            <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-3">
              <div className="text-xs text-gray-400">Total nodes</div>
              <div className="text-2xl font-bold text-white">
                {overview.total_leagues + overview.total_teams + overview.total_events_future}
              </div>
            </div>
          </div>
        )}

        <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6">
          <h2 className="text-lg font-bold text-white mb-3">🔍 Esplora i link di un'entità</h2>
          <SeoTargetSelector value={target} onChange={setTarget} compact />
          <div className="mt-3 flex justify-end">
            <button
              onClick={loadLinks}
              disabled={loadingLinks || !(target.leagueSlug || target.teamSlug || target.eventSlug)}
              className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold inline-flex items-center gap-2 disabled:opacity-50"
            >
              {loadingLinks ? <Loader2 className="w-4 h-4 animate-spin" /> : <Network className="w-4 h-4" />}
              Mostra Cluster
            </button>
          </div>
        </div>

        {links && (
          <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-bold text-white">
                {links.entity_type}/{links.slug} → {links.count} internal links
              </h2>
            </div>
            <div className="space-y-2">
              {links.links?.map((l, i) => (
                <div key={i} className="flex items-center justify-between gap-2 p-2.5 rounded bg-gray-900/40 border border-gray-700/50">
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-white truncate">{l.anchor}</div>
                    <div className="text-[11px] font-mono text-gray-400 truncate">{l.url}</div>
                  </div>
                  <span className="text-[10px] uppercase font-bold tracking-wide px-2 py-0.5 rounded bg-blue-900/40 text-blue-300 border border-blue-700/50 flex-shrink-0">
                    {l.rel}
                  </span>
                </div>
              ))}
              {(!links.links || links.links.length === 0) && (
                <div className="text-center text-gray-500 py-8 text-sm">Nessun link suggerito</div>
              )}
            </div>
          </div>
        )}

        {/* Top hubs */}
        {overview?.league_hubs && (
          <div className="mt-6 rounded-xl border border-gray-700 bg-gray-800/40 p-5">
            <h2 className="text-base font-bold text-white mb-3">🏆 Top Hub densità (top 10)</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {overview.league_hubs.slice(0, 10).map(h => (
                <div key={h.slug} className="flex items-center justify-between p-2.5 rounded bg-gray-900/40 border border-gray-700/50">
                  <div>
                    <div className="text-sm text-white font-medium">{h.name}</div>
                    <div className="text-[11px] text-gray-400">{h.country}</div>
                  </div>
                  <div className="flex gap-3 text-xs">
                    <span className="text-blue-300">{h.team_count} teams</span>
                    <span className="text-emerald-300">{h.future_events} events</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default TopicCluster;
