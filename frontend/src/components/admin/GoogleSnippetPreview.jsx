import React from 'react';
import { Globe, ExternalLink } from 'lucide-react';

const GoogleSnippetPreview = ({ 
  title = '', 
  description = '', 
  url = '',
  lang = 'it',
  type = 'event' // 'event', 'page', 'team', 'league'
}) => {
  
  const baseUrl = 'https://sports-events-hub.preview.emergentagent.com';
  
  // Truncate title to 60 chars (Google limit)
  const displayTitle = title.length > 60 
    ? title.substring(0, 57) + '...' 
    : title || 'Titolo pagina';
  
  // Truncate description to 160 chars
  const displayDescription = description.length > 160 
    ? description.substring(0, 157) + '...' 
    : description || 'Descrizione della pagina che apparirà nei risultati di ricerca...';
  
  // Generate URL
  const displayUrl = url 
    ? `${baseUrl}/${lang}/${url}`.toLowerCase().replace(/\s+/g, '-')
    : `${baseUrl}/${lang}/${type}/...`;

  // Character counts
  const titleLength = title.length;
  const descLength = description.length;
  const titleStatus = titleLength === 0 ? 'empty' : titleLength <= 60 ? 'good' : 'warning';
  const descStatus = descLength === 0 ? 'empty' : descLength <= 160 ? 'good' : 'warning';

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-2 text-gray-400">
        <Globe className="w-4 h-4" />
        <span className="text-sm font-medium">Anteprima Google ({lang.toUpperCase()})</span>
      </div>
      
      {/* Google Preview Card */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        {/* URL */}
        <div className="flex items-center gap-1 mb-1">
          <div className="w-7 h-7 bg-gray-100 rounded-full flex items-center justify-center">
            <span className="text-xs font-bold text-blue-600">G</span>
          </div>
          <div className="flex flex-col">
            <span className="text-sm text-gray-800">GOLEVENTS</span>
            <span className="text-xs text-gray-500 truncate max-w-[400px]">{displayUrl}</span>
          </div>
        </div>
        
        {/* Title */}
        <h3 className="text-xl text-[#1a0dab] hover:underline cursor-pointer font-normal leading-tight mb-1">
          {displayTitle}
        </h3>
        
        {/* Description */}
        <p className="text-sm text-gray-600 leading-relaxed">
          {displayDescription}
        </p>
      </div>
      
      {/* Character Counts */}
      <div className="flex gap-6 text-xs">
        <div className="flex items-center gap-2">
          <span className="text-gray-400">Title:</span>
          <span className={`font-medium ${
            titleStatus === 'good' ? 'text-green-400' : 
            titleStatus === 'warning' ? 'text-yellow-400' : 'text-gray-500'
          }`}>
            {titleLength}/60
          </span>
          {titleStatus === 'good' && <span className="text-green-400">✓</span>}
          {titleStatus === 'warning' && <span className="text-yellow-400">⚠</span>}
        </div>
        
        <div className="flex items-center gap-2">
          <span className="text-gray-400">Description:</span>
          <span className={`font-medium ${
            descStatus === 'good' ? 'text-green-400' : 
            descStatus === 'warning' ? 'text-yellow-400' : 'text-gray-500'
          }`}>
            {descLength}/160
          </span>
          {descStatus === 'good' && <span className="text-green-400">✓</span>}
          {descStatus === 'warning' && <span className="text-yellow-400">⚠</span>}
        </div>
      </div>
      
      {/* Tips */}
      {(titleStatus === 'warning' || descStatus === 'warning') && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 text-xs text-yellow-400">
          <strong>Suggerimento:</strong> Testi più lunghi potrebbero essere troncati nei risultati di ricerca.
          {titleStatus === 'warning' && ' Riduci il titolo a max 60 caratteri.'}
          {descStatus === 'warning' && ' Riduci la descrizione a max 160 caratteri.'}
        </div>
      )}
      
      {(titleStatus === 'empty' || descStatus === 'empty') && (
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 text-xs text-blue-400">
          <strong>Info:</strong> Compila i campi SEO per migliorare la visibilità sui motori di ricerca.
        </div>
      )}
    </div>
  );
};

// Social Preview Component (Facebook/Twitter)
export const SocialPreview = ({
  title = '',
  description = '',
  image = '',
  platform = 'facebook' // 'facebook' or 'twitter'
}) => {
  const displayTitle = title || 'Titolo pagina';
  const displayDescription = description.length > 100 
    ? description.substring(0, 97) + '...' 
    : description || 'Descrizione della pagina...';

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-gray-400">
        <span className="text-sm font-medium">
          Anteprima {platform === 'facebook' ? 'Facebook' : 'Twitter'}
        </span>
      </div>
      
      <div className={`bg-white rounded-lg overflow-hidden border border-gray-200 ${
        platform === 'twitter' ? 'max-w-[400px]' : ''
      }`}>
        {/* Image */}
        <div className={`bg-gray-200 ${platform === 'twitter' ? 'h-48' : 'h-52'} flex items-center justify-center`}>
          {image ? (
            <img src={image} alt="Preview" className="w-full h-full object-cover" />
          ) : (
            <div className="text-gray-400 text-sm">Nessuna immagine OG</div>
          )}
        </div>
        
        {/* Content */}
        <div className="p-3">
          <p className="text-xs text-gray-500 uppercase mb-1">golevents.com</p>
          <h4 className="text-gray-900 font-semibold text-sm leading-tight mb-1">
            {displayTitle}
          </h4>
          <p className="text-gray-500 text-xs leading-relaxed">
            {displayDescription}
          </p>
        </div>
      </div>
    </div>
  );
};

export default GoogleSnippetPreview;
