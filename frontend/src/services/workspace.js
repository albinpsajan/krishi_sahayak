import { apiCall } from './api';

/** All daily-operation requests go through the same authenticated API client. */
export const workspaceAPI = {
  get: (feature) => apiCall(`/operations/${feature}`),
  create: (feature, value) => apiCall(`/operations/${feature}`, 'POST', value),
  update: (feature, id, status) => apiCall(`/operations/${feature}/${id}`, 'PATCH', { status }),
  join: (id) => apiCall(`/operations/groups/${id}/join`, 'POST'),
  document: (name) => apiCall(`/operations/documents/${encodeURIComponent(name)}`, 'PUT'),
  profile: (value) => apiCall('/operations/profile', 'PUT', value),
};
