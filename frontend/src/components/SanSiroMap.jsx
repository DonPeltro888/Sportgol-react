import React, { useState } from 'react';

const SanSiroMap = ({ sectors = [], onSectorClick, selectedSector }) => {
  const [hoveredSector, setHoveredSector] = useState(null);

  // Mappa settori con i loro colori e posizioni
  const sectorMapping = {
    'Cat 1 Premium': { color: '#FFD700', ring: 'tribuna-onore' },
    'Cat 1 Normal': { color: '#FFA500', ring: 'tribuna-arancio' },
    'Cat 2 Short Side Lower': { color: '#4169E1', ring: 'anello-1-blu' },
    'Cat 2 Long Side Upper': { color: '#FF8C00', ring: 'anello-2-arancio' },
    'Cat 3 Short Side': { color: '#1E90FF', ring: 'anello-3-blu' },
    'Curva Nord': { color: '#2E8B57', ring: 'curva-nord' },
    'Curva Sud': { color: '#2E8B57', ring: 'curva-sud' },
    'Best Available': { color: '#9370DB', ring: 'best' },
  };

  const getSectorInfo = (sectorName) => {
    return sectors.find(s => s.name.includes(sectorName) || sectorName.includes(s.name?.split(' ')[0]));
  };

  const getSectorColor = (sectorName, baseColor) => {
    const sector = getSectorInfo(sectorName);
    if (!sector) return '#ccc';
    if (!sector.available) return '#666';
    if (hoveredSector === sectorName) return '#00ff88';
    if (selectedSector === sectorName) return '#00ff88';
    return baseColor;
  };

  const handleSectorHover = (sectorName) => {
    const sector = getSectorInfo(sectorName);
    if (sector?.available) {
      setHoveredSector(sectorName);
    }
  };

  const handleSectorClick = (sectorName) => {
    const sector = getSectorInfo(sectorName);
    if (sector?.available && onSectorClick) {
      onSectorClick(sector);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Legenda prezzi */}
      <div className="mb-4 flex flex-wrap gap-2 justify-center">
        {sectors.filter(s => s.available).slice(0, 6).map((sector, i) => (
          <div 
            key={i}
            className="flex items-center gap-1 text-xs bg-white px-2 py-1 rounded border cursor-pointer hover:bg-gray-50"
            onClick={() => onSectorClick?.(sector)}
          >
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: Object.values(sectorMapping)[i]?.color || '#ccc' }}
            />
            <span className="font-medium">€{sector.price}</span>
          </div>
        ))}
      </div>

      {/* SVG Mappa San Siro */}
      <svg viewBox="0 0 400 300" className="w-full h-auto">
        {/* Sfondo */}
        <rect x="0" y="0" width="400" height="300" fill="#1a1a2e" />
        
        {/* 3° Anello (esterno) */}
        <ellipse 
          cx="200" cy="150" rx="180" ry="130" 
          fill={getSectorColor('Cat 3 Short Side', '#1E90FF')}
          stroke="#fff" strokeWidth="2"
          style={{ cursor: getSectorInfo('Cat 3 Short Side')?.available ? 'pointer' : 'not-allowed' }}
          onMouseEnter={() => handleSectorHover('Cat 3 Short Side')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleSectorClick('Cat 3 Short Side')}
        />
        
        {/* 2° Anello */}
        <ellipse 
          cx="200" cy="150" rx="150" ry="105" 
          fill={getSectorColor('Cat 2 Long Side Upper', '#FF8C00')}
          stroke="#fff" strokeWidth="2"
          style={{ cursor: getSectorInfo('Cat 2 Long Side Upper')?.available ? 'pointer' : 'not-allowed' }}
          onMouseEnter={() => handleSectorHover('Cat 2 Long Side Upper')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleSectorClick('Cat 2 Long Side Upper')}
        />
        
        {/* 1° Anello */}
        <ellipse 
          cx="200" cy="150" rx="120" ry="80" 
          fill={getSectorColor('Cat 2 Short Side Lower', '#4169E1')}
          stroke="#fff" strokeWidth="2"
          style={{ cursor: getSectorInfo('Cat 2 Short Side Lower')?.available ? 'pointer' : 'not-allowed' }}
          onMouseEnter={() => handleSectorHover('Cat 2 Short Side Lower')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleSectorClick('Cat 2 Short Side Lower')}
        />
        
        {/* Tribuna (lato lungo) */}
        <rect 
          x="60" y="120" width="280" height="60" rx="5"
          fill={getSectorColor('Cat 1 Normal', '#FFA500')}
          stroke="#fff" strokeWidth="2"
          style={{ cursor: getSectorInfo('Cat 1 Normal')?.available ? 'pointer' : 'not-allowed' }}
          onMouseEnter={() => handleSectorHover('Cat 1 Normal')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleSectorClick('Cat 1 Normal')}
        />
        
        {/* Tribuna d'Onore (centrale) */}
        <rect 
          x="140" y="130" width="120" height="40" rx="3"
          fill={getSectorColor('Cat 1 Premium', '#FFD700')}
          stroke="#fff" strokeWidth="2"
          style={{ cursor: getSectorInfo('Cat 1 Premium')?.available ? 'pointer' : 'not-allowed' }}
          onMouseEnter={() => handleSectorHover('Cat 1 Premium')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleSectorClick('Cat 1 Premium')}
        />
        
        {/* Campo da gioco */}
        <rect 
          x="100" y="100" width="200" height="100" rx="3"
          fill="#2d5a27" stroke="#fff" strokeWidth="2"
        />
        {/* Linee campo */}
        <line x1="200" y1="100" x2="200" y2="200" stroke="#fff" strokeWidth="1" opacity="0.5" />
        <circle cx="200" cy="150" r="20" fill="none" stroke="#fff" strokeWidth="1" opacity="0.5" />
        <rect x="100" y="125" width="30" height="50" fill="none" stroke="#fff" strokeWidth="1" opacity="0.5" />
        <rect x="270" y="125" width="30" height="50" fill="none" stroke="#fff" strokeWidth="1" opacity="0.5" />
        
        {/* Curva Nord (sinistra) */}
        <path 
          d="M 30 150 Q 30 80 100 100 L 100 200 Q 30 220 30 150"
          fill={getSectorColor('Curva Nord', '#2E8B57')}
          stroke="#fff" strokeWidth="2"
          style={{ cursor: getSectorInfo('Curva Nord')?.available ? 'pointer' : 'not-allowed', opacity: getSectorInfo('Curva Nord')?.available ? 1 : 0.4 }}
          onMouseEnter={() => handleSectorHover('Curva Nord')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleSectorClick('Curva Nord')}
        />
        
        {/* Curva Sud (destra) */}
        <path 
          d="M 370 150 Q 370 80 300 100 L 300 200 Q 370 220 370 150"
          fill={getSectorColor('Curva Sud', '#2E8B57')}
          stroke="#fff" strokeWidth="2"
          style={{ cursor: 'pointer' }}
          onMouseEnter={() => handleSectorHover('Curva Sud')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleSectorClick('Curva Sud')}
        />
        
        {/* Labels */}
        <text x="65" y="155" fill="#fff" fontSize="10" fontWeight="bold">CURVA</text>
        <text x="65" y="167" fill="#fff" fontSize="10" fontWeight="bold">NORD</text>
        <text x="320" y="155" fill="#fff" fontSize="10" fontWeight="bold">CURVA</text>
        <text x="322" y="167" fill="#fff" fontSize="10" fontWeight="bold">SUD</text>
        <text x="165" y="155" fill="#000" fontSize="12" fontWeight="bold">TRIBUNA VIP</text>
        <text x="180" y="250" fill="#fff" fontSize="10">3° ANELLO</text>
        <text x="180" y="235" fill="#fff" fontSize="10">2° ANELLO</text>
        <text x="180" y="85" fill="#fff" fontSize="10">1° ANELLO</text>
      </svg>

      {/* Info settore hover */}
      {hoveredSector && (
        <div className="mt-4 p-3 bg-white rounded-lg border border-gray-200 text-center">
          <div className="font-bold text-gray-900">{getSectorInfo(hoveredSector)?.name}</div>
          <div className="text-2xl font-bold text-green-600">€{getSectorInfo(hoveredSector)?.price}</div>
          {getSectorInfo(hoveredSector)?.notes && (
            <div className="text-sm text-gray-500">{getSectorInfo(hoveredSector)?.notes}</div>
          )}
        </div>
      )}
    </div>
  );
};

export default SanSiroMap;
