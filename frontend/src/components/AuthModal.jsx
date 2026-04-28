import React, { useState } from 'react';
import { loginWithGoogle, loginWithEmail, registerWithEmail } from '../services/auth';
import './AuthModal.css';

const AuthModal = ({ isOpen, onClose, onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  if (!isOpen) return null;

  const handleGoogle = async () => {
    setLoading(true);
    setError(null);
    try {
      const { user } = await loginWithGoogle();
      onLogin(user);
      onClose();
    } catch (err) {
      setError(err.message || "Failed to sign in with Google.");
    } finally {
      setLoading(false);
    }
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      if (isLogin) {
        const user = await loginWithEmail(email, password);
        onLogin(user);
        onClose();
      } else {
        await registerWithEmail(email, password);
        setMessage("Registration successful! Please check your email to verify your account before logging in.");
        setIsLogin(true);
        setPassword('');
      }
    } catch (err) {
      setError(err.message || "Authentication failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-modal__overlay">
      <div className="auth-modal">
        <button className="auth-modal__close" onClick={onClose}>×</button>
        
        <div className="auth-modal__header">
          <h2 className="font-serif">{isLogin ? 'Welcome Back' : 'Join CodeSentinel'}</h2>
          <p className="text-muted">
            {isLogin 
              ? 'Sign in to access your cloud IDE and Google Drive.' 
              : 'Create an account to securely sync your code.'}
          </p>
        </div>

        <div className="auth-modal__body">
          <button 
            className="btn-pill auth-modal__google-btn" 
            onClick={handleGoogle}
            disabled={loading}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.16v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.16C1.43 8.55 1 10.22 1 12s.43 3.45 1.16 4.93l3.68-2.84z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.16 7.07l3.68 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Continue with Google
          </button>

          <div className="auth-modal__divider">
            <span className="tech-label">OR</span>
          </div>

          <form onSubmit={handleEmailSubmit} className="auth-modal__form">
            <div className="form-group">
              <label>Email Address</label>
              <input 
                type="email" 
                value={email} 
                onChange={e => setEmail(e.target.value)} 
                required 
                placeholder="you@example.com"
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input 
                type="password" 
                value={password} 
                onChange={e => setPassword(e.target.value)} 
                required 
                placeholder="••••••••"
                minLength="6"
              />
            </div>

            {error && <div className="auth-modal__error">{error}</div>}
            {message && <div className="auth-modal__message">{message}</div>}

            <button type="submit" className="btn-pill btn-emerald auth-modal__submit" disabled={loading}>
              {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Create Account')}
            </button>
          </form>
        </div>

        <div className="auth-modal__footer">
          <p className="text-muted">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button 
              className="auth-modal__toggle" 
              onClick={() => { setIsLogin(!isLogin); setError(null); setMessage(null); }}
            >
              {isLogin ? 'Sign Up' : 'Log In'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
