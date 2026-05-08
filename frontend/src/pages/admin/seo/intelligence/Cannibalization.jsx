import React, { useEffect, useState } from 'react';
import AdminLayout from '../../../../components/admin/AdminLayout';
import { useAdminAuth } from '../../../../contexts/AdminAuthContext';
import { Link } from 'react-router-dom';
import { Loader2, Copy, ChevronLeft, AlertTriangle } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const SEV_COLOR = { HIGH: 'bg-red-600 text-white', MEDIUM: 'bg-amber-600 text-white', LOW: 'bg-gray-600 text-gray-200' };

const Cannibalization = () => {
  const { authFetch } = useAdminAuth();
  const [data, setData] = useState(null);
  const [threshold, setThreshold] = useState(85);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try {
      const r = await authFetch(`${API_URL}/api/seo/intelligence/cannibalization/scan?threshold=${threshold}&limit=200`);
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
          <Copy className="w-7 h-7 text-orange-400" /> Cannibalization Detector
        </h1>
        <p className="text-sm text-gray-400 mt-1 mb-5">
          Entità che competono per la stessa keyword primaria (rapidfuzz token_set_ratio).
        </p>

        <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5 mb-6 flex flex-wrap items-end gap-3">
          <div className="flex-1 min-w-[180px]">
            <label className="text-xs text-gray-400 mb-1 block">Threshold similarità (%)</label>
            <input
              type="range"
              min="70"
              max="100"
              value={threshold}
              onChange={e => setThreshold(parseInt(e.target.value, 10))}
              className="w-full"
            />
            <div className="text-sm text-white mt-1 font-mono">{threshold}%</div>
          </div>
          <button
            onClick={load}
            data-testid="cannibal-scan-btn"
            disabled={loading}
            className="px-5 py-2.5 rounded-lg bg-orange-600 hover:bg-orange-700 text-white text-sm font-semibold inline-flex items-center gap-2 disabled:opacity-50"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Copy className="w-4 h-4" />}
            Scan
          </button>
        </div>

        {data && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-3">
              <div className="text-xs text-gray-400">Scanned</div>
              <div className="text-2xl font-bold text-white">{data.total_entities_scanned}</div>
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

        {data?.issues?.length > 0 && (
          <div className="rounded-xl border border-gray-700 bg-gray-800/40 p-5">
            <h2 className="text-base font-bold text-white mb-3 inline-flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" /> {data.issues.length} issues
            </h2>
            <div className="overflow-x-auto max-h-[600px]">
              <table className="w-full text-sm">
                <thead className="bg-gray-900/40 text-gray-400 text-xs uppercase">
                  <tr>
                    <th className="text-left px-3 py-2">Sev</th>
                    <th className="text-left px-3 py-2">Sim</th>
                    <th className="text-left px-3 py-2">Entità A</th>
                    <th className="text-left px-3 py-2">Entità B</th>
                    <th className="text-left px-3 py-2">Raccomandazione</th>
                  </tr>
                </thead>
                <tbody>
                  {data.issues.map((i, idx) => (
                    <tr key={idx} className="border-t border-gray-700/50 hover:bg-gray-900/30">
                      <td className="px-3 py-2">
                        <span className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${SEV_COLOR[i.severity]}`}>
                          {i.severity}
                        </span>
                      </td>
                      <td className="px-3 py-2 text-amber-300 font-mono text-xs">{i.similarity}%</td>
                      <td className="px-3 py-2 text-white">
                        <span className="text-[10px] text-blue-300 mr-1">{i.entity_a.type}</span>
                        {i.entity_a.title}
                        <span className="text-[10px] text-gray-500 ml-1">[{i.entity_a.status}]</span>
                      </td>
                      <td className="px-3 py-2 text-white">
                        <span className="text-[10px] text-blue-300 mr-1">{i.entity_b.type}</span>
                        {i.entity_b.title}
                        <span className="text-[10px] text-gray-500 ml-1">[{i.entity_b.status}]</span>
                      </td>
                      <td className="px-3 py-2 text-gray-400 text-xs">{i.recommendation}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
};

export default Cannibalization;
