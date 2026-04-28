import React from 'react';
import './BackgroundGlow.css';

const BackgroundGlow = () => {
  return (
    <div className="background-glow-wrapper" aria-hidden="true">
      <div className="morphing-glow glow-1"></div>
      <div className="morphing-glow glow-2"></div>
      <div className="morphing-glow glow-3"></div>
    </div>
  );
};

export default BackgroundGlow;
