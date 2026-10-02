import { useState, useEffect } from 'react';
import { authAPI } from '../services/api';

/**
 * useAuthGate - token validation, login state and logout.
 * Keeps the auth lifecycle out of the App shell (docs/architecture.md: separate UI concerns).
 */
export default function useAuthGate() {
  const [user, setUser] = useState(null);
  const [authChecked, setAuthChecked] = useState(false); // true once stored token (if any) is validated
  const [needsOnboarding, setNeedsOnboarding] = useState(false); // account exists but details are missing

  useEffect(() => {
    const token = localStorage.getItem('krishi_token');
    if (!token) {
      setAuthChecked(true);
      return;
    }
    authAPI
      .getMe()
      .then((u) => {
        setUser(u);
        setAuthChecked(true);
        setNeedsOnboarding(!u.profile_completed);
      })
      .catch(() => {
        localStorage.removeItem('krishi_token');
        setUser(null);
        setAuthChecked(true);
      });
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('krishi_token');
    setUser(null);
    setNeedsOnboarding(false);
  };

  return { user, setUser, authChecked, needsOnboarding, setNeedsOnboarding, handleLogout };
}
