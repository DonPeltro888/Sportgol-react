import React, { useEffect, useState } from 'react';
import AdminLayout from '../../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../../contexts/AdminAuthContext';
import { Link } from 'react-router-dom';
import { Loader2, FileCode2, ChevronLeft } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const SEV_COLOR = { HIGH: 'bg-red-600 text-white', MEDIUM: 'bg-amber-600 text-white', LOW: 'bg-gray-600 text-gray-200' };

const JsonLdValidator = () => {
  const { authFetch } = useAdminAuth();
  const [data, setData] = useState(null);
  const [type, setType] = useState('all');
  const [lang, setLang] = useState('it');
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/intelligence/jsonld/scan?entity_type=${type}&lang=${lang}&limit=200`);
      if (r.ok) setData(await r.json());
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, [type, lang]);

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-6xl mx-auto">
        <Link to="/admin/seo/intelligence" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
          <ChevronLeft className="w-4 h-4" /> Torna a Intelligence Hub
        </Link>
        <h1 className="text-2xl font-bold text-white inline-flex items-center gap-2">
          <FileCode2 className="w-7 h-7 text-pink-400" /> JSON-LD Schema.org Validator
        </h1>
        <p className="text-sm text-gray-400 mt-1 mb-5">
          Valida required props (Event, SportsTeam, FAQPage, BreadcrumbList), date ISO 8601, URL, sameAs.
        </p>

        <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6 flex flex-wrap items-end gap-3">
          <div>
            <label className="text-xs text-gray-400 mb-1 block">Tipo</label>
            <select value={type} onChange={e => setType(e.target.value)} className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm">
              <option value="all">Tutti</option>
              <option value="event">Eventi</option>
              <option value="team">Squadre</option>
              <option value="league">Leghe</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-400 mb-1 block">Lingua</label>
            <select value={lang} onChange={e => setLang(e.target.value)} className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm">
              <option value="it">Italiano</option>
              <option value="en">English</option>
              <option value="es">Español</option>
            </select>
          </div>
          <button onClick={load} className="ml-auto px-4 py-2 rounded-lg bg-pink-600 hover:bg-pink-700 text-white text-sm font-semibold inline-flex items-center gap-2">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileCode2 className="w-4 h-4" />}
            Refresh
          </button>
        </div>

        {data && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-3">
              <div className="text-xs text-gray-400">Invalid</div>
              <div className="text-2xl font-bold text-white">{data.total_invalid}</div>
            </div>
            <div className="rounded-lg border border-red-700/50 bg-red-900/20 p-3">
              <div className="text-xs text-red-300">HIGH</div>
              <div className="text-2xl font-bold text-red-300">{data.by_severity?.HIGH || 0}</div>
            </div>
            <div className="rounded-lg border border-amber-700/50 bg-amber-900/20 p-3">
              <div className="text-xs text-amber-300">MEDIUM</div>
              <div className="text-2xl font-bold text-amber-300">{data.by_severity?.MEDIUM || 0}</div>
            </div>
            <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-3">
              <div className="text-xs text-gray-400">LOW</div>
              <div className="text-2xl font-bold text-gray-300">{data.by_severity?.LOW || 0}</div>
            </div>
          </div>
        )}

        {data?.rows?.length > 0 && (
          <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
            <h2 className="text-base font-bold text-white mb-3">Entità con problemi</h2>
            <div className="space-y-3 max-h-[600px] overflow-y-auto">
              {data.rows.map((r, idx) => (
                <div key={idx} className="rounded border border-gray-700 bg-gray-900/40 p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className="text-[10px] text-blue-300 mr-2">{r.type}</span>
                      <span className="text-white text-sm">{r.title}</span>
                      <span className="text-[10px] font-mono text-gray-500 ml-2">{r.slug}</span>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-gray-700 text-gray-200">
                      {r.issue_count} issues
                    </span>
                  </div>
                  <div className="space-y-1">
                    {r.top_issues.map((iss, j) => (
                      <div key={j} className="text-xs flex items-start gap-2 p-2 bg-gray-950/50 rounded">
                        <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${SEV_COLOR[iss.severity]}`}>
                          {iss.severity}
                        </span>
                        <div className="flex-1">
                          <div className="text-gray-200">{iss.message}</div>
                          {iss.path && <div className="text-[10px] font-mono text-gray-500">{iss.path}</div>}
                          {iss.fix && <div className="text-emerald-300/80 text-[10px] mt-0.5">→ {iss.fix}</div>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {data && data.total_invalid === 0 && (
          <div className="rounded-xl border border-emerald-700/50 bg-emerald-900/20 p-8 text-center">
            <FileCode2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
            <h3 className="text-lg font-bold text-emerald-200">Tutti i JSON-LD packets sono validi! 🎉</h3>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default JsonLdValidator;
