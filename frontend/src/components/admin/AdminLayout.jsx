import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { 
  LayoutDashboard, Calendar, FolderTree, FileText, 
  Globe, Settings, Languages, LogOut, Menu, X, ChevronDown, Layers, Trophy, RefreshCw, Image as ImageIcon, Key, Database, Sparkles, Wrench
} from 'lucide-react';

const AdminLayout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, logout } = useAdminAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    { path: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/admin/sync', label: 'Sync matchesio.com', icon: RefreshCw },
    { path: '/admin/providers', label: 'Provider & Coverage', icon: Database },
    { path: '/admin/integrations', label: 'Integrazioni API', icon: Key },
    { path: '/admin/teams-logos', label: 'Squadre & Loghi', icon: ImageIcon },
    { path: '/admin/events', label: 'Eventi', icon: Calendar },
    { path: '/admin/sectors', label: 'Settori & Prezzi', icon: Layers },
    { path: '/admin/leagues-teams', label: 'Leghe & Squadre', icon: Trophy },
    { path: '/admin/categories', label: 'Categorie Menu', icon: FolderTree },
    { path: '/admin/pages', label: 'Pagine & Testi', icon: FileText },
    { path: '/admin/seo', label: 'SEO', icon: Globe },
    { path: '/admin/data-tools', label: 'Data Tools', icon: Wrench },
    { path: '/admin/translations', label: 'Traduzioni', icon: Languages },
    { path: '/admin/settings', label: 'Impostazioni', icon: Settings },
  ];

  const handleLogout = () => {
    logout();
    navigate('/admin/login');
  };

  const isActive = (path) => {
    // /admin/seo evidenziato anche su sotto-route /admin/seo/api-tools, /admin/seo/pages, ecc
    if (path === '/admin/seo') return location.pathname.startsWith('/admin/seo');
    if (path === '/admin/data-tools') return location.pathname.startsWith('/admin/data-tools');
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-gray-900 flex">
      {/* Desktop Sidebar */}
      <aside className={`hidden lg:flex flex-col ${sidebarOpen ? 'w-64' : 'w-20'} bg-gray-800 border-r border-gray-700 transition-all duration-300`}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-700">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-sm">G</span>
              </div>
              <span className="text-white font-bold">Admin</span>
            </div>
          )}
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-gray-400 hover:text-white p-1"
          >
            <Menu className="w-5 h-5" />
          </button>
        </div>

        {/* Menu */}
        <nav className="flex-1 py-4 overflow-y-auto">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 mx-2 rounded-lg transition-colors ${
                isActive(item.path) 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:bg-gray-700 hover:text-white'
              }`}
            >
              <item.icon className="w-5 h-5 flex-shrink-0" />
              {sidebarOpen && <span className="text-sm font-medium">{item.label}</span>}
            </Link>
          ))}
        </nav>

        {/* User & Logout */}
        <div className="p-4 border-t border-gray-700">
          {sidebarOpen ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">{user?.username?.[0]?.toUpperCase()}</span>
                </div>
                <span className="text-gray-300 text-sm">{user?.username}</span>
              </div>
              <button 
                onClick={handleLogout}
                className="text-gray-400 hover:text-red-400 transition-colors"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <button 
              onClick={handleLogout}
              className="w-full flex justify-center text-gray-400 hover:text-red-400 transition-colors"
            >
              <LogOut className="w-5 h-5" />
            </button>
          )}
        </div>
      </aside>

      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 h-16 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4 z-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-sm">G</span>
          </div>
          <span className="text-white font-bold">Admin</span>
        </div>
        <button 
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="text-gray-400 hover:text-white"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-0 top-16 bg-gray-800 z-40 overflow-y-auto">
          <nav className="py-4">
            {menuItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-6 py-4 ${
                  isActive(item.path) 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </Link>
            ))}
            <button 
              onClick={handleLogout}
              className="w-full flex items-center gap-3 px-6 py-4 text-red-400 hover:bg-gray-700"
            >
              <LogOut className="w-5 h-5" />
              <span className="font-medium">Logout</span>
            </button>
          </nav>
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 lg:overflow-y-auto">
        <div className="lg:hidden h-16"></div> {/* Spacer for mobile header */}
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  );
};

export default AdminLayout;
