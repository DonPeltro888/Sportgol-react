import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, X, ChevronDown } from 'lucide-react';

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

  const leagues = [
    { label: 'SERIE A', slug: 'serie-a', country: 'Italy' },
    { label: 'PREMIER LEAGUE', slug: 'premier-league', country: 'England' },
    { label: 'LA LIGA', slug: 'la-liga', country: 'Spain' },
    { label: 'BUNDESLIGA', slug: 'bundesliga', country: 'Germany' },
    { label: 'LIGA PORTUGAL', slug: 'liga-portugal', country: 'Portugal' },
    { label: 'CHAMPIONS LEAGUE', slug: 'champions-league', country: 'Europe' },
    { label: 'COPPA ITALIA', slug: 'coppa-italia', country: 'Italy' },
    { label: 'COPA DEL REY', slug: 'copa-del-rey', country: 'Spain' },
    { label: 'FA CUP', slug: 'fa-cup', country: 'England' },
    { label: 'DFB POKAL', slug: 'dfb-pokal', country: 'Germany' },
  ];

  const handleLeagueClick = (slug) => {
    navigate(`/league/${slug}`);
    setOpenDropdown(null);
    setMobileMenuOpen(false);
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
          <nav className="hidden lg:flex items-center gap-6">
            <Link
              to="/"
              className="text-gray-300 hover:text-white font-semibold text-sm transition-all duration-200 relative group"
            >
              EVENTS
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 group-hover:w-full transition-all duration-300"></span>
            </Link>

            {/* Leagues Dropdown */}
            {leagues.map((league) => (
              <div
                key={league.slug}
                className="relative group"
                onMouseEnter={() => setOpenDropdown(league.slug)}
                onMouseLeave={() => setOpenDropdown(null)}
              >
                <button
                  onClick={() => handleLeagueClick(league.slug)}
                  className="text-gray-300 hover:text-white font-semibold text-sm flex items-center gap-1 transition-all duration-200 relative"
                >
                  {league.label}
                  <ChevronDown className="w-4 h-4" />
                  <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 group-hover:w-full transition-all duration-300"></span>
                </button>
              </div>
            ))}

            <Link
              to="/#about"
              className="text-gray-300 hover:text-white font-semibold text-sm transition-all duration-200 relative group"
            >
              ABOUT US
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 group-hover:w-full transition-all duration-300"></span>
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
          <nav className="lg:hidden pb-4 border-t border-gray-800">
            <Link
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              className="block py-3 text-gray-300 hover:text-white font-medium text-sm transition-colors"
            >
              EVENTS
            </Link>
            {leagues.map((league) => (
              <button
                key={league.slug}
                onClick={() => handleLeagueClick(league.slug)}
                className="block w-full text-left py-3 text-gray-300 hover:text-white font-medium text-sm transition-colors"
              >
                {league.label}
              </button>
            ))}
            <Link
              to="/#about"
              onClick={() => setMobileMenuOpen(false)}
              className="block py-3 text-gray-300 hover:text-white font-medium text-sm transition-colors"
            >
              ABOUT US
            </Link>
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;
