import React, { useEffect, useState } from 'react';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import { Link } from 'react-router-dom';
import {
  FileText, ArrowLeft, Search, Loader2, Calendar, Trophy, Users,
  Lock, Sparkles, ExternalLink, ChevronLeft, ChevronRight
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TYPE_META = {
  event: { label: 'Match', icon: Calendar, accent: 'text-blue-300' },
  league: { label: 'Lega', icon: Trophy, accent: 'text-amber-300' },
  team: { label: 'Squadra', icon: Users, accent: 'text-emerald-300' },
};

const STATUS_BADGE = {
  Draft: 'bg-gray-700 text-gray-300',
  Generated: 'bg-blue-900/40 text-blue-300 border border-blue-700',
  'Needs Review': 'bg-amber-900/40 text-amber-300 border border-amber-700',
  Approved: 'bg-emerald-900/40 text-emerald-300 border border-emerald-700',
  Published: 'bg-purple-900/40 text-purple-300 border border-purple-700',
};

const SeoPagesList = () => {
  const { authFetch } = useAdminAuth();
  const [type, setType] = useState('event');
  const [q, setQ] = useState('');
  const [status, setStatus] = useState('');
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [limit] = useState(25);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ type, limit, offset });
      if (q) params.set('q', q);
      if (status) params.set('status', status);
      const r = await authFetch(`${API_URL}/api/seo/targets?${params}`);
      if (r.ok) {
        const d = await r.json();
        setItems(d.items || []);
        setTotal(d.total || 0);
      }
    } catch (e) {
      toast.error('Errore caricamento');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { setOffset(0); }, [type, status]);
  useEffect(() => { load(); /* eslint-disable-next-line */ }, [type, status, offset]);

  const onSearch = (e) => {
    e.preventDefault();
    setOffset(0);
    load();
  };

  const Icon = TYPE_META[type].icon;

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto">
        <Link to="/admin/seo" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
          <ArrowLeft className="w-4 h-4" /> Torna a SEO Dashboard
        </Link>
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6 gap-3">
          <div>
            <h1 className="text-2xl lg:text-3xl font-bold text-white flex items-center gap-3" data-testid="seo-pages-title">
              <FileText className="w-7 h-7 text-purple-400" />
              SEO Pages — Entity esistenti
            </h1>
            <p className="mt-2 text-sm text-gray-400">
              Il SEO Admin scrive su <code className="px-1 bg-gray-800 rounded">events</code>, <code className="px-1 bg-gray-800 rounded">leagues</code>, <code className="px-1 bg-gray-800 rounded">teams</code> già esistenti. Nessuna pagina nuova.
            </p>
          </div>
        </div>

        {/* Type tabs */}
        <div className="flex gap-2 mb-4">
          {['event', 'league', 'team'].map(t => {
            const m = TYPE_META[t];
            const TIcon = m.icon;
            const active = t === type;
            return (
              <button
                key={t}
                onClick={() => setType(t)}
                data-testid={`seo-type-tab-${t}`}
                className={`px-4 py-2 rounded-lg text-sm font-semibold inline-flex items-center gap-2 transition-all ${
                  active
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                <TIcon className={`w-4 h-4 ${active ? 'text-white' : m.accent}`} />
                {m.label}{t === 'event' ? ' (Match)' : ''}
              </button>
            );
          })}
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-12 gap-3 mb-4">
          <form onSubmit={onSearch} className="md:col-span-7 relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              value={q}
              onChange={e => setQ(e.target.value)}
              placeholder={`Cerca ${TYPE_META[type].label.toLowerCase()}...`}
              data-testid="seo-pages-search-input"
              className="w-full pl-10 pr-3 py-2.5 bg-gray-900 border border-gray-700 rounded-lg text-white text-sm focus:border-blue-500 focus:outline-none"
            />
          </form>
          <select
            value={status}
            onChange={e => setStatus(e.target.value)}
            data-testid="seo-pages-status-filter"
            className="md:col-span-3 px-3 py-2.5 bg-gray-900 border border-gray-700 rounded-lg text-white text-sm focus:border-blue-500 focus:outline-none"
          >
            <option value="">Tutti gli stati</option>
            <option value="Draft">Draft</option>
            <option value="Generated">Generated</option>
            <option value="Needs Review">Needs Review</option>
            <option value="Approved">Approved</option>
            <option value="Published">Published</option>
          </select>
          <button
            onClick={onSearch}
            data-testid="seo-pages-search-btn"
            className="md:col-span-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold inline-flex items-center justify-center gap-1"
          >
            <Search className="w-4 h-4" /> Cerca
          </button>
        </div>

        {/* Results */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/40 overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-700 text-xs text-gray-400 flex items-center justify-between">
            <span>Totale: <strong className="text-white">{total.toLocaleString()}</strong> {TYPE_META[type].label.toLowerCase()}</span>
            <span>Pagina {Math.floor(offset / limit) + 1} di {Math.max(1, Math.ceil(total / limit))}</span>
          </div>
          <table className="w-full text-sm">
            <thead className="bg-gray-900/60 text-gray-400 text-xs uppercase tracking-wide">
              <tr>
                <th className="text-left px-4 py-3">Title</th>
                <th className="text-left px-4 py-3 hidden md:table-cell">Slug / Lega</th>
                <th className="text-left px-4 py-3 hidden lg:table-cell">Data</th>
                <th className="text-center px-4 py-3">Stato SEO</th>
                <th className="text-center px-4 py-3">Locks</th>
                <th className="text-right px-4 py-3">Azioni</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr><td colSpan={6} className="px-4 py-12 text-center text-gray-400">
                  <Loader2 className="w-5 h-5 animate-spin mx-auto" />
                </td></tr>
              )}
              {!loading && items.length === 0 && (
                <tr><td colSpan={6} className="px-4 py-12 text-center text-gray-500">Nessun risultato</td></tr>
              )}
              {!loading && items.map(item => (
                <tr key={`${item.type}-${item.id}`} className="border-t border-gray-700/50 hover:bg-gray-900/40">
                  <td className="px-4 py-3 text-white">
                    <div className="flex items-center gap-2">
                      <Icon className="w-4 h-4 text-gray-500 flex-shrink-0" />
                      <span className="font-medium truncate max-w-[260px]" title={item.title}>{item.title}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-xs hidden md:table-cell">
                    <div className="truncate max-w-[180px]">{item.slug || '—'}</div>
                    {item.league && <div className="text-gray-500">{item.league}</div>}
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-xs hidden lg:table-cell whitespace-nowrap">
                    {item.sort_date ? new Date(item.sort_date).toLocaleDateString('it-IT') : '—'}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`text-xs px-2 py-1 rounded ${STATUS_BADGE[item.seo_status] || STATUS_BADGE.Draft}`}>
                      {item.seo_status}
                    </span>
                    {item.has_draft && (
                      <div className="mt-1 text-[10px] text-blue-400">draft pronto</div>
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {item.locked_fields_count > 0 ? (
                      <span className="text-xs inline-flex items-center gap-1 text-amber-300">
                        <Lock className="w-3 h-3" /> {item.locked_fields_count}
                      </span>
                    ) : <span className="text-gray-600 text-xs">—</span>}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      to={`/admin/seo/targets/${item.type}/${item.id}`}
                      data-testid={`seo-target-edit-${item.id}`}
                      className="inline-flex items-center gap-1 text-xs px-3 py-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      <Sparkles className="w-3 h-3" /> SEO
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          {total > limit && (
            <div className="px-4 py-3 border-t border-gray-700 flex items-center justify-between text-xs">
              <button
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - limit))}
                className="px-3 py-1.5 rounded bg-gray-700 hover:bg-gray-600 text-white disabled:opacity-40 inline-flex items-center gap-1"
              >
                <ChevronLeft className="w-3 h-3" /> Precedente
              </button>
              <span className="text-gray-400">{offset + 1} – {Math.min(offset + limit, total)} di {total.toLocaleString()}</span>
              <button
                disabled={offset + limit >= total}
                onClick={() => setOffset(offset + limit)}
                className="px-3 py-1.5 rounded bg-gray-700 hover:bg-gray-600 text-white disabled:opacity-40 inline-flex items-center gap-1"
              >
                Successiva <ChevronRight className="w-3 h-3" />
              </button>
            </div>
          )}
        </div>
      </div>
    </AdminLayout>
  );
};

export default SeoPagesList;
