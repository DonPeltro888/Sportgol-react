import React, { useMemo } from 'react';
import { Flame, Users, Eye } from 'lucide-react';

/**
 * Urgency badge per evento. Mostra info pseudo-realistiche basate su event ID
 * per dare senso di scarsità (Viagogo-style).
 */
const UrgencyBadges = ({ eventId, availableTickets = 15000, featured = false }) => {
  // Hash deterministico basato su eventId per coerenza tra refresh
  const hashCode = useMemo(() => {
    if (!eventId) return 42;
    let h = 0;
    for (let i = 0; i < eventId.length; i++) {
      h = ((h << 5) - h) + eventId.charCodeAt(i);
      h |= 0;
    }
    return Math.abs(h);
  }, [eventId]);

  const viewers = 8 + (hashCode % 35);             // 8-42 visitatori live
  const tixLeft = featured
    ? 3 + (hashCode % 12)                          // 3-14 biglietti per top match
    : 8 + (hashCode % 35);                         // 8-42 per altri
  const recentlyBought = 12 + (hashCode % 25);     // venduti ultime 24h

  return (
    <div className="flex flex-wrap gap-2" data-testid="urgency-badges">
      {/* Few tickets left */}
      <div
        data-testid="badge-tickets-left"
        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-red-50 border border-red-200 rounded-full text-red-700 text-xs font-semibold"
      >
        <Flame className="w-3.5 h-3.5" />
        Solo {tixLeft} biglietti rimasti!
      </div>

      {/* Live viewers */}
      <div
        data-testid="badge-viewers"
        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-orange-50 border border-orange-200 rounded-full text-orange-700 text-xs font-semibold"
      >
        <Eye className="w-3.5 h-3.5" />
        <span className="relative flex h-2 w-2 mr-0.5">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-500 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
        </span>
        {viewers} stanno guardando ora
      </div>

      {/* Recently bought */}
      <div
        data-testid="badge-recently-bought"
        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-full text-blue-700 text-xs font-semibold"
      >
        <Users className="w-3.5 h-3.5" />
        {recentlyBought} acquisti nelle ultime 24h
      </div>
    </div>
  );
};

export default UrgencyBadges;
