/**
 * SeoSchemaInjector — inietta il JSON-LD @graph generato dal SEO Admin
 * nel <head> della pagina pubblica. Fallisce silente se non c'è schema.
 *
 * Uso: <SeoSchemaInjector schema={data.seo_meta_schema_jsonld} />
 *
 * Inserisce un <script type="application/ld+json"> nel head con id="seo-graph-jsonld".
 * Cleanup automatico al cambio pagina.
 */
import { useEffect } from 'react';

const SCRIPT_ID = 'seo-graph-jsonld';

const SeoSchemaInjector = ({ schema }) => {
  useEffect(() => {
    if (!schema || typeof schema !== 'object') return;
    // Ensure has @graph or @type
    const hasGraph = schema['@graph'] && Array.isArray(schema['@graph']) && schema['@graph'].length > 0;
    const hasType = schema['@type'];
    if (!hasGraph && !hasType) return;

    let el = document.getElementById(SCRIPT_ID);
    if (!el) {
      el = document.createElement('script');
      el.type = 'application/ld+json';
      el.id = SCRIPT_ID;
      document.head.appendChild(el);
    }
    try {
      el.textContent = JSON.stringify(schema);
    } catch (e) {
      // fail silently
    }

    return () => {
      const node = document.getElementById(SCRIPT_ID);
      if (node) node.remove();
    };
  }, [schema]);

  return null;
};

export default SeoSchemaInjector;
