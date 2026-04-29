import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, MapPin } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

// City name translations
const CITY_TRANSLATIONS = {
  // Italian cities
  "Milan": { it: "Milano", es: "Milán", en: "Milan" },
  "Rome": { it: "Roma", es: "Roma", en: "Rome" },
  "Turin": { it: "Torino", es: "Turín", en: "Turin" },
  "Naples": { it: "Napoli", es: "Nápoles", en: "Naples" },
  "Florence": { it: "Firenze", es: "Florencia", en: "Florence" },
  "Genoa": { it: "Genova", es: "Génova", en: "Genoa" },
  "Venice": { it: "Venezia", es: "Venecia", en: "Venice" },
  
  // Spanish cities
  "Barcelona": { it: "Barcellona", es: "Barcelona", en: "Barcelona" },
  "Madrid": { it: "Madrid", es: "Madrid", en: "Madrid" },
  "Seville": { it: "Siviglia", es: "Sevilla", en: "Seville" },
  "Valencia": { it: "Valencia", es: "Valencia", en: "Valencia" },
  "Bilbao": { it: "Bilbao", es: "Bilbao", en: "Bilbao" },
  
  // English cities
  "London": { it: "Londra", es: "Londres", en: "London" },
  "Manchester": { it: "Manchester", es: "Mánchester", en: "Manchester" },
  "Liverpool": { it: "Liverpool", es: "Liverpool", en: "Liverpool" },
  "Birmingham": { it: "Birmingham", es: "Birmingham", en: "Birmingham" },
  "Newcastle": { it: "Newcastle", es: "Newcastle", en: "Newcastle" },
  "Leeds": { it: "Leeds", es: "Leeds", en: "Leeds" },
  
  // German cities
  "Munich": { it: "Monaco", es: "Múnich", en: "Munich" },
  "Berlin": { it: "Berlino", es: "Berlín", en: "Berlin" },
  "Frankfurt": { it: "Francoforte", es: "Fráncfort", en: "Frankfurt" },
  "Dortmund": { it: "Dortmund", es: "Dortmund", en: "Dortmund" },
  "Leipzig": { it: "Lipsia", es: "Leipzig", en: "Leipzig" },
  "Cologne": { it: "Colonia", es: "Colonia", en: "Cologne" },
  
  // Portuguese cities
  "Lisbon": { it: "Lisbona", es: "Lisboa", en: "Lisbon" },
  "Porto": { it: "Porto", es: "Oporto", en: "Porto" },
  "Braga": { it: "Braga", es: "Braga", en: "Braga" },
  
  // French cities
  "Paris": { it: "Parigi", es: "París", en: "Paris" },
  "Lyon": { it: "Lione", es: "Lyon", en: "Lyon" },
  "Marseille": { it: "Marsiglia", es: "Marsella", en: "Marseille" },
  
  // Turkish cities
  "Istanbul": { it: "Istanbul", es: "Estambul", en: "Istanbul" }
};

// Translate city name based on language
const translateCity = (city, lang) => {
  if (!city) return city;
  const translation = CITY_TRANSLATIONS[city];
  if (translation) {
    return translation[lang] || city;
  }
  return city;
};

// Format cup event title: replace (1st Leg), (Quarter Final), etc. with "- Cup Name"
const formatCupTitle = (title, league) => {
  if (!title || !league) return title;
  
  // Check if it's a cup competition
  const cupLeagues = ['COPPA ITALIA', 'CHAMPIONS LEAGUE', 'EUROPA LEAGUE', 'FA CUP', 'DFB POKAL', 'COPA DEL REY'];
  const isCup = cupLeagues.some(cup => league.toUpperCase().includes(cup));
  
  if (!isCup) return title;
  
  // Remove round info like (1st Leg), (Quarter Final), (Semi Final - 1st Leg), etc.
  const cleanTitle = title
    .replace(/\s*\([^)]*(?:Leg|Final|Round)[^)]*\)\s*/gi, '')
    .trim();
  
  // Format league name nicely
  const cupName = league
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
  
  return `${cleanTitle} - ${cupName}`;
};

const EventListItem = ({ event }) => {
  const { lang } = useLanguage();
  
  // Get locale for date formatting
  const getLocale = () => {
    switch(lang) {
      case 'it': return 'it-IT';
      case 'es': return 'es-ES';
      default: return 'en-GB';
    }
  };
  
  // Parse date to get day, month, year, day of week
  const parseDate = (dateStr, sortDate) => {
    const locale = getLocale();
    
    // First try sort_date (ISO format) which is more reliable
    if (sortDate) {
      try {
        const date = new Date(sortDate);
        if (!isNaN(date.getTime())) {
          return {
            dayOfWeek: date.toLocaleDateString(locale, { weekday: 'short' }).toUpperCase(),
            day: date.getDate(),
            month: date.toLocaleDateString(locale, { month: 'short' }),
            year: date.getFullYear()
          };
        }
      } catch {
        // Fall through to try dateStr
      }
    }
    
    // Then try dateStr
    try {
      const date = new Date(dateStr);
      if (!isNaN(date.getTime())) {
        return {
          dayOfWeek: date.toLocaleDateString(locale, { weekday: 'short' }).toUpperCase(),
          day: date.getDate(),
          month: date.toLocaleDateString(locale, { month: 'short' }),
          year: date.getFullYear()
        };
      }
      
      // Try parsing Italian format like "Domenica, 3 Maggio 2026"
      const italianMonths = {
        'gennaio': 0, 'febbraio': 1, 'marzo': 2, 'aprile': 3, 'maggio': 4, 'giugno': 5,
        'luglio': 6, 'agosto': 7, 'settembre': 8, 'ottobre': 9, 'novembre': 10, 'dicembre': 11
      };
      const match = dateStr.match(/(\d+)\s+(\w+)\s+(\d{4})/i);
      if (match) {
        const day = parseInt(match[1]);
        const monthName = match[2].toLowerCase();
        const year = parseInt(match[3]);
        const month = italianMonths[monthName];
        if (month !== undefined) {
          const parsedDate = new Date(year, month, day);
          return {
            dayOfWeek: parsedDate.toLocaleDateString(locale, { weekday: 'short' }).toUpperCase(),
            day: parsedDate.getDate(),
            month: parsedDate.toLocaleDateString(locale, { month: 'short' }),
            year: parsedDate.getFullYear()
          };
        }
      }
    } catch {
      // Return fallback
    }
    
    return { dayOfWeek: 'TBD', day: '--', month: '---', year: '----' };
  };

  const dateInfo = parseDate(event.date, event.sort_date);
  const eventId = event.id || event._id;
  const rawTitle = typeof event.title === 'object' ? (event.title.it || event.title.en || '') : event.title;
  const title = formatCupTitle(rawTitle, event.league);
  const rawLocation = typeof event.location === 'object' ? (event.location.it || event.location.en || '') : event.location;
  const location = translateCity(rawLocation, lang);

  return (
    <Link 
      to={`/event/${eventId}`}
      className="flex items-stretch bg-white hover:bg-gray-50 border-b border-gray-100 transition-colors group"
    >
      {/* Date Box */}
      <div className="flex-shrink-0 w-20 md:w-24 py-3 px-2 flex flex-col items-center justify-center border-r border-gray-100">
        <span className="text-[10px] text-gray-500 font-semibold tracking-wide">{dateInfo.dayOfWeek}</span>
        <span className="text-2xl md:text-3xl font-bold text-[#2D3436]">{dateInfo.day}</span>
        <span className="text-xs text-gray-500">
          {dateInfo.month} {dateInfo.year}
        </span>
      </div>

      {/* Team logos (home vs away) */}
      {(event.home_team_logo || event.away_team_logo) && (
        <div className="hidden sm:flex flex-shrink-0 items-center gap-1 px-3 border-r border-gray-100">
          {event.home_team_logo ? (
            <img
              src={event.home_team_logo}
              alt={`Logo ${event.home_team || ''}`}
              className="w-7 h-7 object-contain"
              loading="lazy"
              decoding="async"
            />
          ) : (
            <div className="w-7 h-7 bg-gray-100 rounded-full" />
          )}
          <span className="text-[10px] text-gray-400 font-bold">vs</span>
          {event.away_team_logo ? (
            <img
              src={event.away_team_logo}
              alt={`Logo ${event.away_team || ''}`}
              className="w-7 h-7 object-contain"
              loading="lazy"
              decoding="async"
            />
          ) : (
            <div className="w-7 h-7 bg-gray-100 rounded-full" />
          )}
        </div>
      )}

      {/* Event Info */}
      <div className="flex-1 py-3 px-3 min-w-0 flex flex-col justify-center">
        {/* Title */}
        <h3 className="text-sm md:text-base font-bold text-[#0984E3] group-hover:text-[#FF6B35] transition-colors leading-tight">
          {title}
        </h3>
        
        {/* Stadium */}
        <p className="text-gray-500 text-xs mt-1 truncate">
          {event.stadium || 'Stadium TBD'}
        </p>
        
        {/* Location */}
        <div className="flex items-center gap-2 mt-1">
          <span className="text-gray-500 text-xs flex items-center gap-1 truncate">
            <MapPin className="w-3 h-3 flex-shrink-0" />
            {location || 'Location TBD'}
          </span>
        </div>
      </div>

      {/* Arrow */}
      <div className="flex-shrink-0 flex items-center px-2">
        <ChevronRight className="w-5 h-5 text-[#0984E3] group-hover:text-[#FF6B35] transition-colors" />
      </div>
    </Link>
  );
};

export default EventListItem;
