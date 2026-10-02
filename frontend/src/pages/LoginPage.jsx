import React, { useState } from 'react';
import { authAPI } from '../services/api';

/**
 * LoginPage handles three modes:
 *   1. "login"     - sign in with email OR username + password
 *   2. "signup"    - step 1: email + username + password
 *   3. "details"   - step 2 onboarding: full name, age, role (Farmer/Officer)
 *
 * After signup, the user is prompted for basic details, then routed to the
 * Farmer or Officer portal based on the selected role.
 */
export default function LoginPage({ onAuthSuccess, initialMode = 'login' }) {
  const [mode, setMode] = useState(initialMode); // 'login' | 'signup' | 'details'
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // login form
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');

  // signup form (step 1)
  const [suEmail, setSuEmail] = useState('');
  const [suUsername, setSuUsername] = useState('');
  const [suPassword, setSuPassword] = useState('');
  const [suConfirm, setSuConfirm] = useState('');

  // onboarding form (step 2)
  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState('');
  const [role, setRole] = useState('FARMER');
  const [phone, setPhone] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (!identifier.trim() || !password) {
      setErrorMsg('Please enter your email/username and password.');
      return;
    }

    setLoading(true);
    try {
      const res = await authAPI.login(identifier.trim(), password);
      onAuthSuccess(res);
    } catch (err) {
      setErrorMsg(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (!suEmail.trim() || !suUsername.trim() || !suPassword) {
      setErrorMsg('Email, username and password are all required.');
      return;
    }
    if (suPassword.length < 6) {
      setErrorMsg('Password must be at least 6 characters.');
      return;
    }
    if (suPassword !== suConfirm) {
      setErrorMsg('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const res = await authAPI.register({
        email: suEmail.trim(),
        username: suUsername.trim(),
        password: suPassword,
      });
      // Store the token now so the authenticated details (onboarding) call works
      localStorage.setItem('krishi_token', res.access_token);
      // Account created - move to the basic details (onboarding) step
      setMode('details');
    } catch (err) {
      setErrorMsg(err.message || 'Signup failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDetails = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    const ageNum = parseInt(age, 10);
    if (!fullName.trim()) {
      setErrorMsg('Please enter your full name.');
      return;
    }
    if (!age || isNaN(ageNum) || ageNum < 10 || ageNum > 120) {
      setErrorMsg('Please enter a valid age (10-120).');
      return;
    }

    setLoading(true);
    try {
      const res = await authAPI.updateDetails({
        full_name: fullName.trim(),
        age: ageNum,
        role: role,
        phone: phone.trim() || null,
      });
      onAuthSuccess(res);
    } catch (err) {
      setErrorMsg(err.message || 'Could not save your details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-panel">
        <div className="auth-brand">
          <div className="auth-brand-icon">🌱</div>
          <div>
            <div className="auth-brand-title">KrishiSahayak AI</div>
            <div className="auth-brand-sub">AI-Assisted, Officer-Verified Agricultural Administration</div>
          </div>
        </div>

        {errorMsg && <div className="auth-error">⚠️ {errorMsg}</div>}

        {/* ================= LOGIN ================= */}
        {mode === 'login' && (
          <form onSubmit={handleLogin}>
            <h2 className="auth-title">Welcome back</h2>
            <p className="auth-subtitle">Sign in to your account to continue.</p>

            <div className="ks-form-group">
              <label className="ks-label">Email or Username</label>
              <input
                className="ks-input"
                type="text"
                placeholder="you@example.com or username"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                autoComplete="username"
                required
              />
            </div>

            <div className="ks-form-group">
              <label className="ks-label">Password</label>
              <input
                className="ks-input"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </div>

            <button type="submit" className="ks-btn ks-btn-primary auth-submit" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign In'}
            </button>

            <p className="auth-switch">
              New to KrishiSahayak?{' '}
              <button type="button" className="auth-link" onClick={() => { setMode('signup'); setErrorMsg(''); }}>
                Create an account
              </button>
            </p>

            <div className="auth-demo">
              <strong>Demo accounts:</strong><br />
              👨‍🌾 Farmer — <code>farmer</code> / farmer123<br />
              🏛️ Officer — <code>officer</code> / officer123
            </div>
          </form>
        )}

        {/* ================= SIGNUP (STEP 1) ================= */}
        {mode === 'signup' && (
          <form onSubmit={handleSignup}>
            <h2 className="auth-title">Create your account</h2>
            <p className="auth-subtitle">Step 1 of 2 — account credentials. You'll add your basic details next.</p>

            <div className="ks-form-group">
              <label className="ks-label">Email Address</label>
              <input
                className="ks-input"
                type="email"
                placeholder="you@example.com"
                value={suEmail}
                onChange={(e) => setSuEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>

            <div className="ks-form-group">
              <label className="ks-label">Username</label>
              <input
                className="ks-input"
                type="text"
                placeholder="e.g. ramanan_nair"
                value={suUsername}
                onChange={(e) => setSuUsername(e.target.value)}
                autoComplete="username"
                required
              />
            </div>

            <div className="ks-form-group">
              <label className="ks-label">Password</label>
              <input
                className="ks-input"
                type="password"
                placeholder="Minimum 6 characters"
                value={suPassword}
                onChange={(e) => setSuPassword(e.target.value)}
                autoComplete="new-password"
                required
              />
            </div>

            <div className="ks-form-group">
              <label className="ks-label">Confirm Password</label>
              <input
                className="ks-input"
                type="password"
                placeholder="Re-enter your password"
                value={suConfirm}
                onChange={(e) => setSuConfirm(e.target.value)}
                autoComplete="new-password"
                required
              />
            </div>

            <button type="submit" className="ks-btn ks-btn-primary auth-submit" disabled={loading}>
              {loading ? 'Creating account...' : 'Continue →'}
            </button>

            <p className="auth-switch">
              Already have an account?{' '}
              <button type="button" className="auth-link" onClick={() => { setMode('login'); setErrorMsg(''); }}>
                Sign in
              </button>
            </p>
          </form>
        )}

        {/* ================= BASIC DETAILS (STEP 2 ONBOARDING) ================= */}
        {mode === 'details' && (
          <form onSubmit={handleDetails}>
            <h2 className="auth-title">Complete your profile</h2>
            <p className="auth-subtitle">Step 2 of 2 — tell us a bit about yourself so we can tailor your experience.</p>

            <div className="ks-form-group">
              <label className="ks-label">Full Name</label>
              <input
                className="ks-input"
                type="text"
                placeholder="e.g. Ramanan Nair"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>

            <div className="ks-form-group">
              <label className="ks-label">Age</label>
              <input
                className="ks-input"
                type="number"
                min="10"
                max="120"
                placeholder="e.g. 35"
                value={age}
                onChange={(e) => setAge(e.target.value)}
                required
              />
            </div>

            <div className="ks-form-group">
              <label className="ks-label">I am registering as a...</label>
              <div className="auth-role-cards">
                <button
                  type="button"
                  className={`auth-role-card ${role === 'FARMER' ? 'selected' : ''}`}
                  onClick={() => setRole('FARMER')}
                >
                  <span className="auth-role-icon">👨‍🌾</span>
                  <span className="auth-role-name">Farmer</span>
                  <span className="auth-role-desc">Get AI crop diagnosis, officer-verified guidance & subsidies</span>
                </button>
                <button
                  type="button"
                  className={`auth-role-card ${role === 'OFFICER' ? 'selected' : ''}`}
                  onClick={() => setRole('OFFICER')}
                >
                  <span className="auth-role-icon">🏛️</span>
                  <span className="auth-role-name">Agricultural Officer</span>
                  <span className="auth-role-desc">Review cases, verify diagnoses & approve subsidies</span>
                </button>
              </div>
            </div>

            <div className="ks-form-group">
              <label className="ks-label">Phone (optional)</label>
              <input
                className="ks-input"
                type="tel"
                placeholder="+91 ..."
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>

            <button type="submit" className="ks-btn ks-btn-primary auth-submit" disabled={loading}>
              {loading ? 'Saving...' : role === 'FARMER' ? '🌾 Enter Farmer Portal' : '🏛️ Enter Officer Portal'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
