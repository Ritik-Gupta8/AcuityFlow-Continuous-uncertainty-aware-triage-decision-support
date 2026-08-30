import React, { useState } from 'react';
import { Users, AlertTriangle, HeartPulse, HelpCircle, ArrowUpRight, Search, Zap, Clock } from 'lucide-react';
import type { Patient } from '../types';

interface CommandCenterProps {
  patients: Patient[];
  surgeActive: boolean;
  onSelectPatient: (patient: Patient) => void;
  onTriggerDeterioration: (patientId: string) => void;
}

export const CommandCenter: React.FC<CommandCenterProps> = ({
  patients,
  surgeActive,
  onSelectPatient,
  onTriggerDeterioration,
}) => {
  const [search, setSearch] = useState('');
  const [profileFilter, setProfileFilter] = useState<string>('ALL');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');

  // Compute metrics
  const totalCount = patients.length;
  const criticalCount = patients.filter((p) => p.current_priority === 'IMMEDIATE' || p.current_priority === 'HIGH').length;
  const reassessCount = patients.filter((p) => p.needs_reassessment).length;
  const uncertainCount = patients.filter((p) => p.current_confidence < 65.0).length;

  // Filter and sort attention queue strictly by operational hierarchy:
  // 1. Deteriorating (1000) -> 2. Reassessment Overdue (500) -> 3. Low Confidence (300) -> 4. High Priority (120+)
  const getAttentionKey = (p: Patient) => {
    let score = 0;
    if (p.reassessment_reasons?.some((r) => r.toLowerCase().includes('deterioration'))) score += 1000;
    if (p.reassessment_reasons?.some((r) => r.toLowerCase().includes('overdue'))) score += 500;
    if (p.current_confidence < 65.0) score += 300;
    if (p.current_priority === 'IMMEDIATE') score += 150;
    else if (p.current_priority === 'HIGH') score += 120;
    else if (p.current_priority === 'REVIEW') score += 80;
    else if (p.current_priority === 'MODERATE') score += 40;
    else score += 10;
    score += Math.min(50, p.waiting_minutes);
    return score;
  };

  const attentionPatients = [...patients.filter((p) => p.needs_reassessment)].sort(
    (a, b) => getAttentionKey(b) - getAttentionKey(a)
  );

  // Filter main queue
  const filteredPatients = patients.filter((p) => {
    const matchesSearch =
      p.patient_id.toLowerCase().includes(search.toLowerCase()) ||
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.chief_complaint.toLowerCase().includes(search.toLowerCase());

    const matchesProfile =
      profileFilter === 'ALL' || p.population_profile.toUpperCase() === profileFilter.toUpperCase();

    const matchesPriority =
      priorityFilter === 'ALL' || p.current_priority === priorityFilter;

    return matchesSearch && matchesProfile && matchesPriority;
  });

  return (
    <div className="main-content">
      {/* Metrics Row */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'rgba(59, 130, 246, 0.2)', color: '#60a5fa' }}>
            <Users size={22} />
          </div>
          <div className="metric-data">
            <h4>Waiting Queue Size</h4>
            <div className="metric-value">{totalCount} {surgeActive ? '(3× Surge Active)' : ''}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#f87171' }}>
            <AlertTriangle size={22} />
          </div>
          <div className="metric-data">
            <h4>Urgent / High Priority</h4>
            <div className="metric-value" style={{ color: '#f87171' }}>{criticalCount}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'rgba(217, 119, 6, 0.2)', color: '#fbbf24' }}>
            <HeartPulse size={22} />
          </div>
          <div className="metric-data">
            <h4>Attention / Deteriorations</h4>
            <div className="metric-value" style={{ color: '#fbbf24' }}>{reassessCount}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon" style={{ background: 'rgba(168, 85, 247, 0.2)', color: '#c084fc' }}>
            <HelpCircle size={22} />
          </div>
          <div className="metric-data">
            <h4>High Uncertainty / Review</h4>
            <div className="metric-value" style={{ color: '#c084fc' }}>{uncertainCount}</div>
          </div>
        </div>
      </div>

      {/* Attention Queue (AcuityWatch Banner) */}
      {attentionPatients.length > 0 && (
        <div className="attention-banner">
          <div className="attention-header">
            <div className="attention-title">
              <Zap size={20} />
              <span>AcuityWatch Attention Queue ({attentionPatients.length} Cases Requiring Reassessment)</span>
              <span className="attention-badge-count">
                {surgeActive ? '3× SURGE ATTENTION-FIRST' : 'URGENT'}
              </span>
            </div>
          </div>

          <div className="attention-grid">
            {attentionPatients.map((patient) => {
              const isDet = patient.reassessment_reasons?.some((r) => r.toLowerCase().includes('deterioration'));
              const isOverdue = patient.reassessment_reasons?.some((r) => r.toLowerCase().includes('overdue'));
              const isUncertain = patient.current_confidence < 65.0;

              return (
                <div
                  key={patient.patient_id}
                  className="attention-card"
                  onClick={() => onSelectPatient(patient)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{ fontWeight: 800, color: isDet ? '#f87171' : '#60a5fa' }}>
                        {patient.patient_id}
                      </span>
                      {isDet && (
                        <span style={{ fontSize: '0.64rem', background: '#dc2626', color: 'white', padding: '1px 5px', borderRadius: 3, fontWeight: 700 }}>
                          ⚡ DETERIORATING
                        </span>
                      )}
                      {!isDet && isOverdue && (
                        <span style={{ fontSize: '0.64rem', background: 'rgba(217, 119, 6, 0.3)', color: '#fbbf24', border: '1px solid #d97706', padding: '1px 5px', borderRadius: 3, fontWeight: 700 }}>
                          ⏱️ OVERDUE
                        </span>
                      )}
                      {!isDet && !isOverdue && isUncertain && (
                        <span style={{ fontSize: '0.64rem', background: 'rgba(168, 85, 247, 0.3)', color: '#c084fc', border: '1px solid #9333ea', padding: '1px 5px', borderRadius: 3, fontWeight: 700 }}>
                          ⚠️ LOW CONF
                        </span>
                      )}
                    </div>
                    <span className={`priority-tag priority-${patient.current_priority}`}>
                      {patient.current_priority}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600 }}>{patient.name}</div>
                  <div style={{ fontSize: '0.78rem', color: isDet ? '#fca5a5' : '#fed7aa' }}>
                    {patient.reassessment_reasons[0] || 'Reassessment triggered'}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#9ca3af', marginTop: 4 }}>
                    <span>Waiting: {patient.waiting_minutes}m</span>
                    <span style={{ color: '#60a5fa', fontWeight: 600 }}>Review & Triage &rarr;</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Main Queue Section */}
      <div className="queue-section">
        <div className="queue-header">
          <div>
            <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>
              {surgeActive ? 'Surge Mode: Active Attention-First Queue' : 'Emergency Department Waiting Queue'}
            </h2>
            <p style={{ fontSize: '0.78rem', color: '#9ca3af' }}>
              Continuous decision-support monitoring for 24 simulated test patients
            </p>
          </div>

          {/* Search & Filters */}
          <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
            <div style={{ position: 'relative' }}>
              <Search size={14} style={{ position: 'absolute', left: 10, top: 10, color: '#6b7280' }} />
              <input
                type="text"
                placeholder="Search patient or complaint..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{
                  background: '#1f2937',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: 6,
                  padding: '6px 12px 6px 30px',
                  color: 'white',
                  fontSize: '0.82rem',
                  outline: 'none',
                }}
              />
            </div>

            <div className="queue-filters">
              {['ALL', 'PEDIATRIC', 'ADULT', 'GERIATRIC'].map((p) => (
                <button
                  key={p}
                  className={`filter-chip ${profileFilter === p ? 'active' : ''}`}
                  onClick={() => setProfileFilter(p)}
                >
                  {p}
                </button>
              ))}
            </div>

            <div className="queue-filters">
              {['ALL', 'IMMEDIATE', 'HIGH', 'MODERATE', 'LOW', 'REVIEW'].map((pr) => (
                <button
                  key={pr}
                  className={`filter-chip ${priorityFilter === pr ? 'active' : ''}`}
                  onClick={() => setPriorityFilter(pr)}
                >
                  {pr}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Patient Table Rows */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {filteredPatients.map((patient) => {
            const latestObs = patient.observations[0];
            return (
              <div
                key={patient.patient_id}
                className={`patient-row ${patient.needs_reassessment ? 'reassessment-urgent' : ''}`}
                onClick={() => onSelectPatient(patient)}
              >
                {/* ID & Profile */}
                <div>
                  <div style={{ fontWeight: 700, fontSize: '0.88rem' }}>{patient.patient_id}</div>
                  <span className={`profile-tag profile-${patient.population_profile}`}>
                    {patient.population_profile}
                  </span>
                </div>

                {/* Name & Age */}
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{patient.name}</div>
                  <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                    {patient.age_years ? `${patient.age_years} yrs` : 'Age unknown'} • {patient.sex || 'Unknown'}
                  </div>
                </div>

                {/* Chief Complaint */}
                <div>
                  <div style={{ fontSize: '0.83rem', fontWeight: 500 }}>{patient.chief_complaint}</div>
                  {latestObs && (
                    <div style={{ fontSize: '0.74rem', color: '#9ca3af', fontFamily: 'JetBrains Mono', marginTop: 2 }}>
                      HR: {latestObs.heart_rate ?? '--'} | SpO2: {latestObs.spo2 ? `${latestObs.spo2}%` : '--'} | BP: {latestObs.systolic_bp ?? '--'}/{latestObs.diastolic_bp ?? '--'}
                    </div>
                  )}
                </div>

                {/* Waiting Time */}
                <div style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'flex', alignItems: 'center', gap: 4 }}>
                  <Clock size={13} />
                  <span>{patient.waiting_minutes}m waiting</span>
                </div>

                {/* Priority */}
                <div>
                  <span className={`priority-tag priority-${patient.current_priority}`}>
                    {patient.current_priority}
                  </span>
                </div>

                {/* Confidence */}
                <div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700 }}>{patient.current_confidence}%</div>
                  <div style={{ fontSize: '0.68rem', color: patient.current_confidence < 65 ? '#f87171' : '#6ee7b7' }}>
                    {patient.current_confidence < 65 ? 'Low Conf' : 'High Conf'}
                  </div>
                </div>

                {/* Action CTA */}
                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 6 }}>
                  {patient.patient_id === 'PT-021' && (
                    <button
                      className="btn btn-warning"
                      style={{ padding: '4px 8px', fontSize: '0.72rem' }}
                      title="Inject vital deterioration for PT-021"
                      onClick={(e) => {
                        e.stopPropagation();
                        onTriggerDeterioration('PT-021');
                      }}
                    >
                      <Zap size={12} />
                      Deteriorate
                    </button>
                  )}
                  <button className="btn btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }}>
                    <ArrowUpRight size={13} />
                    View
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
