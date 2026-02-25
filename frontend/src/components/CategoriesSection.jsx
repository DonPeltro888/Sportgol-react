import React from 'react';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';
import { getTeamLogo } from '../data/teamLogos';
import { getTeamUrl } from '../utils/seoHelpers';

const CategoriesSection = ({ categories }) => {
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);
  
  return (
    <section className="py-16 px-4 bg-gray-50 relative overflow-hidden">
      <div className="container mx-auto relative z-10">
        <div className="text-center mb-10">
          <h2 className="text-2xl md:text-3xl font-black text-[#2D3436] mb-3">
            {t('teamsTitle')} <span className="text-[#0984E3]">{t('teamsCountry')}</span>
          </h2>
          <p className="text-gray-500 text-sm md:text-base">{t('teamsSubtitle')}</p>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7 gap-4">
          {categories.map((category, index) => {
            const logo = getTeamLogo(category.name);
            
            return (
              <Link
                to={getTeamUrl(category.slug, lang)}
                key={index}
                className="group relative bg-white border border-gray-200 hover:border-[#0984E3] rounded-xl p-4 text-center cursor-pointer transition-all duration-300 transform hover:-translate-y-2 hover:shadow-lg overflow-hidden"
              >
                <div className="relative flex flex-col items-center">
                  {/* Team Logo */}
                  {logo && (
                    <div className="w-12 h-12 mb-3 flex items-center justify-center">
                      <img 
                        src={logo} 
                        alt={`${t('seoTickets')} ${category.name}`}
                        className="w-full h-full object-contain"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    </div>
                  )}
                  
                  <h3 className="font-bold text-[#2D3436] text-sm mb-2 group-hover:text-[#0984E3] transition-colors">
                    {lang === 'en' ? `${category.name} ${t('tickets')}` : `${t('tickets')} ${category.name}`}
                  </h3>
                  <div className="flex items-center justify-center gap-1 text-[#FF6B35] text-xs font-semibold">
                    <span>{t('viewEvents')}</span>
                    <ArrowRight className="w-3 h-3 transform group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default CategoriesSection;