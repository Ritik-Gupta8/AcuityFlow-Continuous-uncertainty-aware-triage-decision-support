import React, { useState } from 'react';
import { Activity, ShieldAlert, Lock, UserCheck, ArrowRight, Shield, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import type { User } from '../types';

interface LoginPageProps {
  onLoginSuccess: (user: User) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('nurse101');
  const [password, setPassword] = useState('Password@123');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.login({ username: username.trim(), password });
      const user = await api.getMe();
      onLoginSuccess(user);
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSelect = (uName: string) => {
    setUsername(uName);
    setPassword('Password@123');
    setError(null);
  };

  return (
    <div className="login-page-wrapper">
      {/* Prototype Safety Disclaimer Banner */}
      <div className="disclaimer-banner">
        <ShieldAlert size={15} />
        <span>
          <strong>CONCEPT PROTOTYPE</strong> — Synthetic Data • Not for clinical diagnosis or treatment • Continuous decision-support prototype
        </span>
      </div>

      <div className="login-container">
        {/* Left / Top Hero Section */}
        <div className="login-hero-card">
          <div className="login-brand-header">
            <div className="brand-logo" style={{ width: 44, height: 44 }}>
              <Activity size={26} color="#fff" />
            </div>
            <div>
              <h1 className="login-title">AcuityFlow AI</h1>
              <p className="login-subtitle">Continuous Uncertainty-Aware Triage Decision Support</p>
            </div>
          </div>

          <div className="login-info-box">
            <div className="login-info-title">
              <Shield size={16} className="text-accent" />
              <span>Backend-Enforced Role-Based Access Control</span>
            </div>
            <p className="login-info-desc">
              All clinical triage, overrides, and audit trails require authenticated cryptographic JWT session tokens with role verification.
            </p>
          </div>

          <div className="role-showcase-grid">
            <div
              className={`role-showcase-card ${username === 'nurse101' ? 'active-nurse' : ''}`}
              onClick={() => handleQuickSelect('nurse101')}
            >
              <div className="role-card-badge role-nurse">NURSE</div>
              <div className="role-card-user">nurse101</div>
              <div className="role-card-desc">Triage queue, vital observations, clinical overrides, patient audit</div>
            </div>

            <div
              className={`role-showcase-card ${username === 'supervisor101' ? 'active-supervisor' : ''}`}
              onClick={() => handleQuickSelect('supervisor101')}
            >
              <div className="role-card-badge role-supervisor">SUPERVISOR</div>
              <div className="role-card-user">supervisor101</div>
              <div className="role-card-desc">All nurse triage features + full system audit trail explorer & override review</div>
            </div>

            <div
              className={`role-showcase-card ${username === 'admin101' ? 'active-admin' : ''}`}
              onClick={() => handleQuickSelect('admin101')}
            >
              <div className="role-card-badge role-admin">ADMIN</div>
              <div className="role-card-user">admin101</div>
              <div className="role-card-desc">Demographic policy boundaries, system configuration & user management</div>
            </div>
          </div>
        </div>

        {/* Right / Login Form Card */}
        <div className="login-form-card">
          <div className="form-header">
            <div className="form-header-icon">
              <Lock size={20} />
            </div>
            <h2>Sign In to Session</h2>
            <p>Select a synthetic role above or enter credentials</p>
          </div>

          {error && (
            <div className="login-error-banner">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="login-form">
            <div className="form-group">
              <label htmlFor="login-username">Username</label>
              <input
                id="login-username"
                type="text"
                className="input-field"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username (e.g. nurse101)"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="login-password">Password</label>
              <input
                id="login-password"
                type="password"
                className="input-field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                required
              />
            </div>

            <div className="demo-hint-box">
              <UserCheck size={14} />
              <span>Default prototype password: <code>Password@123</code></span>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-login-submit"
            >
              {loading ? (
                <span>Authenticating...</span>
              ) : (
                <>
                  <span>Sign In as {username}</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>

          <div className="login-footer-note">
            Synthetic demonstration environment • Non-clinical evaluation prototype
          </div>
        </div>
      </div>
    </div>
  );
};
