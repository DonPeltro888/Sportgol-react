import React from 'react';
import { Calendar, MapPin, ArrowRight } from 'lucide-react';

const EventCard = ({ event }) => {
  return (
    <div className="group relative bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-2xl overflow-hidden hover:border-blue-500/50 transition-all duration-500 hover:shadow-2xl hover:shadow-blue-500/20 transform hover:-translate-y-2">
      {/* Image Container with Overlay */}
      <div className="relative h-52 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/50 to-transparent z-10 opacity-60 group-hover:opacity-40 transition-opacity duration-300"></div>
        <img
          src={event.image}
          alt={event.title}
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
        />
        {/* Shine effect */}
        <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
        </div>
        {/* Premium Badge */}
        <div className="absolute top-4 right-4 z-20 bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-xs font-bold px-3 py-1.5 rounded-full">
          FEATURED
        </div>
      </div>
      
      {/* Content */}
      <div className="p-6">
        <h3 className="text-xl font-bold text-white mb-4 group-hover:text-blue-400 transition-colors duration-300">
          {event.title}
        </h3>
        
        {/* Categories */}
        <div className="flex flex-wrap gap-2 mb-4">
          {event.categories.slice(0, 3).map((category, index) => (
            <span
              key={index}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xs font-bold px-3 py-1.5 rounded-lg hover:from-blue-500 hover:to-purple-500 transition-all duration-300 transform hover:scale-105 cursor-pointer"
            >
              {category}
            </span>
          ))}
          {event.categories.length > 3 && (
            <span className="bg-gray-700 text-gray-300 text-xs font-semibold px-3 py-1.5 rounded-lg">
              +{event.categories.length - 3}
            </span>
          )}
        </div>
        
        {/* Info */}
        <div className="space-y-2 mb-4">
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <Calendar className="w-4 h-4 text-blue-400" />
            <span>{event.date}</span>
          </div>
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <MapPin className="w-4 h-4 text-purple-400" />
            <span>{event.location}</span>
          </div>
        </div>

        {/* CTA Button */}
        <button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold py-3 rounded-xl transition-all duration-300 flex items-center justify-center gap-2 group/btn shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40">
          <span>View Details</span>
          <ArrowRight className="w-4 h-4 transform group-hover/btn:translate-x-1 transition-transform" />
        </button>
      </div>
    </div>
  );
};

export default EventCard;