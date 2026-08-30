import React, { useEffect, useState } from 'react';
import { Settings, X, CheckCircle, AlertTriangle, Shield } from 'lucide-react';
import { api } from '../services/api';
import type { AdminConfig } from '../types';

interface AdminConfigModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AdminConfigModal: React.FC<AdminConfigModalProps> = ({ isOpen, onClose }) => {
  const [config, setConfig] = useState<AdminConfig | null>(null);
  const [pediatricAge, setPediatricAge] = useState<number>(17);
  const [geriatricAge, setGeriatricAge] = useState<number>(65);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadConfig();
    }
  }, [isOpen]);

  const loadConfig = async () => {
    setLoading(true);
    setStatusMsg(null);
    try {
      const data = await api.getAdminConfig();
      setConfig(data);
      setPediatricAge(data.pediatric_max_age);
      setGeriatricAge(data.geriatric_min_age);
    } catch (err: any) {
      setStatusMsg({ type: 'error', text: err.message || 'Failed to load configuration' });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setStatusMsg(null);
    try {
      const updated = await api.updateAdminConfig({
        pediatric_max_age: pediatricAge,
        geriatric_min_age: geriatricAge,
      });
      setConfig(updated);
      setStatusMsg({ type: 'success', text: 'Demographic policy configuration updated and administrative audit event logged.' });
    } catch (err: any) {
      setStatusMsg({ type: 'error', text: err.message || 'Failed to save configuration' });
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" style={{ maxWidth: 620 }} onClick={(e) => e.stopPropagation()}>
        <div className="modal-header" style={{ background: 'linear-gradient(90deg, #311042, #111827)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <Settings size={20} color="#f59e0b" />
            <div>
              <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>
                System & Population Policy Configuration
              </h2>
              <div style={{ fontSize: '0.72rem', color: '#fbbf24', display: 'flex', alignItems: 'center', gap: 4 }}>
                <Shield size={12} /> Protected Administrative Interface (Role: ADMIN)
              </div>
            </div>
          </div>
          <button className="btn btn-secondary" onClick={onClose} style={{ padding: 6 }}>
            <X size={16} />
          </button>
        </div>

        <div className="modal-body">
          {loading ? (
            <div style={{ textAlign: 'center', padding: 30, color: 'var(--text-secondary)' }}>
              Loading system configuration...
            </div>
          ) : (
            <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
              {/* System Metadata */}
              <div style={{ background: '#1f2937', padding: 14, borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Project:</span>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f9fafb' }}>{config?.project_name}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Version:</span>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f9fafb' }}>{config?.version}</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Min Confidence Gate:</span>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#2dd4bf' }}>{config?.min_confidence_threshold}%</div>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Min Completeness Gate:</span>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#60a5fa' }}>{config?.min_completeness_threshold}%</div>
                </div>
              </div>

              {/* Age Thresholds */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  Demographic Profile Age Cutoffs
                </div>

                <div className="form-group">
                  <label htmlFor="pediatric-age">Pediatric Upper Age Limit (Years)</label>
                  <input
                    id="pediatric-age"
                    type="number"
                    min="1"
                    max="25"
                    value={pediatricAge}
                    onChange={(e) => setPediatricAge(parseInt(e.target.value) || 17)}
                    className="input-field"
                    required
                  />
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    Patients with age &le; this limit resolve to the pediatric scoring policy profile.
                  </span>
                </div>

                <div className="form-group">
                  <label htmlFor="geriatric-age">Geriatric Lower Age Limit (Years)</label>
                  <input
                    id="geriatric-age"
                    type="number"
                    min="50"
                    max="100"
                    value={geriatricAge}
                    onChange={(e) => setGeriatricAge(parseInt(e.target.value) || 65)}
                    className="input-field"
                    required
                  />
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    Patients with age &ge; this limit resolve to the geriatric scoring policy profile.
                  </span>
                </div>
              </div>

              {/* Status Message */}
              {statusMsg && (
                <div
                  className={statusMsg.type === 'success' ? 'warning-box' : 'danger-box'}
                  style={statusMsg.type === 'success' ? { background: 'rgba(16, 185, 129, 0.15)', borderColor: '#10b981', color: '#6ee7b7' } : {}}
                >
                  {statusMsg.type === 'success' ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
                  <span>{statusMsg.text}</span>
                </div>
              )}

              <div className="modal-footer" style={{ padding: '12px 0 0 0', background: 'transparent', borderTop: '1px solid var(--border-color)' }}>
                <button type="button" className="btn btn-secondary" onClick={onClose}>
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="btn btn-primary"
                  style={{ background: 'linear-gradient(135deg, #d97706, #b45309)', borderColor: '#f59e0b' }}
                >
                  {saving ? 'Updating...' : 'Save Configuration'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
