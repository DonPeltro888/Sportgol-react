import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, X, ChevronDown, ChevronRight, Trophy, Flag } from 'lucide-react';
import LanguageSwitcher from './LanguageSwitcher';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [openDropdown, setOpenDropdown] = useState(null);
  const [desktopMenuOpen, setDesktopMenuOpen] = useState(false);
  const [expandedCategory, setExpandedCategory] = useState(null);
  const desktopMenuRef = useRef(null);
  const navigate = useNavigate();
  const { lang, setLang } = useLanguage();
  
  const t = (key) => getTranslation(lang, key);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close desktop menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (desktopMenuRef.current && !desktopMenuRef.current.contains(event.target)) {
        setDesktopMenuOpen(false);
        setExpandedCategory(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const leagues = [
    {
      label: 'SERIE A',
      slug: 'serie-a',
      country: 'Italy',
      flag: '🇮🇹',
      teams: [
        'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina',
        'Genoa', 'Hellas Verona', 'Inter', 'Juventus', 'Lazio', 'Lecce',
        'Milan', 'Napoli', 'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese'
      ]
    },
    {
      label: 'PREMIER LEAGUE',
      slug: 'premier-league',
      country: 'England',
      flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
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
      country: 'Spain',
      flag: '🇪🇸',
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
      country: 'Germany',
      flag: '🇩🇪',
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
      country: 'Portugal',
      flag: '🇵🇹',
      teams: [
        'Arouca', 'AVS', 'Benfica', 'Boavista', 'Braga', 'Casa Pia',
        'Estoril', 'Farense', 'Famalicão', 'Gil Vicente', 'Moreirense', 'Nacional',
        'Porto', 'Rio Ave', 'Santa Clara', 'Sporting CP', 'Estrela', 'Vitória Guimarães'
      ]
    },
    {
      label: 'LIGUE 1',
      slug: 'ligue-1',
      country: 'France',
      flag: '🇫🇷',
      teams: [
        'PSG', 'Monaco', 'Marseille', 'Lyon', 'Angers', 'Le Havre'
      ]
    },
    {
      label: 'SUPER LIG',
      slug: 'super-lig',
      country: 'Turkey',
      flag: '🇹🇷',
      teams: [
        'Galatasaray', 'Fenerbahçe', 'Beşiktaş', 'Trabzonspor', 'Alanyaspor', 'Antalyaspor', 'Kocaelispor'
      ]
    }
  ];

  const cups = [
    { label: 'CHAMPIONS LEAGUE', slug: 'champions-league', country: 'Europe', flag: '🏆' },
    { label: 'EUROPA LEAGUE', slug: 'europa-league', country: 'Europe', flag: '🏆' },
    { label: 'COPPA ITALIA', slug: 'coppa-italia', country: 'Italy', flag: '🇮🇹' },
    { label: 'COPA DEL REY', slug: 'copa-del-rey', country: 'Spain', flag: '🇪🇸' },
    { label: 'FA CUP', slug: 'fa-cup', country: 'England', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿' },
    { label: 'DFB POKAL', slug: 'dfb-pokal', country: 'Germany', flag: '🇩🇪' }
  ];

  const getTeamSlug = (teamName) => {
    return teamName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  };

  const handleLeagueClick = (slug) => {
    navigate(`/league/${slug}`);
    setDesktopMenuOpen(false);
    setExpandedCategory(null);
    setMobileMenuOpen(false);
    setOpenDropdown(null);
  };

  const handleTeamClick = (teamName) => {
    navigate(`/team/${getTeamSlug(teamName)}`);
    setDesktopMenuOpen(false);
    setExpandedCategory(null);
    setMobileMenuOpen(false);
    setOpenDropdown(null);
  };

  const toggleMobileDropdown = (label, e) => {
    e.stopPropagation();
    setOpenDropdown(openDropdown === label ? null : label);
  };

  const toggleDesktopCategory = (slug) => {
    setExpandedCategory(expandedCategory === slug ? null : slug);
  };

  return (
    <header 
      data-testid="header"
      className={`sticky top-0 z-50 transition-all duration-300 ${
        scrolled 
          ? 'bg-gray-900/95 backdrop-blur-lg shadow-lg shadow-blue-500/10' 
          : 'bg-gray-900/80 backdrop-blur-md'
      }`}
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center group cursor-pointer" data-testid="logo-link">
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
          <nav className="hidden lg:flex items-center gap-2">
            <Link
              to="/"
              data-testid="nav-home"
              className="text-gray-300 hover:text-white font-semibold text-sm transition-all duration-200 relative group/link px-3 py-2"
            >
              {t('home')}
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 group-hover/link:w-full transition-all duration-300"></span>
            </Link>

            {/* All Categories Button */}
            <div ref={desktopMenuRef} className="relative">
              <button
                onClick={() => setDesktopMenuOpen(!desktopMenuOpen)}
                data-testid="categories-menu-btn"
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-sm transition-all duration-200 ${
                  desktopMenuOpen 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-300 hover:text-white hover:bg-gray-800'
                }`}
              >
                <Flag className="w-4 h-4" />
                {t('allCategories')}
                <ChevronDown className={`w-4 h-4 transition-transform ${desktopMenuOpen ? 'rotate-180' : ''}`} />
              </button>

              {/* Mega Menu */}
              {desktopMenuOpen && (
                <div 
                  data-testid="desktop-mega-menu"
                  className="absolute top-full left-0 mt-2 w-[700px] bg-gray-900/98 backdrop-blur-xl border border-gray-700 rounded-2xl shadow-2xl shadow-blue-500/20 overflow-hidden"
                >
                  <div className="grid grid-cols-2 gap-0">
                    {/* Leagues Column */}
                    <div className="border-r border-gray-700">
                      <div className="px-4 py-3 bg-gradient-to-r from-blue-600/20 to-transparent border-b border-gray-700">
                        <h3 className="text-sm font-bold text-blue-400 flex items-center gap-2">
                          <Flag className="w-4 h-4" />
                          {t('leagues')}
                        </h3>
                      </div>
                      <div className="max-h-[400px] overflow-y-auto">
                        {leagues.map((league) => (
                          <div key={league.slug} className="border-b border-gray-800 last:border-b-0">
                            <div className="flex items-center">
                              <button
                                onClick={() => handleLeagueClick(league.slug)}
                                className="flex-1 text-left px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-gray-800/50 transition-colors flex items-center gap-2"
                              >
                                <span className="text-lg">{league.flag}</span>
                                <span className="font-medium">{league.label}</span>
                              </button>
                              <button
                                onClick={() => toggleDesktopCategory(league.slug)}
                                className="p-3 text-gray-400 hover:text-blue-400 hover:bg-gray-800/50 transition-colors"
                                data-testid={`expand-${league.slug}`}
                              >
                                <ChevronRight className={`w-4 h-4 transition-transform ${expandedCategory === league.slug ? 'rotate-90' : ''}`} />
                              </button>
                            </div>
                            
                            {/* Teams Submenu */}
                            {expandedCategory === league.slug && (
                              <div className="bg-gray-800/30 border-t border-gray-800 py-2 px-2 grid grid-cols-2 gap-1">
                                {league.teams.map((team) => (
                                  <button
                                    key={team}
                                    onClick={() => handleTeamClick(team)}
                                    className="text-left px-3 py-2 text-xs text-gray-400 hover:text-white hover:bg-gray-700/50 rounded-md transition-colors truncate"
                                  >
                                    {team}
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Cups Column */}
                    <div>
                      <div className="px-4 py-3 bg-gradient-to-r from-purple-600/20 to-transparent border-b border-gray-700">
                        <h3 className="text-sm font-bold text-purple-400 flex items-center gap-2">
                          <Trophy className="w-4 h-4" />
                          {t('cups')}
                        </h3>
                      </div>
                      <div className="p-2">
                        {cups.map((cup) => (
                          <button
                            key={cup.slug}
                            onClick={() => handleLeagueClick(cup.slug)}
                            className="w-full text-left px-4 py-3 text-sm text-gray-300 hover:text-white hover:bg-gray-800/50 rounded-lg transition-colors flex items-center gap-3"
                          >
                            <span className="text-lg">{cup.flag}</span>
                            <div>
                              <div className="font-medium">{cup.label}</div>
                              <div className="text-xs text-gray-500">{cup.country}</div>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <Link
              to="/#about"
              data-testid="nav-about"
              className="text-gray-300 hover:text-white font-semibold text-sm transition-all duration-200 relative group/link px-3 py-2"
            >
              {t('aboutUs')}
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 group-hover/link:w-full transition-all duration-300"></span>
            </Link>

            <LanguageSwitcher />
          </nav>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            data-testid="mobile-menu-btn"
            className="lg:hidden p-2 text-gray-300 hover:text-white transition-colors"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav data-testid="mobile-menu" className="lg:hidden pb-4 border-t border-gray-800 max-h-[70vh] overflow-y-auto">
            <Link
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              className="block py-3 text-gray-300 hover:text-white font-medium text-sm transition-colors"
            >
              {t('home')}
            </Link>

            {/* Leagues Section */}
            <div className="py-2">
              <div className="text-xs text-blue-400 font-bold uppercase tracking-wider px-1 py-2 flex items-center gap-2">
                <Flag className="w-3 h-3" />
                {t('leagues')}
              </div>
              {leagues.map((league) => (
                <div key={league.slug}>
                  <div className="flex items-center justify-between">
                    <button
                      onClick={() => handleLeagueClick(league.slug)}
                      className="flex-1 text-left py-3 text-gray-300 hover:text-white font-medium text-sm transition-colors flex items-center gap-2"
                    >
                      <span>{league.flag}</span>
                      {league.label}
                    </button>
                    <button
                      onClick={(e) => toggleMobileDropdown(league.slug, e)}
                      className="p-2 text-gray-400 hover:text-white"
                    >
                      <ChevronDown
                        className={`w-4 h-4 transition-transform ${
                          openDropdown === league.slug ? 'rotate-180' : ''
                        }`}
                      />
                    </button>
                  </div>
                  
                  {/* Mobile Teams Dropdown */}
                  {openDropdown === league.slug && (
                    <div className="pl-4 pb-2 border-l-2 border-blue-500/30 ml-2 grid grid-cols-2 gap-1">
                      {league.teams.map((team) => (
                        <button
                          key={team}
                          onClick={() => handleTeamClick(team)}
                          className="text-left py-2 text-xs text-gray-400 hover:text-blue-400 transition-colors truncate"
                        >
                          {team}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {/* Cups Section */}
            <div className="py-2 border-t border-gray-800">
              <div className="text-xs text-purple-400 font-bold uppercase tracking-wider px-1 py-2 flex items-center gap-2">
                <Trophy className="w-3 h-3" />
                {t('cups')}
              </div>
              {cups.map((cup) => (
                <button
                  key={cup.slug}
                  onClick={() => handleLeagueClick(cup.slug)}
                  className="w-full text-left py-3 text-gray-300 hover:text-white font-medium text-sm transition-colors flex items-center gap-2"
                >
                  <span>{cup.flag}</span>
                  {cup.label}
                </button>
              ))}
            </div>

            <Link
              to="/#about"
              onClick={() => setMobileMenuOpen(false)}
              className="block py-3 text-gray-300 hover:text-white font-medium text-sm transition-colors border-t border-gray-800 mt-2"
            >
              ABOUT US
            </Link>

            {/* Language Switcher Mobile */}
            <div className="py-3 border-t border-gray-800 mt-2">
              <div className="text-xs text-gray-500 font-bold uppercase tracking-wider px-1 py-2">
                Language
              </div>
              <div className="flex gap-2">
                {['it', 'es', 'en'].map((l) => {
                  const flagData = { it: { flag: '🇮🇹', label: 'Italiano' }, es: { flag: '🇪🇸', label: 'Español' }, en: { flag: '🇬🇧', label: 'English' } };
                  return (
                    <button
                      key={l}
                      onClick={() => {
                        const event = new CustomEvent('changeLanguage', { detail: l });
                        window.dispatchEvent(event);
                        setMobileMenuOpen(false);
                      }}
                      className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg bg-gray-800 hover:bg-blue-600 text-gray-300 hover:text-white transition-colors"
                    >
                      <span className="text-lg">{flagData[l].flag}</span>
                      <span className="text-xs font-medium">{flagData[l].label}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;
