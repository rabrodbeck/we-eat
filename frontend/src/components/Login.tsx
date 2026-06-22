import React, { useState } from 'react';
import { auth, googleProvider, signInWithPopup } from '../firebase';

interface UserData {
  uid: string;
  email: string | null;
  displayName: string | null;
  token: string;
}

interface LoginProps {
  onLoginSuccess: (user: UserData) => void;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGoogleSignIn = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const token = await result.user.getIdToken();
      onLoginSuccess({
        uid: result.user.uid,
        email: result.user.email,
        displayName: result.user.displayName,
        token: token
      });
    } catch (err: any) {
      setError(err.message || 'Failed to sign in with Google');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoSignIn = () => {
    onLoginSuccess({
      uid: 'user123',
      email: 'mock-user123@example.com',
      displayName: 'Mock User',
      token: 'mock-user123'
    });
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>Welcome to WeEat</h2>
        <p className="subtitle">Plan your family meals without the vetoes</p>
        
        {error && <div className="error-message">{error}</div>}
        
        <button
          onClick={handleGoogleSignIn}
          disabled={loading}
          className="google-signin-btn"
        >
          {loading ? 'Connecting...' : 'Sign in with Google'}
        </button>
        
        <div className="divider">
          <span>or</span>
        </div>
        
        <button
          onClick={handleDemoSignIn}
          className="demo-signin-btn"
        >
          Demo Sign In (Offline Bypass)
        </button>
      </div>
    </div>
  );
};

export default Login;