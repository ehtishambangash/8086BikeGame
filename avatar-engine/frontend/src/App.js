import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import AvatarsPage from './pages/AvatarsPage';
import CreateAvatarPage from './pages/CreateAvatarPage';
import GeneratePage from './pages/GeneratePage';
import GalleryPage from './pages/GalleryPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-base-100">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/avatars" element={<AvatarsPage />} />
            <Route path="/create-avatar" element={<CreateAvatarPage />} />
            <Route path="/generate" element={<GeneratePage />} />
            <Route path="/gallery" element={<GalleryPage />} />
          </Routes>
        </main>
        <Toaster 
          position="bottom-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1f2937',
              color: '#f9fafb',
              border: '1px solid #374151'
            }
          }}
        />
      </div>
    </Router>
  );
}

export default App;