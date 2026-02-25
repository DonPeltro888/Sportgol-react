import React, { useState, useEffect } from 'react';
import { eventsAPI, categoriesAPI, searchAPI } from '../services/api';
import Header from '../components/Header';
import StickySearch from '../components/StickySearch';
import HeroSearch from '../components/HeroSearch';
import EventsGrid from '../components/EventsGrid';
import CategoriesSection from '../components/CategoriesSection';
import Footer from '../components/Footer';
import SEOHead from '../components/SEOHead';
import { OrganizationSchema } from '../components/SchemaOrg';
import { toast } from 'sonner';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';
import { getSeoTitle, getSeoDescription } from '../utils/seoHelpers';

const Home = () => {
  const { lang } = useLanguage();
  const [events, setEvents] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const t = (key) => getTranslation(lang, key);

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

  const seoTitle = getSeoTitle('home', '', lang);
  const seoDescription = getSeoDescription('home', '', lang);
  const canonicalUrl = window.location.origin;

  return (
    <>
      <SEOHead 
        title={seoTitle}
        description={seoDescription}
        canonicalUrl={canonicalUrl}
        ogImage="https://images.unsplash.com/photo-1574629810360-7efbbe195018"
      />
      
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