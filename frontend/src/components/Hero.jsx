import React from 'react';
import './Hero.css';

const Hero = () => {
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <section className="hero" id="hero">
      <div className="container hero__grid">
        {/* Left Column */}
        <div className="hero__content">
          <div className="hero__label">
            <span className="hero__pulse-dot"></span>
            <span className="tech-label text-emerald">System v2.4 Online</span>
          </div>

          <h1 className="hero__title font-serif tracking-tighter">
            The Future of<br />
            Digital <em className="hero__italic text-emerald">Elegance</em>
          </h1>

          <p className="hero__subtitle">
            A classical-tech hybrid experience. Blending the timeless beauty
            of editorial typography with the high-performance utility of modern interfaces.
          </p>

          <div className="hero__actions">
            <button className="btn-pill btn-emerald hero__btn-primary" onClick={() => scrollTo('analyzer')}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
              Start Analyzing
            </button>
            <button className="btn-pill btn-ghost" onClick={() => scrollTo('features')}>
              View Features
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/></svg>
            </button>
          </div>

          <div className="hero__stats">
            <div className="hero__stat">
              <span className="hero__stat-value font-mono text-emerald">99.9%</span>
              <span className="hero__stat-label tech-label">Uptime</span>
            </div>
            <div className="hero__stat-divider"></div>
            <div className="hero__stat">
              <span className="hero__stat-value font-mono text-emerald">12ms</span>
              <span className="hero__stat-label tech-label">Latency</span>
            </div>
            <div className="hero__stat-divider"></div>
            <div className="hero__stat">
              <span className="hero__stat-value font-mono text-emerald">50k+</span>
              <span className="hero__stat-label tech-label">Users</span>
            </div>
          </div>
        </div>

        {/* Right Column — Floating UI Mockup */}
        <div className="hero__visual">
          <div className="hero__mockup">
            {/* Main card */}
            <div className="hero__card hero__card--main">
              <div className="hero__card-dots">
                <span></span><span></span><span></span>
              </div>
              <div className="hero__card-lines">
                <div className="hero__line" style={{ width: '75%' }}></div>
                <div className="hero__line" style={{ width: '100%' }}></div>
                <div className="hero__line" style={{ width: '60%' }}></div>
                <div className="hero__line" style={{ width: '85%' }}></div>
                <div className="hero__line" style={{ width: '45%' }}></div>
              </div>
              <div className="hero__card-code">
                <span className="tech-label text-emerald">{'>'} sentinel.analyze()</span>
              </div>
            </div>

            {/* Stats card */}
            <div className="hero__card hero__card--stats">
              <span className="tech-label" style={{ color: 'rgba(235,235,235,0.4)' }}>Latency</span>
              <span className="hero__card-value font-mono text-emerald">12ms</span>
              <div className="hero__card-bar">
                <div className="hero__card-bar-fill"></div>
              </div>
            </div>

            {/* Floating orb */}
            <div className="hero__orb"></div>

            {/* Status badge */}
            <div className="hero__card hero__card--badge">
              <div className="hero__badge-dot"></div>
              <span className="tech-label">All systems operational</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
