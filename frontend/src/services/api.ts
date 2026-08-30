import type {
  Patient,
  Observation,
  TriageResult,
  ClinicianDecisionPayload,
  AuditEvent,
  SimulationStatus,
  User,
  LoginCredentials,
  AuthResponse,
  AdminConfig
} from '../types';

const API_BASE = 'http://localhost:8000/api';
const TOKEN_KEY = 'acuityflow_token';
const USER_KEY = 'acuityflow_user';

function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token: string | null) {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}

function getAuthHeaders(): Record<string, string> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

async function handleResponse<T>(res: Response, defaultErrMsg: string): Promise<T> {
  if (!res.ok) {
    const errorBody = await res.json().catch(() => ({ detail: defaultErrMsg }));
    const errorMsg = errorBody.detail || defaultErrMsg;
    if (res.status === 403) {
      throw new Error(`Access Denied (HTTP 403): ${errorMsg}`);
    }
    if (res.status === 401) {
      throw new Error(`Authentication Required (HTTP 401): ${errorMsg}`);
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export const api = {
  // --- Authentication ---
  getToken,
  setToken,
  
  getCurrentStoredUser(): User | null {
    const userStr = localStorage.getItem(USER_KEY);
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
    });
    const authData = await handleResponse<AuthResponse>(res, 'Invalid credentials');
    setToken(authData.access_token);
    const userObj: User = {
      user_id: authData.user_id,
      username: authData.username,
      role: authData.role,
      is_active: true,
      created_at: new Date().toISOString()
    };
    localStorage.setItem(USER_KEY, JSON.stringify(userObj));
    return authData;
  },

  async getMe(): Promise<User> {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getAuthHeaders(),
    });
    const user = await handleResponse<User>(res, 'Failed to fetch user session');
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    return user;
  },

  logout() {
    setToken(null);
  },

  // --- Patients & Triage ---
  async getPatients(surge: boolean = false): Promise<Patient[]> {
    const res = await fetch(`${API_BASE}/patients?surge=${surge}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<Patient[]>(res, 'Failed to fetch patients');
  },

  async getPatient(id: string): Promise<Patient> {
    const res = await fetch(`${API_BASE}/patients/${id}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<Patient>(res, 'Failed to fetch patient details');
  },

  async getLatestTriageResult(id: string): Promise<TriageResult> {
    const res = await fetch(`${API_BASE}/patients/${id}/triage-latest`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<TriageResult>(res, 'Failed to fetch triage result');
  },

  async addObservation(patientId: string, obs: Partial<Observation>): Promise<Observation> {
    const res = await fetch(`${API_BASE}/patients/${patientId}/observations`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(obs),
    });
    return handleResponse<Observation>(res, 'Failed to record observation');
  },

  async recordDecision(patientId: string, payload: ClinicianDecisionPayload) {
    const res = await fetch(`${API_BASE}/patients/${patientId}/decision`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse(res, 'Failed to record decision');
  },

  async getAttentionQueue(): Promise<Patient[]> {
    const res = await fetch(`${API_BASE}/reassessment/queue`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<Patient[]>(res, 'Failed to fetch reassessment queue');
  },

  // --- Simulation Controls ---
  async getSimulationStatus(): Promise<SimulationStatus> {
    const res = await fetch(`${API_BASE}/simulation/status`);
    return handleResponse<SimulationStatus>(res, 'Failed to get simulation status');
  },

  async advanceTime(minutes: number) {
    const res = await fetch(`${API_BASE}/simulation/advance-time`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ minutes }),
    });
    return handleResponse(res, 'Failed to advance time');
  },

  async toggleSurge(surge_active: boolean) {
    const res = await fetch(`${API_BASE}/simulation/surge`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ surge_active }),
    });
    return handleResponse(res, 'Failed to toggle surge mode');
  },

  async injectDeterioration(patientId: string) {
    const res = await fetch(`${API_BASE}/simulation/inject-deterioration`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ patient_id: patientId }),
    });
    return handleResponse(res, 'Failed to inject deterioration');
  },

  async resetSimulation() {
    const res = await fetch(`${API_BASE}/simulation/reset`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    return handleResponse(res, 'Failed to reset simulation');
  },

  // --- Audit Trail ---
  async getAuditTrail(patientId?: string): Promise<AuditEvent[]> {
    const url = patientId ? `${API_BASE}/audit?patient_id=${patientId}` : `${API_BASE}/audit`;
    const res = await fetch(url, {
      headers: getAuthHeaders(),
    });
    return handleResponse<AuditEvent[]>(res, 'Failed to fetch audit trail');
  },

  // --- NLP & Symptom Confirmation ---
  async extractSymptoms(text: string): Promise<{ symptoms: string[]; duration_minutes?: number | null; extracted_by: string; is_ambiguous: boolean }> {
    const res = await fetch(`${API_BASE}/nlp/extract-symptoms`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({ text }),
    });
    return handleResponse(res, 'Failed to extract symptoms');
  },

  async updatePatientSymptoms(patientId: string, payload: { symptoms: string[]; narrative_text?: string; duration_minutes?: number }) {
    const res = await fetch(`${API_BASE}/patients/${patientId}/symptoms`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return handleResponse(res, 'Failed to update symptoms');
  },

  // --- Admin Configuration ---
  async getAdminConfig(): Promise<AdminConfig> {
    const res = await fetch(`${API_BASE}/admin/config`, {
      headers: getAuthHeaders(),
    });
    return handleResponse<AdminConfig>(res, 'Failed to fetch admin configuration');
  },

  async updateAdminConfig(update: Partial<AdminConfig>): Promise<AdminConfig> {
    const res = await fetch(`${API_BASE}/admin/config`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(update),
    });
    return handleResponse<AdminConfig>(res, 'Failed to update admin configuration');
  }
};
