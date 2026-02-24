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

const EventsGrid = ({ events, loading }) => {
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);
  
  // Split events into local and international
  const localLocations = LOCAL_LOCATIONS[lang] || LOCAL_LOCATIONS.it;
  
  const localEvents = events.filter(event => 
    localLocations.includes(event.location)
  );
  
  const internationalEvents = events.filter(event => 
    !localLocations.includes(event.location)
  );

  return (
    <section className="py-12 px-4 bg-gradient-to-b from-gray-900 to-black relative overflow-hidden z-0">
      <div className="container mx-auto relative">
        {/* Section Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-blue-500/10 border border-blue-500/30 rounded-full text-blue-400 text-xs font-semibold mb-3">
            <Trophy className="w-3 h-3" />
            {t('topEvents')}
          </div>
          <h2 className="text-2xl md:text-3xl font-black mb-2">
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">{t('upcomingEvents')}</span>
          </h2>
          <p className="text-gray-400 text-sm max-w-2xl mx-auto">
            {t('eventsSubtitle')}
          </p>
        </div>
        
        {/* Loading State */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
            <p className="text-gray-400">{t('loadingEvents')}</p>
          </div>
        ) : events.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Local Events Column */}
            <div className="bg-gray-800/30 backdrop-blur rounded-xl border border-gray-700/50 overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-700/50 flex items-center gap-2">
                <MapPin className="w-4 h-4 text-green-400" />
                <span className="text-sm text-white font-semibold">
                  {t('eventsCountry')}
                </span>
                <span className="text-xs text-gray-500 ml-auto">
                  {localEvents.length} {t('events')}
                </span>
              </div>
              <div className="max-h-[600px] overflow-y-auto">
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
            <div className="bg-gray-800/30 backdrop-blur rounded-xl border border-gray-700/50 overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-700/50 flex items-center gap-2">
                <Globe className="w-4 h-4 text-blue-400" />
                <span className="text-sm text-white font-semibold">
                  {t('eventsInternational')}
                </span>
                <span className="text-xs text-gray-500 ml-auto">
                  {internationalEvents.length} {t('events')}
                </span>
              </div>
              <div className="max-h-[600px] overflow-y-auto">
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
            <div className="text-gray-400 text-xl mb-2">{t('noEventsFound')}</div>
            <p className="text-gray-500">{t('adjustSearch')}</p>
          </div>
        )}
      </div>
    </section>
  );
};

export default EventsGrid;
