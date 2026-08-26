import type { Patient, Observation, TriageResult, ClinicianDecisionPayload, AuditEvent, SimulationStatus } from '../types';

const API_BASE = 'http://localhost:8000/api';

export const api = {
  async getPatients(surge: boolean = false): Promise<Patient[]> {
    const res = await fetch(`${API_BASE}/patients?surge=${surge}`);
    if (!res.ok) throw new Error('Failed to fetch patients');
    return res.json();
  },

  async getPatient(id: string): Promise<Patient> {
    const res = await fetch(`${API_BASE}/patients/${id}`);
    if (!res.ok) throw new Error('Failed to fetch patient details');
    return res.json();
  },

  async getLatestTriageResult(id: string): Promise<TriageResult> {
    const res = await fetch(`${API_BASE}/patients/${id}/triage-latest`);
    if (!res.ok) throw new Error('Failed to fetch triage result');
    return res.json();
  },

  async addObservation(patientId: string, obs: Partial<Observation>): Promise<Observation> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/observations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(obs),
    });
    if (!res.ok) throw new Error('Failed to record observation');
    return res.json();
  },

  async recordDecision(patientId: string, payload: ClinicianDecisionPayload) {
    const res = await fetch(`${API_BASE}/patients/${patientId}/decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to record decision' }));
      throw new Error(err.detail || 'Failed to record decision');
    }
    return res.json();
  },

  async getAttentionQueue(): Promise<Patient[]> {
    const res = await fetch(`${API_BASE}/reassessment/queue`);
    if (!res.ok) throw new Error('Failed to fetch reassessment queue');
    return res.json();
  },

  async getSimulationStatus(): Promise<SimulationStatus> {
    const res = await fetch(`${API_BASE}/simulation/status`);
    if (!res.ok) throw new Error('Failed to get simulation status');
    return res.json();
  },

  async advanceTime(minutes: number) {
    const res = await fetch(`${API_BASE}/simulation/advance-time`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ minutes }),
    });
    if (!res.ok) throw new Error('Failed to advance time');
    return res.json();
  },

  async toggleSurge(surge_active: boolean) {
    const res = await fetch(`${API_BASE}/simulation/surge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ surge_active }),
    });
    if (!res.ok) throw new Error('Failed to toggle surge mode');
    return res.json();
  },

  async injectDeterioration(patientId: string) {
    const res = await fetch(`${API_BASE}/simulation/inject-deterioration`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient_id: patientId }),
    });
    if (!res.ok) throw new Error('Failed to inject deterioration');
    return res.json();
  },

  async resetSimulation() {
    const res = await fetch(`${API_BASE}/simulation/reset`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to reset simulation');
    return res.json();
  },

  async getAuditTrail(patientId?: string): Promise<AuditEvent[]> {
    const url = patientId ? `${API_BASE}/audit?patient_id=${patientId}` : `${API_BASE}/audit`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch audit trail');
    return res.json();
  }
};
