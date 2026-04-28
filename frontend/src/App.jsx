import React, { useState, useEffect } from 'react';
import BackgroundGlow from './components/BackgroundGlow';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Analyzer from './components/Analyzer';
import FeatureGrid from './components/FeatureGrid';
import BenchmarkTable from './components/BenchmarkTable';
import CTA from './components/CTA';
import Footer from './components/Footer';
import AuthModal from './components/AuthModal';
import { subscribeToAuthChanges, logout } from './services/auth';

function App() {
  const [user, setUser] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authInitialized, setAuthInitialized] = useState(false);

  useEffect(() => {
    const unsubscribe = subscribeToAuthChanges((currentUser) => {
      setUser(currentUser);
      setAuthInitialized(true);
    });
    return () => unsubscribe();
  }, []);

  const handleLogout = async () => {
    await logout();
    setUser(null);
  };

  return (
    <>
      <BackgroundGlow />
      <Navbar 
        user={user} 
        onLoginClick={() => setShowAuthModal(true)} 
        onLogoutClick={handleLogout} 
      />
      <main>
        <Hero onLoginClick={() => setShowAuthModal(true)} user={user} />
        <Analyzer user={user} onLoginClick={() => setShowAuthModal(true)} />
        <FeatureGrid />
        <BenchmarkTable />
        <CTA />
      </main>
      <Footer />
      
      {authInitialized && (
        <AuthModal 
          isOpen={showAuthModal} 
          onClose={() => setShowAuthModal(false)}
          onLogin={(u) => setUser(u)}
        />
      )}
    </>
  );
}

export default App;
