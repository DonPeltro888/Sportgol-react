import React, { useState, useEffect, useRef } from 'react';
import { Search, X, Loader2, Users, Trophy, MapPin } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';
import { eventsAPI, categoriesAPI } from '../services/api';
import { getTeamLogo } from '../data/teamLogos';

const StickySearch = () => {
  const [query, setQuery] = useState('');
  const [eventResults, setEventResults] = useState([]);
  const [teamResults, setTeamResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);
  const navigate = useNavigate();
  const searchRef = useRef(null);
  const debounceRef = useRef(null);
  const [allTeams, setAllTeams] = useState([]);

  // Load all teams on mount
  useEffect(() => {
    const loadTeams = async () => {
      try {
        const teams = await categoriesAPI.getAll({});
        setAllTeams(teams || []);
      } catch (error) {
        console.error('Error loading teams:', error);
      }
    };
    loadTeams();
  }, []);

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
    setQuery(value);
    
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    if (value.trim().length >= 2) {
      setLoading(true);
      setShowDropdown(true);
      
      debounceRef.current = setTimeout(async () => {
        try {
          const eventsData = await eventsAPI.getAll({ search: value, lang, limit: 4 });
          setEventResults(eventsData.events || []);
          
          const searchLower = value.toLowerCase();
          const matchingTeams = allTeams.filter(team => 
            team.name.toLowerCase().includes(searchLower)
          ).slice(0, 3);
          setTeamResults(matchingTeams);
        } catch (error) {
          console.error('Search error:', error);
          setEventResults([]);
          setTeamResults([]);
        } finally {
          setLoading(false);
        }
      }, 300);
    } else {
      setEventResults([]);
      setTeamResults([]);
      setShowDropdown(false);
      setLoading(false);
    }
  };

  const handleEventClick = (event) => {
    setShowDropdown(false);
    setQuery('');
    navigate(`/event/${event.id || event._id}`);
  };

  const handleTeamClick = (team) => {
    setShowDropdown(false);
    setQuery('');
    navigate(`/team/${team.slug}`);
  };

  const clearSearch = () => {
    setQuery('');
    setEventResults([]);
    setTeamResults([]);
    setShowDropdown(false);
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString(lang === 'it' ? 'it-IT' : lang === 'es' ? 'es-ES' : 'en-GB', {
      day: 'numeric',
      month: 'short'
    });
  };

  const totalResults = teamResults.length + eventResults.length;

  return (
    <div className="sticky top-[64px] z-[1000] bg-white border-b border-gray-200 py-3 px-4 shadow-sm">
      <div ref={searchRef} className="container mx-auto max-w-3xl relative">
        {/* Search Input */}
        <div className="relative flex items-center bg-gray-50 border border-gray-200 rounded-xl overflow-hidden focus-within:border-[#0984E3] transition-colors">
          <Search className="absolute left-4 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder={t('searchPlaceholder')}
            value={query}
            onChange={handleInputChange}
            onFocus={() => query.length >= 2 && setShowDropdown(true)}
            className="flex-1 pl-12 pr-10 py-3 bg-transparent text-[#2D3436] placeholder-gray-400 outline-none text-sm"
            data-testid="sticky-search-input"
          />
          {query && (
            <button
              type="button"
              onClick={clearSearch}
              className="absolute right-3 p-1 text-gray-400 hover:text-[#2D3436] transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Dropdown Results */}
        {showDropdown && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-xl shadow-xl overflow-y-auto max-h-[350px] z-[1001]">
            {loading ? (
              <div className="flex items-center justify-center py-6">
                <Loader2 className="w-5 h-5 text-[#0984E3] animate-spin" />
                <span className="ml-2 text-gray-500 text-sm">{t('loadingEvents')}</span>
              </div>
            ) : totalResults > 0 ? (
              <div>
                {/* Header */}
                <div className="px-3 py-2 bg-gray-50 border-b border-gray-200">
                  <span className="text-xs text-gray-500">{totalResults} {t('resultsFound')}</span>
                </div>

                {/* Teams */}
                {teamResults.length > 0 && (
                  <div>
                    <div className="px-3 py-1.5 bg-[#0984E3]/10 border-b border-gray-200 flex items-center gap-2">
                      <Users className="w-3 h-3 text-[#0984E3]" />
                      <span className="text-xs font-semibold text-[#0984E3]">{t('teams')}</span>
                    </div>
                    <div className="p-1.5">
                      {teamResults.map((team) => {
                        const logo = getTeamLogo(team.name);
                        return (
                          <button
                            key={team.slug}
                            onClick={() => handleTeamClick(team)}
                            className="w-full flex items-center gap-2 px-2 py-1.5 hover:bg-[#0984E3]/10 rounded-lg transition-colors text-left"
                          >
                            {logo ? (
                              <img src={logo} alt={team.name} className="w-6 h-6 object-contain" onError={(e) => e.target.style.display = 'none'} />
                            ) : (
                              <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center">
                                <Users className="w-3 h-3 text-gray-400" />
                              </div>
                            )}
                            <span className="text-sm font-medium text-[#2D3436]">{team.name}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                )}

                {/* Events */}
                {eventResults.length > 0 && (
                  <div>
                    <div className="px-3 py-1.5 bg-[#FF6B35]/10 border-b border-gray-200 flex items-center gap-2">
                      <Trophy className="w-3 h-3 text-[#FF6B35]" />
                      <span className="text-xs font-semibold text-[#FF6B35]">{t('eventsLabel')}</span>
                    </div>
                    {eventResults.map((event) => (
                      <button
                        key={event.id || event._id}
                        onClick={() => handleEventClick(event)}
                        className="w-full px-3 py-2 flex items-center gap-3 hover:bg-[#FF6B35]/10 transition-colors text-left border-b border-gray-100 last:border-b-0"
                      >
                        <div className="flex-shrink-0 w-10 text-center">
                          <div className="text-xs font-bold text-[#FF6B35]">{formatDate(event.date)}</div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-[#2D3436] truncate">{event.title}</div>
                          <div className="flex items-center gap-1 text-xs text-gray-500">
                            <MapPin className="w-3 h-3" />
                            <span className="truncate">{event.location} {event.stadium && `- ${event.stadium}`}</span>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ) : query.length >= 2 ? (
              <div className="py-6 text-center text-gray-500">
                <Search className="w-6 h-6 mx-auto mb-1 opacity-50" />
                <p className="text-sm">{t('noEventsFound')}</p>
              </div>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
};

export default StickySearch;
