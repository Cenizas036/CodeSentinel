import React from 'react';
import SpotlightCard from './SpotlightCard';
import './FeatureGrid.css';

const FeatureGrid = () => {
  const features = [
    {
      title: 'Editorial Precision',
      description: 'Harness the power of classical serif typography to deliver content with unmatched authority and elegance across every screen.',
      icon: (
        <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" />
        </svg>
      ),
    },
    {
      title: 'Quantum Performance',
      description: 'Engineered for speed. A highly optimized architecture that feels instantaneous, matching your speed of thought.',
      icon: (
        <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
    },
    {
      title: 'Tactile Intelligence',
      description: 'Responsive components that react organically to your interactions, turning static screens into living interfaces.',
      icon: (
        <svg width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5" />
        </svg>
      ),
    },
  ];

  return (
    <section className="features" id="features">
      <div className="container">
        <div className="features__header">
          <span className="tech-label text-emerald">Capabilities</span>
          <h2 className="features__title font-serif">Surgical Precision</h2>
          <p className="features__subtitle">
            Every element is crafted with intent. No superfluous lines, just raw utility wrapped in a beautiful aesthetic.
          </p>
        </div>

        <div className="features__grid">
          {features.map((feature, index) => (
            <SpotlightCard
              key={index}
              title={feature.title}
              description={feature.description}
              icon={feature.icon}
              delay={index * 0.15}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeatureGrid;
