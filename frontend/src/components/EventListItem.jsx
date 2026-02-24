import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, MapPin, Clock } from 'lucide-react';

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
            dayOfWeek: parsed.toLocaleDateString('en-US', { weekday: 'long' }),
            day: parsed.getDate(),
            month: parsed.toLocaleDateString('en-US', { month: 'short' }),
            year: parsed.getFullYear()
          };
        }
      }
      return {
        dayOfWeek: date.toLocaleDateString('en-US', { weekday: 'long' }),
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
      className="flex items-stretch bg-white hover:bg-gray-50 border-b border-gray-200 transition-colors group"
    >
      {/* Date Box */}
      <div className="flex-shrink-0 w-24 md:w-28 py-4 px-3 flex flex-col items-center justify-center bg-gray-50 border-r border-gray-200">
        <span className="text-xs text-gray-500 font-medium uppercase">{dateInfo.dayOfWeek}</span>
        <span className="text-2xl md:text-3xl font-bold text-gray-800">{dateInfo.day}</span>
        <span className="text-xs text-gray-500">
          {dateInfo.month} {dateInfo.year}
        </span>
      </div>

      {/* Event Info */}
      <div className="flex-1 py-4 px-4 min-w-0">
        {/* Title */}
        <h3 className="text-base md:text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-2">
          {title}
        </h3>
        
        {/* Time & Stadium */}
        <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
          {event.time && (
            <span className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {event.time}
            </span>
          )}
          <span>{event.stadium || 'Stadium TBD'}</span>
        </div>
        
        {/* Price & Location */}
        <div className="flex items-center gap-2 mt-2">
          <span className="text-green-600 font-semibold">€{priceMin}+</span>
          <span className="text-gray-400">•</span>
          <span className="text-gray-500 text-sm flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {location || 'Location TBD'}
          </span>
        </div>
      </div>

      {/* Arrow */}
      <div className="flex-shrink-0 flex items-center px-4">
        <ChevronRight className="w-6 h-6 text-gray-400 group-hover:text-blue-500 transition-colors" />
      </div>
    </Link>
  );
};

export default EventListItem;
