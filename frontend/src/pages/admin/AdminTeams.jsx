import React, { useState, useEffect } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { Search, Image as ImageIcon, RefreshCw, Loader2, Filter } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminTeams = () => {
  const { authFetch } = useAdminAuth();
  const [teams, setTeams] = useState([]);
  const [leagues, setLeagues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [leagueFilter, setLeagueFilter] = useState('all');
  const [refreshingId, setRefreshingId] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [tRes, lRes] = await Promise.all([
        fetch(`${API_URL}/api/teams?active_only=false`),
        fetch(`${API_URL}/api/leagues?active_only=false`),
      ]);
      const tData = await tRes.json();
      const lData = await lRes.json();
      setTeams(tData.teams || []);
      setLeagues(lData.leagues || []);
    } catch (e) {
      toast.error('Errore caricamento');
    } finally {
      setLoading(false);
    }
  };

  const refreshLogo = async (teamId, teamName) => {
    try {
      setRefreshingId(teamId);
      const r = await authFetch(`${API_URL}/api/admin/sync/team-logo/${teamId}`, {
        method: 'POST',
      });
      const data = await r.json();
      if (data.success) {
        toast.success(`Logo aggiornato per ${teamName}`);
        fetchData();
      } else {
        toast.warning(data.message || 'Logo non trovato');
      }
    } catch (e) {
      toast.error('Errore: ' + e.message);
    } finally {
      setRefreshingId(null);
    }
  };

  const filtered = teams.filter(t => {
    if (leagueFilter !== 'all' && t.league_slug !== leagueFilter) return false;
    if (search && !t.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const stats = {
    total: teams.length,
    withLogo: teams.filter(t => t.logo_url).length,
    autoCreated: teams.filter(t => t.auto_created).length,
  };

  return (
    <AdminLayout>
      <div className="space-y-6" data-testid="admin-teams-page">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <ImageIcon className="w-6 h-6 text-blue-400" /> Squadre & Loghi
          </h1>
          <p className="text-gray-400">Gestisci tutte le squadre e i loghi dal database (auto-popolati via TheSportsDB)</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="text-gray-400 text-xs">Squadre Totali</div>
            <div className="text-3xl font-bold text-white">{stats.total}</div>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="text-gray-400 text-xs">Con Logo</div>
            <div className="text-3xl font-bold text-green-400">{stats.withLogo}</div>
            <div className="text-xs text-gray-500">{stats.total ? Math.round(stats.withLogo / stats.total * 100) : 0}%</div>
          </div>
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-4">
            <div className="text-gray-400 text-xs">Auto-Create</div>
            <div className="text-3xl font-bold text-blue-400">{stats.autoCreated}</div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-4 flex flex-col sm:flex-row gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Cerca squadra..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              data-testid="search-team-input"
              className="w-full bg-gray-900 border border-gray-700 rounded-lg pl-9 pr-4 py-2 text-white placeholder-gray-500 focus:border-blue-500 outline-none"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <select
              value={leagueFilter}
              onChange={(e) => setLeagueFilter(e.target.value)}
              data-testid="filter-league-select"
              className="bg-gray-900 border border-gray-700 rounded-lg pl-9 pr-4 py-2 text-white focus:border-blue-500 outline-none"
            >
              <option value="all">Tutte le leghe</option>
              {leagues.filter(l => l.type === 'league').map(l => (
                <option key={l.slug} value={l.slug}>{l.name}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Teams grid */}
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-blue-400" />
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3" data-testid="teams-grid">
            {filtered.map(team => (
              <div key={team.id} className="bg-gray-800 border border-gray-700 rounded-xl p-3 flex flex-col items-center text-center">
                <div className="w-16 h-16 bg-white rounded-lg flex items-center justify-center p-1 mb-2">
                  {team.logo_url ? (
                    <img
                      src={team.logo_url}
                      alt={`Logo ${team.name}`}
                      loading="lazy"
                      decoding="async"
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <ImageIcon className="w-8 h-8 text-gray-300" />
                  )}
                </div>
                <div className="text-white font-medium text-xs truncate w-full" title={team.name}>
                  {team.name}
                </div>
                <div className="text-gray-500 text-[10px] mb-2">
                  {team.league_slug || '—'}
                </div>
                <button
                  onClick={() => refreshLogo(team.id, team.name)}
                  disabled={refreshingId === team.id}
                  data-testid={`refresh-logo-${team.id}`}
                  className="w-full px-2 py-1 bg-gray-900 hover:bg-blue-700 disabled:opacity-50 text-white text-xs rounded flex items-center justify-center gap-1 transition-colors"
                >
                  {refreshingId === team.id ? (
                    <><Loader2 className="w-3 h-3 animate-spin" /></>
                  ) : (
                    <><RefreshCw className="w-3 h-3" /> Logo</>
                  )}
                </button>
              </div>
            ))}
            {filtered.length === 0 && (
              <div className="col-span-full text-center text-gray-500 py-12">
                Nessuna squadra trovata
              </div>
            )}
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminTeams;
