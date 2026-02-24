import React, { useState, useEffect } from 'react';
import { Search, TrendingUp, Zap } from 'lucide-react';

const HeroSearch = ({ onSearch, onSearchChange, searchQuery }) => {
  const [localQuery, setLocalQuery] = useState(searchQuery || '');

  useEffect(() => {
    setLocalQuery(searchQuery || '');
  }, [searchQuery]);

  const handleInputChange = (e) => {
    const value = e.target.value;
    setLocalQuery(value);
    if (onSearchChange) {
      onSearchChange(value);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(localQuery);
    }
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
          Live Events • Best Prices • Instant Booking
        </div>

        <h1 className="text-5xl md:text-7xl font-black mb-6 animate-fade-in-up" style={{animationDelay: '0.1s'}}>
          <span className="text-white">Find Your </span>
          <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">Perfect</span>
          <br />
          <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">Sport Event</span>
        </h1>
        
        <p className="text-gray-300 text-lg md:text-xl mb-10 max-w-2xl mx-auto animate-fade-in-up" style={{animationDelay: '0.2s'}}>
          Discover and book tickets for the biggest sporting events worldwide. From Serie A to Champions League.
        </p>
        
        <form onSubmit={handleSubmit} className="relative animate-fade-in-up" style={{animationDelay: '0.3s'}}>
          <div className="relative bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl shadow-2xl flex items-center overflow-hidden group hover:shadow-blue-500/20 transition-all duration-300">
            <Search className="absolute left-6 w-6 h-6 text-gray-400" />
            <input
              type="text"
              placeholder="Search for teams, leagues, or events..."
              value={localQuery}
              onChange={handleInputChange}
              className="flex-1 pl-16 pr-6 py-5 bg-transparent text-white placeholder-gray-400 outline-none text-lg"
            />
            <button
              type="submit"
              className="relative bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white px-10 py-5 font-bold transition-all duration-300 flex items-center gap-3 m-1.5 rounded-xl overflow-hidden group"
            >
              <span className="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></span>
              <span className="relative">SEARCH</span>
              <TrendingUp className="relative w-5 h-5" />
            </button>
          </div>
          {localQuery && (
            <div className="mt-3 text-sm text-gray-300 animate-fade-in-up">
              Searching for: <span className="text-blue-400 font-semibold">{localQuery}</span>
            </div>
          )}
        </form>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-6 mt-16 max-w-3xl mx-auto">
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
            <div className="text-3xl font-bold text-white mb-1">500+</div>
            <div className="text-gray-400 text-sm">Live Events</div>
          </div>
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
            <div className="text-3xl font-bold text-white mb-1">50k+</div>
            <div className="text-gray-400 text-sm">Happy Fans</div>
          </div>
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4">
            <div className="text-3xl font-bold text-white mb-1">24/7</div>
            <div className="text-gray-400 text-sm">Support</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroSearch;
