import React, { useState } from 'react';
import { X, ShieldAlert, Check } from 'lucide-react';
import type { Patient } from '../types';
import { api } from '../services/api';

interface OverrideModalProps {
  patient: Patient;
  onClose: () => void;
  onOverrideSuccess: () => void;
}

export const OverrideModal: React.FC<OverrideModalProps> = ({
  patient,
  onClose,
  onOverrideSuccess,
}) => {
  const [finalPriority, setFinalPriority] = useState<any>(patient.current_priority);
  const [reason, setReason] = useState<string>('Additional clinical context from physical exam');
  const [note, setNote] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      await api.recordDecision(patient.patient_id, {
        clinician_id: 'nurse-101',
        actor_role: 'nurse',
        clinician_action: 'override',
        final_priority: finalPriority,
        override_reason: reason,
        clinician_note: note,
      });
      onOverrideSuccess();
      onClose();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 120 }}>
      <div className="modal-content" style={{ maxWidth: 550 }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <ShieldAlert size={18} style={{ color: '#f59e0b' }} />
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700 }}>Clinician Decision Override</h3>
          </div>
          <button className="btn btn-secondary" onClick={onClose} style={{ padding: 4 }}>
            <X size={16} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div style={{ background: '#1f2937', padding: 12, borderRadius: 8, fontSize: '0.82rem' }}>
              <div><strong>Patient:</strong> {patient.name} ({patient.patient_id})</div>
              <div style={{ marginTop: 4 }}>
                <strong>AI Recommended Priority: </strong>
                <span className={`priority-tag priority-${patient.current_priority}`} style={{ marginLeft: 6 }}>
                  {patient.current_priority}
                </span>
                <span style={{ marginLeft: 8, color: '#9ca3af' }}>({patient.current_confidence}% confidence)</span>
              </div>
            </div>

            {/* Final Priority Selector */}
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#9ca3af', marginBottom: 6 }}>
                New Clinician Priority:
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 6 }}>
                {['IMMEDIATE', 'HIGH', 'MODERATE', 'LOW', 'REVIEW'].map((p) => (
                  <button
                    type="button"
                    key={p}
                    className={`btn ${finalPriority === p ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ fontSize: '0.72rem', padding: '6px 2px', justifyContent: 'center' }}
                    onClick={() => setFinalPriority(p)}
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>

            {/* Mandatory Override Reason */}
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#9ca3af', marginBottom: 6 }}>
                Mandatory Override Reason:
              </label>
              <select
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                style={{
                  width: '100%',
                  background: '#1f2937',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: 6,
                  padding: 8,
                  color: 'white',
                  fontSize: '0.82rem',
                }}
              >
                <option value="Additional clinical context from physical exam">Additional clinical context from physical exam</option>
                <option value="Known baseline anomaly / chronic condition">Known baseline anomaly / chronic condition</option>
                <option value="Direct physician assessment override">Direct physician assessment override</option>
                <option value="Atypical presentation identified">Atypical presentation identified</option>
                <option value="Environmental or social risk factor">Environmental or social risk factor</option>
              </select>
            </div>

            {/* Clinical Note */}
            <div>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#9ca3af', marginBottom: 6 }}>
                Clinical Explanation / Note (Logged to Audit Trail):
              </label>
              <textarea
                rows={3}
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Enter clinical rationale for override decision..."
                style={{
                  width: '100%',
                  background: '#1f2937',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: 6,
                  padding: 8,
                  color: 'white',
                  fontSize: '0.82rem',
                  resize: 'vertical',
                }}
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              <Check size={14} />
              {submitting ? 'Logging...' : 'Confirm & Log Override'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
