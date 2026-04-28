import React, { useState } from 'react';

const SanSiroMap = ({ sectors = [], onSectorClick, selectedSector }) => {
  const [hoveredSector, setHoveredSector] = useState(null);

  // Map sector names to SVG regions - Viagogo style naming
  const sectorConfig = {
    'primo-anello-arancio': { match: ['Cat 1', 'Tribuna', '1° Anello', 'First Ring', 'Orange'], color: '#FF8C00' },
    'primo-anello-blu': { match: ['Cat 2', 'Short Side', '1° Anello Blu', 'Blue'], color: '#4169E1' },
    'secondo-anello-arancio': { match: ['Cat 2 Long', '2° Anello', 'Second Ring'], color: '#FFA500' },
    'secondo-anello-blu': { match: ['Cat 3', '2° Anello Blu'], color: '#1E90FF' },
    'terzo-anello': { match: ['Cat 3 Short', '3° Anello', 'Third Ring'], color: '#87CEEB' },
    'tribuna-onore': { match: ['Premium', 'VIP', 'Tribuna Onore', 'Honor'], color: '#FFD700' },
    'curva-nord': { match: ['Curva Nord', 'North Curve'], color: '#2E8B57' },
    'curva-sud': { match: ['Curva Sud', 'South Curve'], color: '#32CD32' },
  };

  const findSectorByName = (name) => {
    return sectors.find(s => {
      const sectorName = (s.name || '').toLowerCase();
      return sectorName.includes(name.toLowerCase()) || name.toLowerCase().includes(sectorName.split(' ')[0]?.toLowerCase());
    });
  };

  const getSectorForRegion = (regionId) => {
    const config = sectorConfig[regionId];
    if (!config) return null;
    
    for (const sector of sectors) {
      const sectorName = (sector.name || '').toLowerCase();
      for (const match of config.match) {
        if (sectorName.includes(match.toLowerCase())) {
          return sector;
        }
      }
    }
    return null;
  };

  const getRegionColor = (regionId, baseColor) => {
    const sector = getSectorForRegion(regionId);
    if (!sector) return '#666';
    if (!sector.available) return '#444';
    if (hoveredSector === regionId || selectedSector === sector.name) return '#00ff88';
    return baseColor;
  };

  const getRegionOpacity = (regionId) => {
    const sector = getSectorForRegion(regionId);
    if (!sector || !sector.available) return 0.4;
    return 1;
  };

  const handleRegionClick = (regionId) => {
    const sector = getSectorForRegion(regionId);
    if (sector?.available && onSectorClick) {
      onSectorClick(sector);
    }
  };

  const handleRegionHover = (regionId) => {
    const sector = getSectorForRegion(regionId);
    if (sector?.available) {
      setHoveredSector(regionId);
    }
  };

  // Get price for legend
  const getPriceForRegion = (regionId) => {
    const sector = getSectorForRegion(regionId);
    return sector?.price || null;
  };

  return (
    <div className="w-full">
      {/* Legend */}
      <div className="mb-4 flex flex-wrap gap-2 justify-center">
        {sectors.filter(s => s.available).map((sector, i) => (
          <button
            key={i}
            onClick={() => onSectorClick?.(sector)}
            className={`flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-full transition-all ${
              selectedSector === sector.name 
                ? 'bg-green-500 text-white' 
                : 'bg-white/10 text-white hover:bg-white/20'
            }`}
          >
            <span className="font-bold">€{sector.price}</span>
            <span className="text-white/70 text-[10px] max-w-[80px] truncate">{sector.name.split('(')[0]}</span>
          </button>
        ))}
      </div>

      {/* SVG Stadium Map - Viagogo Style */}
      <svg viewBox="0 0 500 380" className="w-full h-auto">
        <defs>
          <linearGradient id="fieldGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#2d7a3d" />
            <stop offset="100%" stopColor="#1a5a2d" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
              <feMergeNode in="coloredBlur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>
        
        {/* Background */}
        <rect x="0" y="0" width="500" height="380" fill="#0f1419" rx="10" />
        
        {/* 3° Anello (Outer Ring) */}
        <ellipse 
          cx="250" cy="190" rx="230" ry="170" 
          fill={getRegionColor('terzo-anello', '#87CEEB')}
          opacity={getRegionOpacity('terzo-anello')}
          stroke="#333" strokeWidth="2"
          style={{ cursor: getSectorForRegion('terzo-anello')?.available ? 'pointer' : 'default' }}
          onMouseEnter={() => handleRegionHover('terzo-anello')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleRegionClick('terzo-anello')}
        />
        
        {/* 2° Anello Arancio (Orange Second Ring) */}
        <ellipse 
          cx="250" cy="190" rx="190" ry="140" 
          fill={getRegionColor('secondo-anello-arancio', '#FFA500')}
          opacity={getRegionOpacity('secondo-anello-arancio')}
          stroke="#333" strokeWidth="2"
          style={{ cursor: getSectorForRegion('secondo-anello-arancio')?.available ? 'pointer' : 'default' }}
          onMouseEnter={() => handleRegionHover('secondo-anello-arancio')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleRegionClick('secondo-anello-arancio')}
        />
        
        {/* 2° Anello Blu (Blue Second Ring) - Short sides */}
        <ellipse 
          cx="250" cy="190" rx="155" ry="110" 
          fill={getRegionColor('secondo-anello-blu', '#1E90FF')}
          opacity={getRegionOpacity('secondo-anello-blu')}
          stroke="#333" strokeWidth="2"
          style={{ cursor: getSectorForRegion('secondo-anello-blu')?.available ? 'pointer' : 'default' }}
          onMouseEnter={() => handleRegionHover('secondo-anello-blu')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleRegionClick('secondo-anello-blu')}
        />
        
        {/* 1° Anello Arancio (Orange First Ring) */}
        <ellipse 
          cx="250" cy="190" rx="125" ry="85" 
          fill={getRegionColor('primo-anello-arancio', '#FF8C00')}
          opacity={getRegionOpacity('primo-anello-arancio')}
          stroke="#333" strokeWidth="2"
          style={{ cursor: getSectorForRegion('primo-anello-arancio')?.available ? 'pointer' : 'default' }}
          onMouseEnter={() => handleRegionHover('primo-anello-arancio')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleRegionClick('primo-anello-arancio')}
        />

        {/* Curva Nord (Left) */}
        <path 
          d="M 30 190 Q 30 100 125 110 L 125 270 Q 30 280 30 190"
          fill={getRegionColor('curva-nord', '#2E8B57')}
          opacity={getRegionOpacity('curva-nord')}
          stroke="#333" strokeWidth="2"
          style={{ cursor: getSectorForRegion('curva-nord')?.available ? 'pointer' : 'default' }}
          onMouseEnter={() => handleRegionHover('curva-nord')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleRegionClick('curva-nord')}
        />
        
        {/* Curva Sud (Right) */}
        <path 
          d="M 470 190 Q 470 100 375 110 L 375 270 Q 470 280 470 190"
          fill={getRegionColor('curva-sud', '#32CD32')}
          opacity={getRegionOpacity('curva-sud')}
          stroke="#333" strokeWidth="2"
          style={{ cursor: getSectorForRegion('curva-sud')?.available ? 'pointer' : 'default' }}
          onMouseEnter={() => handleRegionHover('curva-sud')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleRegionClick('curva-sud')}
        />
        
        {/* Tribuna d'Onore (VIP Central) */}
        <rect 
          x="175" y="150" width="150" height="80" rx="5"
          fill={getRegionColor('tribuna-onore', '#FFD700')}
          opacity={getRegionOpacity('tribuna-onore')}
          stroke="#333" strokeWidth="2"
          filter={selectedSector && getSectorForRegion('tribuna-onore')?.name === selectedSector ? 'url(#glow)' : ''}
          style={{ cursor: getSectorForRegion('tribuna-onore')?.available ? 'pointer' : 'default' }}
          onMouseEnter={() => handleRegionHover('tribuna-onore')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleRegionClick('tribuna-onore')}
        />
        
        {/* Playing Field */}
        <rect x="140" y="135" width="220" height="110" rx="3" fill="url(#fieldGradient)" stroke="#fff" strokeWidth="2" />
        
        {/* Field markings */}
        <line x1="250" y1="135" x2="250" y2="245" stroke="#fff" strokeWidth="1.5" opacity="0.7" />
        <circle cx="250" cy="190" r="25" fill="none" stroke="#fff" strokeWidth="1.5" opacity="0.7" />
        <rect x="140" y="165" width="35" height="50" fill="none" stroke="#fff" strokeWidth="1.5" opacity="0.7" />
        <rect x="325" y="165" width="35" height="50" fill="none" stroke="#fff" strokeWidth="1.5" opacity="0.7" />
        <circle cx="250" cy="190" r="3" fill="#fff" opacity="0.7" />
        
        {/* Labels */}
        <text x="65" y="195" fill="#fff" fontSize="11" fontWeight="bold" textAnchor="middle">CURVA</text>
        <text x="65" y="208" fill="#fff" fontSize="11" fontWeight="bold" textAnchor="middle">NORD</text>
        <text x="435" y="195" fill="#fff" fontSize="11" fontWeight="bold" textAnchor="middle">CURVA</text>
        <text x="435" y="208" fill="#fff" fontSize="11" fontWeight="bold" textAnchor="middle">SUD</text>
        <text x="250" y="195" fill="#000" fontSize="10" fontWeight="bold" textAnchor="middle" opacity="0.8">VIP</text>
        
        {/* Ring Labels */}
        <text x="250" y="45" fill="#fff" fontSize="9" textAnchor="middle" opacity="0.6">3° ANELLO</text>
        <text x="250" y="70" fill="#fff" fontSize="9" textAnchor="middle" opacity="0.6">2° ANELLO</text>
        <text x="250" y="100" fill="#fff" fontSize="9" textAnchor="middle" opacity="0.6">1° ANELLO</text>
        
        {/* Price indicators on hover */}
        {hoveredSector && (
          <g>
            <rect x="200" y="300" width="100" height="35" rx="5" fill="#000" opacity="0.9" />
            <text x="250" y="320" fill="#00ff88" fontSize="16" fontWeight="bold" textAnchor="middle">
              €{getSectorForRegion(hoveredSector)?.price || '?'}
            </text>
            <text x="250" y="332" fill="#fff" fontSize="8" textAnchor="middle" opacity="0.7">
              {getSectorForRegion(hoveredSector)?.name?.substring(0, 25) || ''}
            </text>
          </g>
        )}
      </svg>
      
      {/* Info Panel */}
      {(hoveredSector || selectedSector) && (
        <div className="mt-3 p-3 bg-white/10 rounded-lg text-center">
          <div className="text-white font-bold">
            {getSectorForRegion(hoveredSector)?.name || sectors.find(s => s.name === selectedSector)?.name}
          </div>
          <div className="text-green-400 text-xl font-bold">
            €{getSectorForRegion(hoveredSector)?.price || sectors.find(s => s.name === selectedSector)?.price}
          </div>
          {(getSectorForRegion(hoveredSector)?.notes || sectors.find(s => s.name === selectedSector)?.notes) && (
            <div className="text-gray-400 text-xs mt-1">
              {getSectorForRegion(hoveredSector)?.notes || sectors.find(s => s.name === selectedSector)?.notes}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SanSiroMap;
