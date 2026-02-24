// SEO Helpers for URL generation and meta tags

import { getTranslation } from '../translations';

// Get URL suffix for English (tickets goes after the name)
// IT: /biglietti/inter (prefix)
// EN: /inter/tickets (suffix)
// ES: /entradas/inter (prefix)

// Generate team URL with translated structure
export const getTeamUrl = (slug, lang) => {
  const cleanSlug = slug.toLowerCase().replace(/\s+/g, '-');
  
  if (lang === 'en') {
    // English: name first, then tickets -> /inter/tickets
    return `/${cleanSlug}/tickets`;
  } else if (lang === 'es') {
    // Spanish: entradas first -> /entradas/inter
    return `/entradas/${cleanSlug}`;
  } else {
    // Italian: biglietti first -> /biglietti/inter
    return `/biglietti/${cleanSlug}`;
  }
};

// Generate league URL with translated structure
export const getLeagueUrl = (league, lang) => {
  const cleanLeague = league.toLowerCase().replace(/\s+/g, '-');
  
  if (lang === 'en') {
    // English: name first -> /serie-a/tickets
    return `/${cleanLeague}/tickets`;
  } else if (lang === 'es') {
    // Spanish: entradas-liga first -> /entradas-liga/serie-a
    return `/entradas-liga/${cleanLeague}`;
  } else {
    // Italian: biglietti-campionato first -> /biglietti-campionato/serie-a
    return `/biglietti-campionato/${cleanLeague}`;
  }
};

// Generate canonical URL
export const getCanonicalUrl = (baseUrl, path, lang) => {
  return `${baseUrl}${path}`;
};

// Generate hreflang URLs for a page
export const getHreflangUrls = (baseUrl, pageType, slug) => {
  const languages = ['it', 'es', 'en'];
  return languages.map(lang => ({
    lang,
    url: pageType === 'team' 
      ? `${baseUrl}${getTeamUrl(slug, lang)}`
      : pageType === 'league'
        ? `${baseUrl}${getLeagueUrl(slug, lang)}`
        : `${baseUrl}/?lang=${lang}`
  }));
};

// Get SEO title based on page type and language
export const getSeoTitle = (pageType, name, lang) => {
  const t = (key) => getTranslation(lang, key);
  const ticketWord = t('seoTickets');
  
  switch(pageType) {
    case 'team':
      // Format: "Biglietti Inter" (IT) / "Inter Tickets" (EN) / "Entradas Inter" (ES)
      return lang === 'en' 
        ? `${name} ${ticketWord} | GOLEVENTS`
        : `${ticketWord} ${name} | GOLEVENTS`;
    case 'league':
      return lang === 'en'
        ? `${name} ${ticketWord} | GOLEVENTS`
        : `${ticketWord} ${name} | GOLEVENTS`;
    case 'event':
      return lang === 'en'
        ? `${name} ${ticketWord} | GOLEVENTS`
        : `${ticketWord} ${name} | GOLEVENTS`;
    case 'home':
      return t('seoSiteTitle');
    default:
      return `${ticketWord} ${name} | GOLEVENTS`;
  }
};

// Get SEO description based on page type and language
export const getSeoDescription = (pageType, name, lang, extra = {}) => {
  const t = (key) => getTranslation(lang, key);
  
  switch(pageType) {
    case 'team':
      return `${t('seoBuy')} ${name}. ${t('seoAllMatches')} ${t('seoHomeAway')}.`;
    case 'league':
      const teamCount = extra.teamCount || '';
      return `${t('seoBuy')} ${name}. ${teamCount ? teamCount + ' ' : ''}${t('seoLeagueTeams')}.`;
    case 'event':
      const date = extra.date || '';
      const location = extra.location || '';
      return `${t('seoBuy')} ${name}. ${date}${location ? ' - ' + location : ''}.`;
    case 'home':
      return t('seoSiteDescription');
    default:
      return t('seoSiteDescription');
  }
};

// Extract slug from URL path (handles both old and new URL formats)
export const extractSlugFromPath = (pathname) => {
  // Match patterns like /biglietti-inter, /tickets-inter, /entradas-inter
  const match = pathname.match(/^\/(biglietti|tickets|entradas)-(.+)$/);
  if (match) {
    return match[2];
  }
  // Fallback for old format /team/inter or /league/serie-a
  const parts = pathname.split('/');
  return parts[parts.length - 1];
};
