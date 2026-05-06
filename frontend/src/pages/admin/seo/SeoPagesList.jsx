import React from 'react';
import AdminLayout from '../../../components/admin/AdminLayout';
import { Link } from 'react-router-dom';
import { FileText, ArrowLeft, AlertCircle } from 'lucide-react';

const SeoPagesList = () => (
  <AdminLayout>
    <div className="p-6 lg:p-8 max-w-7xl mx-auto">
      <Link to="/admin/seo" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
        <ArrowLeft className="w-4 h-4" /> Torna a SEO Dashboard
      </Link>
      <h1 className="text-2xl font-bold text-white flex items-center gap-2" data-testid="seo-pages-title">
        <FileText className="w-6 h-6 text-purple-400" /> Pagine SEO
      </h1>
      <p className="mt-2 text-sm text-gray-400 mb-6">Lista di tutte le pagine SEO con stato, score, filtri.</p>

      <div className="rounded-xl border border-amber-700/40 bg-amber-900/10 p-6 text-amber-200">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <strong>Fase 2 in arrivo:</strong> creazione pagina match, pipeline asincrona Dual-Engine
            (Claude + Gemini + DataForSEO + Perplexity + DeepL), editor multi-tab con field locking,
            audit SEO score 0-100, export JSON/HTML/schema, auto-publish su <code className="bg-amber-900/40 px-1 rounded">events.seo_meta</code>.
            <p className="mt-2 text-xs text-amber-300/70">
              Foundation P0 completata: 4 API testate live (DataForSEO, Perplexity, Claude 4.5, Gemini 3 Pro).
            </p>
          </div>
        </div>
      </div>
    </div>
  </AdminLayout>
);

export default SeoPagesList;
