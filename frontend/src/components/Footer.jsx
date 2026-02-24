import React from 'react';
import { MessageCircle, Mail, Phone, MapPin } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { getTranslation } from '../translations';

const Footer = () => {
  const { lang } = useLanguage();
  const t = (key) => getTranslation(lang, key);
  
  return (
    <footer className="bg-black border-t border-gray-800 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-t from-blue-950/20 to-transparent"></div>
      
      <div className="container mx-auto px-4 py-12 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {/* Logo and Info */}
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xl">G</span>
              </div>
              <div>
                <div className="font-bold text-lg bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">GOLEVENTS</div>
                <div className="text-xs text-gray-500 tracking-wider font-medium">TRAVEL SPORT FUN</div>
              </div>
            </div>
            <p className="text-gray-400 text-sm mb-4">
              {t('footerDescription')}
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-bold text-white mb-4">{t('quickLinks')}</h3>
            <div className="space-y-2">
              <a href="#about" className="block text-gray-400 hover:text-blue-400 text-sm transition-colors">{t('aboutUs')}</a>
              <a href="#events" className="block text-gray-400 hover:text-blue-400 text-sm transition-colors">{t('allEvents')}</a>
              <a href="#calendar" className="block text-gray-400 hover:text-blue-400 text-sm transition-colors">{t('calendar')}</a>
              <a href="#contact" className="block text-gray-400 hover:text-blue-400 text-sm transition-colors">{t('contact')}</a>
            </div>
          </div>

          {/* Legal */}
          <div>
            <h3 className="font-bold text-white mb-4">{t('legal')}</h3>
            <div className="space-y-2">
              <a href="#terms" className="block text-gray-400 hover:text-blue-400 text-sm transition-colors">{t('termsConditions')}</a>
              <a href="#privacy" className="block text-gray-400 hover:text-blue-400 text-sm transition-colors">{t('privacyPolicy')}</a>
              <a href="#refund" className="block text-gray-400 hover:text-blue-400 text-sm transition-colors">{t('refundPolicy')}</a>
              <a href="#cookies" className="block text-gray-400 hover:text-blue-400 text-sm transition-colors">{t('cookiePolicy')}</a>
            </div>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-bold text-white mb-4">{t('getInTouch')}</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-gray-400 text-sm">
                <Mail className="w-4 h-4 text-blue-400" />
                <span>info@golevents.com</span>
              </div>
              <div className="flex items-center gap-2 text-gray-400 text-sm">
                <Phone className="w-4 h-4 text-purple-400" />
                <span>+1 (555) 123-4567</span>
              </div>
              <div className="flex items-center gap-2 text-gray-400 text-sm">
                <MapPin className="w-4 h-4 text-pink-400" />
                <span>Milan, Italy</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 pt-8 border-t border-gray-800">
          <p className="text-gray-500 text-sm">
            © 2026 Golevents. {t('allRightsReserved')}
          </p>
          
          <a
            href="https://wa.me/"
            target="_blank"
            rel="noopener noreferrer"
            className="relative group bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white px-6 py-3 rounded-xl flex items-center gap-2 font-bold transition-all duration-300 shadow-lg shadow-green-500/20 hover:shadow-green-500/40 transform hover:scale-105"
          >
            <span className="absolute inset-0 bg-white/20 rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"></span>
            <MessageCircle className="relative w-5 h-5" />
            <span className="relative">{t('whatsappUs')}</span>
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;