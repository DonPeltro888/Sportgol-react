import React from 'react';
import { MessageCircle } from 'lucide-react';

/**
 * Floating WhatsApp button visible on all public pages.
 * Uses brand WhatsApp green color.
 */
const WhatsAppButton = ({ phone = '', message = '' }) => {
  const defaultPhone = phone || '393000000000'; // Update with real number
  const defaultMessage = encodeURIComponent(
    message || 'Ciao! Vorrei informazioni sui biglietti.'
  );
  const href = `https://wa.me/${defaultPhone}?text=${defaultMessage}`;

  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      data-testid="whatsapp-floating-btn"
      aria-label="Contattaci su WhatsApp"
      className="fixed bottom-6 right-6 z-50 bg-[#25D366] hover:bg-[#1fb858] text-white p-4 rounded-full shadow-2xl hover:shadow-[#25D366]/50 transition-all duration-300 hover:scale-110 group"
    >
      <MessageCircle className="w-7 h-7" fill="currentColor" />
      <span className="absolute right-full mr-3 top-1/2 -translate-y-1/2 bg-[#2D3436] text-white text-xs font-medium px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap shadow-lg">
        Scrivici su WhatsApp
      </span>
      <span className="absolute -top-1 -right-1 flex h-3 w-3">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#25D366] opacity-75"></span>
        <span className="relative inline-flex rounded-full h-3 w-3 bg-[#25D366]"></span>
      </span>
    </a>
  );
};

export default WhatsAppButton;
