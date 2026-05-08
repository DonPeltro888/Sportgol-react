import React, { useEffect, useState } from 'react';
import AdminLayout from '../../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../../contexts/AdminAuthContext';
import { Link } from 'react-router-dom';
import { Loader2, Globe2, ChevronLeft } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const SEV_COLOR = { HIGH: 'bg-red-600 text-white', MEDIUM: 'bg-amber-600 text-white', LOW: 'bg-gray-600 text-gray-200' };

const Hreflang = () => {
  const { authFetch } = useAdminAuth();
  const [data, setData] = useState(null);
  const [type, setType] = useState('all');
  const [loading, setLoading] = useState(true);

  const load = async (t = type) => {
    setLoading(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/intelligence/hreflang/scan?entity_type=${t}&limit=300`);
      if (r.ok) setData(await r.json());
    } finally { setLoading(false); }
  };

  useEffect(() => { load(); /* eslint-disable-next-line */ }, []);

  return (
    <AdminLayout>
      <div className="p-6 lg:p-8 max-w-6xl mx-auto">
        <Link to="/admin/seo/intelligence" className="text-sm text-gray-400 hover:text-white inline-flex items-center gap-1 mb-3">
          <ChevronLeft className="w-4 h-4" /> Torna a Intelligence Hub
        </Link>
        <h1 className="text-2xl font-bold text-white inline-flex items-center gap-2">
          <Globe2 className="w-7 h-7 text-purple-400" /> Hreflang Validator
        </h1>
        <p className="text-sm text-gray-400 mt-1 mb-5">
          Valida lingue obbligatorie (it/en/es), x-default, URL pattern, codici ISO 639-1.
        </p>

        <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6 flex flex-wrap items-end gap-3">
          <div>
            <label className="text-xs text-gray-400 mb-1 block">Tipo entità</label>
            <select
              value={type}
              onChange={e => { setType(e.target.value); load(e.target.value); }}
              className="px-3 py-2 bg-gray-900 border border-gray-700 rounded text-white text-sm"
            >
              <option value="all">Tutti</option>
              <option value="event">Eventi</option>
              <option value="team">Squadre</option>
              <option value="league">Leghe</option>
            </select>
          </div>
          <button onClick={() => load()} className="px-4 py-2 rounded-lg bg-purple-600 hover:bg-purple-700 text-white text-sm font-semibold inline-flex items-center gap-2">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Globe2 className="w-4 h-4" />}
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
                  <div className="flex items-center justify-between flex-wrap gap-2">
                    <div className="flex-1">
                      <span className="text-[10px] text-blue-300 mr-2">{r.type}</span>
                      <span className="text-white font-mono text-sm">{r.slug}</span>
                      <span className="text-[10px] text-gray-500 ml-2">[{r.seo_status}]</span>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-gray-700 text-gray-200">
                      {r.issue_count} issues
                    </span>
                  </div>
                  <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2">
                    {r.issues.slice(0, 4).map((iss, j) => (
                      <div key={j} className="text-xs flex items-start gap-2 p-2 bg-gray-950/50 rounded">
                        <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold ${SEV_COLOR[iss.severity]}`}>
                          {iss.severity}
                        </span>
                        <div>
                          <div className="text-gray-200">{iss.message}</div>
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
      </div>
    </AdminLayout>
  );
};

export default Hreflang;
