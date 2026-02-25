import React from 'react';
import { Helmet } from 'react-helmet-async';

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
    "endDate": event.sort_date || event.date,
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
      "url": `${baseUrl}/event/${event.id || event._id}`,
      "validFrom": new Date().toISOString()
    },
    "performer": event.categories?.map(team => ({
      "@type": "SportsTeam",
      "name": team
    })) || [],
    "organizer": {
      "@type": "Organization",
      "name": event.league,
      "url": baseUrl
    },
    "image": event.image || event.imageUrl || `${baseUrl}/og-image.jpg`
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {`${JSON.stringify(schema)}`}
      </script>
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
    "url": baseUrl,
    "logo": `${baseUrl}/logo.png`,
    "contactPoint": {
      "@type": "ContactPoint",
      "contactType": "customer service",
      "availableLanguage": ["Italian", "English", "Spanish"]
    },
    "sameAs": [
      "https://www.facebook.com/golevents",
      "https://www.instagram.com/golevents",
      "https://twitter.com/golevents"
    ]
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {`${JSON.stringify(schema)}`}
      </script>
    </Helmet>
  );
};

// Schema.org per Team Page
export const TeamSchema = ({ teamName, events, lang = 'it' }) => {
  const baseUrl = process.env.REACT_APP_BACKEND_URL || 'https://campionato-demo.preview.emergentagent.com';
  
  const schema = {
    "@context": "https://schema.org",
    "@type": "SportsTeam",
    "name": teamName,
    "sport": "Football",
    "url": `${baseUrl}/biglietti-${teamName.toLowerCase().replace(/\s+/g, '-')}`,
    "event": events?.slice(0, 10).map(event => ({
      "@type": "SportsEvent",
      "name": event.title,
      "startDate": event.sort_date || event.date,
      "location": {
        "@type": "StadiumOrArena",
        "name": event.stadium
      }
    })) || []
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
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
    "url": `${baseUrl}/biglietti-${leagueName.toLowerCase().replace(/\s+/g, '-')}`,
    "member": teams?.map(team => ({
      "@type": "SportsTeam",
      "name": team
    })) || []
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
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

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
    </Helmet>
  );
};

// Schema.org per FAQ (utile per SEO)
export const FAQSchema = ({ faqs }) => {
  if (!faqs || faqs.length === 0) return null;
  
  const schema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map(faq => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer
      }
    }))
  };

  return (
    <Helmet>
      <script type="application/ld+json">
        {JSON.stringify(schema)}
      </script>
    </Helmet>
  );
};

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

export default { EventSchema, OrganizationSchema, TeamSchema, LeagueSchema, BreadcrumbSchema, FAQSchema };
