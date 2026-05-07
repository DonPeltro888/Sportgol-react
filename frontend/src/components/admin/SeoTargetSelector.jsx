import React, { useEffect, useState, useCallback } from 'react';
import { Trophy, Users, Calendar } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

/**
 * Selettore a cascata Lega → Squadra → Evento.
 * Props:
 *  - value: { leagueSlug, teamSlug, eventSlug }
 *  - onChange(value)
 *  - authFetch: optional (per chiamate autenticate)
 *  - compact: boolean (riduce padding)
 *  - allowEmpty: bool (default true) → permette "Tutte le leghe"
 */
const SeoTargetSelector = ({ value = {}, onChange, authFetch, compact = false }) => {
  const [leagues, setLeagues] = useState([]);
  const [teams, setTeams] = useState([]);
  const [events, setEvents] = useState([]);
  const [loadingTeams, setLoadingTeams] = useState(false);
  const [loadingEvents, setLoadingEvents] = useState(false);

  const { leagueSlug = '', teamSlug = '', eventSlug = '' } = value;

  // Load leagues once
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API_URL}/api/leagues?active_only=false`);
        if (r.ok) {
          const d = await r.json();
          const list = (d.leagues || []).sort((a, b) => (a.name || '').localeCompare(b.name || ''));
          setLeagues(list);
        }
      } catch (e) { /* ignore */ }
    })();
  }, []);

  // Load teams when league changes
  const loadTeams = useCallback(async (slug) => {
    if (!slug) { setTeams([]); return; }
    setLoadingTeams(true);
    try {
      const r = await fetch(`${API_URL}/api/leagues/${slug}`);
      if (r.ok) {
        const d = await r.json();
        const list = (d.teams || []).sort((a, b) => (a.name || '').localeCompare(b.name || ''));
        setTeams(list);
      } else { setTeams([]); }
    } catch (e) { setTeams([]); }
    finally { setLoadingTeams(false); }
  }, []);

  // Load events when team changes
  const loadEvents = useCallback(async (tSlug) => {
    if (!tSlug) { setEvents([]); return; }
    setLoadingEvents(true);
    try {
      const r = await fetch(`${API_URL}/api/events/by-team-slug/${tSlug}?limit=100`);
      if (r.ok) {
        const d = await r.json();
        setEvents(d.events || []);
      } else { setEvents([]); }
    } catch (e) { setEvents([]); }
    finally { setLoadingEvents(false); }
  }, []);

  useEffect(() => { loadTeams(leagueSlug); }, [leagueSlug, loadTeams]);
  useEffect(() => { loadEvents(teamSlug); }, [teamSlug, loadEvents]);

  const onLeague = (e) => {
    onChange({ leagueSlug: e.target.value, teamSlug: '', eventSlug: '' });
  };
  const onTeam = (e) => {
    onChange({ leagueSlug, teamSlug: e.target.value, eventSlug: '' });
  };
  const onEvent = (e) => {
    onChange({ leagueSlug, teamSlug, eventSlug: e.target.value });
  };

  const padY = compact ? 'py-2' : 'py-2.5';

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
      {/* League */}
      <div>
        <label className="text-xs text-gray-400 mb-1 flex items-center gap-1.5">
          <Trophy className="w-3.5 h-3.5 text-amber-400" /> Lega
        </label>
        <select
          value={leagueSlug}
          onChange={onLeague}
          data-testid="target-selector-league"
          className={`w-full px-3 ${padY} bg-gray-900 border border-gray-700 rounded text-white text-sm focus:border-blue-500 focus:outline-none`}
        >
          <option value="">— Tutte le leghe —</option>
          {leagues.map(l => (
            <option key={l.slug} value={l.slug}>{l.name} ({l.country})</option>
          ))}
        </select>
      </div>

      {/* Team */}
      <div>
        <label className="text-xs text-gray-400 mb-1 flex items-center gap-1.5">
          <Users className="w-3.5 h-3.5 text-emerald-400" /> Squadra {loadingTeams && <span className="text-[10px] text-gray-500">(carico…)</span>}
        </label>
        <select
          value={teamSlug}
          onChange={onTeam}
          disabled={!leagueSlug || loadingTeams}
          data-testid="target-selector-team"
          className={`w-full px-3 ${padY} bg-gray-900 border border-gray-700 rounded text-white text-sm focus:border-blue-500 focus:outline-none disabled:opacity-40`}
        >
          <option value="">— Tutte le squadre —</option>
          {teams.map(t => (
            <option key={t.slug} value={t.slug}>{t.name}</option>
          ))}
        </select>
      </div>

      {/* Event */}
      <div>
        <label className="text-xs text-gray-400 mb-1 flex items-center gap-1.5">
          <Calendar className="w-3.5 h-3.5 text-blue-400" /> Evento {loadingEvents && <span className="text-[10px] text-gray-500">(carico…)</span>}
        </label>
        <select
          value={eventSlug}
          onChange={onEvent}
          disabled={!teamSlug || loadingEvents}
          data-testid="target-selector-event"
          className={`w-full px-3 ${padY} bg-gray-900 border border-gray-700 rounded text-white text-sm focus:border-blue-500 focus:outline-none disabled:opacity-40`}
        >
          <option value="">— Tutti gli eventi —</option>
          {events.map(ev => {
            const slug = ev.slug || ev.id || ev._id;
            const lbl = `${ev.home_team || '?'} vs ${ev.away_team || '?'}${ev.sort_date ? ` · ${ev.sort_date}` : ''}`;
            return <option key={slug} value={slug}>{lbl}</option>;
          })}
        </select>
      </div>
    </div>
  );
};

export default SeoTargetSelector;
