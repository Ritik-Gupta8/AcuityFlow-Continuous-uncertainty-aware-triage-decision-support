import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { CommandCenter } from './components/CommandCenter';
import { PatientDetailModal } from './components/PatientDetailModal';
import { OverrideModal } from './components/OverrideModal';
import { AuditTrailModal } from './components/AuditTrailModal';
import type { Patient, SimulationStatus } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
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

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, [simulationStatus.surge_active]);

  const fetchData = async () => {
    try {
      const [patientsData, simData] = await Promise.all([
        api.getPatients(simulationStatus.surge_active),
        api.getSimulationStatus(),
      ]);
      setPatients(patientsData);
      setSimulationStatus(simData);

      // If a patient modal is open, refresh their data too
      setSelectedPatient(prev => prev ? (patientsData.find(p => p.patient_id === prev.patient_id) || prev) : null);
    } catch (err) {
      console.error('Error polling data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAdvanceTime = async (mins: number) => {
    try {
      await api.advanceTime(mins);
      await fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleToggleSurge = async (active: boolean) => {
    try {
      await api.toggleSurge(active);
      await fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleReset = async () => {
    try {
      await api.resetSimulation();
      await fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleTriggerDeterioration = async (patientId: string) => {
    try {
      await api.injectDeterioration(patientId);
      await fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="app-container">
      <Header
        simulationStatus={simulationStatus}
        onAdvanceTime={handleAdvanceTime}
        onToggleSurge={handleToggleSurge}
        onReset={handleReset}
        onOpenAudit={() => setShowAuditModal(true)}
      />

      <main>
        {loading ? (
          <div style={{ textAlign: 'center', padding: 50, color: '#9ca3af' }}>
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
    </div>
  );
};

export default App;
