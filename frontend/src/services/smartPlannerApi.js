import { apiCall } from './api';

export const smartPlannerAPI = {
  rules: () => apiCall('/smart-planner/rules'),
  plots: () => apiCall('/smart-planner/plots'),
  createPlot: (payload) => apiCall('/smart-planner/plots', 'POST', payload),
  plan: (payload) => apiCall('/smart-planner/plans/generate', 'POST', payload),
  plans: () => apiCall('/smart-planner/plans'),
  getPlan: (id) => apiCall(`/smart-planner/plans/${id}`),
  requestReview: (id, note = '') => apiCall(`/smart-planner/plans/${id}/request-review`, 'POST', { note }),
  pending: () => apiCall('/smart-planner/officer/pending'),
  review: (id, payload) => apiCall(`/smart-planner/plans/${id}/review`, 'PATCH', payload),
  saveLocation: payload => apiCall('/smart-planner/locations', 'POST', payload),
  customize: (id, payload) => apiCall(`/smart-planner/plans/${id}/customize`, 'POST', payload),
  versions: id => apiCall(`/smart-planner/plans/${id}/versions`),
};
