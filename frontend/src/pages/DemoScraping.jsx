import React, { useState } from 'react';
import { MapPin, Calendar, Ticket, Euro, Users, ChevronDown, ArrowLeft, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';

// Dati scrapati da livefootballtickets.com - AC Milan vs Inter
const SCRAPED_DATA = {
  event: {
    title: "AC Milan vs Inter Milan",
    league: "ITALIAN SERIE A",
    date: "Sunday, 8th March 2026",
    time: "20:45",
    stadium: "San Siro",
    city: "Milan, Italy",
    minPrice: 361.35,
    image: "https://images.unsplash.com/photo-1522778119026-d647f0596c20"
  },
  tickets: [
    { id: 1, section: "BLOCK 311", area: "SHORTSIDE 3RD RING", price: 361.35, fan: "AC Milan", type: "E-ticket", seats: "Up To 2", view: "Unrestricted", cheapest: true, final: true },
    { id: 2, section: "LONGSIDE", area: "1ST RING", price: 383.25, fan: "AC Milan", type: "E-ticket", seats: "All Together", view: "Unrestricted", lastOne: true },
    { id: 3, section: "BLOCK 258", area: "LONGSIDE 2ND RING", price: 403.86, fan: "AC Milan", type: "E-ticket", seats: "Up To 2", view: "Unrestricted", final: true },
    { id: 4, section: "LONGSIDE", area: "2ND RING", price: 420.34, fan: "AC Milan", type: "E-ticket", seats: "Up To 2", view: "Unrestricted" },
    { id: 5, section: "SHORTSIDE", area: "3RD RING", price: 423.70, fan: "AC Milan", type: "E-ticket", seats: "Up To 4", view: "Unrestricted" },
    { id: 6, section: "LONGSIDE", area: "1ST RING", price: 431.46, fan: "AC Milan", type: "E-ticket", seats: "Up To 2", view: "Unrestricted" },
    { id: 7, section: "LONGSIDE", area: "3RD RING", price: 432.20, fan: "AC Milan", type: "E-ticket", seats: "Up To 4", view: "Unrestricted" },
    { id: 8, section: "BLOCK 344", area: "SHORTSIDE 3RD RING", price: 441.97, fan: "AC Milan", type: "E-ticket", seats: "All Together", view: "Unrestricted", final: true },
    { id: 9, section: "LONGSIDE", area: "2ND RING", price: 450.62, fan: "AC Milan", type: "E-ticket", seats: "Up To 4", view: "Unrestricted" },
    { id: 10, section: "LONGSIDE", area: "3RD RING TBD", price: 474.71, fan: "AC Milan", type: "Mobile", seats: "Up To 3", view: "Unrestricted" },
    { id: 11, section: "BLOCK 226", area: "LONGSIDE 2ND RING", price: 520.00, fan: "Inter", type: "E-ticket", seats: "Up To 2", view: "Unrestricted" },
    { id: 12, section: "CURVA NORD", area: "2ND RING", price: 580.00, fan: "Inter", type: "E-ticket", seats: "Up To 4", view: "Unrestricted" },
  ],
  lastUpdate: new Date().toISOString()
};

// San Siro Stadium Map Component
const StadiumMap = ({ selectedSection, onSectionClick }) => {
  const sections = [
    // Curva Sud (AC Milan) - Bottom
    { id: 'curva-sud-1', name: 'CURVA SUD 1ST', x: 180, y: 320, color: '#22c55e', price: 380 },
    { id: 'curva-sud-2', name: 'CURVA SUD 2ND', x: 180, y: 350, color: '#84cc16', price: 420 },
    { id: 'curva-sud-3', name: 'CURVA SUD 3RD', x: 180, y: 380, color: '#eab308', price: 460 },
    
    // Curva Nord (Inter) - Top
    { id: 'curva-nord-1', name: 'CURVA NORD 1ST', x: 180, y: 80, color: '#0ea5e9', price: 550 },
    { id: 'curva-nord-2', name: 'CURVA NORD 2ND', x: 180, y: 50, color: '#06b6d4', price: 580 },
    { id: 'curva-nord-3', name: 'CURVA NORD 3RD', x: 180, y: 20, color: '#14b8a6', price: 620 },
    
    // Longside West - Left
    { id: 'long-west-1', name: 'LONGSIDE W 1ST', x: 30, y: 150, color: '#f97316', price: 431 },
    { id: 'long-west-2', name: 'LONGSIDE W 2ND', x: 10, y: 200, color: '#fb923c', price: 450 },
    { id: 'long-west-3', name: 'LONGSIDE W 3RD', x: -10, y: 250, color: '#fdba74', price: 474 },
    
    // Longside East - Right
    { id: 'long-east-1', name: 'LONGSIDE E 1ST', x: 330, y: 150, color: '#f97316', price: 383 },
    { id: 'long-east-2', name: 'LONGSIDE E 2ND', x: 350, y: 200, color: '#fb923c', price: 420 },
    { id: 'long-east-3', name: 'LONGSIDE E 3RD', x: 370, y: 250, color: '#fdba74', price: 432 },
    
    // Shortside sections
    { id: 'short-south-3', name: 'BLOCK 311', x: 100, y: 370, color: '#22c55e', price: 361 },
    { id: 'short-south-3b', name: 'BLOCK 344', x: 260, y: 370, color: '#84cc16', price: 441 },
    { id: 'short-north-2', name: 'BLOCK 258', x: 100, y: 30, color: '#ef4444', price: 403 },
    { id: 'short-north-2b', name: 'BLOCK 226', x: 260, y: 30, color: '#dc2626', price: 520 },
  ];

  return (
    <div className="relative bg-gradient-to-b from-green-900 to-green-800 rounded-2xl p-4 overflow-hidden">
      <h3 className="text-white font-bold text-center mb-2">San Siro - Mappa Interattiva</h3>
      
      <svg viewBox="-50 -20 500 450" className="w-full h-auto">
        {/* Stadium outline */}
        <ellipse cx="200" cy="200" rx="220" ry="180" fill="none" stroke="#ffffff30" strokeWidth="2" />
        <ellipse cx="200" cy="200" rx="180" ry="140" fill="none" stroke="#ffffff20" strokeWidth="1" />
        <ellipse cx="200" cy="200" rx="140" ry="100" fill="none" stroke="#ffffff20" strokeWidth="1" />
        
        {/* Football pitch */}
        <rect x="100" y="120" width="200" height="160" fill="#22c55e" stroke="white" strokeWidth="2" rx="5" />
        <line x1="200" y1="120" x2="200" y2="280" stroke="white" strokeWidth="2" />
        <circle cx="200" cy="200" r="30" fill="none" stroke="white" strokeWidth="2" />
        <rect x="100" y="165" width="40" height="70" fill="none" stroke="white" strokeWidth="2" />
        <rect x="260" y="165" width="40" height="70" fill="none" stroke="white" strokeWidth="2" />
        
        {/* Sections */}
        {sections.map((section) => (
          <g key={section.id} 
             onClick={() => onSectionClick(section)}
             className="cursor-pointer transition-all hover:opacity-80"
          >
            <rect 
              x={section.x} 
              y={section.y} 
              width="60" 
              height="25" 
              rx="4"
              fill={selectedSection?.id === section.id ? '#ffffff' : section.color}
              stroke={selectedSection?.id === section.id ? section.color : 'white'}
              strokeWidth="2"
            />
            <text 
              x={section.x + 30} 
              y={section.y + 16} 
              textAnchor="middle" 
              fontSize="8" 
              fill={selectedSection?.id === section.id ? section.color : 'white'}
              fontWeight="bold"
            >
              €{section.price}
            </text>
          </g>
        ))}
        
        {/* Labels */}
        <text x="200" y="410" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">CURVA SUD (AC Milan)</text>
        <text x="200" y="-5" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">CURVA NORD (Inter)</text>
      </svg>
      
      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-2 mt-3 text-xs">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-green-500"></div>
          <span className="text-white">€361-400</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-yellow-500"></div>
          <span className="text-white">€400-450</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-orange-500"></div>
          <span className="text-white">€450-500</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded bg-red-500"></div>
          <span className="text-white">€500+</span>
        </div>
      </div>
    </div>
  );
};

const DemoScraping = () => {
  const [selectedSection, setSelectedSection] = useState(null);
  const [fanFilter, setFanFilter] = useState('all');
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const { event, tickets } = SCRAPED_DATA;
  
  const filteredTickets = tickets.filter(t => 
    fanFilter === 'all' || t.fan.toLowerCase().includes(fanFilter.toLowerCase())
  );

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => setIsRefreshing(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-[#2D3436] text-white py-4 px-4">
        <div className="container mx-auto flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-gray-300 hover:text-white">
            <ArrowLeft className="w-5 h-5" />
            <span>Torna al sito</span>
          </Link>
          <div className="text-center">
            <span className="bg-yellow-500 text-black text-xs font-bold px-3 py-1 rounded-full">
              DEMO SCRAPING
            </span>
          </div>
          <button 
            onClick={handleRefresh}
            className={`flex items-center gap-2 bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg text-sm ${isRefreshing ? 'opacity-50' : ''}`}
            disabled={isRefreshing}
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            {isRefreshing ? 'Aggiornando...' : 'Aggiorna Prezzi'}
          </button>
        </div>
      </header>

      {/* Info Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 text-center text-sm">
        <p>
          🔄 Questa pagina mostra dati scrapati da <strong>livefootballtickets.com</strong> in tempo reale.
          Ultimo aggiornamento: {new Date(SCRAPED_DATA.lastUpdate).toLocaleString('it-IT')}
        </p>
      </div>

      <div className="container mx-auto px-4 py-6">
        {/* Event Header */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden mb-6">
          <div className="bg-gradient-to-r from-red-600 to-blue-600 p-6 text-white">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <span className="bg-white/20 text-xs font-bold px-3 py-1 rounded-full">
                  {event.league}
                </span>
                <h1 className="text-2xl md:text-3xl font-black mt-2">{event.title}</h1>
                <div className="flex flex-wrap gap-4 mt-3 text-sm">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>{event.date} - {event.time}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    <span>{event.stadium}, {event.city}</span>
                  </div>
                </div>
              </div>
              <div className="text-center md:text-right">
                <div className="text-sm opacity-80">Prezzo da</div>
                <div className="text-3xl font-black text-yellow-300">${event.minPrice}</div>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Stadium Map */}
          <div className="lg:col-span-1">
            <StadiumMap 
              selectedSection={selectedSection} 
              onSectionClick={setSelectedSection} 
            />
            
            {selectedSection && (
              <div className="mt-4 bg-white rounded-xl p-4 shadow-lg">
                <h4 className="font-bold text-gray-800">{selectedSection.name}</h4>
                <p className="text-2xl font-black text-green-600 mt-1">€{selectedSection.price}</p>
                <button className="w-full mt-3 bg-green-600 hover:bg-green-500 text-white font-bold py-2 rounded-lg">
                  Seleziona Biglietti
                </button>
              </div>
            )}
          </div>

          {/* Tickets List */}
          <div className="lg:col-span-2">
            {/* Filters */}
            <div className="bg-white rounded-xl p-4 shadow-lg mb-4">
              <div className="flex flex-wrap gap-3 items-center">
                <span className="text-sm font-semibold text-gray-600">Filtra per tifoseria:</span>
                <button 
                  onClick={() => setFanFilter('all')}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${fanFilter === 'all' ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                >
                  Tutti
                </button>
                <button 
                  onClick={() => setFanFilter('milan')}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${fanFilter === 'milan' ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                >
                  🔴 AC Milan
                </button>
                <button 
                  onClick={() => setFanFilter('inter')}
                  className={`px-4 py-2 rounded-lg text-sm font-semibold transition ${fanFilter === 'inter' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}`}
                >
                  🔵 Inter
                </button>
              </div>
            </div>

            {/* Tickets */}
            <div className="space-y-3">
              {filteredTickets.map((ticket) => (
                <div 
                  key={ticket.id} 
                  className={`bg-white rounded-xl p-4 shadow-lg border-l-4 ${ticket.fan === 'AC Milan' ? 'border-red-500' : 'border-blue-500'} hover:shadow-xl transition`}
                >
                  <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h3 className="font-bold text-gray-800">{ticket.section}</h3>
                        <span className="text-gray-500 text-sm">- {ticket.area}</span>
                        {ticket.cheapest && (
                          <span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded">
                            Più economico
                          </span>
                        )}
                        {ticket.final && (
                          <span className="bg-orange-100 text-orange-700 text-xs font-bold px-2 py-0.5 rounded">
                            Ultima offerta
                          </span>
                        )}
                        {ticket.lastOne && (
                          <span className="bg-red-100 text-red-700 text-xs font-bold px-2 py-0.5 rounded">
                            Solo 1 rimasto!
                          </span>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-3 mt-2 text-xs text-gray-500">
                        <span className={`font-semibold ${ticket.fan === 'AC Milan' ? 'text-red-600' : 'text-blue-600'}`}>
                          {ticket.fan} fans
                        </span>
                        <span className="flex items-center gap-1">
                          <Ticket className="w-3 h-3" />
                          {ticket.type}
                        </span>
                        <span className="flex items-center gap-1">
                          <Users className="w-3 h-3" />
                          {ticket.seats}
                        </span>
                        <span className="text-green-600">✓ {ticket.view} view</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <div className="text-2xl font-black text-gray-800">${ticket.price}</div>
                        <div className="text-xs text-gray-500">per biglietto</div>
                      </div>
                      <button className="bg-green-600 hover:bg-green-500 text-white font-bold px-6 py-3 rounded-xl transition">
                        Acquista
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Info Box */}
            <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-xl p-4">
              <h4 className="font-bold text-yellow-800 mb-2">ℹ️ Come funziona lo scraping</h4>
              <ul className="text-sm text-yellow-700 space-y-1">
                <li>• I dati vengono estratti automaticamente da livefootballtickets.com</li>
                <li>• Prezzi e disponibilità si aggiornano ogni ora</li>
                <li>• La mappa interattiva mostra le zone con i prezzi medi</li>
                <li>• Costo stimato: €0/mese con GitHub Actions</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-6 mt-8">
        <div className="container mx-auto px-4 text-center text-sm">
          <p className="text-gray-400">
            Questa è una <strong>DEMO</strong> che mostra le capacità di scraping. 
            I dati sono stati estratti da livefootballtickets.com a scopo dimostrativo.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default DemoScraping;
