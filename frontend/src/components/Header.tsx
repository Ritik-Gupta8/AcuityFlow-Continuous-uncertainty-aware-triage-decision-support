import React from 'react';
import { Activity, Clock, Flame, RotateCcw, ShieldAlert, FileText, PlusCircle, UserCheck, Settings, LogOut } from 'lucide-react';
import type { SimulationStatus, User } from '../types';

interface HeaderProps {
  simulationStatus: SimulationStatus;
  currentUser: User | null;
  onAdvanceTime: (mins: number) => void;
  onToggleSurge: (active: boolean) => void;
  onReset: () => void;
  onOpenAudit: () => void;
  onOpenAdmin: () => void;
  onLogout: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  simulationStatus,
  currentUser,
  onAdvanceTime,
  onToggleSurge,
  onReset,
  onOpenAudit,
  onOpenAdmin,
  onLogout,
}) => {
  const roleColor =
    currentUser?.role === 'admin'
      ? '#f59e0b'
      : currentUser?.role === 'supervisor'
      ? '#818cf8'
      : '#2dd4bf';

  const roleBg =
    currentUser?.role === 'admin'
      ? 'rgba(245, 158, 11, 0.15)'
      : currentUser?.role === 'supervisor'
      ? 'rgba(99, 102, 241, 0.15)'
      : 'rgba(20, 184, 166, 0.15)';

  const roleBorder =
    currentUser?.role === 'admin'
      ? '#b45309'
      : currentUser?.role === 'supervisor'
      ? '#4338ca'
      : '#0f766e';

  return (
    <>
      {/* Prototype Safety Disclaimer */}
      <div className="disclaimer-banner">
        <ShieldAlert size={15} />
        <span>
          <strong>CONCEPT PROTOTYPE</strong> — Synthetic Data • Not for clinical diagnosis or treatment • Continuous decision-support prototype
        </span>
      </div>

      <header className="top-header">
        <div className="brand-section">
          <div className="brand-logo">
            <Activity size={22} />
          </div>
          <div>
            <h1 className="brand-title">AcuityFlow AI</h1>
            <div className="brand-subtitle">Continuous Uncertainty-Aware Emergency Triage Support</div>
          </div>
        </div>

        <div className="header-controls">
          {/* User Session & Role Badge */}
          {currentUser && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}
            >
              <div
                style={{
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  padding: '5px 10px',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  background: roleBg,
                  color: roleColor,
                  border: `1px solid ${roleBorder}`,
                }}
                title={`Authenticated as ${currentUser.username} (${currentUser.role.toUpperCase()})`}
              >
                <UserCheck size={14} />
                <span>{currentUser.username} ({currentUser.role.toUpperCase()})</span>
              </div>

              <button
                onClick={onLogout}
                className="btn btn-secondary"
                style={{ padding: '5px 10px', fontSize: '0.75rem' }}
                title="Log out and return to Login Screen"
              >
                <LogOut size={13} />
                Switch User
              </button>
            </div>
          )}

          {/* Model Status Indicator */}
          <div
            style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              padding: '4px 10px',
              borderRadius: 6,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: simulationStatus.model_available === false ? 'rgba(245, 158, 11, 0.2)' : 'rgba(16, 185, 129, 0.15)',
              color: simulationStatus.model_available === false ? '#fcd34d' : '#6ee7b7',
              border: `1px solid ${simulationStatus.model_available === false ? '#f59e0b' : '#10b981'}`
            }}
            title={simulationStatus.model_available === false ? 'Calibrated ML artifact unavailable — using deterministic safety fallback' : 'Runtime scikit-learn calibrated pipeline active'}
          >
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: simulationStatus.model_available === false ? '#f59e0b' : '#10b981', display: 'inline-block' }} />
            {simulationStatus.model_available === false ? 'MODEL: FALLBACK' : 'MODEL: CALIBRATED ML'}
          </div>

          {/* Simulation Clock */}
          <div className="clock-badge" title="Simulated Emergency Department Clock">
            <Clock size={14} />
            <span>ED Clock: +{simulationStatus.time_offset_minutes}m</span>
          </div>

          {/* Advance Time Controls */}
          <button
            className="btn btn-secondary"
            onClick={() => onAdvanceTime(5)}
            title="Advance simulated time by 5 minutes"
          >
            <PlusCircle size={14} />
            +5 min
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => onAdvanceTime(15)}
            title="Advance simulated time by 15 minutes"
          >
            <PlusCircle size={14} />
            +15 min
          </button>

          {/* 3x Surge Mode Toggle */}
          <button
            className={`btn btn-surge ${simulationStatus.surge_active ? 'active' : ''}`}
            onClick={() => onToggleSurge(!simulationStatus.surge_active)}
            title="Simulate 3x surge workload pressure"
          >
            <Flame size={15} />
            {simulationStatus.surge_active ? '3× SURGE ACTIVE' : '3× Surge Mode'}
          </button>

          {/* Audit Log Modal Button (Supervisor & Admin access) */}
          <button
            className="btn btn-secondary"
            onClick={onOpenAudit}
            title={currentUser?.role === 'nurse' ? 'Inspect Audit Trail (Patient-specific for nurse, full explorer for supervisor/admin)' : 'Inspect Full FHIR-inspired Audit Trail'}
          >
            <FileText size={14} />
            Audit Trail
          </button>

          {/* Admin Configuration Modal Button (Admin only) */}
          {currentUser?.role === 'admin' && (
            <button
              className="btn btn-secondary"
              onClick={onOpenAdmin}
              style={{ borderColor: '#f59e0b', color: '#fcd34d' }}
              title="System & Population Configuration (Admin Only)"
            >
              <Settings size={14} />
              Config
            </button>
          )}

          {/* Reset Simulation */}
          <button className="btn btn-secondary" onClick={onReset} title="Reset database and re-seed 24 test cases">
            <RotateCcw size={14} />
            Reset
          </button>
        </div>
      </header>
    </>
  );
};
