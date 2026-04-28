import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Home, Search, ArrowLeft } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import SEOHead from '../components/SEOHead';
import { useLanguage } from '../contexts/LanguageContext';

const NotFound = () => {
  const navigate = useNavigate();
  const { lang } = useLanguage();

  const messages = {
    it: {
      code: '404',
      title: 'Pagina non trovata',
      subtitle: 'Sembra che la pagina che stai cercando sia fuori gioco!',
      home: 'Torna alla Home',
      back: 'Indietro',
      explore: 'Esplora gli eventi',
    },
    es: {
      code: '404',
      title: 'Página no encontrada',
      subtitle: '¡Parece que la página que buscas está fuera de juego!',
      home: 'Volver al inicio',
      back: 'Atrás',
      explore: 'Explorar eventos',
    },
    en: {
      code: '404',
      title: 'Page not found',
      subtitle: 'Looks like the page you are looking for is offside!',
      home: 'Back to Home',
      back: 'Go back',
      explore: 'Explore events',
    },
  };

  const t = messages[lang] || messages.it;

  return (
    <div className="min-h-screen bg-white flex flex-col" data-testid="not-found-page">
      <SEOHead
        title="404 - Page Not Found | GOLEVENTS"
        description="La pagina richiesta non esiste."
      />
      <Header />

      <main className="flex-1 flex items-center justify-center px-4 py-16">
        <div className="max-w-2xl w-full text-center">
          {/* Animated soccer ball */}
          <div className="relative mx-auto mb-8 w-32 h-32">
            <div className="absolute inset-0 bg-gradient-to-br from-[#FF6B35] to-[#0984E3] rounded-full opacity-20 blur-3xl"></div>
            <svg
              className="relative w-full h-full animate-bounce-slow"
              viewBox="0 0 100 100"
              xmlns="http://www.w3.org/2000/svg"
            >
              <circle cx="50" cy="50" r="48" fill="white" stroke="#2D3436" strokeWidth="2" />
              <polygon points="50,20 60,30 56,42 44,42 40,30" fill="#2D3436" />
              <polygon points="32,40 42,40 38,52 28,50 26,42" fill="#2D3436" />
              <polygon points="68,40 72,42 74,50 62,52 58,40" fill="#2D3436" />
              <polygon points="40,55 48,55 50,65 44,72 36,68" fill="#2D3436" />
              <polygon points="60,55 64,68 56,72 50,65 52,55" fill="#2D3436" />
            </svg>
          </div>

          {/* 404 code */}
          <h1 className="text-7xl md:text-9xl font-black bg-gradient-to-r from-[#FF6B35] to-[#0984E3] bg-clip-text text-transparent leading-none">
            {t.code}
          </h1>

          {/* Title */}
          <h2 className="text-2xl md:text-3xl font-bold text-[#2D3436] mt-4">
            {t.title}
          </h2>
          <p className="text-gray-500 mt-2 text-base md:text-lg">
            {t.subtitle}
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center mt-8">
            <Link
              to="/"
              data-testid="not-found-home-btn"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-[#0984E3] hover:bg-[#0784c3] text-white font-bold rounded-lg transition-colors"
            >
              <Home className="w-5 h-5" />
              {t.home}
            </Link>
            <button
              onClick={() => navigate(-1)}
              data-testid="not-found-back-btn"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-gray-300 hover:border-[#0984E3] text-[#2D3436] hover:text-[#0984E3] font-bold rounded-lg transition-all"
            >
              <ArrowLeft className="w-5 h-5" />
              {t.back}
            </button>
            <Link
              to="/"
              className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-[#FF6B35] text-[#FF6B35] hover:bg-[#FF6B35] hover:text-white font-bold rounded-lg transition-all"
            >
              <Search className="w-5 h-5" />
              {t.explore}
            </Link>
          </div>
        </div>
      </main>

      <Footer />

      <style>{`
        @keyframes bounce-slow {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-15px); }
        }
        .animate-bounce-slow {
          animation: bounce-slow 2.2s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};

export default NotFound;
