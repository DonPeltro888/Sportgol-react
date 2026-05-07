/**
 * SeoContentBlock — renderizza i campi SEO multilingua (seo_intro, seo_cta, seo_event_info, ecc.)
 * generati e pubblicati dal SEO Admin sulle entity events/leagues/teams.
 *
 * Uso:
 *   <SeoContentBlock data={leagueData} lang={lang} />
 *
 * I campi sono di forma { it: "...", en: "...", es: "..." }.
 * Se non c'è valore per la lingua corrente prova con fallback: it → en → primo disponibile.
 */
import React from 'react';

const pickLang = (field, lang) => {
  if (!field) return '';
  if (typeof field === 'string') return field;
  return field[lang] || field.it || field.en || field.es || '';
};

const SeoContentBlock = ({ data, lang = 'it' }) => {
  if (!data) return null;
  const intro = pickLang(data.seo_intro, lang);
  const cta = pickLang(data.seo_cta, lang);
  const eventInfo = pickLang(data.seo_event_info, lang);
  const ticketsInfo = pickLang(data.seo_tickets_info, lang);
  const sectors = pickLang(data.seo_sectors, lang);
  const pricing = pickLang(data.seo_pricing, lang);
  const venue = pickLang(data.seo_venue, lang);

  // FAQ items (only events have these)
  const faqs = [1, 2, 3].map(i => ({
    q: pickLang(data[`faq_${i}_q`], lang),
    a: pickLang(data[`faq_${i}_a`], lang),
  })).filter(f => f.q || f.a);

  const hasContent = intro || cta || eventInfo || ticketsInfo || sectors || pricing || venue || faqs.length > 0;
  if (!hasContent) return null;

  return (
    <section className="bg-white py-8 md:py-12 px-4" data-testid="seo-content-block">
      <div className="container mx-auto max-w-4xl space-y-6">
        {intro && (
          <div className="prose prose-gray max-w-none">
            <p className="text-base md:text-lg text-gray-700 leading-relaxed">{intro}</p>
          </div>
        )}

        {eventInfo && (
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-5">
            <h2 className="text-lg font-bold text-gray-900 mb-2">Informazioni Evento</h2>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{eventInfo}</p>
          </div>
        )}

        {ticketsInfo && (
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-5">
            <h2 className="text-lg font-bold text-gray-900 mb-2">Biglietti Disponibili</h2>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{ticketsInfo}</p>
          </div>
        )}

        {sectors && (
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-5">
            <h2 className="text-lg font-bold text-gray-900 mb-2">Settori Consigliati</h2>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{sectors}</p>
          </div>
        )}

        {pricing && (
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-5">
            <h2 className="text-lg font-bold text-gray-900 mb-2">Prezzi e Domanda</h2>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{pricing}</p>
          </div>
        )}

        {venue && (
          <div className="rounded-lg border border-gray-200 bg-gray-50 p-5">
            <h2 className="text-lg font-bold text-gray-900 mb-2">Lo Stadio</h2>
            <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">{venue}</p>
          </div>
        )}

        {faqs.length > 0 && (
          <div className="space-y-2">
            <h2 className="text-xl font-bold text-gray-900">Domande Frequenti</h2>
            {faqs.map((f, i) => (
              <details key={i} className="rounded-lg border border-gray-200 bg-white p-4 group">
                <summary className="cursor-pointer font-semibold text-gray-900 list-none flex items-center justify-between">
                  <span>{f.q}</span>
                  <span className="text-gray-400 group-open:rotate-180 transition">▾</span>
                </summary>
                <p className="mt-2 text-sm text-gray-700 leading-relaxed whitespace-pre-line">{f.a}</p>
              </details>
            ))}
          </div>
        )}

        {cta && (
          <div className="rounded-lg bg-gradient-to-r from-[#FF6B35] to-[#0984E3] p-6 text-white text-center">
            <p className="text-base md:text-lg font-semibold">{cta}</p>
          </div>
        )}
      </div>
    </section>
  );
};

export const getSeoMetaTitle = (data, lang, fallback) => {
  if (!data) return fallback;
  return pickLang(data.seo_title, lang) || fallback;
};

export const getSeoMetaDescription = (data, lang, fallback) => {
  if (!data) return fallback;
  return pickLang(data.seo_description, lang) || fallback;
};

export const getSeoH1 = (data, lang, fallback) => {
  if (!data) return fallback;
  return pickLang(data.seo_h1, lang) || fallback;
};

export default SeoContentBlock;
