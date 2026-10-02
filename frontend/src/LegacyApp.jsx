import React, { useState, useEffect } from 'react';
import Header from './layouts/Header';
import NavBar from './layouts/NavBar';
import FarmerDashboard from './pages/FarmerDashboard';
import OfficerDashboard from './pages/OfficerDashboard';
import CasesPage from './pages/CasesPage';
import SubsidiesPage from './pages/SubsidiesPage';
import NotificationsPage from './pages/NotificationsPage';
import ProfilePage from './pages/ProfilePage';
import AuditPage from './pages/AuditPage';
import CropCaseWizardModal from './components/CropCaseWizardModal';
import CaseDetailModal from './components/CaseDetailModal';
import AutoClerkModal from './components/AutoClerkModal';
import useAuthGate from './hooks/useAuthGate';
import useAppData from './hooks/useAppData';
import LoginPage from './pages/LoginPage';
import { subsidiesAPI, officerAPI } from './services/api';
import { isFarmerRole, isOfficerRole, homeTabForRole } from './utils/roles';

export default function App() {
  const {
    user, setUser, authChecked, needsOnboarding, setNeedsOnboarding, handleLogout,
  } = useAuthGate();
  const {
    cases, subsidies, applications, auditLogs, notifications, userProfile, loadAllData,
  } = useAppData(user);

  const [currentTab, setCurrentTab] = useState('home');
  const [showNewCaseModal, setShowNewCaseModal] = useState(false);
  const [selectedCase, setSelectedCase] = useState(null);
  const [autoClerkReport, setAutoClerkReport] = useState(null);
  const [lang, setLang] = useState('en'); // 'en' or 'ml'

  // Route to the portal matching the role once the user is loaded
  useEffect(() => {
    if (user?.profile_completed) {
      setCurrentTab(homeTabForRole(user.role));
    }
  }, [user]);

  const isFarmer = isFarmerRole(user);
  const isOfficer = isOfficerRole(user);

  const refreshData = async () => {
    await loadAllData();
  };

  // ---- Auth gate: login page & onboarding before anything else ----
  if (!authChecked) {
    return (
      <div className="auth-page">
        <div className="auth-panel" style={{ textAlign: 'center', color: 'var(--text-secondary)' }}>
          🌱 Loading KrishiSahayak AI...
        </div>
      </div>
    );
  }

  if (!user || needsOnboarding) {
    return (
      <AuthGateWrapper
        needsOnboarding={needsOnboarding}
        setUser={setUser}
        setNeedsOnboarding={setNeedsOnboarding}
        refreshData={refreshData}
      />
    );
  }

  return (
    <div className="app-root">
      <Header lang={lang} onToggleLang={() => setLang(lang === 'en' ? 'ml' : 'en')} onLogout={handleLogout} />

      <NavBar
        isFarmer={isFarmer}
        isOfficer={isOfficer}
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        unreadCount={notifications.filter((n) => !n.is_read).length}
      />

      <main className="main-content">
        {isFarmer && currentTab === 'home' && (
          <FarmerDashboard
            user={user}
            cases={cases}
            subsidies={subsidies}
            auditLogs={auditLogs}
            lang={lang}
            onNewCase={() => setShowNewCaseModal(true)}
            onViewCase={setSelectedCase}
          />
        )}

        {isOfficer && currentTab === 'dashboard' && (
          <OfficerDashboard cases={cases} applications={applications} onReviewCase={setSelectedCase} />
        )}

        {currentTab === 'cases' && (
          <CasesPage cases={cases} onViewCase={setSelectedCase} />
        )}

        {currentTab === 'subsidies' && (
          <SubsidiesPage
            subsidies={subsidies}
            applications={applications}
            isFarmer={isFarmer}
            isOfficer={isOfficer}
            onApply={async (scheme) => {
              try {
                await subsidiesAPI.apply({ scheme_id: scheme.id, requested_subsidy_amount: scheme.max_subsidy_amount });
                alert('Subsidy Application submitted to SubsidyChain Rule Engine!');
                await refreshData();
              } catch (e) {
                alert('Error submitting application: ' + e.message);
              }
            }}
            onDecide={async (application, decision) => {
              await subsidiesAPI.decideApplication(application.id, decision);
              await refreshData();
            }}
          />
        )}

        {currentTab === 'notifications' && <NotificationsPage notifications={notifications} />}

        {currentTab === 'profile' && <ProfilePage userProfile={userProfile} />}

        {currentTab === 'audit' && <AuditPage auditLogs={auditLogs} />}
      </main>

      {/* MODAL: NEW CROP CASE & CROPDOCTOR AI WIZARD */}
      {showNewCaseModal && (
        <CropCaseWizardModal
          onClose={() => setShowNewCaseModal(false)}
          onSuccess={async () => {
            setShowNewCaseModal(false);
            await refreshData();
          }}
        />
      )}

      {/* MODAL: CASE DETAIL & OFFICER REVIEW */}
      {selectedCase && (
        <CaseDetailModal
          caseData={selectedCase}
          isOfficer={isOfficer}
          onClose={() => setSelectedCase(null)}
          onUpdate={async () => {
            setSelectedCase(null);
            await refreshData();
          }}
          onGenerateAutoClerk={async (id) => {
            const rep = await officerAPI.getAutoClerkReport(id);
            setAutoClerkReport(rep);
          }}
        />
      )}

      {/* MODAL: AUTOCLERK REPORT DISPLAY */}
      {autoClerkReport && <AutoClerkModal report={autoClerkReport} onClose={() => setAutoClerkReport(null)} />}
    </div>
  );
}

// Small wrapper so App stays readable: wires LoginPage to auth success handling
function AuthGateWrapper({ needsOnboarding, setUser, setNeedsOnboarding, refreshData }) {
  const [token, setToken] = [localStorage.getItem('krishi_token'), (t) => {
    if (t) localStorage.setItem('krishi_token', t);
    else localStorage.removeItem('krishi_token');
  }];

  const handleAuthSuccess = async (res) => {
    setToken(res.access_token);
    setUser(res.user);
    const incomplete = !res.user.profile_completed;
    setNeedsOnboarding(incomplete);
    await refreshData();
  };

  return (
    <LoginPage
      key={needsOnboarding ? 'details' : 'login'}
      initialMode={needsOnboarding ? 'details' : 'login'}
      onAuthSuccess={handleAuthSuccess}
    />
  );
}