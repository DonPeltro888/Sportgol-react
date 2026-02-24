import React, { useState, useEffect } from 'react';
import AdminLayout from '../../components/admin/AdminLayout';
import { useAdminAuth } from '../../contexts/AdminAuthContext';
import { Calendar, FolderTree, TrendingUp, Star, Trophy } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

const AdminDashboard = () => {
  const { authFetch } = useAdminAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await authFetch(`${API_URL}/api/admin/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ icon: Icon, label, value, color }) => (
    <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm">{label}</p>
          <p className="text-3xl font-bold text-white mt-1">{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-gray-400">Panoramica del sistema</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard 
            icon={Calendar} 
            label="Eventi Totali" 
            value={stats?.total_events || 0} 
            color="bg-blue-600"
          />
          <StatCard 
            icon={FolderTree} 
            label="Categorie" 
            value={stats?.total_categories || 0} 
            color="bg-purple-600"
          />
          <StatCard 
            icon={Star} 
            label="In Evidenza" 
            value={stats?.featured_events || 0} 
            color="bg-yellow-600"
          />
          <StatCard 
            icon={Trophy} 
            label="Campionati" 
            value={stats?.events_by_league?.length || 0} 
            color="bg-green-600"
          />
        </div>

        {/* Events by League */}
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Eventi per Campionato</h2>
          </div>
          <div className="divide-y divide-gray-700">
            {stats?.events_by_league?.map((league, index) => (
              <div key={index} className="px-6 py-4 flex items-center justify-between">
                <span className="text-gray-300">{league._id || 'N/A'}</span>
                <span className="text-blue-400 font-semibold">{league.count} eventi</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <a 
            href="/admin/events" 
            className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 rounded-xl p-6 text-white transition-all"
          >
            <Calendar className="w-8 h-8 mb-3" />
            <h3 className="font-semibold text-lg">Gestisci Eventi</h3>
            <p className="text-blue-200 text-sm mt-1">Aggiungi, modifica o elimina eventi</p>
          </a>
          <a 
            href="/admin/categories" 
            className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 rounded-xl p-6 text-white transition-all"
          >
            <FolderTree className="w-8 h-8 mb-3" />
            <h3 className="font-semibold text-lg">Categorie Menu</h3>
            <p className="text-purple-200 text-sm mt-1">Organizza i campionati e le coppe</p>
          </a>
          <a 
            href="/admin/translations" 
            className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 rounded-xl p-6 text-white transition-all"
          >
            <TrendingUp className="w-8 h-8 mb-3" />
            <h3 className="font-semibold text-lg">Traduzioni</h3>
            <p className="text-green-200 text-sm mt-1">Gestisci i contenuti multilingua</p>
          </a>
        </div>
      </div>
    </AdminLayout>
  );
};

export default AdminDashboard;
