import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';

const Breadcrumbs = ({ items }) => {
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);
  
  // Always start with Home
  const breadcrumbItems = [
    { name: t('home'), url: '/' },
    ...items
  ];

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1 text-xs text-gray-400 overflow-x-auto whitespace-nowrap pb-1">
      {breadcrumbItems.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && (
            <ChevronRight className="w-3 h-3 flex-shrink-0 text-gray-500" />
          )}
          {index === 0 ? (
            <Link 
              to={item.url} 
              className="flex items-center gap-1 hover:text-white transition-colors flex-shrink-0"
            >
              <Home className="w-3 h-3" />
              <span className="hidden sm:inline">{item.name}</span>
            </Link>
          ) : index === breadcrumbItems.length - 1 ? (
            <span className="text-gray-300 font-medium truncate max-w-[150px] sm:max-w-none">
              {item.name}
            </span>
          ) : (
            <Link 
              to={item.url} 
              className="hover:text-white transition-colors truncate max-w-[100px] sm:max-w-none"
            >
              {item.name}
            </Link>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

export default Breadcrumbs;
