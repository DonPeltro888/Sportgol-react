import React from 'react';
import { Calendar } from 'lucide-react';

const EventCard = ({ event }) => {
  return (
    <div className="bg-white rounded-lg overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer">
      {/* Event Image */}
      <div className="relative h-48 overflow-hidden">
        <img
          src={event.image}
          alt={event.title}
          className="w-full h-full object-cover transition-transform duration-300 hover:scale-110"
        />
      </div>
      
      {/* Event Details */}
      <div className="p-5">
        <h3 className="text-xl font-bold text-gray-900 mb-4">
          {event.title}
        </h3>
        
        {/* Categories */}
        <div className="flex flex-wrap gap-2 mb-4">
          {event.categories.map((category, index) => (
            <span
              key={index}
              className="bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-full hover:bg-blue-700 transition-colors"
            >
              {category}
            </span>
          ))}
        </div>
        
        {/* Date */}
        <div className="flex items-center gap-2 text-gray-600 text-sm">
          <Calendar className="w-4 h-4" />
          <span>{event.date}</span>
        </div>
      </div>
    </div>
  );
};

export default EventCard;
