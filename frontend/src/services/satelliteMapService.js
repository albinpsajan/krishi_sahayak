export const SATELLITE_TILE_URL = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
export const SATELLITE_ATTRIBUTION = 'Imagery © Esri';
export const MAP_PROVIDERS = {
  esri: { label: 'Esri World Imagery', url: SATELLITE_TILE_URL, attribution: SATELLITE_ATTRIBUTION, maxNativeZoom: 19, imagery: true },
  hybrid: { label: 'Esri imagery + labels', url: SATELLITE_TILE_URL, attribution: SATELLITE_ATTRIBUTION, maxNativeZoom: 19, imagery: true },
  map: { label: 'OpenStreetMap map', url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', attribution: '© OpenStreetMap contributors', maxNativeZoom: 19, imagery: false },
};
