import React, { useState, useEffect, useRef } from 'react';
import { Search, TrendingUp, Zap, Calendar, MapPin, Loader2, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';
import { eventsAPI } from '../services/api';

const HeroSearch = ({ onSearch, onSearchChange, searchQuery }) => {
  const [localQuery, setLocalQuery] = useState(searchQuery || '');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);
  const navigate = useNavigate();
  const searchRef = useRef(null);
  const debounceRef = useRef(null);

  useEffect(() => {
    setLocalQuery(searchQuery || '');
  }, [searchQuery]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // AJAX search with debounce
  const handleInputChange = (e) => {
    const value = e.target.value;
    setLocalQuery(value);
    
    // Clear previous debounce
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    if (value.trim().length >= 2) {
      setLoading(true);
      setShowDropdown(true);
      
      // Debounce API call
      debounceRef.current = setTimeout(async () => {
        try {
          const data = await eventsAPI.getAll({ search: value, lang, limit: 8 });
          setResults(data.events || []);
        } catch (error) {
          console.error('Search error:', error);
          setResults([]);
        } finally {
          setLoading(false);
        }
      }, 300);
    } else {
      setResults([]);
      setShowDropdown(false);
      setLoading(false);
    }

    if (onSearchChange) {
      onSearchChange(value);
    }
  };

  const handleResultClick = (event) => {
    setShowDropdown(false);
    setLocalQuery('');
    navigate(`/event/${event.id || event._id}`);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setShowDropdown(false);
    if (onSearch) {
      onSearch(localQuery);
    }
  };

  const clearSearch = () => {
    setLocalQuery('');
    setResults([]);
    setShowDropdown(false);
    if (onSearchChange) {
      onSearchChange('');
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(lang === 'it' ? 'it-IT' : lang === 'es' ? 'es-ES' : 'en-GB', {
      day: 'numeric',
      month: 'short'
    });
  };

  return (
    <div className="relative py-24 px-4 overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900 via-purple-900 to-gray-900"></div>
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-20 left-20 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl animate-float"></div>
          <div className="absolute top-40 right-20 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl animate-float" style={{animationDelay: '1s'}}></div>
          <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl animate-float" style={{animationDelay: '2s'}}></div>
        </div>
        {/* Grid pattern */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAxMCAwIEwgMCAwIDAgMTAiIGZpbGw9Im5vbmUiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMC41IiBvcGFjaXR5PSIwLjEiLz48L3BhdHRlcm4+PC9kZWZzPjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjZ3JpZCkiLz48L3N2Zz4=')] opacity-20"></div>
      </div>
      
      <div className="relative container mx-auto max-w-5xl text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-white text-sm font-semibold mb-6 animate-fade-in-up">
          <Zap className="w-4 h-4 text-yellow-400" />
          {t('liveEvents')} • {t('bestPrices')} • {t('instantBooking')}
        </div>

        <h1 className="text-5xl md:text-7xl font-black mb-6 animate-fade-in-up" style={{animationDelay: '0.1s'}}>
          <span className="text-white">{t('findYour')} </span>
          <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">{t('perfect')}</span>
          <br />
          <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">{t('sportEvent')}</span>
        </h1>
        
        <p className="text-gray-300 text-lg md:text-xl mb-10 max-w-2xl mx-auto animate-fade-in-up" style={{animationDelay: '0.2s'}}>
          {t('heroSubtitle')}
        </p>
        
        {/* Search with AJAX dropdown */}
        <div ref={searchRef} className="relative animate-fade-in-up" style={{animationDelay: '0.3s'}}>
          <form onSubmit={handleSubmit}>
            <div className="relative bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl shadow-2xl flex items-center overflow-hidden group hover:shadow-blue-500/20 transition-all duration-300">
              <Search className="absolute left-6 w-6 h-6 text-gray-400" />
              <input
                type="text"
                placeholder={t('searchPlaceholder')}
                value={localQuery}
                onChange={handleInputChange}
                onFocus={() => localQuery.length >= 2 && setShowDropdown(true)}
                className="flex-1 pl-16 pr-12 py-5 bg-transparent text-white placeholder-gray-400 outline-none text-lg"
                data-testid="search-input"
              />
              {localQuery && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="absolute right-36 p-2 text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
              <button
                type="submit"
                className="relative bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-10 py-5 font-bold transition-all duration-300 flex items-center gap-3 m-1.5 rounded-xl overflow-hidden group"
                data-testid="search-btn"
              >
                <span className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></span>
                <span className="relative">{t('search')}</span>
                <TrendingUp className="relative w-5 h-5" />
              </button>
            </div>
          </form>

          {/* AJAX Results Dropdown */}
          {showDropdown && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-gray-900/95 backdrop-blur-xl border border-gray-700 rounded-xl shadow-2xl overflow-hidden z-50 max-h-[400px] overflow-y-auto">
              {loading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
                  <span className="ml-3 text-gray-400">{t('loadingEvents')}</span>
                </div>
              ) : results.length > 0 ? (
                <div>
                  <div className="px-4 py-2 bg-gray-800/50 border-b border-gray-700">
                    <span className="text-xs text-gray-400 font-medium">
                      {results.length} {t('events')} {lang === 'it' ? 'trovati' : lang === 'es' ? 'encontrados' : 'found'}
                    </span>
                  </div>
                  {results.map((event) => (
                    <button
                      key={event.id || event._id}
                      onClick={() => handleResultClick(event)}
                      className="w-full px-4 py-3 flex items-center gap-4 hover:bg-blue-600/20 transition-colors text-left border-b border-gray-800 last:border-b-0"
                      data-testid={`search-result-${event.id || event._id}`}
                    >
                      {/* Date */}
                      <div className="flex-shrink-0 w-14 text-center">
                        <div className="text-lg font-bold text-blue-400">
                          {formatDate(event.date)}
                        </div>
                      </div>
                      
                      {/* Event Info */}
                      <div className="flex-1 min-w-0">
                        <div className="font-semibold text-white truncate">
                          {event.title}
                        </div>
                        <div className="flex items-center gap-3 text-sm text-gray-400 mt-1">
                          <span className="flex items-center gap-1">
                            <MapPin className="w-3 h-3" />
                            {event.location}
                          </span>
                          {event.stadium && (
                            <span className="truncate">{event.stadium}</span>
                          )}
                        </div>
                      </div>
                      
                      {/* Price */}
                      <div className="flex-shrink-0 text-right">
                        <div className="text-green-400 font-bold">
                          €{event.price || event.minPrice || '25'}+
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              ) : localQuery.length >= 2 ? (
                <div className="py-8 text-center text-gray-400">
                  <Search className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>{t('noEventsFound')}</p>
                </div>
              ) : null}
            </div>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-6 mt-16 max-w-3xl mx-auto">
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
            <div className="text-3xl font-bold text-white mb-1">500+</div>
            <div className="text-gray-400 text-sm">{t('liveEventsCount')}</div>
          </div>
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
            <div className="text-3xl font-bold text-white mb-1">50k+</div>
            <div className="text-gray-400 text-sm">{t('happyFans')}</div>
          </div>
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
            <div className="text-3xl font-bold text-white mb-1">24/7</div>
            <div className="text-gray-400 text-sm">{t('support')}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroSearch;
