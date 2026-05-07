import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import SeoTargetSelector from './SeoTargetSelector';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { Loader2, Sparkles, ExternalLink, Filter as FilterIcon } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const STATUS_BADGE = {
  Draft: 'bg-gray-700 text-gray-300',
  Generating: 'bg-blue-700 text-blue-100',
  Generated: 'bg-blue-900/40 text-blue-300 border border-blue-700',
  'Needs Review': 'bg-amber-900/40 text-amber-300 border border-amber-700',
  Approved: 'bg-emerald-900/40 text-emerald-300 border border-emerald-700',
  Published: 'bg-purple-900/40 text-purple-300 border border-purple-700',
};

const TYPE_LABEL = { league: 'Lega', team: 'Squadra', event: 'Evento' };

/**
 * Pannello "Filter & Status" — lega → squadra → evento + tabella entità con stato.
 * Usato in SEO Dashboard.
 */
const SeoFilterStatusPanel = () => {
  const { authFetch } = useAdminAuth();
  const [target, setTarget] = useState({ leagueSlug: '', teamSlug: '', eventSlug: '' });
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [type, setType] = useState('team'); // event | team | league

  // Auto-set type based on selection
  useEffect(() => {
    if (target.eventSlug) setType('event');
    else if (target.teamSlug) setType('event'); // events of selected team
    else if (target.leagueSlug) setType(t => (t === 'league' ? 'league' : t));
  }, [target.leagueSlug, target.teamSlug, target.eventSlug]);

  const fetchItems = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ type, limit: '50', offset: '0' });
      if (target.leagueSlug) params.set('league_slug', target.leagueSlug);
      if (target.teamSlug && type === 'event') params.set('team_slug', target.teamSlug);
      if (target.eventSlug && type === 'event') params.set('q', target.eventSlug);
      const r = await authFetch(`${API_URL}/api/seo/targets?${params}`);
      if (r.ok) {
        const d = await r.json();
        setItems(d.items || []);
        setTotal(d.total || 0);
      } else { setItems([]); setTotal(0); }
    } catch (e) { setItems([]); setTotal(0); }
    finally { setLoading(false); }
  }, [authFetch, type, target.leagueSlug, target.teamSlug, target.eventSlug]);

  useEffect(() => { fetchItems(); }, [fetchItems]);

  const launchSingle = async (it) => {
    if (!window.confirm(`Avvio generazione SEO per "${it.title}"?`)) return;
    try {
      const r = await authFetch(`${API_URL}/api/seo/targets/${it.type}/${it.id}/generate`, { method: 'POST' });
      if (r.ok) { fetchItems(); } else { /* ignore */ }
    } catch (e) { /* ignore */ }
  };

  return (
    <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-8" data-testid="seo-filter-status-panel">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
        <h2 className="text-lg font-bold text-white inline-flex items-center gap-2">
          <FilterIcon className="w-5 h-5 text-blue-400" /> Filtra & Stato Entità
        </h2>
        <div className="flex gap-1 bg-gray-900 rounded-lg p-0.5">
          {['league', 'team', 'event'].map(t => (
            <button
              key={t}
              onClick={() => setType(t)}
              data-testid={`seo-filter-type-${t}`}
              className={`px-3 py-1 rounded text-xs font-semibold transition-colors ${
                type === t ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              {TYPE_LABEL[t]}
            </button>
          ))}
        </div>
      </div>

      <SeoTargetSelector value={target} onChange={setTarget} compact />

      <div className="mt-4 rounded-lg border border-gray-700 overflow-hidden">
        <div className="px-4 py-2 bg-gray-900/60 text-xs text-gray-400 flex items-center justify-between">
          <span>Risultati: <strong className="text-white">{total.toLocaleString()}</strong> {TYPE_LABEL[type]?.toLowerCase()}</span>
          {loading && <Loader2 className="w-4 h-4 text-gray-500 animate-spin" />}
        </div>
        <div className="overflow-x-auto max-h-[420px]">
          <table className="w-full text-sm">
            <thead className="bg-gray-900/40 text-gray-400 text-xs uppercase">
              <tr>
                <th className="text-left px-3 py-2">Titolo</th>
                <th className="text-left px-3 py-2 hidden md:table-cell">Slug</th>
                <th className="text-center px-3 py-2">Stato SEO</th>
                <th className="text-center px-3 py-2">Score</th>
                <th className="text-right px-3 py-2">Azioni</th>
              </tr>
            </thead>
            <tbody>
              {items.length === 0 && !loading && (
                <tr><td colSpan={5} className="py-8 text-center text-gray-500 text-sm">Nessun risultato</td></tr>
              )}
              {items.map(it => {
                const status = it.seo_status || 'Draft';
                const isLive = status === 'Published';
                return (
                  <tr key={`${it.type}-${it.id}`} className="border-t border-gray-700/50 hover:bg-gray-900/30">
                    <td className="px-3 py-2 text-white">
                      <span className="font-medium truncate inline-block max-w-[280px]" title={it.title}>{it.title}</span>
                      {it.has_draft && <span className="ml-2 text-[10px] text-blue-400">draft</span>}
                    </td>
                    <td className="px-3 py-2 text-gray-400 text-xs hidden md:table-cell font-mono">{it.slug || '—'}</td>
                    <td className="px-3 py-2 text-center">
                      <span className={`text-[10px] uppercase font-bold tracking-wide px-2 py-0.5 rounded ${STATUS_BADGE[status] || STATUS_BADGE.Draft}`}>
                        {isLive ? 'Live' : status}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-center text-xs">
                      {it.seo_score != null ? <span className="font-bold text-emerald-300">{it.seo_score}</span> : <span className="text-gray-600">—</span>}
                    </td>
                    <td className="px-3 py-2 text-right">
                      <div className="inline-flex gap-1">
                        <button
                          onClick={() => launchSingle(it)}
                          data-testid={`seo-quick-generate-${it.id}`}
                          className="text-[11px] px-2 py-1 rounded bg-blue-600 hover:bg-blue-700 text-white inline-flex items-center gap-1"
                        >
                          <Sparkles className="w-3 h-3" /> Genera
                        </button>
                        <Link
                          to={`/admin/seo/targets/${it.type}/${it.id}`}
                          className="text-[11px] px-2 py-1 rounded bg-gray-700 hover:bg-gray-600 text-white inline-flex items-center gap-1"
                        >
                          <ExternalLink className="w-3 h-3" /> Apri
                        </Link>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default SeoFilterStatusPanel;
