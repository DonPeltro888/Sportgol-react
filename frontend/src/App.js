import React, { useEffect } from 'react';
import './App.css';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import EventDetail from './pages/EventDetail';
import TeamPage from './pages/TeamPage';
import LeaguePage from './pages/LeaguePage';
import { Toaster } from './components/ui/sonner';

function App() {
  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  return (
    <Router>
      <div className="App min-h-screen bg-black">
        <Toaster position="top-right" richColors />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/event/:id" element={<EventDetail />} />
          <Route path="/team/:slug" element={<TeamPage />} />
          <Route path="/league/:league" element={<LeaguePage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
