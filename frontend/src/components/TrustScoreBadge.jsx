import React, { useEffect, useState } from 'react';
import { ShieldCheck } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const COLOR_MAP = {
  green: 'bg-emerald-100 text-emerald-700 border-emerald-300',
  blue: 'bg-blue-100 text-blue-700 border-blue-300',
  amber: 'bg-amber-100 text-amber-700 border-amber-300',
  gray: 'bg-gray-100 text-gray-600 border-gray-300',
};

/**
 * Mostra un badge "Verified by N sources" sulle pagine pubbliche di event/team/league.
 * Calcolato server-side via /api/seo/intelligence/trust-score/{type}/{slug}.
 */
const TrustScoreBadge = ({ entityType, slug, compact = false }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!slug) return;
    (async () => {
      try {
        const r = await fetch(`${API_URL}/api/seo/intelligence/trust-score/${entityType}/${slug}`);
        if (r.ok) setData(await r.json());
      } catch (e) { /* ignore */ }
    })();
  }, [entityType, slug]);

  if (!data || data.source_count === 0) return null;
  const cls = COLOR_MAP[data.color] || COLOR_MAP.gray;

  if (compact) {
    return (
      <span
        className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded border ${cls}`}
        title={`Trust score ${data.trust_score}/100 — ${data.sources.join(', ')}`}
        data-testid="trust-score-badge"
      >
        <ShieldCheck className="w-3 h-3" /> {data.source_count}
      </span>
    );
  }

  return (
    <div
      className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full border ${cls}`}
      title={`Sources: ${data.sources.join(', ')}`}
      data-testid="trust-score-badge"
    >
      <ShieldCheck className="w-3.5 h-3.5" />
      {data.badge}
      <span className="opacity-70 ml-1">({data.trust_score}/100)</span>
    </div>
  );
};

export default TrustScoreBadge;
