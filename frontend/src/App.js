import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import HeroSearch from './components/HeroSearch';
import EventsGrid from './components/EventsGrid';
import CategoriesSection from './components/CategoriesSection';
import Footer from './components/Footer';
import { mockEvents, categories } from './data/mockEvents';
import { Toaster } from './components/ui/sonner';
import { toast } from './hooks/use-toast';

function App() {
  const [filteredEvents, setFilteredEvents] = useState(mockEvents);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query) => {
    setSearchQuery(query);
    
    if (!query.trim()) {
      setFilteredEvents(mockEvents);
      return;
    }

    const filtered = mockEvents.filter((event) => {
      const searchLower = query.toLowerCase();
      return (
        event.title.toLowerCase().includes(searchLower) ||
        event.categories.some((cat) => cat.toLowerCase().includes(searchLower)) ||
        event.location.toLowerCase().includes(searchLower)
      );
    });

    setFilteredEvents(filtered);
    
    if (filtered.length === 0) {
      toast({
        title: "No events found",
        description: `No events match your search for "${query}".`,
      });
    }
  };

  useEffect(() => {
    // Scroll to top on mount
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="App min-h-screen bg-gray-50">
      <Toaster />
      <Header />
      <HeroSearch onSearch={handleSearch} />
      <EventsGrid events={filteredEvents} />
      <CategoriesSection categories={categories} />
      <Footer />
    </div>
  );
}

export default App;
