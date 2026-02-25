import React from 'react';
import { Helmet } from 'react-helmet-async';

// Helper function per country code
function getCountryCode(location) {
  const countryMap = {
    'Milan': 'IT', 'Rome': 'IT', 'Turin': 'IT', 'Naples': 'IT', 'Florence': 'IT',
    'London': 'GB', 'Manchester': 'GB', 'Liverpool': 'GB', 'Birmingham': 'GB',
    'Madrid': 'ES', 'Barcelona': 'ES', 'Seville': 'ES', 'Valencia': 'ES',
    'Munich': 'DE', 'Berlin': 'DE', 'Dortmund': 'DE', 'Frankfurt': 'DE',
    'Paris': 'FR', 'Lyon': 'FR', 'Marseille': 'FR',
    'Lisbon': 'PT', 'Porto': 'PT',
    'Istanbul': 'TR'
  };
  return countryMap[location] || 'EU';
}

// Schema.org JSON-LD per Eventi
export const EventSchema = ({ event, lang = 'it' }) => {
  if (!event) return null;
  
  const baseUrl = process.env.REACT_APP_BACKEND_URL || 'https://campionato-demo.preview.emergentagent.com';
  
  const schema = {
    "@context": "https://schema.org",
    "@type": "SportsEvent",
    "name": event.title,
    "description": `Biglietti per ${event.title} - ${event.stadium}, ${event.location}`,
    "startDate": event.sort_date || event.date,
    "eventStatus": "https://schema.org/EventScheduled",
    "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
    "location": {
      "@type": "StadiumOrArena",
      "name": event.stadium,
      "address": {
        "@type": "PostalAddress",
        "addressLocality": event.location,
        "addressCountry": getCountryCode(event.location)
      }
    },
    "offers": {
      "@type": "AggregateOffer",
      "lowPrice": event.price_range?.min || 45,
      "highPrice": event.price_range?.max || 500,
      "priceCurrency": "EUR",
      "availability": "https://schema.org/InStock",
      "url": `${baseUrl}/event/${event.id || event._id}`
    },
    "performer": event.categories?.map(team => ({
      "@type": "SportsTeam",
      "name": team
    })) || []
  };

  const jsonString = JSON.stringify(schema);

  return (
    <Helmet>
      <script type="application/ld+json">{jsonString}</script>
    </Helmet>
  );
};

// Schema.org per Organizzazione (Homepage)
export const OrganizationSchema = () => {
  const baseUrl = process.env.REACT_APP_BACKEND_URL || 'https://campionato-demo.preview.emergentagent.com';
  
  const schema = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "GolEvents",
    "description": "Biglietti per eventi sportivi - Calcio, Champions League, Serie A, Premier League",
    "url": baseUrl
  };

  const jsonString = JSON.stringify(schema);

  return (
    <Helmet>
      <script type="application/ld+json">{jsonString}</script>
    </Helmet>
  );
};

// Schema.org per League Page
export const LeagueSchema = ({ leagueName, teams, lang = 'it' }) => {
  const baseUrl = process.env.REACT_APP_BACKEND_URL || 'https://campionato-demo.preview.emergentagent.com';
  
  const schema = {
    "@context": "https://schema.org",
    "@type": "SportsOrganization",
    "name": leagueName,
    "sport": "Football",
    "url": `${baseUrl}/biglietti-${leagueName?.toLowerCase().replace(/\s+/g, '-')}`,
    "member": teams?.map(team => ({
      "@type": "SportsTeam",
      "name": team
    })) || []
  };

  const jsonString = JSON.stringify(schema);

  return (
    <Helmet>
      <script type="application/ld+json">{jsonString}</script>
    </Helmet>
  );
};

// Schema.org per Breadcrumbs
export const BreadcrumbSchema = ({ items }) => {
  const baseUrl = process.env.REACT_APP_BACKEND_URL || 'https://campionato-demo.preview.emergentagent.com';
  
  const schema = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": items.map((item, index) => ({
      "@type": "ListItem",
      "position": index + 1,
      "name": item.name,
      "item": item.url ? `${baseUrl}${item.url}` : undefined
    }))
  };

  const jsonString = JSON.stringify(schema);

  return (
    <Helmet>
      <script type="application/ld+json">{jsonString}</script>
    </Helmet>
  );
};

export default { EventSchema, OrganizationSchema, LeagueSchema, BreadcrumbSchema };
