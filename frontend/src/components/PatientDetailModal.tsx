import React, { useState, useEffect } from 'react';
import { X, ShieldAlert, CheckCircle, AlertTriangle, Activity, Zap, FileText } from 'lucide-react';
import type { Patient, TriageResult } from '../types';
import { api } from '../services/api';

interface PatientDetailModalProps {
  patient: Patient;
  onClose: () => void;
  onOpenOverride: (patient: Patient) => void;
  onDecisionSubmitted: () => void;
  onTriggerDeterioration: (patientId: string) => void;
}

export const PatientDetailModal: React.FC<PatientDetailModalProps> = ({
  patient,
  onClose,
  onOpenOverride,
  onDecisionSubmitted,
  onTriggerDeterioration,
}) => {
  const [triageResult, setTriageResult] = useState<TriageResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTriageResult();
  }, [patient.patient_id]);

  const loadTriageResult = async () => {
    try {
      setLoading(true);
      const res = await api.getLatestTriageResult(patient.patient_id);
      setTriageResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async () => {
    try {
      await api.recordDecision(patient.patient_id, {
        clinician_id: 'nurse-101',
        actor_role: 'nurse',
        clinician_action: 'accept',
        final_priority: patient.current_priority,
        clinician_note: 'Recommendation accepted by triage nurse.',
      });
      onDecisionSubmitted();
      onClose();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleEscalate = async () => {
    try {
      await api.recordDecision(patient.patient_id, {
        clinician_id: 'nurse-101',
        actor_role: 'nurse',
        clinician_action: 'escalate',
        final_priority: 'HIGH',
        override_reason: 'Clinician clinical escalation based on direct patient evaluation',
        clinician_note: 'Escalated for immediate senior physician review.',
      });
      onDecisionSubmitted();
      onClose();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const latestObs = patient.observations[0];
  const prevObs = patient.observations[1];

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#60a5fa' }}>{patient.patient_id}</span>
            <span style={{ fontSize: '1.1rem', fontWeight: 700 }}>{patient.name}</span>
            <span className={`profile-tag profile-${patient.population_profile}`}>
              {patient.population_profile}
            </span>
          </div>
          <button className="btn btn-secondary" onClick={onClose} style={{ padding: 4 }}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body">
          {/* Reassessment Banner */}
          {patient.needs_reassessment && (
            <div className="danger-box">
              <Zap size={20} style={{ color: '#ef4444', flexShrink: 0 }} />
              <div>
                <strong>AcuityWatch Active Reassessment Recommendation</strong>
                <ul style={{ paddingLeft: 18, marginTop: 4 }}>
                  {patient.reassessment_reasons.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Zero History Warning */}
          {(patient.first_time_patient || !patient.history_available) && (
            <div className="warning-box">
              <ShieldAlert size={20} style={{ color: '#f59e0b', flexShrink: 0 }} />
              <div>
                <strong>Zero Prior History / First-Time Presentation</strong>
                <div style={{ marginTop: 2 }}>
                  No prior electronic health records found for this patient. Missing history is NOT treated as negative. Completeness is penalized to avoid under-triage.
                </div>
              </div>
            </div>
          )}

          {/* Demographics & Complaint */}
          <div style={{ background: '#1f2937', padding: 16, borderRadius: 10 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
              <div>
                <span style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Age & Sex</span>
                <div style={{ fontWeight: 600 }}>{patient.age_years ?? 'Unknown'} yrs • {patient.sex ?? 'Unknown'}</div>
              </div>
              <div>
                <span style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Arrival Mode</span>
                <div style={{ fontWeight: 600, textTransform: 'capitalize' }}>{patient.arrival_mode}</div>
              </div>
              <div>
                <span style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Waiting Time</span>
                <div style={{ fontWeight: 600 }}>{patient.waiting_minutes} minutes</div>
              </div>
              <div>
                <span style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Pain Score</span>
                <div style={{ fontWeight: 600 }}>{patient.pain_score != null ? `${patient.pain_score} / 10` : 'Not recorded'}</div>
              </div>
            </div>

            <div style={{ marginTop: 12, borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: 10 }}>
              <span style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Chief Complaint & Narrative</span>
              <div style={{ fontWeight: 600, fontSize: '0.92rem', color: '#e2e8f0' }}>{patient.chief_complaint}</div>
              {patient.symptom_text && (
                <div style={{ fontSize: '0.82rem', color: '#cbd5e1', marginTop: 4 }}>
                  &ldquo;{patient.symptom_text}&rdquo;
                </div>
              )}
            </div>

            {patient.observed_cues && patient.observed_cues.length > 0 && (
              <div style={{ marginTop: 8 }}>
                <span style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Observed Clinical Cues: </span>
                <span style={{ fontSize: '0.8rem', color: '#fca5a5', fontWeight: 600 }}>
                  {patient.observed_cues.join(', ')}
                </span>
              </div>
            )}
          </div>

          {/* Vitals Overview */}
          <div>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
              <Activity size={16} style={{ color: '#3b82f6' }} />
              Latest Physiological Observations
            </h3>

            {latestObs ? (
              <div className="vitals-grid">
                <div className="vital-stat-box">
                  <div className="vital-name">Heart Rate</div>
                  <div className="vital-val" style={{ color: (latestObs.heart_rate ?? 0) > 100 ? '#f87171' : '#f9fafb' }}>
                    {latestObs.heart_rate ?? '--'} <span style={{ fontSize: '0.75rem', fontWeight: 400 }}>bpm</span>
                  </div>
                  {prevObs?.heart_rate && (
                    <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>Prev: {prevObs.heart_rate}</div>
                  )}
                </div>

                <div className="vital-stat-box">
                  <div className="vital-name">Respiration</div>
                  <div className="vital-val" style={{ color: (latestObs.respiratory_rate ?? 0) > 22 ? '#f87171' : '#f9fafb' }}>
                    {latestObs.respiratory_rate ?? '--'} <span style={{ fontSize: '0.75rem', fontWeight: 400 }}>/min</span>
                  </div>
                </div>

                <div className="vital-stat-box">
                  <div className="vital-name">Blood Pressure</div>
                  <div className="vital-val">
                    {latestObs.systolic_bp ?? '--'}/{latestObs.diastolic_bp ?? '--'}
                  </div>
                </div>

                <div className="vital-stat-box">
                  <div className="vital-name">SpO2 Oxygen</div>
                  <div className="vital-val" style={{ color: (latestObs.spo2 ?? 100) < 94 ? '#f87171' : '#34d399' }}>
                    {latestObs.spo2 ? `${latestObs.spo2}%` : '--'}
                  </div>
                  {prevObs?.spo2 && (
                    <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>Prev: {prevObs.spo2}%</div>
                  )}
                </div>

                <div className="vital-stat-box">
                  <div className="vital-name">Temperature</div>
                  <div className="vital-val">
                    {latestObs.temperature_c ? `${latestObs.temperature_c}°C` : '--'}
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ color: '#9ca3af', fontSize: '0.85rem' }}>No observations recorded yet.</div>
            )}
          </div>

          {/* Triage Recommendation Card */}
          {loading ? (
            <div>Loading recommendation...</div>
          ) : triageResult ? (
            <div className="triage-recommendation-panel">
              <div className="triage-status-bar">
                <div>
                  <span style={{ fontSize: '0.72rem', color: '#93c5fd', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    AI Decision Support Recommendation
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 4 }}>
                    <span className={`priority-tag priority-${triageResult.priority}`} style={{ fontSize: '0.95rem', padding: '6px 14px' }}>
                      {triageResult.priority}
                    </span>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#93c5fd' }}>
                      Action: {triageResult.action}
                    </span>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: '0.72rem', color: '#93c5fd' }}>Model Confidence</span>
                  <div style={{ fontSize: '1.2rem', fontWeight: 800, color: triageResult.confidence_score < 65 ? '#f87171' : '#6ee7b7' }}>
                    {triageResult.confidence_score}%
                  </div>
                </div>
              </div>

              {/* Completeness Bar */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.74rem', color: '#9ca3af', marginBottom: 4 }}>
                  <span>Data Completeness Score</span>
                  <span>{triageResult.data_completeness}%</span>
                </div>
                <div className="progress-container">
                  <div
                    className="progress-bar"
                    style={{
                      width: `${triageResult.data_completeness}%`,
                      background: triageResult.data_completeness < 60 ? '#f59e0b' : '#3b82f6',
                    }}
                  />
                </div>
              </div>

              {/* Explanation Narrative */}
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: 12, borderRadius: 8, fontSize: '0.82rem', color: '#cbd5e1' }}>
                <strong>Triage Rationale: </strong> {triageResult.explanation}
              </div>

              {/* Safety Flags & Missing Info */}
              {triageResult.safety_flags.length > 0 && (
                <div>
                  <span style={{ fontSize: '0.74rem', color: '#f87171', fontWeight: 700 }}>Active Safety Flags:</span>
                  <ul style={{ fontSize: '0.78rem', color: '#fca5a5', paddingLeft: 16, marginTop: 2 }}>
                    {triageResult.safety_flags.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>
              )}

              {triageResult.missing_information.length > 0 && (
                <div>
                  <span style={{ fontSize: '0.74rem', color: '#fbbf24', fontWeight: 700 }}>Known Unknowns / Missing Information:</span>
                  <ul style={{ fontSize: '0.78rem', color: '#fde68a', paddingLeft: 16, marginTop: 2 }}>
                    {triageResult.missing_information.map((m, i) => (
                      <li key={i}>{m}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : null}
        </div>

        {/* Footer Actions */}
        <div className="modal-footer">
          <button
            className="btn btn-warning"
            onClick={() => onTriggerDeterioration(patient.patient_id)}
            title="Simulate sudden vital deterioration for this patient"
          >
            <Zap size={14} />
            Simulate Deterioration
          </button>

          <button className="btn btn-danger" onClick={handleEscalate}>
            <AlertTriangle size={14} />
            Escalate
          </button>

          <button className="btn btn-surge" onClick={() => onOpenOverride(patient)}>
            <FileText size={14} />
            Override Priority
          </button>

          <button className="btn btn-primary" onClick={handleAccept}>
            <CheckCircle size={14} />
            Accept Recommendation
          </button>
        </div>
      </div>
    </div>
  );
};
