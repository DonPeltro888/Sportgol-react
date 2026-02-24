import React from 'react';
import EventCard from './EventCard';
import { Trophy } from 'lucide-react';

const EventsGrid = ({ events }) => {
  return (
    <section className="py-20 px-4 bg-gradient-to-b from-gray-900 to-black relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500 rounded-full filter blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500 rounded-full filter blur-3xl"></div>
      </div>

      <div className="container mx-auto relative z-10">
        {/* Section Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/30 rounded-full text-blue-400 text-sm font-semibold mb-4">
            <Trophy className="w-4 h-4" />
            Top Events
          </div>
          <h2 className="text-5xl md:text-6xl font-black mb-4">
            <span className="text-white">Upcoming </span>
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Events</span>
          </h2>
          <p className="text-gray-400 text-lg max-w-2xl mx-auto">
            Don't miss out on the most exciting sporting events of the season
          </p>
        </div>
        
        {/* Events Grid */}
        {events.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
            {events.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="text-gray-400 text-xl mb-4">No events found</div>
            <p className="text-gray-500">Try adjusting your search criteria</p>
          </div>
        )}
      </div>
    </section>
  );
};

export default EventsGrid;