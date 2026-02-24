import React from 'react';
import EventListItem from './EventListItem';
import { Trophy, Loader2, Globe, MapPin } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';

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

const COUNTRY_NAMES = {
  it: "Italia",
  es: "España", 
  en: "UK"
};

const EventsGrid = ({ events, loading }) => {
  const { lang } = useLanguage();
  
  // Split events into local and international
  const localLocations = LOCAL_LOCATIONS[lang] || LOCAL_LOCATIONS.it;
  const countryName = COUNTRY_NAMES[lang] || "Italia";
  
  const localEvents = events.filter(event => 
    localLocations.includes(event.location)
  );
  
  const internationalEvents = events.filter(event => 
    !localLocations.includes(event.location)
  );

  return (
    <section className="py-12 px-4 bg-gradient-to-b from-gray-900 to-black relative overflow-hidden">
      <div className="container mx-auto relative z-10">
        {/* Section Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/30 rounded-full text-blue-400 text-sm font-semibold mb-4">
            <Trophy className="w-4 h-4" />
            Top Events
          </div>
          <h2 className="text-4xl md:text-5xl font-black mb-3">
            <span className="text-white">Upcoming </span>
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Events</span>
          </h2>
          <p className="text-gray-400 text-base max-w-2xl mx-auto">
            Don't miss out on the most exciting sporting events of the season
          </p>
        </div>
        
        {/* Loading State */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
            <p className="text-gray-400">Loading events...</p>
          </div>
        ) : events.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Local Events Column */}
            <div className="bg-gray-800/30 backdrop-blur rounded-xl border border-gray-700/50 overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-700/50 flex items-center gap-2">
                <MapPin className="w-4 h-4 text-green-400" />
                <span className="text-sm text-white font-semibold">
                  Eventi {countryName}
                </span>
                <span className="text-xs text-gray-500 ml-auto">
                  {localEvents.length} eventi
                </span>
              </div>
              <div className="max-h-[600px] overflow-y-auto">
                {localEvents.length > 0 ? (
                  localEvents.map((event) => (
                    <EventListItem key={event.id || event._id} event={event} />
                  ))
                ) : (
                  <div className="p-8 text-center text-gray-500">
                    Nessun evento locale disponibile
                  </div>
                )}
              </div>
            </div>
            
            {/* International Events Column */}
            <div className="bg-gray-800/30 backdrop-blur rounded-xl border border-gray-700/50 overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-700/50 flex items-center gap-2">
                <Globe className="w-4 h-4 text-blue-400" />
                <span className="text-sm text-white font-semibold">
                  Eventi Internazionali
                </span>
                <span className="text-xs text-gray-500 ml-auto">
                  {internationalEvents.length} eventi
                </span>
              </div>
              <div className="max-h-[600px] overflow-y-auto">
                {internationalEvents.length > 0 ? (
                  internationalEvents.map((event) => (
                    <EventListItem key={event.id || event._id} event={event} />
                  ))
                ) : (
                  <div className="p-8 text-center text-gray-500">
                    Nessun evento internazionale disponibile
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🔍</div>
            <div className="text-gray-400 text-xl mb-2">No events found</div>
            <p className="text-gray-500">Try adjusting your search criteria</p>
          </div>
        )}
      </div>
    </section>
  );
};

export default EventsGrid;
