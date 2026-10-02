import { apiCall } from './api';
export const liveDataAPI = {
  weather: (lat = 10.7867, lng = 76.6548) => apiCall(`/weather/current?lat=${lat}&lng=${lng}`),
  farmerWeather: id => apiCall(`/weather/farm/${id}`),
  market: ({ commodity = 'banana', state = 'Kerala', district = 'Thrissur' } = {}) => apiCall(`/market-prices?commodity=${encodeURIComponent(commodity)}&state=${encodeURIComponent(state)}&district=${encodeURIComponent(district)}`),
  farmerMarket: id => apiCall(`/market-prices/farmer/${id}`),
  assistant: (query, language) => apiCall('/assistant/query', 'POST', { query, language }),
};
