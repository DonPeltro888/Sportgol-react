import React, { useState } from 'react';

const SanSiroMap = ({ sectors = [], onSectorClick, selectedSector }) => {
  const [hoveredSector, setHoveredSector] = useState(null);

  // Mappa settori San Siro -> Categorie generali
  const sectorToCategory = {
    // Cat 1 Premium
    'tribuna-onore': { category: 'Cat 1 Premium', label: '1° Anello Arancio Centrale', color: '#FFD700' },
    // Cat 1  
    'primo-arancio': { category: 'Cat 1', label: '1° Anello Arancio', color: '#FF8C00' },
    // Cat 2
    'primo-blu': { category: 'Cat 2', label: '1° Anello Blu', color: '#1E90FF' },
    'secondo-arancio': { category: 'Cat 2', label: '2° Anello Arancio', color: '#FFA500' },
    // Cat 3
    'secondo-blu': { category: 'Cat 3', label: '2° Anello Blu', color: '#4169E1' },
    'terzo-rosso': { category: 'Cat 3', label: '3° Anello Rosso', color: '#DC143C' },
    'terzo-arancio': { category: 'Cat 3', label: '3° Anello Arancio', color: '#FF6347' },
    // Cat 4
    'curva-nord': { category: 'Cat 4', label: 'Curva Nord', color: '#228B22' },
    'curva-sud': { category: 'Cat 4 - Ospiti', label: 'Curva Sud', color: '#32CD32' },
  };

  const getCategoryForRegion = (regionId) => {
    const mapping = sectorToCategory[regionId];
    if (!mapping) return null;
    return sectors.find(s => s.name === mapping.category || s.name.includes(mapping.category));
  };

  const getRegionStyle = (regionId) => {
    const mapping = sectorToCategory[regionId];
    const sector = getCategoryForRegion(regionId);
    const isSelected = sector && selectedSector === sector.name;
    const isHovered = hoveredSector === regionId;
    const hasSelection = selectedSector !== null;
    
    if (!sector) return { fill: '#333', opacity: 0.3, cursor: 'default' };
    if (!sector.available) return { fill: '#444', opacity: 0.3, cursor: 'not-allowed' };
    
    // Se c'è una selezione, mostra colorato solo il settore selezionato
    if (hasSelection && !isSelected) {
      return {
        fill: isHovered ? mapping?.color || '#666' : '#333',
        opacity: isHovered ? 0.7 : 0.3,
        cursor: 'pointer',
        transition: 'all 0.2s ease'
      };
    }
    
    return {
      fill: isSelected ? '#00FF7F' : isHovered ? '#00FF7F' : mapping?.color || '#666',
      opacity: 1,
      cursor: 'pointer',
      transition: 'all 0.2s ease'
    };
  };

  const handleClick = (regionId) => {
    const sector = getCategoryForRegion(regionId);
    if (sector?.available && onSectorClick) {
      onSectorClick(sector);
    }
  };

  const getHoverInfo = () => {
    if (!hoveredSector) return null;
    const mapping = sectorToCategory[hoveredSector];
    const sector = getCategoryForRegion(hoveredSector);
    if (!mapping || !sector) return null;
    return { label: mapping.label, category: sector.name, price: sector.price };
  };

  const hoverInfo = getHoverInfo();

  return (
    <div className="w-full">
      {/* Legenda Categorie */}
      <div className="mb-4 flex flex-wrap gap-2 justify-center">
        {sectors.filter(s => s.available).map((sector, i) => (
          <button
            key={i}
            onClick={() => onSectorClick?.(sector)}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
              selectedSector === sector.name 
                ? 'bg-green-500 text-white ring-2 ring-green-300' 
                : 'bg-white/10 text-white hover:bg-white/20'
            }`}
          >
            {sector.name} - €{sector.price}
          </button>
        ))}
      </div>

      {/* San Siro Map */}
      <svg viewBox="0 0 600 450" className="w-full h-auto">
        <defs>
          <linearGradient id="grass" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#2d8a3e" />
            <stop offset="100%" stopColor="#1a6b2c" />
          </linearGradient>
        </defs>
        
        {/* Background */}
        <rect x="0" y="0" width="600" height="450" fill="#0a0f14" rx="12" />
        
        {/* === TERZO ANELLO (Esterno) === */}
        {/* 3° Anello Rosso - Long Side Top */}
        <path
          d="M 100 55 Q 300 15 500 55 L 480 95 Q 300 60 120 95 Z"
          style={getRegionStyle('terzo-rosso')}
          onMouseEnter={() => setHoveredSector('terzo-rosso')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('terzo-rosso')}
        />
        {/* 3° Anello Rosso - Long Side Bottom */}
        <path
          d="M 100 395 Q 300 435 500 395 L 480 355 Q 300 390 120 355 Z"
          style={getRegionStyle('terzo-rosso')}
          onMouseEnter={() => setHoveredSector('terzo-rosso')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('terzo-rosso')}
        />
        {/* 3° Anello Arancio - Short Side Left */}
        <path
          d="M 55 100 Q 15 225 55 350 L 95 325 Q 60 225 95 125 Z"
          style={getRegionStyle('terzo-arancio')}
          onMouseEnter={() => setHoveredSector('terzo-arancio')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('terzo-arancio')}
        />
        {/* 3° Anello Arancio - Short Side Right */}
        <path
          d="M 545 100 Q 585 225 545 350 L 505 325 Q 540 225 505 125 Z"
          style={getRegionStyle('terzo-arancio')}
          onMouseEnter={() => setHoveredSector('terzo-arancio')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('terzo-arancio')}
        />

        {/* === SECONDO ANELLO === */}
        {/* 2° Anello Arancio - Long Side Top */}
        <path
          d="M 120 95 Q 300 60 480 95 L 460 135 Q 300 105 140 135 Z"
          style={getRegionStyle('secondo-arancio')}
          onMouseEnter={() => setHoveredSector('secondo-arancio')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('secondo-arancio')}
        />
        {/* 2° Anello Arancio - Long Side Bottom */}
        <path
          d="M 120 355 Q 300 390 480 355 L 460 315 Q 300 345 140 315 Z"
          style={getRegionStyle('secondo-arancio')}
          onMouseEnter={() => setHoveredSector('secondo-arancio')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('secondo-arancio')}
        />
        {/* 2° Anello Blu - Short Side Left */}
        <path
          d="M 95 125 Q 60 225 95 325 L 135 300 Q 105 225 135 150 Z"
          style={getRegionStyle('secondo-blu')}
          onMouseEnter={() => setHoveredSector('secondo-blu')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('secondo-blu')}
        />
        {/* 2° Anello Blu - Short Side Right */}
        <path
          d="M 505 125 Q 540 225 505 325 L 465 300 Q 495 225 465 150 Z"
          style={getRegionStyle('secondo-blu')}
          onMouseEnter={() => setHoveredSector('secondo-blu')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('secondo-blu')}
        />

        {/* === PRIMO ANELLO === */}
        {/* 1° Anello Arancio - Long Side Top */}
        <path
          d="M 140 135 Q 300 105 460 135 L 440 175 Q 300 150 160 175 Z"
          style={getRegionStyle('primo-arancio')}
          onMouseEnter={() => setHoveredSector('primo-arancio')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('primo-arancio')}
        />
        {/* 1° Anello Arancio - Long Side Bottom */}
        <path
          d="M 140 315 Q 300 345 460 315 L 440 275 Q 300 300 160 275 Z"
          style={getRegionStyle('primo-arancio')}
          onMouseEnter={() => setHoveredSector('primo-arancio')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('primo-arancio')}
        />
        {/* 1° Anello Blu - Short Side Left */}
        <path
          d="M 135 150 Q 105 225 135 300 L 175 275 Q 150 225 175 175 Z"
          style={getRegionStyle('primo-blu')}
          onMouseEnter={() => setHoveredSector('primo-blu')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('primo-blu')}
        />
        {/* 1° Anello Blu - Short Side Right */}
        <path
          d="M 465 150 Q 495 225 465 300 L 425 275 Q 450 225 425 175 Z"
          style={getRegionStyle('primo-blu')}
          onMouseEnter={() => setHoveredSector('primo-blu')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('primo-blu')}
        />

        {/* === TRIBUNA D'ONORE (VIP) === */}
        <rect
          x="220" y="155" width="160" height="30" rx="4"
          style={getRegionStyle('tribuna-onore')}
          onMouseEnter={() => setHoveredSector('tribuna-onore')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('tribuna-onore')}
        />
        <rect
          x="220" y="265" width="160" height="30" rx="4"
          style={getRegionStyle('tribuna-onore')}
          onMouseEnter={() => setHoveredSector('tribuna-onore')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('tribuna-onore')}
        />

        {/* === CURVE === */}
        {/* Curva Nord - Angoli a sinistra */}
        <path
          d="M 55 100 L 100 55 L 120 95 L 95 125 Z"
          style={getRegionStyle('curva-nord')}
          onMouseEnter={() => setHoveredSector('curva-nord')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('curva-nord')}
        />
        <path
          d="M 55 350 L 100 395 L 120 355 L 95 325 Z"
          style={getRegionStyle('curva-nord')}
          onMouseEnter={() => setHoveredSector('curva-nord')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('curva-nord')}
        />
        {/* Curva Sud - Angoli a destra */}
        <path
          d="M 545 100 L 500 55 L 480 95 L 505 125 Z"
          style={getRegionStyle('curva-sud')}
          onMouseEnter={() => setHoveredSector('curva-sud')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('curva-sud')}
        />
        <path
          d="M 545 350 L 500 395 L 480 355 L 505 325 Z"
          style={getRegionStyle('curva-sud')}
          onMouseEnter={() => setHoveredSector('curva-sud')}
          onMouseLeave={() => setHoveredSector(null)}
          onClick={() => handleClick('curva-sud')}
        />

        {/* === CAMPO DA GIOCO === */}
        <rect x="175" y="190" width="250" height="70" rx="3" fill="url(#grass)" stroke="#fff" strokeWidth="2" />
        <line x1="300" y1="190" x2="300" y2="260" stroke="#fff" strokeWidth="1" opacity="0.6" />
        <circle cx="300" cy="225" r="18" fill="none" stroke="#fff" strokeWidth="1" opacity="0.6" />
        <rect x="175" y="200" width="30" height="50" fill="none" stroke="#fff" strokeWidth="1" opacity="0.6" />
        <rect x="395" y="200" width="30" height="50" fill="none" stroke="#fff" strokeWidth="1" opacity="0.6" />

        {/* === LABELS SETTORI === */}
        <text x="300" y="42" fill="#DC143C" fontSize="11" fontWeight="bold" textAnchor="middle">3° Anello Rosso</text>
        <text x="300" y="82" fill="#FFA500" fontSize="10" textAnchor="middle">2° Anello Arancio</text>
        <text x="300" y="122" fill="#FF8C00" fontSize="10" textAnchor="middle">1° Anello Arancio</text>
        <text x="300" y="172" fill="#FFD700" fontSize="9" fontWeight="bold" textAnchor="middle">TRIBUNA VIP</text>
        
        <text x="40" y="225" fill="#228B22" fontSize="9" fontWeight="bold" textAnchor="middle" transform="rotate(-90 40 225)">Curva Nord</text>
        <text x="560" y="225" fill="#32CD32" fontSize="9" fontWeight="bold" textAnchor="middle" transform="rotate(90 560 225)">Curva Sud</text>
        
        <text x="115" y="225" fill="#1E90FF" fontSize="8" textAnchor="middle" transform="rotate(-90 115 225)">1° Blu</text>
        <text x="485" y="225" fill="#1E90FF" fontSize="8" textAnchor="middle" transform="rotate(90 485 225)">1° Blu</text>
        
        <text x="75" y="225" fill="#4169E1" fontSize="8" textAnchor="middle" transform="rotate(-90 75 225)">2° Blu</text>
        <text x="525" y="225" fill="#4169E1" fontSize="8" textAnchor="middle" transform="rotate(90 525 225)">2° Blu</text>

        <text x="35" y="225" fill="#FF6347" fontSize="8" textAnchor="middle" transform="rotate(-90 35 225)">3° Ar.</text>
        <text x="565" y="225" fill="#FF6347" fontSize="8" textAnchor="middle" transform="rotate(90 565 225)">3° Ar.</text>

        <text x="300" y="408" fill="#DC143C" fontSize="11" fontWeight="bold" textAnchor="middle">3° Anello Rosso</text>

        {/* === HOVER INFO BOX === */}
        {hoverInfo && (
          <g>
            <rect x="175" y="310" width="250" height="55" rx="8" fill="rgba(0,0,0,0.95)" stroke="#00FF7F" strokeWidth="1" />
            <text x="300" y="332" fill="#00FF7F" fontSize="20" fontWeight="bold" textAnchor="middle">€{hoverInfo.price}</text>
            <text x="300" y="350" fill="#fff" fontSize="11" textAnchor="middle">{hoverInfo.label}</text>
            <text x="300" y="362" fill="#aaa" fontSize="9" textAnchor="middle">({hoverInfo.category})</text>
          </g>
        )}
      </svg>

      {/* Selected Category Info */}
      {selectedSector && (
        <div className="mt-4 p-4 bg-green-500/20 border border-green-500/50 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-green-400 text-xs font-semibold uppercase tracking-wide">Categoria Selezionata</div>
              <div className="text-white text-lg font-bold">{selectedSector}</div>
            </div>
            <div className="text-3xl font-bold text-green-400">
              €{sectors.find(s => s.name === selectedSector)?.price}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SanSiroMap;
