import React, { useState, useEffect } from 'react';
import { eventsAPI, categoriesAPI, searchAPI } from '../services/api';
import Header from '../components/Header';
import HeroSearch from '../components/HeroSearch';
import EventsGrid from '../components/EventsGrid';
import CategoriesSection from '../components/CategoriesSection';
import Footer from '../components/Footer';
import { toast } from 'sonner';
import { useLanguage } from '../contexts/LanguageContext';

const Home = () => {
  const { lang } = useLanguage();
  const [events, setEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchEvents();
    fetchCategories();
  }, [lang]); // Re-fetch when language changes

  // Debounced search effect
  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      if (searchQuery.trim()) {
        handleSearch(searchQuery);
      } else {
        fetchEvents();
      }
    }, 500); // 500ms delay

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  const fetchEvents = async (params = {}) => {
    try {
      setLoading(true);
      const data = await eventsAPI.getAll({ ...params, lang, limit: 50 });
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
      const data = await categoriesAPI.getAll({ lang });
      setCategories(data || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const handleSearch = async (query) => {
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

  const handleSearchChange = (query) => {
    setSearchQuery(query);
  };

  return (
    <>
      <Header />
      <HeroSearch 
        onSearch={handleSearch} 
        onSearchChange={handleSearchChange}
        searchQuery={searchQuery}
      />
      <EventsGrid events={events} loading={loading} />
      <CategoriesSection categories={categories} />
      <Footer />
    </>
  );
};

export default Home;