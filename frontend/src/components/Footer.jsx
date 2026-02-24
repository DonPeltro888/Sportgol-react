import React from 'react';
import { MessageCircle } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white py-12 px-4">
      <div className="container mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-center gap-6">
          {/* Logo and Info */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-purple-500 to-orange-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold text-lg">G</span>
            </div>
            <div>
              <div className="font-bold text-lg">GOLEVENTS</div>
              <div className="text-xs text-gray-400 tracking-wider">TRAVEL SPORT FUN</div>
            </div>
          </div>

          {/* Links */}
          <div className="flex flex-wrap justify-center gap-6 text-sm">
            <a href="#about" className="hover:text-blue-400 transition-colors">About Us</a>
            <a href="#contact" className="hover:text-blue-400 transition-colors">Contact</a>
            <a href="#terms" className="hover:text-blue-400 transition-colors">Terms & Conditions</a>
            <a href="#privacy" className="hover:text-blue-400 transition-colors">Privacy Policy</a>
          </div>

          {/* WhatsApp Button */}
          <a
            href="https://wa.me/"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-full flex items-center gap-2 font-semibold transition-all duration-300 hover:shadow-lg"
          >
            <MessageCircle className="w-5 h-5" />
            WHATSAPP US
          </a>
        </div>

        {/* Copyright */}
        <div className="text-center text-gray-400 text-sm mt-8 pt-8 border-t border-gray-800">
          <p>© 2026 Golevents. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
