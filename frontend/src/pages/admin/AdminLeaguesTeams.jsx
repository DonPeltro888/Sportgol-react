import React, { useState, useEffect } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { 
  Loader2, Plus, Trash2, Save, Edit2, ChevronDown, ChevronUp, 
  Trophy, Users, Search, Database, Check, X
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminLeaguesTeams = () => {
  const [leagues, setLeagues] = useState([]);
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('leagues');
  const [expandedLeague, setExpandedLeague] = useState(null);
  const [editingLeague, setEditingLeague] = useState(null);
  const [editingTeam, setEditingTeam] = useState(null);
  const [newLeague, setNewLeague] = useState({ name: '', slug: '', country: '', type: 'league' });
  const [newTeam, setNewTeam] = useState({ name: '', slug: '', league_slug: '', city: '', stadium: '' });
  const [showNewLeagueForm, setShowNewLeagueForm] = useState(false);
  const [showNewTeamForm, setShowNewTeamForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLeagueFilter, setSelectedLeagueFilter] = useState('');
  const [seeding, setSeeding] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [leaguesRes, teamsRes] = await Promise.all([
        fetch(`${API_URL}/api/admin/leagues`),
        fetch(`${API_URL}/api/admin/teams`)
      ]);
      
      const leaguesData = await leaguesRes.json();
      const teamsData = await teamsRes.json();
      
      setLeagues(leaguesData.leagues || []);
      setTeams(teamsData.teams || []);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Errore nel caricamento dati');
    } finally {
      setLoading(false);
    }
  };

  const handleSeedData = async () => {
    try {
      setSeeding(true);
      
      // Seed leagues first
      const leaguesRes = await fetch(`${API_URL}/api/admin/leagues/seed`, { method: 'POST' });
      const leaguesData = await leaguesRes.json();
      
      // Then seed teams
      const teamsRes = await fetch(`${API_URL}/api/admin/teams/seed`, { method: 'POST' });
      const teamsData = await teamsRes.json();
      
      toast.success(`Creati ${leaguesData.inserted} leghe e ${teamsData.inserted} squadre`);
      fetchData();
    } catch (error) {
      console.error('Error seeding:', error);
      toast.error('Errore nel seeding');
    } finally {
      setSeeding(false);
    }
  };

  // League functions
  const handleCreateLeague = async () => {
    if (!newLeague.name || !newLeague.slug) {
      toast.warning('Nome e slug sono obbligatori');
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/admin/leagues`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newLeague)
      });
      
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Error creating league');
      }
      
      toast.success('Lega creata');
      setNewLeague({ name: '', slug: '', country: '', type: 'league' });
      setShowNewLeagueForm(false);
      fetchData();
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleUpdateLeague = async (leagueId) => {
    try {
      const res = await fetch(`${API_URL}/api/admin/leagues/${leagueId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingLeague)
      });
      
      if (!res.ok) throw new Error('Error updating');
      
      toast.success('Lega aggiornata');
      setEditingLeague(null);
      fetchData();
    } catch (error) {
      toast.error('Errore aggiornamento');
    }
  };

  const handleDeleteLeague = async (leagueId) => {
    if (!window.confirm('Eliminare questa lega e tutte le squadre associate?')) return;
    
    try {
      await fetch(`${API_URL}/api/admin/leagues/${leagueId}`, { method: 'DELETE' });
      toast.success('Lega eliminata');
      fetchData();
    } catch (error) {
      toast.error('Errore eliminazione');
    }
  };

  // Team functions
  const handleCreateTeam = async () => {
    if (!newTeam.name || !newTeam.league_slug) {
      toast.warning('Nome e lega sono obbligatori');
      return;
    }
    
    const slug = newTeam.slug || newTeam.name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
    
    try {
      const res = await fetch(`${API_URL}/api/admin/teams`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newTeam, slug })
      });
      
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Error creating team');
      }
      
      toast.success('Squadra creata');
      setNewTeam({ name: '', slug: '', league_slug: '', city: '', stadium: '' });
      setShowNewTeamForm(false);
      fetchData();
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleUpdateTeam = async (teamId) => {
    try {
      const res = await fetch(`${API_URL}/api/admin/teams/${teamId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingTeam)
      });
      
      if (!res.ok) throw new Error('Error updating');
      
      toast.success('Squadra aggiornata');
      setEditingTeam(null);
      fetchData();
    } catch (error) {
      toast.error('Errore aggiornamento');
    }
  };

  const handleDeleteTeam = async (teamId) => {
    if (!window.confirm('Eliminare questa squadra?')) return;
    
    try {
      await fetch(`${API_URL}/api/admin/teams/${teamId}`, { method: 'DELETE' });
      toast.success('Squadra eliminata');
      fetchData();
    } catch (error) {
      toast.error('Errore eliminazione');
    }
  };

  // Filter teams
  const filteredTeams = teams.filter(team => {
    const matchesSearch = team.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLeague = !selectedLeagueFilter || team.league_slug === selectedLeagueFilter;
    return matchesSearch && matchesLeague;
  });

  // Get teams by league
  const getTeamsByLeague = (leagueSlug) => teams.filter(t => t.league_slug === leagueSlug);

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Leghe & Squadre</h1>
            <p className="text-gray-500 text-sm mt-1">
              Gestisci leghe, coppe e squadre del database
            </p>
          </div>
          
          {leagues.length === 0 && (
            <Button
              onClick={handleSeedData}
              disabled={seeding}
              className="gap-2 bg-green-600 hover:bg-green-700"
            >
              {seeding ? <Loader2 className="w-4 h-4 animate-spin" /> : <Database className="w-4 h-4" />}
              Popola Database
            </Button>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Trophy className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{leagues.filter(l => l.type === 'league').length}</div>
                <div className="text-sm text-gray-500">Campionati</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                <Trophy className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{leagues.filter(l => l.type === 'cup').length}</div>
                <div className="text-sm text-gray-500">Coppe</div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">{teams.length}</div>
                <div className="text-sm text-gray-500">Squadre</div>
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl border border-gray-200 p-1 flex gap-1">
          <button
            onClick={() => setActiveTab('leagues')}
            className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'leagues' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Trophy className="w-4 h-4 inline mr-2" />
            Leghe & Coppe ({leagues.length})
          </button>
          <button
            onClick={() => setActiveTab('teams')}
            className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'teams' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'
            }`}
          >
            <Users className="w-4 h-4 inline mr-2" />
            Squadre ({teams.length})
          </button>
        </div>

        {/* Leagues Tab */}
        {activeTab === 'leagues' && (
          <div className="space-y-4">
            {/* Add League Button */}
            <div className="flex justify-end">
              <Button
                onClick={() => setShowNewLeagueForm(!showNewLeagueForm)}
                className="gap-2"
              >
                <Plus className="w-4 h-4" />
                Nuova Lega
              </Button>
            </div>

            {/* New League Form */}
            {showNewLeagueForm && (
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <h3 className="font-semibold text-blue-900 mb-3">Nuova Lega/Coppa</h3>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                  <Input
                    placeholder="Nome (es. Serie A)"
                    value={newLeague.name}
                    onChange={(e) => setNewLeague({ ...newLeague, name: e.target.value, slug: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                  />
                  <Input
                    placeholder="Slug (es. serie-a)"
                    value={newLeague.slug}
                    onChange={(e) => setNewLeague({ ...newLeague, slug: e.target.value })}
                  />
                  <Input
                    placeholder="Paese"
                    value={newLeague.country}
                    onChange={(e) => setNewLeague({ ...newLeague, country: e.target.value })}
                  />
                  <select
                    value={newLeague.type}
                    onChange={(e) => setNewLeague({ ...newLeague, type: e.target.value })}
                    className="border border-gray-200 rounded-lg px-3 py-2"
                  >
                    <option value="league">Campionato</option>
                    <option value="cup">Coppa</option>
                  </select>
                  <Button onClick={handleCreateLeague} className="bg-green-600 hover:bg-green-700">
                    <Check className="w-4 h-4 mr-1" /> Crea
                  </Button>
                </div>
              </div>
            )}

            {/* Leagues List */}
            <div className="space-y-2">
              {leagues.map((league) => (
                <div key={league.id} className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                  <div 
                    className="p-4 flex items-center justify-between cursor-pointer hover:bg-gray-50"
                    onClick={() => setExpandedLeague(expandedLeague === league.id ? null : league.id)}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                        league.type === 'cup' ? 'bg-orange-100' : 'bg-blue-100'
                      }`}>
                        <Trophy className={`w-5 h-5 ${league.type === 'cup' ? 'text-orange-600' : 'text-blue-600'}`} />
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">{league.name}</div>
                        <div className="text-sm text-gray-500">
                          {league.country} • {league.team_count} squadre • /{league.slug}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        league.type === 'cup' ? 'bg-orange-100 text-orange-700' : 'bg-blue-100 text-blue-700'
                      }`}>
                        {league.type === 'cup' ? 'Coppa' : 'Campionato'}
                      </span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => { e.stopPropagation(); setEditingLeague(league); }}
                      >
                        <Edit2 className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => { e.stopPropagation(); handleDeleteLeague(league.id); }}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                      {expandedLeague === league.id ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                    </div>
                  </div>
                  
                  {/* Expanded: Show teams */}
                  {expandedLeague === league.id && (
                    <div className="border-t border-gray-200 p-4 bg-gray-50">
                      <div className="flex flex-wrap gap-2">
                        {getTeamsByLeague(league.slug).map((team) => (
                          <span key={team.id} className="px-3 py-1 bg-white border border-gray-200 rounded-full text-sm">
                            {team.name}
                          </span>
                        ))}
                        {getTeamsByLeague(league.slug).length === 0 && (
                          <span className="text-gray-500 text-sm">Nessuna squadra</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {leagues.length === 0 && (
                <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
                  <Trophy className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Nessuna lega. Clicca "Popola Database" per iniziare.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Teams Tab */}
        {activeTab === 'teams' && (
          <div className="space-y-4">
            {/* Filters & Add */}
            <div className="flex flex-col md:flex-row gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <Input
                  placeholder="Cerca squadra..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <select
                value={selectedLeagueFilter}
                onChange={(e) => setSelectedLeagueFilter(e.target.value)}
                className="border border-gray-200 rounded-lg px-3 py-2 min-w-[200px]"
              >
                <option value="">Tutte le leghe</option>
                {leagues.map((l) => (
                  <option key={l.id} value={l.slug}>{l.name}</option>
                ))}
              </select>
              <Button onClick={() => setShowNewTeamForm(!showNewTeamForm)} className="gap-2">
                <Plus className="w-4 h-4" />
                Nuova Squadra
              </Button>
            </div>

            {/* New Team Form */}
            {showNewTeamForm && (
              <div className="bg-green-50 border border-green-200 rounded-xl p-4">
                <h3 className="font-semibold text-green-900 mb-3">Nuova Squadra</h3>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                  <Input
                    placeholder="Nome squadra"
                    value={newTeam.name}
                    onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })}
                  />
                  <select
                    value={newTeam.league_slug}
                    onChange={(e) => setNewTeam({ ...newTeam, league_slug: e.target.value })}
                    className="border border-gray-200 rounded-lg px-3 py-2"
                  >
                    <option value="">Seleziona lega</option>
                    {leagues.filter(l => l.type === 'league').map((l) => (
                      <option key={l.id} value={l.slug}>{l.name}</option>
                    ))}
                  </select>
                  <Input
                    placeholder="Città"
                    value={newTeam.city}
                    onChange={(e) => setNewTeam({ ...newTeam, city: e.target.value })}
                  />
                  <Input
                    placeholder="Stadio"
                    value={newTeam.stadium}
                    onChange={(e) => setNewTeam({ ...newTeam, stadium: e.target.value })}
                  />
                  <Button onClick={handleCreateTeam} className="bg-green-600 hover:bg-green-700">
                    <Check className="w-4 h-4 mr-1" /> Crea
                  </Button>
                </div>
              </div>
            )}

            {/* Teams Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {filteredTeams.map((team) => (
                <div key={team.id} className="bg-white rounded-xl border border-gray-200 p-4">
                  {editingTeam?.id === team.id ? (
                    <div className="space-y-2">
                      <Input
                        value={editingTeam.name}
                        onChange={(e) => setEditingTeam({ ...editingTeam, name: e.target.value })}
                        placeholder="Nome"
                      />
                      <Input
                        value={editingTeam.city || ''}
                        onChange={(e) => setEditingTeam({ ...editingTeam, city: e.target.value })}
                        placeholder="Città"
                      />
                      <Input
                        value={editingTeam.stadium || ''}
                        onChange={(e) => setEditingTeam({ ...editingTeam, stadium: e.target.value })}
                        placeholder="Stadio"
                      />
                      <div className="flex gap-2">
                        <Button size="sm" onClick={() => handleUpdateTeam(team.id)} className="flex-1 bg-green-600">
                          <Check className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => setEditingTeam(null)}>
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="font-semibold text-gray-900">{team.name}</div>
                          <div className="text-sm text-gray-500">{team.league_slug}</div>
                          {team.city && <div className="text-xs text-gray-400">{team.city}</div>}
                        </div>
                        <div className="flex gap-1">
                          <a
                            href={`/admin/seo/targets/team/${team.slug}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            data-testid={`seo-ai-from-team-${team.slug}`}
                            className="px-2 py-1 rounded bg-gradient-to-r from-purple-600 to-blue-600 text-white text-[11px] font-semibold inline-flex items-center"
                            title="Apri SEO Admin"
                          >
                            ✨
                          </a>
                          <Button variant="ghost" size="sm" onClick={() => setEditingTeam(team)}>
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button 
                            variant="ghost" 
                            size="sm" 
                            onClick={() => handleDeleteTeam(team.id)}
                            className="text-red-500"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>

            {filteredTeams.length === 0 && (
              <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
                <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">Nessuna squadra trovata</p>
              </div>
            )}
          </div>
        )}

        {/* Edit League Modal */}
        {editingLeague && !editingLeague.id?.startsWith('new') && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 w-full max-w-md">
              <h3 className="text-lg font-bold mb-4 flex items-center justify-between">
                <span>Modifica Lega</span>
                {editingLeague.slug && (
                  <a
                    href={`/admin/seo/targets/league/${editingLeague.slug}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    data-testid="seo-ai-from-league-edit"
                    className="text-xs px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 text-white inline-flex items-center gap-1 font-semibold"
                  >
                    ✨ SEO AI
                  </a>
                )}
              </h3>
              <div className="space-y-3">
                <Input
                  placeholder="Nome"
                  value={editingLeague.name}
                  onChange={(e) => setEditingLeague({ ...editingLeague, name: e.target.value })}
                />
                <Input
                  placeholder="Slug"
                  value={editingLeague.slug}
                  onChange={(e) => setEditingLeague({ ...editingLeague, slug: e.target.value })}
                />
                <Input
                  placeholder="Paese"
                  value={editingLeague.country}
                  onChange={(e) => setEditingLeague({ ...editingLeague, country: e.target.value })}
                />
                <select
                  value={editingLeague.type}
                  onChange={(e) => setEditingLeague({ ...editingLeague, type: e.target.value })}
                  className="w-full border border-gray-200 rounded-lg px-3 py-2"
                >
                  <option value="league">Campionato</option>
                  <option value="cup">Coppa</option>
                </select>
              </div>
              <div className="flex gap-2 mt-4">
                <Button onClick={() => handleUpdateLeague(editingLeague.id)} className="flex-1 bg-green-600">
                  Salva
                </Button>
                <Button variant="outline" onClick={() => setEditingLeague(null)}>
                  Annulla
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminLeaguesTeams;
