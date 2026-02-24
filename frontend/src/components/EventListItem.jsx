import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, MapPin } from 'lucide-react';

const EventListItem = ({ event }) => {
  // Parse date to get day, month, year, day of week
  const parseDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) {
        // Try parsing "March 15, 2026" format
        const parsed = new Date(Date.parse(dateStr));
        if (!isNaN(parsed.getTime())) {
          return {
            dayOfWeek: parsed.toLocaleDateString('en-US', { weekday: 'long' }).toUpperCase(),
            day: parsed.getDate(),
            month: parsed.toLocaleDateString('en-US', { month: 'short' }),
            year: parsed.getFullYear()
          };
        }
      }
      return {
        dayOfWeek: date.toLocaleDateString('en-US', { weekday: 'long' }).toUpperCase(),
        day: date.getDate(),
        month: date.toLocaleDateString('en-US', { month: 'short' }),
        year: date.getFullYear()
      };
    } catch {
      return { dayOfWeek: 'TBD', day: '--', month: '---', year: '----' };
    }
  };

  const dateInfo = parseDate(event.date || event.sort_date);
  const eventId = event.id || event._id;
  const title = typeof event.title === 'object' ? (event.title.it || event.title.en || '') : event.title;
  const location = typeof event.location === 'object' ? (event.location.it || event.location.en || '') : event.location;
  const priceMin = event.price_range?.min || event.ticket_categories?.[0]?.price_min || 45;

  return (
    <Link 
      to={`/event/${eventId}`}
      className="flex items-stretch bg-gray-800/50 hover:bg-gray-700/50 border-b border-gray-700/50 transition-colors group"
    >
      {/* Date Box */}
      <div className="flex-shrink-0 w-20 md:w-24 py-3 px-2 flex flex-col items-center justify-center border-r border-gray-700/50">
        <span className="text-[10px] text-gray-400 font-semibold tracking-wide">{dateInfo.dayOfWeek}</span>
        <span className="text-2xl md:text-3xl font-bold text-white">{dateInfo.day}</span>
        <span className="text-xs text-gray-400">
          {dateInfo.month} {dateInfo.year}
        </span>
      </div>

      {/* Event Info */}
      <div className="flex-1 py-3 px-3 min-w-0 flex flex-col justify-center">
        {/* Title */}
        <h3 className="text-sm md:text-base font-bold text-blue-400 group-hover:text-blue-300 transition-colors leading-tight">
          {title}
        </h3>
        
        {/* Stadium */}
        <p className="text-gray-400 text-xs mt-1 truncate">
          {event.stadium || 'Stadium TBD'}
        </p>
        
        {/* Price & Location */}
        <div className="flex items-center gap-2 mt-1">
          <span className="text-green-400 font-bold text-sm">€{priceMin}+</span>
          <span className="text-gray-600">•</span>
          <span className="text-gray-400 text-xs flex items-center gap-1 truncate">
            <MapPin className="w-3 h-3 flex-shrink-0" />
            {location || 'Location TBD'}
          </span>
        </div>
      </div>

      {/* Arrow */}
      <div className="flex-shrink-0 flex items-center px-2">
        <ChevronRight className="w-5 h-5 text-blue-400 group-hover:text-blue-300 transition-colors" />
      </div>
    </Link>
  );
};

export default EventListItem;
