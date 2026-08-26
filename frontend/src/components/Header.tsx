import React from 'react';
import { Activity, Clock, Flame, RotateCcw, ShieldAlert, FileText, PlusCircle } from 'lucide-react';
import type { SimulationStatus } from '../types';

interface HeaderProps {
  simulationStatus: SimulationStatus;
  onAdvanceTime: (mins: number) => void;
  onToggleSurge: (active: boolean) => void;
  onReset: () => void;
  onOpenAudit: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  simulationStatus,
  onAdvanceTime,
  onToggleSurge,
  onReset,
  onOpenAudit,
}) => {
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

          {/* Audit Log Modal Button */}
          <button className="btn btn-secondary" onClick={onOpenAudit} title="Inspect FHIR-inspired Audit Trail">
            <FileText size={14} />
            Audit Trail
          </button>

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
