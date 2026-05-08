import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import AdminLayout from '../../../components/admin/AdminLayout';
import { ShieldCheck, TrendingUp, Wrench, Database, Trash2, ListChecks, Loader2 } from 'lucide-react';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const DataToolsDashboard = () => {
  const { authFetch } = useAdminAuth();
  const [running, setRunning] = useState(null); // 'dedup' | 'validate' | null

  const runDedup = async () => {
    if (!window.confirm('Eseguo la deduplicazione su events/teams/leagues?\nVerrà creato un backup automatico. Tempo: ~30s.')) return;
    setRunning('dedup');
    try {
      const r = await authFetch(`${API_URL}/api/data-tools/maintenance/dedup`, { method: 'POST' });
      const d = await r.json();
      if (r.ok) {
        toast.success(`Dedup OK: events=${d.events?.duplicates ?? 0}, teams=${d.teams?.duplicates ?? 0}, leagues=${d.leagues?.duplicates ?? 0}`);
      } else toast.error('Errore dedup');
    } catch (e) { toast.error('Errore di rete'); }
    finally { setRunning(null); }
  };

  const runValidateLeagues = async () => {
    if (!window.confirm('Valido tutte le leghe contro OpenFootball + Perplexity?\nLe squadre obsolete (es. Venezia in Serie A 2024/25) saranno archiviate.')) return;
    setRunning('validate');
    try {
      const r = await authFetch(`${API_URL}/api/data-tools/maintenance/validate-leagues`, { method: 'POST' });
      const d = await r.json();
      if (r.ok) {
        const total_orphans = (d.results || []).reduce((s, x) => s + (x.orphans?.length || 0), 0);
        toast.success(`Validazione OK: ${total_orphans} squadre archiviate su ${(d.results || []).length} leghe`);
      } else toast.error('Errore validazione');
    } catch (e) { toast.error('Errore di rete'); }
    finally { setRunning(null); }
  };

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white inline-flex items-center gap-2">
            <Wrench className="w-7 h-7 text-orange-400" /> Data Tools
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Strumenti specifici per la qualità del database GoLevents: diagnosi, auto-fix con AI, monitoring real-time.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Link to="/admin/data-tools/health" data-testid="dt-quick-health" className="group rounded-xl border border-gray-700 bg-gray-800/40 p-6 hover:border-emerald-500 hover:bg-gray-800/70 transition-all">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 rounded-lg bg-emerald-600/20 flex items-center justify-center">
                <ShieldCheck className="w-6 h-6 text-emerald-400" />
              </div>
              <h3 className="text-lg text-white font-semibold">Data Health Check</h3>
            </div>
            <p className="text-sm text-gray-400">
              Diagnosi & auto-fix con AI (Perplexity + Gemini Vision): rileva loghi sbagliati, dati mancanti
              (stadium/city/country), name confusion (Inter ⊂ Inter Miami) e duplicati.
              Bulk fix per categoria.
            </p>
          </Link>

          <Link to="/admin/data-tools/sync-quality" data-testid="dt-quick-sync-quality" className="group rounded-xl border border-gray-700 bg-gray-800/40 p-6 hover:border-cyan-500 hover:bg-gray-800/70 transition-all">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 rounded-lg bg-cyan-600/20 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-cyan-400" />
              </div>
              <h3 className="text-lg text-white font-semibold">Sync Quality</h3>
            </div>
            <p className="text-sm text-gray-400">
              Metriche real-time del DB: events/teams/leagues totali, normalize 24h/7g, AI fixes,
              logo coverage %, top team con dati mancanti, trend storico (snapshot giornalieri).
            </p>
          </Link>

          <Link to="/admin/data-tools/data-recovery" data-testid="dt-quick-data-recovery" className="group rounded-xl border border-gray-700 bg-gray-800/40 p-6 hover:border-blue-500 hover:bg-gray-800/70 transition-all">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-12 h-12 rounded-lg bg-blue-600/20 flex items-center justify-center">
                <Database className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-lg text-white font-semibold">Data Recovery</h3>
            </div>
            <p className="text-sm text-gray-400">
              Multi-source aggregator: <strong className="text-blue-300">ESPN</strong> (primary, no auth),
              OpenFootball, TheSportsDB + AI Gap Detector via Perplexity. Resync on-demand per lega.
            </p>
          </Link>
        </div>

        {/* Maintenance: dedup + validate-leagues — DB hygiene golevents-specific (NON SEO) */}
        <div className="mt-6 rounded-xl border border-amber-700/40 bg-gradient-to-br from-amber-900/15 to-orange-900/10 p-5">
          <h3 className="text-base font-bold text-white mb-2 inline-flex items-center gap-2">
            <Wrench className="w-5 h-5 text-amber-400" /> Manutenzione DB
          </h3>
          <p className="text-xs text-amber-200/90 mb-4">
            Operazioni di hygiene da lanciare dopo un sync MIX multi-fonte: rimuove duplicati cross-provider
            (es. "AC Milan" vs "Milan", "Atalanta" vs "Atalanta Bc") e archivia squadre obsolete dalle leghe.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <button
              onClick={runDedup}
              disabled={running !== null}
              data-testid="dt-dedup-btn"
              className="flex items-center justify-between gap-3 px-4 py-3 rounded-lg bg-amber-600/20 hover:bg-amber-600/30 border border-amber-700/50 text-left transition-colors disabled:opacity-50"
            >
              <div className="flex items-center gap-3">
                <Trash2 className="w-5 h-5 text-amber-400" />
                <div>
                  <div className="text-white font-semibold text-sm">Esegui Dedup ora</div>
                  <div className="text-amber-200/70 text-[11px] mt-0.5">events + teams + leagues, backup auto</div>
                </div>
              </div>
              {running === 'dedup' && <Loader2 className="w-5 h-5 animate-spin text-amber-400" />}
            </button>

            <button
              onClick={runValidateLeagues}
              disabled={running !== null}
              data-testid="dt-validate-leagues-btn"
              className="flex items-center justify-between gap-3 px-4 py-3 rounded-lg bg-purple-600/20 hover:bg-purple-600/30 border border-purple-700/50 text-left transition-colors disabled:opacity-50"
            >
              <div className="flex items-center gap-3">
                <ListChecks className="w-5 h-5 text-purple-400" />
                <div>
                  <div className="text-white font-semibold text-sm">Valida Composizione Leghe</div>
                  <div className="text-purple-200/70 text-[11px] mt-0.5">vs OpenFootball + Perplexity, archivia obsoleti</div>
                </div>
              </div>
              {running === 'validate' && <Loader2 className="w-5 h-5 animate-spin text-purple-400" />}
            </button>
          </div>
        </div>

        <div className="mt-6 rounded-xl border border-gray-700 bg-gray-800/30 p-5">
          <h3 className="text-base font-bold text-white mb-2">🤖 Automazione attiva</h3>
          <ul className="text-xs text-gray-400 space-y-1 list-disc list-inside">
            <li><strong className="text-blue-300">ESPN multi-source sync</strong>: 04:00 e 19:00 UTC (PRIMARY, no auth)</li>
            <li><strong className="text-purple-300">OpenFootball + TheSportsDB</strong>: stesso slot (fallback ridondanti)</li>
            <li><strong className="text-emerald-300">AI Gap Detector (Perplexity)</strong>: in coda al sync (recupera match mancanti residui)</li>
            <li><strong className="text-gray-300">Normalize backstop</strong>: 04:30 e 19:30 UTC</li>
            <li><strong className="text-gray-300">Daily snapshot</strong>: 02:00 UTC (trend storico)</li>
            <li><strong className="text-gray-300">Health autofix AI</strong>: 03:00 UTC (Perplexity + Gemini Vision per loghi/dati mancanti)</li>
            <li><strong className="text-cyan-300">Team Verifier weekly</strong>: lunedì 05:00 UTC (Perplexity verifica team metadata + loghi)</li>
          </ul>
        </div>
      </div>
    </AdminLayout>
  );
};

export default DataToolsDashboard;
