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
        {/* Hero is always visible — it's the landing page */}
        <Hero onLoginClick={() => setShowAuthModal(true)} user={user} />

        {/* Everything below is gated behind authentication */}
        {user ? (
          <>
            <Analyzer user={user} onLoginClick={() => setShowAuthModal(true)} />
            <FeatureGrid />
            <BenchmarkTable />
          </>
        ) : (
          <section id="analyzer" style={{
            padding: '6rem 0 8rem',
            textAlign: 'center',
            position: 'relative',
            zIndex: 1,
          }}>
            <div className="container" style={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              gap: '1.5rem' 
            }}>
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.2)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '2rem',
              }}>
                🔒
              </div>
              <h2 className="font-serif" style={{ fontSize: 'clamp(1.5rem, 3vw, 2.25rem)' }}>
                Sign in to unlock the IDE
              </h2>
              <p className="text-muted" style={{ maxWidth: '480px', lineHeight: 1.6 }}>
                Access the full CodeSentinel experience — AI-powered code analysis, optimization engine, and Google Drive integration.
              </p>
              <button 
                className="btn-pill btn-emerald" 
                onClick={() => setShowAuthModal(true)}
                style={{ padding: '0.85rem 2.5rem', fontSize: '1rem', marginTop: '0.5rem' }}
              >
                Sign In to Continue
              </button>
            </div>
          </section>
        )}

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
