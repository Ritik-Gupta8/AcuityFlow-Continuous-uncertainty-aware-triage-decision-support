import React, { useState } from 'react';
import { api } from '../services/api';
import type { User } from '../types';

interface LoginModalProps {
  isOpen: boolean;
  currentUser: User | null;
  onLoginSuccess: (user: User) => void;
  onClose: () => void;
}

export const LoginModal: React.FC<LoginModalProps> = ({
  isOpen,
  currentUser,
  onLoginSuccess,
  onClose,
}) => {
  const [username, setUsername] = useState('nurse101');
  const [password, setPassword] = useState('Password@123');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleLogin = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await api.login({ username: username.trim(), password });
      const user = await api.getMe();
      onLoginSuccess(user);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSelect = (uName: string) => {
    setUsername(uName);
    setPassword('Password@123');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden text-slate-100 animate-in fade-in zoom-in duration-200">
        <div className="bg-gradient-to-r from-teal-900/60 to-slate-800 p-6 border-b border-slate-800 flex justify-between items-center">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xl">🔐</span>
              <h2 className="text-lg font-bold tracking-wide text-white">Prototype Authentication & RBAC</h2>
            </div>
            <p className="text-xs text-slate-400 mt-1">Backend-enforced JWT access control & audit trail identity</p>
          </div>
          {currentUser && (
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
            >
              ✕
            </button>
          )}
        </div>

        <div className="p-6 space-y-6">
          {/* Quick Demo Switcher */}
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
              Select Synthetic Demo Account
            </label>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickSelect('nurse101')}
                className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
                  username === 'nurse101'
                    ? 'border-teal-500 bg-teal-950/40 text-teal-200 shadow-md shadow-teal-950'
                    : 'border-slate-800 bg-slate-800/50 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="text-xs font-bold">nurse101</div>
                <div className="text-[10px] text-teal-400 font-semibold mt-1">NURSE</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickSelect('supervisor101')}
                className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
                  username === 'supervisor101'
                    ? 'border-indigo-500 bg-indigo-950/40 text-indigo-200 shadow-md shadow-indigo-950'
                    : 'border-slate-800 bg-slate-800/50 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="text-xs font-bold">supervisor101</div>
                <div className="text-[10px] text-indigo-400 font-semibold mt-1">SUPERVISOR</div>
              </button>

              <button
                type="button"
                onClick={() => handleQuickSelect('admin101')}
                className={`p-3 rounded-xl border text-left transition flex flex-col justify-between ${
                  username === 'admin101'
                    ? 'border-amber-500 bg-amber-950/40 text-amber-200 shadow-md shadow-amber-950'
                    : 'border-slate-800 bg-slate-800/50 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div className="text-xs font-bold">admin101</div>
                <div className="text-[10px] text-amber-400 font-semibold mt-1">ADMIN</div>
              </button>
            </div>
          </div>

          {/* Form */}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-teal-500"
                required
              />
            </div>

            <div>
              <label className="text-xs font-medium text-slate-300 block mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-teal-500"
                required
              />
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800/80 text-rose-200 text-xs flex items-center gap-2">
                <span>⚠️</span>
                <span>{error}</span>
              </div>
            )}

            <div className="pt-2 flex gap-3">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-gradient-to-r from-teal-500 to-emerald-600 hover:from-teal-400 hover:to-emerald-500 text-slate-950 font-bold py-2.5 rounded-xl shadow-lg transition duration-150 disabled:opacity-50"
              >
                {loading ? 'Authenticating...' : `Log In as ${username}`}
              </button>
              {currentUser && (
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2.5 rounded-xl border border-slate-700 hover:bg-slate-800 text-slate-300 text-sm font-medium transition"
                >
                  Cancel
                </button>
              )}
            </div>
          </form>

          {/* Role matrix reminder */}
          <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800 text-[11px] text-slate-400 space-y-1">
            <div className="font-semibold text-slate-300">Prototype Role Matrix:</div>
            <div>• <strong className="text-teal-400">Nurse:</strong> Queue, triage, observations, overrides, patient audit</div>
            <div>• <strong className="text-indigo-400">Supervisor:</strong> All nurse features + full audit trail explorer</div>
            <div>• <strong className="text-amber-400">Admin:</strong> Demographic config & prototype user management</div>
          </div>
        </div>
      </div>
    </div>
  );
};
