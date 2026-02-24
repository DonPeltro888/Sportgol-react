import React, { useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

const SEOHead = ({ 
  title, 
  description, 
  keywords,
  ogImage,
  canonicalUrl,
  type = 'website',
  event = null // For event pages with Schema.org
}) => {
  const { lang } = useLanguage();
  
  useEffect(() => {
    // Update document title
    if (title) {
      document.title = title;
    }
    
    // Update meta tags
    const updateMeta = (name, content, isProperty = false) => {
      if (!content) return;
      
      const attr = isProperty ? 'property' : 'name';
      let meta = document.querySelector(`meta[${attr}="${name}"]`);
      
      if (!meta) {
        meta = document.createElement('meta');
        meta.setAttribute(attr, name);
        document.head.appendChild(meta);
      }
      meta.setAttribute('content', content);
    };
    
    // Standard meta tags
    updateMeta('description', description);
    updateMeta('keywords', keywords);
    updateMeta('language', lang);
    
    // Open Graph
    updateMeta('og:title', title, true);
    updateMeta('og:description', description, true);
    updateMeta('og:type', type, true);
    updateMeta('og:image', ogImage, true);
    updateMeta('og:locale', lang === 'it' ? 'it_IT' : lang === 'es' ? 'es_ES' : 'en_US', true);
    
    // Twitter Card
    updateMeta('twitter:card', 'summary_large_image');
    updateMeta('twitter:title', title);
    updateMeta('twitter:description', description);
    updateMeta('twitter:image', ogImage);
    
    // Canonical URL
    if (canonicalUrl) {
      let link = document.querySelector('link[rel="canonical"]');
      if (!link) {
        link = document.createElement('link');
        link.setAttribute('rel', 'canonical');
        document.head.appendChild(link);
      }
      link.setAttribute('href', canonicalUrl);
    }
    
    // Hreflang tags for multilingual
    const baseUrl = window.location.origin;
    const path = window.location.pathname;
    
    ['it', 'es', 'en'].forEach(l => {
      const hreflangId = `hreflang-${l}`;
      let link = document.getElementById(hreflangId);
      if (!link) {
        link = document.createElement('link');
        link.id = hreflangId;
        link.setAttribute('rel', 'alternate');
        link.setAttribute('hreflang', l);
        document.head.appendChild(link);
      }
      link.setAttribute('href', `${baseUrl}${path}?lang=${l}`);
    });
    
    // Schema.org for events
    if (event) {
      const schemaId = 'schema-org-event';
      let script = document.getElementById(schemaId);
      
      if (!script) {
        script = document.createElement('script');
        script.id = schemaId;
        script.type = 'application/ld+json';
        document.head.appendChild(script);
      }
      
      const eventSchema = {
        "@context": "https://schema.org",
        "@type": "SportsEvent",
        "name": event.title,
        "description": description || `Biglietti per ${event.title}`,
        "startDate": event.dateISO || event.date,
        "location": {
          "@type": "Place",
          "name": event.stadium || event.location,
          "address": {
            "@type": "PostalAddress",
            "addressLocality": event.location
          }
        },
        "organizer": {
          "@type": "Organization",
          "name": "GOLEVENTS"
        },
        "performer": event.categories?.map(team => ({
          "@type": "SportsTeam",
          "name": team
        })) || [],
        "eventStatus": "https://schema.org/EventScheduled",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "offers": event.ticket_categories?.length > 0 ? {
          "@type": "AggregateOffer",
          "lowPrice": Math.min(...event.ticket_categories.map(t => t.price_min || 0)),
          "highPrice": Math.max(...event.ticket_categories.map(t => t.price_max || 0)),
          "priceCurrency": "EUR",
          "availability": "https://schema.org/InStock",
          "url": window.location.href
        } : undefined,
        "image": event.imageUrl || ogImage
      };
      
      script.textContent = JSON.stringify(eventSchema);
    }
    
    // Cleanup function
    return () => {
      // Remove schema.org script on unmount
      const schemaScript = document.getElementById('schema-org-event');
      if (schemaScript) {
        schemaScript.remove();
      }
    };
  }, [title, description, keywords, ogImage, canonicalUrl, type, event, lang]);
  
  return null; // This component doesn't render anything
};

export default SEOHead;
