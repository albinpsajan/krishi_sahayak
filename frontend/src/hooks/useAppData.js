import { useState, useEffect } from 'react';
import {
  casesAPI,
  subsidiesAPI,
  auditAPI,
  notificationsAPI,
  profileAPI,
} from '../services/api';

/**
 * useAppData - loads every portal dataset once a user is present.
 * Centralizes fetching so pages stay presentational.
 */
export default function useAppData(user) {
  const [cases, setCases] = useState([]);
  const [subsidies, setSubsidies] = useState([]);
  const [applications, setApplications] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [userProfile, setUserProfile] = useState(null);

  const loadAllData = async () => {
    if (!user) return;
    try {
      const [c, s, a, log, n, prof] = await Promise.all([
        casesAPI.getCases(),
        subsidiesAPI.getSchemes(),
        subsidiesAPI.getApplications(),
        auditAPI.getLedger(),
        notificationsAPI.getNotifications(),
        profileAPI.getProfile(),
      ]);
      setCases(c);
      setSubsidies(s);
      setApplications(a);
      setAuditLogs(log);
      setNotifications(n);
      setUserProfile(prof);
    } catch (e) {
      console.error('Data load error:', e);
    }
  };

  useEffect(() => {
    if (user?.profile_completed) {
      loadAllData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id, user?.profile_completed]);

  const clearAll = () => {
    setCases([]);
    setSubsidies([]);
    setApplications([]);
    setAuditLogs([]);
    setNotifications([]);
    setUserProfile(null);
  };

  return {
    cases, setCases,
    subsidies, setSubsidies,
    applications, setApplications,
    auditLogs, setAuditLogs,
    notifications, setNotifications,
    userProfile, setUserProfile,
    loadAllData,
    clearAll,
  };
}
