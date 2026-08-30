import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { CommandCenter } from './components/CommandCenter';
import { PatientDetailModal } from './components/PatientDetailModal';
import { OverrideModal } from './components/OverrideModal';
import { AuditTrailModal } from './components/AuditTrailModal';
import { LoginPage } from './components/LoginPage';
import { AdminConfigModal } from './components/AdminConfigModal';
import type { Patient, SimulationStatus, User } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [checkingAuth, setCheckingAuth] = useState<boolean>(true);
  const [showAdminModal, setShowAdminModal] = useState<boolean>(false);
  const [authErrorBanner, setAuthErrorBanner] = useState<string | null>(null);

  const [patients, setPatients] = useState<Patient[]>([]);
  const [simulationStatus, setSimulationStatus] = useState<SimulationStatus>({
    surge_active: false,
    time_offset_minutes: 0,
    disclaimer: 'Concept prototype • Synthetic data',
  });

  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [overridePatient, setOverridePatient] = useState<Patient | null>(null);
  const [showAuditModal, setShowAuditModal] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Validate existing stored token on mount
  useEffect(() => {
    checkInitialAuth();
  }, []);

  const checkInitialAuth = async () => {
    const token = api.getToken();
    if (token) {
      try {
        const user = await api.getMe();
        setCurrentUser(user);
      } catch {
        api.logout();
        setCurrentUser(null);
      }
    } else {
      setCurrentUser(null);
    }
    setCheckingAuth(false);
  };

  useEffect(() => {
    if (currentUser) {
      fetchData();
      const interval = setInterval(fetchData, 4000);
      return () => clearInterval(interval);
    }
  }, [currentUser, simulationStatus.surge_active]);

  const fetchData = async () => {
    try {
      setAuthErrorBanner(null);
      const [patientsData, simData] = await Promise.all([
        api.getPatients(simulationStatus.surge_active),
        api.getSimulationStatus(),
      ]);
      setPatients(patientsData);
      setSimulationStatus(simData);

      // If a patient modal is open, refresh their data too
      setSelectedPatient(prev => prev ? (patientsData.find(p => p.patient_id === prev.patient_id) || prev) : null);
    } catch (err: any) {
      console.error('Error polling data:', err);
      if (err.message && (err.message.includes('401') || err.message.includes('403'))) {
        setAuthErrorBanner(err.message);
        if (err.message.includes('401')) {
          handleLogout();
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAdvanceTime = async (mins: number) => {
    try {
      await api.advanceTime(mins);
      await fetchData();
    } catch (err: any) {
      setAuthErrorBanner(err.message);
    }
  };

  const handleToggleSurge = async (active: boolean) => {
    try {
      await api.toggleSurge(active);
      await fetchData();
    } catch (err: any) {
      setAuthErrorBanner(err.message);
    }
  };

  const handleReset = async () => {
    try {
      await api.resetSimulation();
      await fetchData();
    } catch (err: any) {
      setAuthErrorBanner(err.message);
    }
  };

  const handleTriggerDeterioration = async (patientId: string) => {
    try {
      await api.injectDeterioration(patientId);
      await fetchData();
    } catch (err: any) {
      setAuthErrorBanner(err.message);
    }
  };

  const handleLoginSuccess = (user: User) => {
    setCurrentUser(user);
    setAuthErrorBanner(null);
    setLoading(true);
  };

  const handleLogout = () => {
    api.logout();
    setCurrentUser(null);
    setSelectedPatient(null);
    setOverridePatient(null);
    setShowAuditModal(false);
    setShowAdminModal(false);
  };

  // 1. Initial auth check spinner
  if (checkingAuth) {
    return (
      <div className="login-page-wrapper" style={{ justifyContent: 'center', alignItems: 'center' }}>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Initializing AcuityFlow session...
        </div>
      </div>
    );
  }

  // 2. Unauthenticated: Render dedicated Login Page
  if (!currentUser) {
    return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  }

  // 3. Authenticated: Render Emergency Department Dashboard
  return (
    <div className="app-container">
      <Header
        simulationStatus={simulationStatus}
        currentUser={currentUser}
        onAdvanceTime={handleAdvanceTime}
        onToggleSurge={handleToggleSurge}
        onReset={handleReset}
        onOpenAudit={() => setShowAuditModal(true)}
        onOpenAdmin={() => setShowAdminModal(true)}
        onLogout={handleLogout}
      />

      {/* 403 / 401 Authorization Error Notification Banner */}
      {authErrorBanner && (
        <div className="danger-box" style={{ margin: '10px 24px 0 24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
            <span>
              <strong>Access Restriction:</strong> {authErrorBanner}
            </span>
            <button
              onClick={() => setAuthErrorBanner(null)}
              style={{ background: 'transparent', border: 'none', color: '#fca5a5', cursor: 'pointer', textDecoration: 'underline', fontSize: '0.75rem' }}
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      <main>
        {loading ? (
          <div style={{ textAlign: 'center', padding: 50, color: 'var(--text-secondary)' }}>
            Loading Emergency Department queue...
          </div>
        ) : (
          <CommandCenter
            patients={patients}
            surgeActive={simulationStatus.surge_active}
            onSelectPatient={(p) => setSelectedPatient(p)}
            onTriggerDeterioration={handleTriggerDeterioration}
          />
        )}
      </main>

      {/* Patient Detail Modal */}
      {selectedPatient && (
        <PatientDetailModal
          patient={selectedPatient}
          onClose={() => setSelectedPatient(null)}
          onOpenOverride={(p) => setOverridePatient(p)}
          onDecisionSubmitted={fetchData}
          onTriggerDeterioration={handleTriggerDeterioration}
        />
      )}

      {/* Clinician Override Modal */}
      {overridePatient && (
        <OverrideModal
          patient={overridePatient}
          onClose={() => setOverridePatient(null)}
          onOverrideSuccess={fetchData}
        />
      )}

      {/* Audit Trail Modal */}
      {showAuditModal && <AuditTrailModal onClose={() => setShowAuditModal(false)} />}

      {/* Admin Configuration Modal */}
      <AdminConfigModal
        isOpen={showAdminModal}
        onClose={() => setShowAdminModal(false)}
      />
    </div>
  );
};

export default App;
