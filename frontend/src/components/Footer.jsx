import React from 'react';
import './Footer.css';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="container">
        <div className="footer__top">
          <div className="footer__brand">
            <div className="footer__logo">
              <div className="footer__logo-icon">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3H6a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3V6a3 3 0 0 0-3-3 3 3 0 0 0-3 3 3 3 0 0 0 3 3h12a3 3 0 0 0 3-3 3 3 0 0 0-3-3z" />
                </svg>
              </div>
              <span className="font-serif">CodeSentinel</span>
            </div>
            <p className="footer__tagline text-muted">
              Classical elegance meets modern performance.
            </p>
          </div>

          <div className="footer__links-group">
            <div className="footer__col">
              <h4 className="footer__col-title tech-label">Product</h4>
              <a href="#features" className="footer__link">Features</a>
              <a href="#performance" className="footer__link">Performance</a>
              <a href="#cta" className="footer__link">Get Access</a>
            </div>
            <div className="footer__col">
              <h4 className="footer__col-title tech-label">Company</h4>
              <a href="#" className="footer__link">About</a>
              <a href="#" className="footer__link">Blog</a>
              <a href="#" className="footer__link">Careers</a>
            </div>
            <div className="footer__col">
              <h4 className="footer__col-title tech-label">Connect</h4>
              <a href="#" className="footer__link">GitHub</a>
              <a href="#" className="footer__link">Twitter</a>
              <a href="#" className="footer__link">Discord</a>
            </div>
          </div>
        </div>

        <div className="footer__bottom">
          <p className="footer__copy text-muted">
            &copy; {currentYear} CodeSentinel. All rights reserved.
          </p>
          <div className="footer__bottom-links">
            <a href="#" className="footer__link">Privacy Policy</a>
            <a href="#" className="footer__link">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
