/**
 * KrishiSahayak AI API Client (single place for all backend calls).
 * Feature groupings mirror the backend routers (docs/architecture.md section 6).
 */

const API_BASE = '/api';

export const apiCall = async (endpoint, method = 'GET', body = null, token = null) => {
  const headers = {
    'Content-Type': 'application/json',
  };

  const storedToken = token || localStorage.getItem('krishi_token');
  if (storedToken) {
    headers['Authorization'] = `Bearer ${storedToken}`;
  }

  const options = { method, headers };
  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Network request failed' }));
      // Backend errors carry {code, message}; fall back to raw detail for simple errors
      const detail = err.detail;
      const msg = Array.isArray(detail) ? detail.map(item => `${item.loc?.slice(1).join('.') || 'Input'}: ${item.msg}`).join('; ') : typeof detail === 'object' && detail !== null ? detail.message : detail;
      throw new Error(msg || `Error ${res.status}`);
    }
    return await res.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
};

export const authAPI = {
  // identifier can be either an email address or a username
  login: (identifier, password) => apiCall('/auth/login', 'POST', { identifier, password }),
  register: (payload) => apiCall('/auth/register', 'POST', payload),
  updateDetails: (payload) => apiCall('/auth/details', 'PUT', payload),
  getMe: () => apiCall('/auth/me', 'GET'),
};

export const profileAPI = {
  getProfile: () => apiCall('/profile', 'GET'),
};

export const uploadAPI = {
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const token = localStorage.getItem('krishi_token');
    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    });
    if (!res.ok) throw new Error('File upload failed');
    return await res.json();
  },
};

export const inputGuardAPI = {
  list: () => apiCall('/input-guard'),
  submit: (payload) => apiCall('/input-guard/check', 'POST', payload),
  update: (id, payload) => apiCall(`/input-guard/${id}`, 'PATCH', payload),
  pending: () => apiCall('/input-guard/officer/pending'),
  review: (id, decision, note) => apiCall(`/input-guard/officer/${id}/review`, 'PATCH', { decision, note }),
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const token = localStorage.getItem('krishi_token');
    const res = await fetch(`${API_BASE}/input-guard/upload`, { method: 'POST', headers: { Authorization: `Bearer ${token}` }, body: formData });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      const detail = error.detail;
      throw new Error(typeof detail === 'string' ? detail : detail?.message || 'Photo upload failed.');
    }
    return res.json();
  },
};

export const casesAPI = {
  getCases: () => apiCall('/cases', 'GET'),
  getCaseDetail: (id) => apiCall(`/cases/${id}`, 'GET'),
  createCase: (payload) => apiCall('/cases', 'POST', payload),
  submitOfficerReview: (caseId, payload) => apiCall(`/cases/${caseId}/review`, 'POST', payload),
};

export const subsidiesAPI = {
  getSchemes: () => apiCall('/subsidies', 'GET'),
  apply: (payload) => apiCall('/subsidies/apply', 'POST', payload),
  getApplications: () => apiCall('/subsidies/applications', 'GET'),
  decideApplication: (appId, payload) => apiCall(`/subsidies/applications/${appId}/decide`, 'POST', payload),
};

export const officerAPI = {
  getAutoClerkReport: (caseId) => apiCall(`/officer/autoclerk/${caseId}`, 'GET'),
};

export const auditAPI = {
  getLedger: () => apiCall('/audit/ledger', 'GET'),
  verifyIntegrity: () => apiCall('/audit/verify', 'GET'),
};

export const notificationsAPI = {
  getNotifications: () => apiCall('/notifications', 'GET'),
  markAsRead: (id) => apiCall(`/notifications/${id}/read`, 'PUT'),
};
