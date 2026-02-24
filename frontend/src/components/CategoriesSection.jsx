import React from 'react';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';

const TRANSLATIONS = {
  it: {
    title: "Squadre",
    country: "Italiane",
    subtitle: "Esplora gli eventi delle squadre più importanti",
    tickets: "Biglietti",
    viewEvents: "Vedi eventi"
  },
  es: {
    title: "Equipos",
    country: "Españoles",
    subtitle: "Explora los eventos de los equipos más importantes",
    tickets: "Entradas",
    viewEvents: "Ver eventos"
  },
  en: {
    title: "UK",
    country: "Teams",
    subtitle: "Explore events from the biggest clubs",
    tickets: "Tickets",
    viewEvents: "View events"
  }
};

const CategoriesSection = ({ categories }) => {
  const { lang } = useLanguage();
  const t = TRANSLATIONS[lang] || TRANSLATIONS.it;
  
  return (
    <section className="py-20 px-4 bg-black relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-black via-gray-900 to-black"></div>
      
      <div className="container mx-auto relative z-10">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            {t.title} <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">{t.country}</span>
          </h2>
          <p className="text-gray-400 text-lg">{t.subtitle}</p>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4">
          {categories.map((category, index) => (
            <Link
              to={`/team/${category.slug}`}
              key={index}
              className="group relative bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 hover:border-blue-500 rounded-xl p-6 text-center cursor-pointer transition-all duration-300 transform hover:-translate-y-2 hover:shadow-2xl hover:shadow-blue-500/20 overflow-hidden"
            >
              {/* Shine effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-blue-500/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
              
              <div className="relative">
                <h3 className="font-bold text-white text-sm mb-2 group-hover:text-blue-400 transition-colors">
                  {t.tickets} {category.name}
                </h3>
                <div className="flex items-center justify-center gap-1 text-blue-400 text-xs font-semibold">
                  <span>{t.viewEvents}</span>
                  <ArrowRight className="w-3 h-3 transform group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
};

export default CategoriesSection;