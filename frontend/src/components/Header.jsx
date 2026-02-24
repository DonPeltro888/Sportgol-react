import React, { useState } from 'react';
import { Menu, X, ChevronDown } from 'lucide-react';

const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const menuItems = [
    { label: 'EVENTS', href: '#events' },
    { label: 'SERIE A', href: '#', hasDropdown: true },
    { label: 'PREMIER LEAGUE', href: '#', hasDropdown: true },
    { label: 'SPANISH LEAGUE', href: '#', hasDropdown: true },
    { label: 'CHAMPIONS LEAGUE', href: '#' },
    { label: 'CALENDAR', href: '#calendar' },
    { label: 'ABOUT US', href: '#about' },
  ];

  return (
    <header className="bg-white shadow-sm sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <div className="flex items-center">
            <div className="flex items-center gap-2">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 via-purple-500 to-orange-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-xl">G</span>
              </div>
              <div>
                <div className="font-bold text-xl text-blue-600">GOLEVENTS</div>
                <div className="text-xs text-gray-600 tracking-wider">TRAVEL SPORT FUN</div>
              </div>
            </div>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-6">
            {menuItems.map((item, index) => (
              <div key={index} className="relative group">
                <a
                  href={item.href}
                  className="text-gray-700 hover:text-blue-600 font-medium text-sm flex items-center gap-1 transition-colors"
                >
                  {item.label}
                  {item.hasDropdown && <ChevronDown className="w-4 h-4" />}
                </a>
              </div>
            ))}
            <button className="flex items-center gap-2 text-gray-700 hover:text-blue-600 transition-colors">
              <img
                src="https://flagcdn.com/w20/gb.png"
                alt="English"
                className="w-5 h-4"
              />
              <ChevronDown className="w-4 h-4" />
            </button>
          </nav>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 text-gray-700 hover:text-blue-600"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="lg:hidden pb-4 border-t">
            {menuItems.map((item, index) => (
              <a
                key={index}
                href={item.href}
                className="block py-3 text-gray-700 hover:text-blue-600 font-medium text-sm"
              >
                {item.label}
              </a>
            ))}
          </nav>
        )}
      </div>
    </header>
  );
};

export default Header;
