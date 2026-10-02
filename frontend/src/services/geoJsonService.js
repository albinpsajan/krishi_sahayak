export const pointsFromGeoJson = (geojson) => geojson?.coordinates?.[0]?.slice(0, -1) || [];
export const polygonFromPoints = (points) => ({ type: 'Polygon', coordinates: points.length ? [[...points, points[0]]] : [[]] });
