import React, { useEffect, useState } from 'react';
import AdminLayout from '../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../contexts/AdminAuthContext';
import { Link } from 'react-router-dom';
import {
  Sparkles, FileText, Settings2, BarChart3, ShieldCheck, History, Download,
  KeyRound, Wand2, Bot, Languages, Search, Image as ImageIcon, AlertCircle, Loader2
} from 'lucide-react';
import { toast } from 'sonner';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const StatCard = ({ icon: Icon, label, value, hint, accent = 'blue' }) => {
  const colors = {
    blue: 'from-blue-500/20 to-blue-700/10 border-blue-700/40 text-blue-300',
    green: 'from-emerald-500/20 to-emerald-700/10 border-emerald-700/40 text-emerald-300',
    amber: 'from-amber-500/20 to-amber-700/10 border-amber-700/40 text-amber-300',
    purple: 'from-purple-500/20 to-purple-700/10 border-purple-700/40 text-purple-300',
  };
  return (
    <div className={`rounded-xl border bg-gradient-to-br ${colors[accent]} p-5`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs uppercase tracking-wide opacity-70 font-semibold">{label}</p>
          <p className="mt-2 text-3xl font-bold text-white">{value}</p>
          {hint && <p className="mt-1 text-xs text-gray-400">{hint}</p>}
        </div>
        <Icon className="w-6 h-6 opacity-70" />
      </div>
    </div>
  );
};

const SeoDashboard = () => {
  const { authFetch } = useAdminAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/dashboard/stats`);
      if (r.ok) setStats(await r.json());
    } catch (e) {
      toast.error('Errore caricamento stats');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-8">
          <div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl lg:text-3xl font-bold text-white" data-testid="seo-dashboard-title">
                SEO Automation Admin
              </h1>
            </div>
            <p className="mt-2 text-sm text-gray-400">
              Pipeline Dual-Engine: Claude (copy) + Gemini (schema/struct) + DataForSEO + Perplexity + DeepL.
            </p>
          </div>
          <Link
            to="/admin/seo/api-tools"
            data-testid="seo-cta-api-tools"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold transition-colors"
          >
            <KeyRound className="w-4 h-4" />
            Configura API & Tools
          </Link>
        </div>

        {/* Maintenance: dedup runner */}
        <div className="rounded-xl border border-amber-700/40 bg-amber-900/10 p-4 mb-6 flex flex-col sm:flex-row sm:items-center gap-3">
          <div className="flex-1 text-xs text-amber-200">
            <strong>Manutenzione DB:</strong> rilancia la deduplicazione dopo un MIX sync per rimuovere automaticamente i duplicati provenienti da provider diversi (es. "AC Milan" vs "Milan", "Atalanta" vs "Atalanta Bc").
          </div>
          <button
            onClick={async () => {
              if (!window.confirm('Eseguo la deduplicazione su events/teams/leagues? Verrà creato un backup automatico.')) return;
              try {
                const token = localStorage.getItem('admin_token');
                const r = await fetch(`${API_URL}/api/seo/maintenance/dedup`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
                const d = await r.json();
                if (r.ok) {
                  toast.success(`Dedup OK: events=${d.events?.duplicates}, teams=${d.teams?.duplicates}, leagues=${d.leagues?.duplicates}`);
                  load();
                } else toast.error('Errore dedup');
              } catch (e) { toast.error('Errore di rete'); }
            }}
            data-testid="seo-dedup-btn"
            className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-700 text-white text-xs font-semibold whitespace-nowrap"
          >
            Esegui Dedup ora
          </button>
          <button
            onClick={async () => {
              if (!window.confirm('Valido tutte le leghe contro OpenFootball + Perplexity? Le squadre obsolete (es. Venezia in Serie A 2024/25) saranno archiviate.')) return;
              try {
                const token = localStorage.getItem('admin_token');
                const r = await fetch(`${API_URL}/api/seo/maintenance/validate-leagues`, { method: 'POST', headers: { Authorization: `Bearer ${token}` } });
                const d = await r.json();
                if (r.ok) {
                  const total_orphans = (d.results || []).reduce((s, x) => s + (x.orphans?.length || 0), 0);
                  toast.success(`Validazione OK: ${total_orphans} squadre archiviate`);
                  load();
                } else toast.error('Errore validazione');
              } catch (e) { toast.error('Errore di rete'); }
            }}
            data-testid="seo-validate-leagues-btn"
            className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 text-white text-xs font-semibold whitespace-nowrap"
          >
            Valida Composizione Leghe
          </button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <StatCard
            icon={FileText}
            label="Entity totali"
            value={loading ? '…' : (stats?.total_pages?.toLocaleString() ?? 0)}
            hint={loading ? '' : `${stats?.by_type?.event?.total ?? 0} match · ${stats?.by_type?.league?.total ?? 0} leghe · ${stats?.by_type?.team?.total ?? 0} squadre`}
            accent="blue"
          />
          <StatCard
            icon={Wand2}
            label="In Draft"
            value={loading ? '…' : (stats?.by_status?.Draft ?? 0).toLocaleString()}
            hint="Mai generate"
            accent="amber"
          />
          <StatCard
            icon={ShieldCheck}
            label="Published"
            value={loading ? '…' : (stats?.by_status?.Published ?? 0).toLocaleString()}
            hint="SEO live"
            accent="green"
          />
          <StatCard
            icon={KeyRound}
            label="Tool attivi"
            value={loading ? '…' : `${stats?.tools_active ?? 0}/${stats?.tools_total ?? 0}`}
            hint={`${stats?.tools_with_key ?? 0} con chiave`}
            accent="purple"
          />
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
          <Link to="/admin/seo/pages/new" data-testid="seo-quick-create" className="group rounded-xl border border-gray-700 bg-gray-800/40 p-5 hover:border-blue-500 hover:bg-gray-800/70 transition-all">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-blue-600/20 flex items-center justify-center">
                <Bot className="w-5 h-5 text-blue-400" />
              </div>
              <h3 className="text-white font-semibold">Sfoglia Match (1188)</h3>
            </div>
            <p className="text-xs text-gray-400">Genera SEO sui match esistenti — events DB</p>
          </Link>

          <Link to="/admin/seo/pages" data-testid="seo-quick-pages" className="group rounded-xl border border-gray-700 bg-gray-800/40 p-5 hover:border-purple-500 hover:bg-gray-800/70 transition-all">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-purple-600/20 flex items-center justify-center">
                <FileText className="w-5 h-5 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold">Tutte le pagine SEO</h3>
            </div>
            <p className="text-xs text-gray-400">Lista, filtri, status, audit score</p>
          </Link>

          <Link to="/admin/seo/api-tools" data-testid="seo-quick-tools" className="group rounded-xl border border-gray-700 bg-gray-800/40 p-5 hover:border-emerald-500 hover:bg-gray-800/70 transition-all">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-emerald-600/20 flex items-center justify-center">
                <Settings2 className="w-5 h-5 text-emerald-400" />
              </div>
              <h3 className="text-white font-semibold">API & Tools</h3>
            </div>
            <p className="text-xs text-gray-400">Configura Claude, Gemini, DataForSEO, Perplexity, DeepL</p>
          </Link>
        </div>

        {/* Pipeline Map */}
        <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-6">
          <h2 className="text-white font-semibold flex items-center gap-2 mb-4">
            <BarChart3 className="w-4 h-4" />
            Pipeline Dual-Engine
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 text-xs">
            <PipelineStep icon={Search} label="1. Research" tools="DataForSEO + Perplexity" />
            <PipelineStep icon={ImageIcon} label="2. Visual" tools="Nano Banana (hero)" />
            <PipelineStep icon={Bot} label="3. Copy IT" tools="Claude 4.5 (master)" />
            <PipelineStep icon={Wand2} label="4. Schema" tools="Gemini 3 Pro (JSON-LD)" />
            <PipelineStep icon={Languages} label="5. Translate" tools="DeepL (EN+ES)" />
            <PipelineStep icon={ShieldCheck} label="6. Audit" tools="SEO score 0-100" />
          </div>
        </div>

        {/* Placeholder roadmap */}
        <div className="mt-6 rounded-xl border border-amber-700/40 bg-amber-900/10 p-4 text-xs text-amber-300 flex items-start gap-3">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <div>
            <strong>Stato P0 (Foundation):</strong> Backend + API Tools Settings + Dashboard ✅. <br />
            <strong>Prossimo:</strong> Pipeline asincrona, Editor multi-tab con field locking, SEO audit, Export JSON/HTML, Auto-publish su <code className="bg-amber-900/30 px-1 rounded">events.seo_meta</code>.
          </div>
        </div>
      </div>
    </AdminLayout>
  );
};

const PipelineStep = ({ icon: Icon, label, tools }) => (
  <div className="rounded-lg bg-gray-900/60 border border-gray-700 p-3 text-center">
    <Icon className="w-5 h-5 text-blue-400 mx-auto mb-1" />
    <p className="text-white font-semibold">{label}</p>
    <p className="text-gray-500 text-[10px] mt-1">{tools}</p>
  </div>
);

export default SeoDashboard;
