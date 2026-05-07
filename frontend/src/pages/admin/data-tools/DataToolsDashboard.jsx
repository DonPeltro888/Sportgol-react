import React from 'react';
import { Link } from 'react-router-dom';
import AdminLayout from '../../../components/admin/AdminLayout';
import { ShieldCheck, TrendingUp, Wrench } from 'lucide-react';

const DataToolsDashboard = () => {
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

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
        </div>

        <div className="mt-6 rounded-xl border border-gray-700 bg-gray-800/30 p-5">
          <h3 className="text-base font-bold text-white mb-2">🤖 Automazione attiva</h3>
          <ul className="text-xs text-gray-400 space-y-1 list-disc list-inside">
            <li><strong className="text-gray-300">Sync matchesio</strong>: ogni giorno alle 04:00 e 19:00 UTC</li>
            <li><strong className="text-gray-300">Normalize backstop</strong>: 04:30 e 19:30 UTC (cattura miss post-sync)</li>
            <li><strong className="text-gray-300">Daily snapshot</strong>: 02:00 UTC (popola trend storico)</li>
            <li><strong className="text-gray-300">Health autofix AI</strong>: 03:00 UTC (Perplexity + Gemini Vision per loghi/dati mancanti)</li>
          </ul>
        </div>
      </div>
    </AdminLayout>
  );
};

export default DataToolsDashboard;
