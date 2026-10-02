import { useCallback, useEffect, useState } from 'react';
import { workspaceAPI } from '../services/workspace';
import { casesAPI, profileAPI, notificationsAPI, subsidiesAPI } from '../services/api';

const initial = { plots: [], resources: [], bookings: [], groups: [], cashbook: [], documents: [], cases: [], profile: null, notifications: [], schemes: [] };

export default function useWorkspace(user) {
  const [data, setData] = useState(initial);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const refresh = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const keys = ['plots', 'resources', 'bookings', 'groups', 'cashbook', 'documents'];
      const result = await Promise.all([...keys.map(k => workspaceAPI.get(k)), casesAPI.getCases(), profileAPI.getProfile(), notificationsAPI.getNotifications(), subsidiesAPI.getSchemes()]);
      setData(Object.fromEntries([...keys, 'cases', 'profile', 'notifications', 'schemes'].map((key, i) => [key, result[i]])));
      setError('');
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  }, [user?.id]);
  useEffect(() => { setData(initial); refresh(); }, [refresh]);
  useEffect(() => {
    const timer = setInterval(() => { if (document.visibilityState === 'visible' && navigator.onLine) refresh(); }, 30000);
    window.addEventListener('online', refresh);
    return () => { clearInterval(timer); window.removeEventListener('online', refresh); };
  }, [refresh]);
  return { data, loading, error, refresh };
}
