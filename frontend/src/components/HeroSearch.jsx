import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';

const HeroSearch = () => {
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);

  return (
    <div className="relative py-8 px-4 bg-gradient-to-br from-[#0984E3]/10 via-white to-[#FF6B35]/10">
      {/* Empty hero section - can be used for promotions or left minimal */}
    </div>
  );
};

export default HeroSearch;
