import React, { useState } from 'react';
import { Search } from 'lucide-react';

const HeroSearch = ({ onSearch }) => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(searchQuery);
    }
  };

  return (
    <div className="relative py-20 px-4 overflow-hidden">
      {/* Gradient Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-300 via-purple-200 to-blue-300"></div>
      
      <div className="relative container mx-auto max-w-4xl text-center">
        <h1 className="text-4xl md:text-5xl font-bold mb-8">
          Event <span className="text-blue-600">Search</span>
        </h1>
        
        <form onSubmit={handleSubmit} className="relative">
          <div className="bg-white rounded-full shadow-lg flex items-center overflow-hidden">
            <input
              type="text"
              placeholder="What are you looking for?"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1 px-6 py-4 text-gray-700 outline-none text-lg"
            />
            <button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 font-semibold transition-colors flex items-center gap-2 rounded-full m-1"
            >
              <Search className="w-5 h-5" />
              SEARCH
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default HeroSearch;
