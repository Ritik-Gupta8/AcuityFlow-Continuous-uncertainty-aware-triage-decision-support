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

  // Free-text Symptom Extraction State
  const [freeText, setFreeText] = useState(patient.symptom_text || '');
  const [extractedSymptoms, setExtractedSymptoms] = useState<string[]>([]);
  const [extractedDuration, setExtractedDuration] = useState<number | null>(null);
  const [, setExtractedBy] = useState<string | null>(null);
  const [isAmbiguous, setIsAmbiguous] = useState<boolean>(false);
  const [isExtracting, setIsExtracting] = useState<boolean>(false);
  const [extractionError, setExtractionError] = useState<string | null>(null);
  const [newCustomSymptom, setNewCustomSymptom] = useState('');
  const [appliedSuccess, setAppliedSuccess] = useState(false);

  useEffect(() => {
    loadTriageResult();
    setFreeText(patient.symptom_text || '');
    setExtractedSymptoms([]);
    setExtractionError(null);
  }, [patient.patient_id, patient.observations?.length, patient.waiting_minutes, patient.current_risk_score]);

  const handleExtractSymptoms = async () => {
    if (!freeText.trim()) return;
    try {
      setIsExtracting(true);
      setExtractionError(null);
      const res = await api.extractSymptoms(freeText.trim());
      setExtractedSymptoms(res.symptoms);
      setExtractedDuration(res.duration_minutes || null);
      setExtractedBy(res.extracted_by);
      setIsAmbiguous(res.is_ambiguous);
    } catch (err: any) {
      setExtractionError(err.message || 'Failed to extract symptoms');
    } finally {
      setIsExtracting(false);
    }
  };

  const removeSymptomTag = (idx: number) => {
    setExtractedSymptoms(prev => prev.filter((_, i) => i !== idx));
  };

  const addCustomSymptom = () => {
    const trimmed = newCustomSymptom.trim();
    if (trimmed && !extractedSymptoms.includes(trimmed)) {
      setExtractedSymptoms(prev => [...prev, trimmed]);
      setNewCustomSymptom('');
    }
  };

  const handleConfirmAndApply = async () => {
    try {
      await api.updatePatientSymptoms(patient.patient_id, {
        symptoms: extractedSymptoms,
        narrative_text: freeText,
        duration_minutes: extractedDuration || undefined
      });
      patient.observed_cues = extractedSymptoms;
      patient.symptom_text = freeText;
      if (extractedDuration) patient.symptom_duration_minutes = extractedDuration;
      setAppliedSuccess(true);
      setTimeout(() => setAppliedSuccess(false), 4000);
      await loadTriageResult();
      onDecisionSubmitted();
    } catch (err: any) {
      alert(err.message || 'Failed to apply structured symptoms');
    }
  };

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
      const aiPriorityToAccept = patient.ai_priority || triageResult?.priority || patient.current_priority;
      await api.recordDecision(patient.patient_id, {
        clinician_id: 'nurse-101',
        actor_role: 'nurse',
        clinician_action: 'accept',
        final_priority: aiPriorityToAccept,
        clinician_note: 'AI triage recommendation accepted by triage nurse.',
      });
      onDecisionSubmitted();
      onClose();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleEscalate = async () => {
    try {
      const currentVal = patient.effective_priority || patient.current_priority;
      const targetPriority = currentVal === 'HIGH' || currentVal === 'IMMEDIATE' ? 'IMMEDIATE' : 'HIGH';
      await api.recordDecision(patient.patient_id, {
        clinician_id: 'nurse-101',
        actor_role: 'nurse',
        clinician_action: 'escalate',
        final_priority: targetPriority,
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

  const hasDeterioration = Boolean(
    patient.reassessment_reasons?.some(r => r.toLowerCase().includes('deterioration')) ||
    (prevObs && latestObs && prevObs.spo2 !== latestObs.spo2)
  );

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
            <div
              className="danger-box"
              style={{
                borderLeft: hasDeterioration ? '4px solid #ef4444' : '4px solid #f59e0b',
                background: hasDeterioration ? 'rgba(239, 68, 68, 0.12)' : 'rgba(245, 158, 11, 0.12)',
                padding: '14px 16px',
                borderRadius: 8
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
                {hasDeterioration ? (
                  <Zap size={22} style={{ color: '#ef4444', flexShrink: 0, marginTop: 2 }} />
                ) : (
                  <Activity size={22} style={{ color: '#f59e0b', flexShrink: 0, marginTop: 2 }} />
                )}
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 6 }}>
                    <strong style={{ color: hasDeterioration ? '#fca5a5' : '#fde68a', fontSize: '0.95rem', letterSpacing: '0.02em' }}>
                      {hasDeterioration ? 'REASSESS NOW — CLINICIAN REVIEW REQUIRED' : 'REASSESSMENT OVERDUE — CLINICIAN REVIEW RECOMMENDED'}
                    </strong>
                    <span
                      style={{
                        fontSize: '0.75rem',
                        fontWeight: 800,
                        background: hasDeterioration ? '#ef4444' : '#f59e0b',
                        color: '#fff',
                        padding: '3px 10px',
                        borderRadius: 4
                      }}
                    >
                      {hasDeterioration ? 'Final Action: ESCALATE' : '⏱️ Reassessment Overdue'}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.76rem', color: '#cbd5e1', marginTop: 4 }}>
                    {hasDeterioration
                      ? 'AcuityWatch continuous monitor detected acute physiological deterioration & risk trajectory shift:'
                      : 'AcuityWatch continuous queue monitor: Patient has exceeded scheduled reassessment window for their priority tier:'}
                  </div>
                  <ul style={{ paddingLeft: 18, marginTop: 6, fontSize: '0.78rem', color: hasDeterioration ? '#fecaca' : '#fef3c7', lineHeight: 1.45 }}>
                    {patient.reassessment_reasons.map((r, i) => (
                      <li key={i}>{r}</li>
                    ))}
                  </ul>
                </div>
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
                <div style={{ fontWeight: 600, color: '#f1f5f9' }}>
                  {patient.waiting_minutes} minutes
                </div>
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
                <span style={{ fontSize: '0.72rem', color: '#9ca3af' }}>Active Clinical Cues: </span>
                <span style={{ fontSize: '0.8rem', color: '#fca5a5', fontWeight: 600 }}>
                  {patient.observed_cues.join(', ')}
                </span>
              </div>
            )}
          </div>

          {/* Free-Text Presentation & Symptom Extraction */}
          <div style={{ background: '#1e293b', padding: 14, borderRadius: 10, border: '1px solid rgba(59, 130, 246, 0.2)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: '#93c5fd', display: 'flex', alignItems: 'center', gap: 6 }}>
                <FileText size={15} style={{ color: '#38bdf8' }} />
                Free-Text Presentation & Structured Extraction
              </span>
              <span style={{ fontSize: '0.68rem', color: '#94a3b8', background: 'rgba(255,255,255,0.06)', padding: '2px 8px', borderRadius: 4 }}>
                Source: local-rule-parser (bounded)
              </span>
            </div>

            <textarea
              style={{
                width: '100%',
                background: '#0f172a',
                border: '1px solid rgba(255,255,255,0.12)',
                borderRadius: 6,
                padding: '8px 10px',
                color: '#f1f5f9',
                fontSize: '0.82rem',
                minHeight: '56px',
                resize: 'vertical',
                boxSizing: 'border-box'
              }}
              placeholder="Enter raw narrative (e.g. Patient reports dizziness and weakness since this morning)..."
              value={freeText}
              onChange={(e) => setFreeText(e.target.value)}
            />

            <div style={{ display: 'flex', gap: 8, marginTop: 8, alignItems: 'center' }}>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ padding: '4px 12px', fontSize: '0.78rem' }}
                disabled={isExtracting || !freeText.trim()}
                onClick={handleExtractSymptoms}
              >
                {isExtracting ? 'Extracting...' : 'Structure Symptoms'}
              </button>

              {extractionError && (
                <span style={{ color: '#f87171', fontSize: '0.74rem' }}>{extractionError}</span>
              )}

              {appliedSuccess && (
                <span style={{ color: '#4ade80', fontSize: '0.74rem' }}>✓ Clinical cues updated & triage refreshed!</span>
              )}
            </div>

            {/* Extracted Suggestions Card */}
            {extractedSymptoms.length > 0 && (
              <div style={{ marginTop: 12, background: '#0f172a', padding: 10, borderRadius: 8, border: '1px solid rgba(148, 163, 184, 0.2)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                  <span style={{ fontSize: '0.74rem', color: '#93c5fd', fontWeight: 600 }}>
                    Extracted Symptom Suggestions (Review & Confirm):
                  </span>
                  {isAmbiguous && (
                    <span style={{ fontSize: '0.68rem', color: '#fbbf24', background: 'rgba(245,158,11,0.15)', padding: '2px 6px', borderRadius: 4 }}>
                      ⚠️ Ambiguous Cues Flagged
                    </span>
                  )}
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 8 }}>
                  {extractedSymptoms.map((sym, idx) => (
                    <span
                      key={idx}
                      style={{
                        background: '#1e3a8a',
                        color: '#bfdbfe',
                        padding: '3px 8px',
                        borderRadius: 14,
                        fontSize: '0.74rem',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: 4
                      }}
                    >
                      {sym}
                      <button
                        type="button"
                        onClick={() => removeSymptomTag(idx)}
                        style={{ background: 'none', border: 'none', color: '#93c5fd', cursor: 'pointer', padding: 0, fontSize: '0.75rem' }}
                      >
                        ✕
                      </button>
                    </span>
                  ))}
                </div>

                {/* Add Custom Tag */}
                <div style={{ display: 'flex', gap: 6, marginBottom: 8 }}>
                  <input
                    type="text"
                    placeholder="Add manual symptom tag..."
                    value={newCustomSymptom}
                    onChange={(e) => setNewCustomSymptom(e.target.value)}
                    onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addCustomSymptom(); } }}
                    style={{
                      flex: 1,
                      background: '#1e293b',
                      border: '1px solid rgba(255,255,255,0.1)',
                      borderRadius: 4,
                      padding: '4px 8px',
                      color: '#fff',
                      fontSize: '0.74rem'
                    }}
                  />
                  <button
                    type="button"
                    onClick={addCustomSymptom}
                    style={{ background: '#334155', border: 'none', color: '#cbd5e1', borderRadius: 4, padding: '4px 8px', fontSize: '0.72rem', cursor: 'pointer' }}
                  >
                    + Add
                  </button>
                </div>

                {extractedDuration != null && (
                  <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginBottom: 8 }}>
                    Parsed Duration: <strong>{extractedDuration} minutes</strong>
                  </div>
                )}

                <button
                  type="button"
                  className="btn btn-primary"
                  style={{ width: '100%', padding: '6px', fontSize: '0.78rem' }}
                  onClick={handleConfirmAndApply}
                >
                  Confirm & Apply to Clinical Cues
                </button>
                <div style={{ fontSize: '0.66rem', color: '#64748b', textAlign: 'center', marginTop: 4 }}>
                  Feeds structured symptoms into safety gate & ML risk engine without assigning autonomous priority.
                </div>
              </div>
            )}
          </div>

          {/* Physiological Observations & Deterioration Transition Timeline */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
              <h3 style={{ fontSize: '0.95rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Activity size={16} style={{ color: '#3b82f6' }} />
                {hasDeterioration ? 'Physiological Observation & Deterioration Timeline' : 'Physiological Observations'}
              </h3>
              {hasDeterioration && (
                <span style={{ fontSize: '0.7rem', color: '#fca5a5', fontWeight: 700, background: 'rgba(239, 68, 68, 0.15)', padding: '2px 8px', borderRadius: 4 }}>
                  ⚡ Deterioration Detected
                </span>
              )}
            </div>

            {/* Trajectory Transition Delta Card (only rendered when genuine baseline-to-new-observation transition exists) */}
            {hasDeterioration && prevObs && latestObs && (
              <div style={{ background: '#111827', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 8, padding: 12, marginBottom: 12 }}>
                <div style={{ fontSize: '0.74rem', fontWeight: 700, color: '#f87171', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  AcuityWatch Physiological Transition (Baseline → Latest)
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 8 }}>
                  <div style={{ background: 'rgba(255,255,255,0.03)', padding: 8, borderRadius: 6 }}>
                    <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>SpO2 Saturation</div>
                    <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#f87171' }}>
                      {prevObs.spo2}% → {latestObs.spo2}%
                    </div>
                    <div style={{ fontSize: '0.66rem', color: '#fca5a5' }}>
                      {latestObs.spo2 && prevObs.spo2 ? `${latestObs.spo2 - prevObs.spo2 > 0 ? '+' : ''}${(latestObs.spo2 - prevObs.spo2).toFixed(1)}% drop` : ''}
                    </div>
                  </div>

                  <div style={{ background: 'rgba(255,255,255,0.03)', padding: 8, borderRadius: 6 }}>
                    <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>Heart Rate</div>
                    <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#f87171' }}>
                      {prevObs.heart_rate} → {latestObs.heart_rate} bpm
                    </div>
                    <div style={{ fontSize: '0.66rem', color: '#fca5a5' }}>
                      {latestObs.heart_rate && prevObs.heart_rate ? `+${latestObs.heart_rate - prevObs.heart_rate} bpm spike` : ''}
                    </div>
                  </div>

                  <div style={{ background: 'rgba(255,255,255,0.03)', padding: 8, borderRadius: 6 }}>
                    <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>Blood Pressure</div>
                    <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#f87171' }}>
                      {prevObs.systolic_bp}/{prevObs.diastolic_bp} → {latestObs.systolic_bp}/{latestObs.diastolic_bp}
                    </div>
                    <div style={{ fontSize: '0.66rem', color: '#fca5a5' }}>
                      {latestObs.systolic_bp && prevObs.systolic_bp ? `${latestObs.systolic_bp - prevObs.systolic_bp} mmHg SBP drop` : ''}
                    </div>
                  </div>

                  <div style={{ background: 'rgba(255,255,255,0.03)', padding: 8, borderRadius: 6 }}>
                    <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>Respiration</div>
                    <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#f87171' }}>
                      {prevObs.respiratory_rate}/m → {latestObs.respiratory_rate}/m
                    </div>
                    <div style={{ fontSize: '0.66rem', color: '#fca5a5' }}>
                      {latestObs.respiratory_rate && prevObs.respiratory_rate ? `+${latestObs.respiratory_rate - prevObs.respiratory_rate}/min increase` : ''}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {latestObs ? (
              <div className="vitals-grid">
                <div className="vital-stat-box">
                  <div className="vital-name">Heart Rate (Current)</div>
                  <div className="vital-val" style={{ color: (latestObs.heart_rate ?? 0) > 100 ? '#f87171' : '#f9fafb' }}>
                    {latestObs.heart_rate ?? '--'} <span style={{ fontSize: '0.75rem', fontWeight: 400 }}>bpm</span>
                  </div>
                  {prevObs?.heart_rate && (
                    <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>Baseline: {prevObs.heart_rate} bpm</div>
                  )}
                </div>

                <div className="vital-stat-box">
                  <div className="vital-name">Respiration (Current)</div>
                  <div className="vital-val" style={{ color: (latestObs.respiratory_rate ?? 0) > 22 ? '#f87171' : '#f9fafb' }}>
                    {latestObs.respiratory_rate ?? '--'} <span style={{ fontSize: '0.75rem', fontWeight: 400 }}>/min</span>
                  </div>
                  {prevObs?.respiratory_rate && (
                    <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>Baseline: {prevObs.respiratory_rate}/min</div>
                  )}
                </div>

                <div className="vital-stat-box">
                  <div className="vital-name">Blood Pressure (Current)</div>
                  <div className="vital-val" style={{ color: (latestObs.systolic_bp ?? 120) < 100 ? '#f87171' : '#f9fafb' }}>
                    {latestObs.systolic_bp ?? '--'}/{latestObs.diastolic_bp ?? '--'}
                  </div>
                  {prevObs?.systolic_bp && (
                    <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>Baseline: {prevObs.systolic_bp}/{prevObs.diastolic_bp}</div>
                  )}
                </div>

                <div className="vital-stat-box">
                  <div className="vital-name">SpO2 Oxygen (Current)</div>
                  <div className="vital-val" style={{ color: (latestObs.spo2 ?? 100) < 94 ? '#f87171' : '#34d399' }}>
                    {latestObs.spo2 ? `${latestObs.spo2}%` : '--'}
                  </div>
                  {prevObs?.spo2 && (
                    <div style={{ fontSize: '0.68rem', color: '#9ca3af' }}>Baseline: {prevObs.spo2}%</div>
                  )}
                </div>

                <div className="vital-stat-box">
                  <div className="vital-name">Temperature (Current)</div>
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
                    Decision Support Output
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 4, flexWrap: 'wrap' }}>
                    <div>
                      <span style={{ fontSize: '0.68rem', color: '#9ca3af', display: 'block' }}>AI Recommendation</span>
                      <span className={`priority-tag priority-${triageResult.priority}`} style={{ fontSize: '0.92rem', padding: '4px 12px' }}>
                        {triageResult.priority}
                      </span>
                    </div>
                    <div>
                      <span style={{ fontSize: '0.68rem', color: '#9ca3af', display: 'block' }}>Workflow Action</span>
                      <span style={{ fontSize: '0.86rem', fontWeight: 800, color: triageResult.action === 'ESCALATE' ? '#f87171' : '#60a5fa', background: 'rgba(0,0,0,0.3)', padding: '4px 10px', borderRadius: 4, border: '1px solid rgba(255,255,255,0.1)' }}>
                        {triageResult.action}
                      </span>
                    </div>
                  </div>
                </div>

                <div style={{ display: 'flex', gap: 16, textAlign: 'right' }}>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: '#93c5fd' }}>Risk Score (ML)</span>
                    <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#f1f5f9' }}>
                      {triageResult.risk_score}<span style={{ fontSize: '0.75rem', fontWeight: 500, color: '#94a3b8' }}>/100</span>
                    </div>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: '#93c5fd' }}>Workflow Confidence</span>
                    <div style={{ fontSize: '1.2rem', fontWeight: 800, color: triageResult.confidence_score < 65 ? '#f87171' : '#6ee7b7' }}>
                      {triageResult.confidence_score}%
                    </div>
                  </div>
                </div>
              </div>

              {/* Active Human Override Status */}
              {patient.clinician_decision && patient.clinician_action === 'override' && (
                <div style={{ background: 'rgba(37, 99, 235, 0.15)', border: '1px solid #3b82f6', padding: '10px 14px', borderRadius: 8, marginTop: 10 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '0.78rem', color: '#93c5fd', fontWeight: 800, display: 'flex', alignItems: 'center', gap: 6 }}>
                      👨‍⚕️ Human Override Applied
                    </span>
                    <span style={{ fontSize: '0.68rem', background: '#2563eb', color: 'white', padding: '2px 8px', borderRadius: 4, fontWeight: 700 }}>
                      Clinician Authority Active
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: 16, marginTop: 6, alignItems: 'center', flexWrap: 'wrap' }}>
                    <div>
                      <span style={{ fontSize: '0.68rem', color: '#9ca3af', display: 'block' }}>Clinician Decision:</span>
                      <strong className={`priority-tag priority-${patient.clinician_decision}`} style={{ fontSize: '0.82rem' }}>
                        {patient.clinician_decision}
                      </strong>
                    </div>
                    <div>
                      <span style={{ fontSize: '0.68rem', color: '#9ca3af', display: 'block' }}>Effective Operational Priority:</span>
                      <strong className={`priority-tag priority-${patient.effective_priority || patient.clinician_decision}`} style={{ fontSize: '0.82rem' }}>
                        {patient.effective_priority || patient.clinician_decision}
                      </strong>
                    </div>
                  </div>
                  <div style={{ fontSize: '0.74rem', color: '#cbd5e1', marginTop: 6 }}>
                    <strong>Override Reason:</strong> {patient.override_reason}
                  </div>
                </div>
              )}

              <div style={{ fontSize: '0.68rem', color: '#94a3b8', fontStyle: 'italic', marginTop: -4 }}>
                * Workflow confidence measures intake data completeness and statistical decision boundary margin; it is a decision-support indicator, not a diagnostic probability.
              </div>

              {/* Decision Source & Population Profile Badge */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.74rem', background: 'rgba(59, 130, 246, 0.1)', padding: '6px 10px', borderRadius: 6, border: '1px solid rgba(59, 130, 246, 0.2)' }}>
                <span style={{ color: '#93c5fd' }}>
                  <strong>Decision Authority: </strong> Safety Gate + Calibrated Risk Model
                </span>
                <span style={{ color: '#cbd5e1', fontWeight: 600 }}>
                  Profile: <span style={{ textTransform: 'uppercase', color: '#60a5fa' }}>{triageResult.population_profile}</span>
                </span>
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
