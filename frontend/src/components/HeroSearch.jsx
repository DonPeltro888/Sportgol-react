import React from 'react';
import { Zap } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';

const HeroSearch = () => {
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);

  return (
    <div className="relative py-16 px-4">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900 via-purple-900 to-gray-900"></div>
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-20 left-20 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl animate-float"></div>
          <div className="absolute top-40 right-20 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl animate-float" style={{animationDelay: '1s'}}></div>
          <div className="absolute bottom-20 left-1/2 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl animate-float" style={{animationDelay: '2s'}}></div>
        </div>
      </div>
      
      <div className="relative container mx-auto max-w-5xl text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full text-white text-sm font-semibold mb-6 animate-fade-in-up">
          <Zap className="w-4 h-4 text-yellow-400" />
          {t('liveEvents')} • {t('bestPrices')} • {t('instantBooking')}
        </div>

        <h1 className="text-2xl md:text-3xl lg:text-4xl font-black mb-4 animate-fade-in-up" style={{animationDelay: '0.1s'}}>
          <span className="text-white">{t('findYour')} </span>
          <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">{t('perfect')}</span>
          <br />
          <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">{t('sportEvent')}</span>
        </h1>
        
        <p className="text-gray-300 text-sm md:text-base mb-6 max-w-2xl mx-auto animate-fade-in-up" style={{animationDelay: '0.2s'}}>
          {t('heroSubtitle')}
        </p>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 max-w-xl mx-auto">
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-3">
            <div className="text-xl font-bold text-white mb-1">500+</div>
            <div className="text-gray-400 text-xs">{t('liveEventsCount')}</div>
          </div>
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-3">
            <div className="text-xl font-bold text-white mb-1">50k+</div>
            <div className="text-gray-400 text-xs">{t('happyFans')}</div>
          </div>
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-3">
            <div className="text-xl font-bold text-white mb-1">24/7</div>
            <div className="text-gray-400 text-xs">{t('support')}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroSearch;
