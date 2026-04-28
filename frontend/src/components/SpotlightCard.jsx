import React, { useRef, useState } from 'react';
import './SpotlightCard.css';

const SpotlightCard = ({ icon, title, description, delay = 0 }) => {
  const cardRef = useRef(null);
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    cardRef.current.style.setProperty('--mouse-x', `${x}px`);
    cardRef.current.style.setProperty('--mouse-y', `${y}px`);
  };

  return (
    <div
      className="spotlight-card"
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      style={{ animationDelay: `${delay}s` }}
    >
      {/* Shimmer border pseudo-element is handled via CSS */}
      
      {/* Spotlight radial glow */}
      <div
        className="spotlight-card__glow"
        style={{ opacity: isHovered ? 1 : 0 }}
      ></div>

      {/* Card inner content */}
      <div className="spotlight-card__inner">
        <div className={`spotlight-card__icon ${isHovered ? 'spotlight-card__icon--active' : ''}`}>
          {icon}
        </div>
        <h3 className="spotlight-card__title font-serif">{title}</h3>
        <p className="spotlight-card__desc">{description}</p>
      </div>
    </div>
  );
};

export default SpotlightCard;
