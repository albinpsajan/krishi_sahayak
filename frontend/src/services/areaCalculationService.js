const R = 6371008.8;
export function polygonAreaSqM(points) {
  if (points.length < 3) return 0;
  const lat0 = points.reduce((sum, [, lat]) => sum + lat, 0) / points.length;
  const metres = points.map(([lon, lat]) => [lon * Math.PI / 180 * R * Math.cos(lat0 * Math.PI / 180), lat * Math.PI / 180 * R]);
  return Math.abs(metres.reduce((sum, [x, y], i) => { const [nx, ny] = metres[(i + 1) % metres.length]; return sum + x * ny - nx * y; }, 0) / 2);
}
export const areaLabel = (area) => area < 4046.86 ? `${Math.round(area)} m²` : `${(area / 4046.856).toFixed(2)} acres`;
