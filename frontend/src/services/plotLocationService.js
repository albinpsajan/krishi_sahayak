export function getCurrentLocation() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) return reject(new Error('Location is unavailable in this browser.'));
    navigator.geolocation.getCurrentPosition(({ coords }) => resolve({ lat: coords.latitude, lon: coords.longitude, accuracy: coords.accuracy }), error => reject(new Error(error.code === 1 ? 'Location permission was denied.' : error.code === 3 ? 'Could not get accurate location.' : 'Location is unavailable.')), { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 });
  });
}
export async function searchLocation(query) {
  const response = await fetch(`https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=${encodeURIComponent(query)}`, { headers: { Accept: 'application/json' } });
  const results = await response.json();
  if (!results[0]) throw new Error('Location not found.');
  return { lat: Number(results[0].lat), lon: Number(results[0].lon), label: results[0].display_name };
}
