import React, { useState, useEffect } from 'react';
import './App.css';
import Header from './components/Header';
import HeroSearch from './components/HeroSearch';
import EventsGrid from './components/EventsGrid';
import CategoriesSection from './components/CategoriesSection';
import Footer from './components/Footer';
import { eventsAPI, categoriesAPI, searchAPI } from './services/api';
import { Toaster } from './components/ui/sonner';
import { toast } from 'sonner';

function App() {
  const [events, setEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch initial data
  useEffect(() => {
    fetchEvents();
    fetchCategories();
  }, []);

  const fetchEvents = async (params = {}) => {
    try {
      setLoading(true);
      const data = await eventsAPI.getAll(params);
      setEvents(data.events || []);
    } catch (error) {
      console.error('Error fetching events:', error);
      toast.error('Failed to load events. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const data = await categoriesAPI.getAll();
      setCategories(data || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleSearch = async (query) => {
    setSearchQuery(query);
    
    if (!query.trim()) {
      fetchEvents();
      return;
    }

    try {
      setLoading(true);
      const results = await searchAPI.search(query);
      setEvents(results || []);
      
      if (results.length === 0) {
        toast.error(`No events found for "${query}"`);
      } else {
        toast.success(`Found ${results.length} event(s)`);
      }
    } catch (error) {
      console.error('Error searching:', error);
      toast.error('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <div className="App min-h-screen bg-black">
      <Toaster position="top-right" richColors />
      <Header />
      <HeroSearch onSearch={handleSearch} />
      <EventsGrid events={events} loading={loading} />
      <CategoriesSection categories={categories} />
      <Footer />
    </div>
  );
}

export default App;
