import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, X, ChevronDown, ChevronRight } from 'lucide-react';

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [openDropdown, setOpenDropdown] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const menuStructure = [
    {
      label: 'EVENTS',
      href: '/',
      type: 'link'
    },
    {
      label: 'SERIE A',
      slug: 'serie-a',
      type: 'league',
      country: 'Italy 🇮🇹',
      teams: [
        'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina',
        'Genoa', 'Hellas Verona', 'Inter', 'Juventus', 'Lazio', 'Lecce',
        'Milan', 'Napoli', 'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese'
      ]
    },
    {
      label: 'PREMIER LEAGUE',
      slug: 'premier-league',
      type: 'league',
      country: 'England 🏴󠁧󠁢󠁥󠁮󠁧󠁿',
      teams: [
        'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Burnley',
        'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Leeds United', 'Liverpool',
        'Manchester City', 'Manchester United', 'Newcastle United', 'Nottingham Forest',
        'Sunderland', 'Tottenham', 'West Ham', 'Wolves'
      ]
    },
    {
      label: 'LA LIGA',
      slug: 'la-liga',
      type: 'league',
      country: 'Spain 🇪🇸',
      teams: [
        'Alavés', 'Athletic Bilbao', 'Atlético Madrid', 'Barcelona', 'Betis', 'Celta Vigo',
        'Elche', 'Espanyol', 'Getafe', 'Girona', 'Levante', 'Mallorca',
        'Osasuna', 'Oviedo', 'Rayo Vallecano', 'Real Madrid', 'Real Sociedad', 'Sevilla',
        'Valencia', 'Villarreal'
      ]
    },
    {
      label: 'BUNDESLIGA',
      slug: 'bundesliga',
      type: 'league',
      country: 'Germany 🇩🇪',
      teams: [
        'Augsburg', 'Bayern Munich', 'Borussia Dortmund', 'Borussia Mönchengladbach',
        'Eintracht Frankfurt', 'Freiburg', 'Hamburger SV', 'Heidenheim',
        'Hoffenheim', 'Köln', 'Leverkusen', 'Mainz', 'RB Leipzig', 'St. Pauli',
        'Stuttgart', 'Union Berlin', 'Werder Bremen', 'Wolfsburg'
      ]
    },
    {
      label: 'LIGA PORTUGAL',
      slug: 'liga-portugal',
      type: 'league',
      country: 'Portugal 🇵🇹',
      teams: [
        'Arouca', 'AVS', 'Benfica', 'Boavista', 'Braga', 'Casa Pia',
        'Estoril', 'Farense', 'Famalicão', 'Gil Vicente', 'Moreirense', 'Nacional',
        'Porto', 'Rio Ave', 'Santa Clara', 'Sporting CP', 'Estrela', 'Vitória Guimarães'
      ]
    },
    {
      label: 'LIGUE 1',
      slug: 'ligue-1',
      type: 'league',
      country: 'France 🇫🇷',
      teams: [
        'PSG', 'Monaco', 'Marseille', 'Lyon', 'Angers', 'Le Havre'
      ]
    },
    {
      label: 'SUPER LIG',
      slug: 'super-lig',
      type: 'league',
      country: 'Turkey 🇹🇷',
      teams: [
        'Galatasaray', 'Fenerbahçe', 'Beşiktaş', 'Trabzonspor', 'Alanyaspor', 'Antalyaspor', 'Kocaelispor'
      ]
    },
    {
      label: 'CHAMPIONS LEAGUE',
      slug: 'champions-league',
      type: 'cup',
      country: 'Europe 🏆'
    },
    {
      label: 'EUROPA LEAGUE',
      slug: 'europa-league',
      type: 'cup',
      country: 'Europe 🏆'
    },
    {
      label: 'COPPA ITALIA',
      slug: 'coppa-italia',
      type: 'cup',
      country: 'Italy 🇮🇹'
    },
    {
      label: 'COPA DEL REY',
      slug: 'copa-del-rey',
      type: 'cup',
      country: 'Spain 🇪🇸'
    },
    {
      label: 'FA CUP',
      slug: 'fa-cup',
      type: 'cup',
      country: 'England 🏴󠁧󠁢󠁥󠁮󠁧󠁿'
    },
    {
      label: 'DFB POKAL',
      slug: 'dfb-pokal',
      type: 'cup',
      country: 'Germany 🇩🇪'
    }
  ];

  const getTeamSlug = (teamName) => {
    return teamName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  };

  const handleLeagueClick = (slug) => {
    navigate(`/league/${slug}`);
    setOpenDropdown(null);
    setMobileMenuOpen(false);
  };

  const handleTeamClick = (teamName) => {
    navigate(`/team/${getTeamSlug(teamName)}`);
    setOpenDropdown(null);
    setMobileMenuOpen(false);
  };

  const toggleDropdown = (label, e) => {
    e.stopPropagation();
    setOpenDropdown(openDropdown === label ? null : label);
  };

  return (
    <header 
      className={`sticky top-0 z-50 transition-all duration-300 ${
        scrolled 
          ? 'bg-gray-900/95 backdrop-blur-lg shadow-lg shadow-blue-500/10' 
          : 'bg-gray-900/80 backdrop-blur-md'
      }`}
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center group cursor-pointer">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full blur-md opacity-50 group-hover:opacity-75 transition-opacity"></div>
              <div className="relative w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-full flex items-center justify-center transform group-hover:scale-110 transition-transform">
                <span className="text-white font-bold text-xl">G</span>
              </div>
            </div>
            <div className="ml-3">
              <div className="font-bold text-xl bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">GOLEVENTS</div>
              <div className="text-xs text-gray-400 tracking-widest font-medium">TRAVEL SPORT FUN</div>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-4">
            {menuStructure.map((item, index) => (
              <div
                key={index}
                className="relative group"
                onMouseEnter={() => item.teams && setOpenDropdown(item.label)}
                onMouseLeave={() => setOpenDropdown(null)}
              >
                {item.type === 'link' ? (
                  <Link
                    to={item.href}
                    className="text-gray-300 hover:text-white font-semibold text-sm transition-all duration-200 relative group/link px-3 py-2"
                  >
                    {item.label}
                    <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 group-hover/link:w-full transition-all duration-300"></span>
                  </Link>
                ) : (
                  <>
                    <button
                      onClick={() => handleLeagueClick(item.slug)}
                      className="text-gray-300 hover:text-white font-semibold text-sm flex items-center gap-1 transition-all duration-200 relative px-3 py-2 group/btn"
                    >
                      {item.label}
                      {item.teams && <ChevronDown className="w-4 h-4" />}
                      <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 group-hover/btn:w-full transition-all duration-300"></span>
                    </button>
                    
                    {/* Desktop Dropdown */}
                    {item.teams && openDropdown === item.label && (
                      <div className="absolute top-full left-0 mt-2 w-64 bg-gray-800/95 backdrop-blur-lg border border-gray-700 rounded-xl shadow-2xl shadow-blue-500/10 py-2 max-h-96 overflow-y-auto">
                        <div className="px-4 py-2 border-b border-gray-700">
                          <div className="text-xs text-gray-500 font-semibold">{item.country}</div>
                          <div className="text-sm text-blue-400 font-bold">All Teams</div>
                        </div>
                        {item.teams.map((team, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleTeamClick(team)}
                            className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700/50 hover:text-white transition-colors flex items-center justify-between group/team"
                          >
                            <span>{team}</span>
                            <ChevronRight className="w-4 h-4 opacity-0 group-hover/team:opacity-100 transform group-hover/team:translate-x-1 transition-all" />
                          </button>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            ))}
            
            <Link
              to="/#about"
              className="text-gray-300 hover:text-white font-semibold text-sm transition-all duration-200 relative group/link px-3 py-2"
            >
              ABOUT US
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 group-hover/link:w-full transition-all duration-300"></span>
            </Link>

            <button className="flex items-center gap-2 text-gray-300 hover:text-white transition-colors">
              <img
                src="https://flagcdn.com/w20/gb.png"
                alt="English"
                className="w-5 h-4 rounded"
              />
              <ChevronDown className="w-4 h-4" />
            </button>
          </nav>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 text-gray-300 hover:text-white transition-colors"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="lg:hidden pb-4 border-t border-gray-800 max-h-96 overflow-y-auto">
            {menuStructure.map((item, index) => (
              <div key={index}>
                {item.type === 'link' ? (
                  <Link
                    to={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className="block py-3 text-gray-300 hover:text-white font-medium text-sm transition-colors"
                  >
                    {item.label}
                  </Link>
                ) : (
                  <>
                    <div className="flex items-center justify-between">
                      <button
                        onClick={() => handleLeagueClick(item.slug)}
                        className="flex-1 text-left py-3 text-gray-300 hover:text-white font-medium text-sm transition-colors"
                      >
                        {item.label}
                      </button>
                      {item.teams && (
                        <button
                          onClick={(e) => toggleDropdown(item.label, e)}
                          className="p-2 text-gray-400 hover:text-white"
                        >
                          <ChevronDown
                            className={`w-4 h-4 transition-transform ${
                              openDropdown === item.label ? 'rotate-180' : ''
                            }`}
                          />
                        </button>
                      )}
                    </div>
                    
                    {/* Mobile Dropdown */}
                    {item.teams && openDropdown === item.label && (
                      <div className="pl-4 pb-2 border-l-2 border-blue-500/30 ml-2">
                        {item.teams.map((team, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleTeamClick(team)}
                            className="block w-full text-left py-2 text-sm text-gray-400 hover:text-blue-400 transition-colors"
                          >
                            {team}
                          </button>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            ))}
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;
