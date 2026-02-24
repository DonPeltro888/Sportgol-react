import React, { useState, useEffect } from 'react';
import { eventsAPI, categoriesAPI, searchAPI } from '../services/api';
import Header from '../components/Header';
import StickySearch from '../components/StickySearch';
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

  useEffect(() => {
    fetchEvents();
    fetchCategories();
  }, [lang]);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const data = await eventsAPI.getAll({ lang, limit: 50 });
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

  return (
    <>
      <Header />
      <StickySearch />
      <HeroSearch />
      <EventsGrid events={events} loading={loading} />
      <CategoriesSection categories={categories} />
      <Footer />
    </>
  );
};

export default Home;