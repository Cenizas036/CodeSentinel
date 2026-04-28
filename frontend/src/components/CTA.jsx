import React from 'react';
import './CTA.css';

const CTA = () => {
  const handleClick = () => {
    const el = document.getElementById('analyzer');
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  return (
    <section className="cta" id="cta">
      <div className="container cta__container">
        <div className="cta__badge">
          <span className="tech-label text-emerald">Ready to Deploy</span>
        </div>

        <h2 className="cta__headline font-serif">
          Ready to experience the<br />
          <span className="cta__gradient">CodeSentinel</span> difference?
        </h2>

        <p className="cta__subtitle text-muted">
          Join the elite group of developers building the next generation of web interfaces.
          Start for free, scale to millions.
        </p>

        <div className="cta__actions">
          <button className="btn-pill btn-emerald cta__btn" onClick={handleClick}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z"/>
            </svg>
            Initialize System
          </button>
          <p className="cta__note tech-label" style={{ color: 'rgba(235,235,235,0.3)' }}>
            No credit card required • Free forever tier
          </p>
        </div>
      </div>
    </section>
  );
};

export default CTA;
