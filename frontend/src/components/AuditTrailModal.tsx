import React, { useState, useEffect } from 'react';
import { X, FileText, Filter } from 'lucide-react';
import type { AuditEvent } from '../types';
import { api } from '../services/api';

interface AuditTrailModalProps {
  onClose: () => void;
}

export const AuditTrailModal: React.FC<AuditTrailModalProps> = ({ onClose }) => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterPatient, setFilterPatient] = useState('');

  useEffect(() => {
    loadAudit();
  }, []);

  const loadAudit = async () => {
    try {
      setLoading(true);
      const data = await api.getAuditTrail();
      setEvents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredEvents = events.filter((e) => {
    if (!filterPatient) return true;
    return e.patient_id?.toLowerCase().includes(filterPatient.toLowerCase());
  });

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: 1000 }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <FileText size={18} style={{ color: '#60a5fa' }} />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>FHIR-Inspired Clinical & Security Audit Trail</h3>
          </div>
          <button className="btn btn-secondary" onClick={onClose} style={{ padding: 4 }}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontSize: '0.82rem', color: '#9ca3af' }}>
              Immutable audit log capturing triage recommendations, clinician overrides, and simulation events.
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Filter size={14} style={{ color: '#9ca3af' }} />
              <input
                type="text"
                placeholder="Filter by Patient ID (e.g. PT-001)..."
                value={filterPatient}
                onChange={(e) => setFilterPatient(e.target.value)}
                style={{
                  background: '#1f2937',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: 6,
                  padding: '4px 8px',
                  color: 'white',
                  fontSize: '0.78rem',
                }}
              />
            </div>
          </div>

          {loading ? (
            <div>Loading audit log...</div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table className="audit-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Actor</th>
                    <th>Event Type</th>
                    <th>Patient</th>
                    <th>AI Rec</th>
                    <th>Decision</th>
                    <th>Override Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredEvents.map((evt) => (
                    <tr key={evt.audit_id}>
                      <td style={{ fontFamily: 'JetBrains Mono', fontSize: '0.74rem' }}>
                        {new Date(evt.timestamp).toLocaleTimeString()}
                      </td>
                      <td>
                        <span style={{ fontWeight: 600 }}>{evt.actor_id}</span> ({evt.actor_role})
                      </td>
                      <td>
                        <span
                          style={{
                            padding: '2px 6px',
                            borderRadius: 4,
                            fontSize: '0.7rem',
                            fontWeight: 700,
                            background: evt.event_type === 'override' ? '#7f1d1d' : '#1e3a8a',
                            color: evt.event_type === 'override' ? '#fca5a5' : '#93c5fd',
                          }}
                        >
                          {evt.event_type}
                        </span>
                      </td>
                      <td style={{ fontWeight: 700 }}>{evt.patient_id ?? '--'}</td>
                      <td>{evt.recommendation ?? '--'}</td>
                      <td style={{ fontWeight: 700 }}>{evt.decision ?? '--'}</td>
                      <td style={{ color: evt.override_reason ? '#fde68a' : '#6b7280', fontSize: '0.75rem' }}>
                        {evt.override_reason ?? 'None'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
