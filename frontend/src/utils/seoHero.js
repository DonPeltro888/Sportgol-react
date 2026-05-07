/**
 * Helper per risolvere l'URL pubblico delle hero image generate da Nano Banana 2.
 * I path salvati sono relativi (es. "/api/seo/uploads/foo.png"). Aggiunge il REACT_APP_BACKEND_URL davanti.
 * Se è già un URL assoluto (http/https), lo lascia invariato.
 */
const API_URL = process.env.REACT_APP_BACKEND_URL;

export const resolveSeoHeroUrl = (raw) => {
  if (!raw || typeof raw !== 'string') return '';
  if (raw.startsWith('http://') || raw.startsWith('https://')) return raw;
  if (raw.startsWith('/')) return `${API_URL}${raw}`;
  return `${API_URL}/${raw}`;
};
