import React from 'react';
import { Zap } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';

const HeroSearch = () => {
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);

  return (
    <div className="relative py-16 px-4 bg-gradient-to-br from-[#0984E3]/10 via-white to-[#FF6B35]/10">
      <div className="relative container mx-auto max-w-5xl text-center">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-full text-[#0984E3] text-sm font-semibold mb-6 shadow-sm animate-fade-in-up">
          <Zap className="w-4 h-4 text-[#FF6B35]" />
          {t('liveEvents')} • {t('bestPrices')} • {t('instantBooking')}
        </div>

        <h1 className="text-2xl md:text-3xl lg:text-4xl font-black mb-4 animate-fade-in-up" style={{animationDelay: '0.1s'}}>
          <span className="text-[#2D3436]">{t('findYour')} </span>
          <span className="text-[#FF6B35]">{t('perfect')}</span>
          <br />
          <span className="text-[#0984E3]">{t('sportEvent')}</span>
        </h1>
        
        <p className="text-gray-600 text-sm md:text-base mb-6 max-w-2xl mx-auto animate-fade-in-up" style={{animationDelay: '0.2s'}}>
          {t('heroSubtitle')}
        </p>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 max-w-xl mx-auto">
          <div className="bg-white border border-gray-200 rounded-xl p-3 shadow-sm">
            <div className="text-xl font-bold text-[#2D3436] mb-1">500+</div>
            <div className="text-gray-500 text-xs">{t('liveEventsCount')}</div>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-3 shadow-sm">
            <div className="text-xl font-bold text-[#2D3436] mb-1">50k+</div>
            <div className="text-gray-500 text-xs">{t('happyFans')}</div>
          </div>
          <div className="bg-white border border-gray-200 rounded-xl p-3 shadow-sm">
            <div className="text-xl font-bold text-[#2D3436] mb-1">24/7</div>
            <div className="text-gray-500 text-xs">{t('support')}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeroSearch;
