import React, { useEffect, useState } from 'react';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import { Link } from 'react-router-dom';
import { Loader2, ShieldCheck, ChevronLeft, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const TeamVerifier = () => {
  const { authFetch } = useAdminAuth();
  const [report, setReport] = useState(null);
  const [running, setRunning] = useState(false);
  const [limit, setLimit] = useState(50);
  const [onlyDrift, setOnlyDrift] = useState(false);

  const loadLatest = async () => {
    const r = await authFetch(`${API_URL}/api/data-tools/team-verifier/latest`);
    if (r.ok) setReport(await r.json());
  };

  useEffect(() => { loadLatest(); /* eslint-disable-next-line */ }, []);

  const run = async () => {
    if (!window.confirm(`Lancio verifica AI su ${limit} squadre?\nUsa Perplexity Sonar Pro (~$${(0.005 * limit).toFixed(2)}). Tempo: ~${Math.ceil(limit * 1.5 / 60)} min.`)) return;
    setRunning(true);
    try {
      const r = await authFetch(`${API_URL}/api/data-tools/team-verifier/run?limit=${limit}&only_with_drift=${onlyDrift}`, { method: 'POST' });
      const d = await r.json();
      if (r.ok && !d.error) {
        toast.success(`Verifica completata: ${d.total_checked} teams, ${d.teams_with_drift} drift`);
        setReport(d);
      } else toast.error(d.error || 'Errore');
    } catch (e) { toast.error('Errore di rete'); }
    finally { setRunning(false); }
  };

  const driftRows = (report?.results || []).filter(r => r.needs_review);

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-6xl mx-auto">
        <Link to="/admin/data-tools" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
          <ChevronLeft className="w-4 h-4" /> Torna a Data Tools
        </Link>
        <h1 className="text-2xl font-bold text-white inline-flex items-center gap-2">
          <ShieldCheck className="w-7 h-7 text-cyan-400" /> Team Verifier (AI weekly)
        </h1>
        <p className="text-sm text-gray-400 mt-1 mb-5">
          Perplexity Sonar Pro confronta DB teams con dati ufficiali aggiornati: stadium, city, country, logo URL.
        </p>

        <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6 flex flex-wrap items-end gap-4">
          <div>
            <label className="text-xs text-gray-400 mb-1 block">Limit (teams)</label>
            <input
              type="number"
              value={limit}
              onChange={e => setLimit(parseInt(e.target.value, 10) || 50)}
              min="1"
              max="300"
              className="w-32 px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm"
            />
          </div>
          <label className="text-xs text-gray-200 inline-flex items-center gap-2 mt-5">
            <input
              type="checkbox"
              checked={onlyDrift}
              onChange={e => setOnlyDrift(e.target.checked)}
              className="w-4 h-4"
            />
            Solo team con drift
          </label>
          <button
            onClick={run}
            disabled={running}
            data-testid="verifier-run-btn"
            className="ml-auto px-5 py-2.5 rounded-lg bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-semibold inline-flex items-center gap-2 disabled:opacity-50"
          >
            {running ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
            Lancia verifica
          </button>
        </div>

        {report && !report.error && (
          <>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
              <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-3">
                <div className="text-xs text-gray-400">Checked</div>
                <div className="text-2xl font-bold text-white">{report.total_checked}</div>
              </div>
              <div className="rounded-lg border border-amber-700/50 bg-amber-900/20 p-3">
                <div className="text-xs text-amber-300">Drift</div>
                <div className="text-2xl font-bold text-amber-300">{report.teams_with_drift}</div>
              </div>
              <div className="rounded-lg border border-pink-700/50 bg-pink-900/20 p-3">
                <div className="text-xs text-pink-300">Logo drift</div>
                <div className="text-2xl font-bold text-pink-300">{report.logo_drifts}</div>
              </div>
              <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-3">
                <div className="text-xs text-gray-400">Last run</div>
                <div className="text-sm text-gray-200 mt-1">{(report.ts || '').slice(0, 16).replace('T', ' ')}</div>
              </div>
            </div>

            {driftRows.length > 0 && (
              <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
                <h2 className="text-base font-bold text-white mb-3 inline-flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-400" /> {driftRows.length} squadre con drift
                </h2>
                <div className="space-y-3 max-h-[600px] overflow-y-auto">
                  {driftRows.map((r, i) => (
                    <div key={i} className="rounded border border-amber-700/50 bg-amber-900/10 p-3">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <span className="text-white font-semibold">{r.team_name}</span>
                          <span className="text-[11px] text-gray-400 ml-2">{r.league_slug}</span>
                        </div>
                        <span className="text-[10px] bg-amber-600 text-white px-2 py-0.5 rounded font-bold">
                          {r.drift_count} drift
                        </span>
                      </div>
                      <div className="space-y-1.5">
                        {r.drifts.map((d, j) => (
                          <div key={j} className="text-xs">
                            <span className="text-amber-300 font-mono">{d.field}:</span>
                            <span className="text-red-300 line-through ml-2">{d.db_value || '(vuoto)'}</span>
                            <span className="text-emerald-300 ml-2">→ {d.ai_value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        {report?.error && (
          <div className="rounded-xl border border-red-700/50 bg-red-900/20 p-5 text-sm text-red-300">
            {report.error}
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default TeamVerifier;
