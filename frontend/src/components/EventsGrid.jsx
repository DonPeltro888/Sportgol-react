import React from 'react';
import EventListItem from './EventListItem';
import { Trophy, Loader2, Globe, MapPin } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';

// Local locations per language
const LOCAL_LOCATIONS = {
  it: ["Milan", "Rome", "Turin", "Naples", "Florence", "Bologna", "Genoa", 
       "Bergamo", "Verona", "Udine", "Cagliari", "Lecce", "Parma", "Como",
       "Cremona", "Pisa", "Reggio Emilia"],
  es: ["Madrid", "Barcelona", "Seville", "Valencia", "Bilbao", "Vigo",
       "Girona", "Elche", "Oviedo", "Palma"],
  en: ["London", "Manchester", "Liverpool", "Birmingham", "Newcastle",
       "Leeds", "Brighton", "Bournemouth", "Wolverhampton", "Burnley"]
};

// Priority teams per language
const PRIORITY_TEAMS = {
  it: ["Milan", "Inter", "Juventus", "Roma", "Fiorentina", "Lazio"],
  es: ["Barcelona", "Real Madrid", "Sevilla", "Valencia"],
  en: ["Manchester City", "Manchester United", "Arsenal", "Chelsea", "Liverpool"]
};

// Check if event involves a priority team
const isPriorityEvent = (event, priorityTeams) => {
  const title = typeof event.title === 'object' 
    ? (event.title.it || event.title.en || event.title.es || '') 
    : (event.title || '');
  const categories = event.categories || [];
  
  return priorityTeams.some(team => 
    title.toLowerCase().includes(team.toLowerCase()) ||
    categories.some(cat => cat.toLowerCase().includes(team.toLowerCase()))
  );
};

// Sort events: priority teams first, then by date
const sortEventsByPriority = (events, priorityTeams) => {
  return [...events].sort((a, b) => {
    const aIsPriority = isPriorityEvent(a, priorityTeams);
    const bIsPriority = isPriorityEvent(b, priorityTeams);
    
    // Priority events come first
    if (aIsPriority && !bIsPriority) return -1;
    if (!aIsPriority && bIsPriority) return 1;
    
    // Within same priority, sort by date
    const dateA = new Date(a.sort_date || a.date);
    const dateB = new Date(b.sort_date || b.date);
    return dateA - dateB;
  });
};

const EventsGrid = ({ events, loading }) => {
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);
  
  // Get priority teams for current language
  const priorityTeams = PRIORITY_TEAMS[lang] || PRIORITY_TEAMS.it;
  
  // Split events into local and international
  const localLocations = LOCAL_LOCATIONS[lang] || LOCAL_LOCATIONS.it;
  
  const localEvents = sortEventsByPriority(
    events.filter(event => localLocations.includes(event.location)),
    priorityTeams
  );
  
  const internationalEvents = sortEventsByPriority(
    events.filter(event => !localLocations.includes(event.location)),
    // For international, use ALL priority teams
    [...PRIORITY_TEAMS.it, ...PRIORITY_TEAMS.es, ...PRIORITY_TEAMS.en]
  );

  return (
    <section className="py-12 px-4 bg-white relative overflow-hidden z-0">
      <div className="container mx-auto relative">
        {/* Section Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-[#0984E3]/10 border border-[#0984E3]/30 rounded-full text-[#0984E3] text-xs font-semibold mb-3">
            <Trophy className="w-3 h-3" />
            {t('topEvents')}
          </div>
          <h2 className="text-2xl md:text-3xl font-black">
            <span className="text-[#2D3436]">{t('upcomingEvents')}</span>
          </h2>
        </div>
        
        {/* Loading State */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-12 h-12 text-[#0984E3] animate-spin mb-4" />
            <p className="text-gray-500">{t('loadingEvents')}</p>
          </div>
        ) : events.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Local Events Column */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-200 flex items-center gap-2 bg-gray-50">
                <MapPin className="w-4 h-4 text-[#FF6B35]" />
                <span className="text-sm text-[#2D3436] font-semibold">
                  {t('eventsCountry')}
                </span>
                <span className="text-xs text-gray-500 ml-auto">
                  {localEvents.length} {t('events')}
                </span>
              </div>
              <div>
                {localEvents.length > 0 ? (
                  localEvents.map((event) => (
                    <EventListItem key={event.id || event._id} event={event} />
                  ))
                ) : (
                  <div className="p-8 text-center text-gray-500">
                    {t('noEventsLocal')}
                  </div>
                )}
              </div>
            </div>
            
            {/* International Events Column */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-200 flex items-center gap-2 bg-gray-50">
                <Globe className="w-4 h-4 text-[#0984E3]" />
                <span className="text-sm text-[#2D3436] font-semibold">
                  {t('eventsInternational')}
                </span>
                <span className="text-xs text-gray-500 ml-auto">
                  {internationalEvents.length} {t('events')}
                </span>
              </div>
              <div>
                {internationalEvents.length > 0 ? (
                  internationalEvents.map((event) => (
                    <EventListItem key={event.id || event._id} event={event} />
                  ))
                ) : (
                  <div className="p-8 text-center text-gray-500">
                    {t('noEventsInternational')}
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🔍</div>
            <div className="text-gray-600 text-xl mb-2">{t('noEventsFound')}</div>
            <p className="text-gray-500">{t('adjustSearch')}</p>
          </div>
        )}
      </div>
    </section>
  );
};

export default EventsGrid;
