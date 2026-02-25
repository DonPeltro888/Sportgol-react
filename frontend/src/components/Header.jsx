import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Menu, X, ChevronDown, ChevronRight, Trophy, Flag } from 'lucide-react';
import LanguageSwitcher from './LanguageSwitcher';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';
import { getTeamUrl, getLeagueUrl } from '../utils/seoHelpers';
import { getLeagueLogo } from '../data/teamLogos';

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
      labelKey: 'serieA',
      slug: 'serie-a',
      countryKey: 'italy',
      flag: '🇮🇹',
      teams: [
        'Atalanta', 'Bologna', 'Cagliari', 'Como', 'Cremonese', 'Fiorentina',
        'Genoa', 'Hellas Verona', 'Inter', 'Juventus', 'Lazio', 'Lecce',
        'Milan', 'Napoli', 'Parma', 'Pisa', 'Roma', 'Sassuolo', 'Torino', 'Udinese'
      ]
    },
    {
      labelKey: 'premierLeague',
      slug: 'premier-league',
      countryKey: 'england',
      flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
      teams: [
        'Arsenal', 'Aston Villa', 'Bournemouth', 'Brentford', 'Brighton', 'Burnley',
        'Chelsea', 'Crystal Palace', 'Everton', 'Fulham', 'Leeds United', 'Liverpool',
        'Manchester City', 'Manchester United', 'Newcastle United', 'Nottingham Forest',
        'Sunderland', 'Tottenham', 'West Ham', 'Wolves'
      ]
    },
    {
      labelKey: 'laLiga',
      slug: 'la-liga',
      countryKey: 'spain',
      flag: '🇪🇸',
      teams: [
        'Alavés', 'Athletic Bilbao', 'Atlético Madrid', 'Barcelona', 'Betis', 'Celta Vigo',
        'Elche', 'Espanyol', 'Getafe', 'Girona', 'Levante', 'Mallorca',
        'Osasuna', 'Oviedo', 'Rayo Vallecano', 'Real Madrid', 'Real Sociedad', 'Sevilla',
        'Valencia', 'Villarreal'
      ]
    },
    {
      labelKey: 'bundesliga',
      slug: 'bundesliga',
      countryKey: 'germany',
      flag: '🇩🇪',
      teams: [
        'Augsburg', 'Bayern Munich', 'Borussia Dortmund', 'Borussia Mönchengladbach',
        'Eintracht Frankfurt', 'Freiburg', 'Hamburger SV', 'Heidenheim',
        'Hoffenheim', 'Köln', 'Leverkusen', 'Mainz', 'RB Leipzig', 'St. Pauli',
        'Stuttgart', 'Union Berlin', 'Werder Bremen', 'Wolfsburg'
      ]
    },
    {
      labelKey: 'ligaPortugal',
      slug: 'liga-portugal',
      countryKey: 'portugal',
      flag: '🇵🇹',
      teams: [
        'Arouca', 'AVS', 'Benfica', 'Boavista', 'Braga', 'Casa Pia',
        'Estoril', 'Farense', 'Famalicão', 'Gil Vicente', 'Moreirense', 'Nacional',
        'Porto', 'Rio Ave', 'Santa Clara', 'Sporting CP', 'Estrela', 'Vitória Guimarães'
      ]
    },
    {
      labelKey: 'ligue1',
      slug: 'ligue-1',
      countryKey: 'france',
      flag: '🇫🇷',
      teams: [
        'PSG', 'Monaco', 'Marseille', 'Lyon', 'Angers', 'Le Havre'
      ]
    },
    {
      labelKey: 'superLig',
      slug: 'super-lig',
      countryKey: 'turkey',
      flag: '🇹🇷',
      teams: [
        'Galatasaray', 'Fenerbahçe', 'Beşiktaş', 'Trabzonspor', 'Alanyaspor', 'Antalyaspor', 'Kocaelispor'
      ]
    }
  ];

  const cups = [
    { labelKey: 'championsLeague', slug: 'champions-league', countryKey: 'europe', flag: '🏆' },
    { labelKey: 'europaLeague', slug: 'europa-league', countryKey: 'europe', flag: '🏆' },
    { labelKey: 'coppaItalia', slug: 'coppa-italia', countryKey: 'italy', flag: '🇮🇹' },
    { labelKey: 'copaDelRey', slug: 'copa-del-rey', countryKey: 'spain', flag: '🇪🇸' },
    { labelKey: 'faCup', slug: 'fa-cup', countryKey: 'england', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿' },
    { labelKey: 'dfbPokal', slug: 'dfb-pokal', countryKey: 'germany', flag: '🇩🇪' }
  ];

  const getTeamSlug = (teamName) => {
    return teamName.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  };

  const handleLeagueClick = (slug) => {
    navigate(getLeagueUrl(slug, lang));
    setDesktopMenuOpen(false);
    setExpandedCategory(null);
    setMobileMenuOpen(false);
    setOpenDropdown(null);
  };

  const handleTeamClick = (teamName) => {
    navigate(getTeamUrl(getTeamSlug(teamName), lang));
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
      className={`sticky top-0 z-[1100] transition-all duration-300 ${
        scrolled 
          ? 'bg-[#2D3436] shadow-lg' 
          : 'bg-[#2D3436]'
      }`}
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center group cursor-pointer" data-testid="logo-link">
            <div className="relative">
              <div className="relative w-12 h-12 bg-gradient-to-br from-[#FF6B35] to-[#0984E3] rounded-full flex items-center justify-center transform group-hover:scale-110 transition-transform">
                <span className="text-white font-bold text-xl">G</span>
              </div>
            </div>
            <div className="ml-3">
              <div className="font-bold text-xl text-white">GOLEVENTS</div>
              <div className="text-xs text-gray-300 tracking-widest font-medium">TRAVEL SPORT FUN</div>
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
                    ? 'bg-[#FF6B35] text-white' 
                    : 'text-gray-300 hover:text-white hover:bg-gray-700'
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
                  className="absolute top-full left-0 mt-2 w-[700px] bg-white border border-gray-200 rounded-2xl shadow-2xl overflow-hidden"
                >
                  <div className="grid grid-cols-2 gap-0">
                    {/* Leagues Column */}
                    <div className="border-r border-gray-200">
                      <div className="px-4 py-3 bg-[#0984E3] border-b border-gray-200">
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                          <Flag className="w-4 h-4" />
                          {t('leagues')}
                        </h3>
                      </div>
                      <div className="max-h-[400px] overflow-y-auto">
                        {leagues.map((league) => (
                          <div key={league.slug} className="border-b border-gray-100 last:border-b-0">
                            <div className="flex items-center">
                              <button
                                onClick={() => handleLeagueClick(league.slug)}
                                className="flex-1 text-left px-4 py-3 text-sm text-gray-700 hover:text-[#FF6B35] hover:bg-gray-50 transition-colors flex items-center gap-2"
                              >
                                {getLeagueLogo(league.slug) ? (
                                  <img 
                                    src={getLeagueLogo(league.slug)} 
                                    alt={t(league.labelKey)}
                                    className="w-6 h-6 object-contain"
                                  />
                                ) : (
                                  <span className="text-lg">{league.flag}</span>
                                )}
                                <span className="font-medium">{t(league.labelKey)}</span>
                              </button>
                              <button
                                onClick={() => toggleDesktopCategory(league.slug)}
                                className="p-3 text-gray-400 hover:text-[#0984E3] hover:bg-gray-50 transition-colors"
                                data-testid={`expand-${league.slug}`}
                              >
                                <ChevronRight className={`w-4 h-4 transition-transform ${expandedCategory === league.slug ? 'rotate-90' : ''}`} />
                              </button>
                            </div>
                            
                            {/* Teams Submenu */}
                            {expandedCategory === league.slug && (
                              <div className="bg-gray-50 border-t border-gray-100 py-2 px-2 grid grid-cols-2 gap-1">
                                {league.teams.map((team) => (
                                  <button
                                    key={team}
                                    onClick={() => handleTeamClick(team)}
                                    className="text-left px-3 py-2 text-xs text-gray-600 hover:text-[#FF6B35] hover:bg-gray-100 rounded-md transition-colors truncate"
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
                      <div className="px-4 py-3 bg-[#FF6B35] border-b border-gray-200">
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                          <Trophy className="w-4 h-4" />
                          {t('cups')}
                        </h3>
                      </div>
                      <div className="p-2">
                        {cups.map((cup) => (
                          <button
                            key={cup.slug}
                            onClick={() => handleLeagueClick(cup.slug)}
                            className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:text-[#FF6B35] hover:bg-gray-50 rounded-lg transition-colors flex items-center gap-3"
                          >
                            {getLeagueLogo(cup.slug) ? (
                              <img 
                                src={getLeagueLogo(cup.slug)} 
                                alt={t(cup.labelKey)}
                                className="w-6 h-6 object-contain"
                              />
                            ) : (
                              <span className="text-lg">{cup.flag}</span>
                            )}
                            <div>
                              <div className="font-medium">{t(cup.labelKey)}</div>
                              <div className="text-xs text-gray-500">{t(cup.countryKey)}</div>
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
              <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-[#FF6B35] group-hover/link:w-full transition-all duration-300"></span>
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
                      {t(league.labelKey)}
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
                  {t(cup.labelKey)}
                </button>
              ))}
            </div>

            <Link
              to="/#about"
              onClick={() => setMobileMenuOpen(false)}
              className="block py-3 text-gray-300 hover:text-white font-medium text-sm transition-colors border-t border-gray-800 mt-2"
            >
              {t('aboutUs')}
            </Link>

            {/* Language Switcher Mobile */}
            <div className="py-3 border-t border-gray-800 mt-2">
              <div className="text-xs text-gray-500 font-bold uppercase tracking-wider px-1 py-2">
                {t('language')}
              </div>
              <div className="flex gap-2">
                {['it', 'es', 'en'].map((l) => {
                  const flagData = { it: { flag: '🇮🇹', label: 'Italiano' }, es: { flag: '🇪🇸', label: 'Español' }, en: { flag: '🇬🇧', label: 'English' } };
                  return (
                    <button
                      key={l}
                      onClick={() => {
                        setLang(l);
                        setMobileMenuOpen(false);
                      }}
                      className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-lg transition-colors ${
                        lang === l 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white'
                      }`}
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
