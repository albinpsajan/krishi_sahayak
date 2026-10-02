import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { LocateFixed, MapPin, RotateCcw, Search, Trash2 } from 'lucide-react';
import { Button } from '../ui/Primitives';
import { pointsFromGeoJson, polygonFromPoints } from '../../services/geoJsonService';
import { areaLabel, polygonAreaSqM } from '../../services/areaCalculationService';
import { getCurrentLocation, searchLocation } from '../../services/plotLocationService';
import { MAP_PROVIDERS } from '../../services/satelliteMapService';

const DEFAULT_CENTER = [10.7867, 76.6548];

/** Satellite-assisted selection. The farmer confirms every point; imagery never claims land ownership. */
export default function SatellitePlotMap({ value, onChange, onLocation }) {
  const host = useRef(null); const mapRef = useRef(null); const tileRef = useRef(null); const markers = useRef([]); const line = useRef(null); const locationMarker = useRef(null); const accuracyCircle = useRef(null); const valueRef = useRef(value);
  const [query, setQuery] = useState(''); const [provider, setProvider] = useState('esri'); const [status, setStatus] = useState('Use location or search to reach your farm area.'); const [zoomStatus, setZoomStatus] = useState('Satellite detail up to zoom 19 is available from this provider.');
  const points = pointsFromGeoJson(value);
  valueRef.current = value;

  useEffect(() => {
    if (!host.current || mapRef.current) return;
    const map = L.map(host.current, { zoomControl: true, minZoom: 3, maxZoom: 19 }).setView(DEFAULT_CENTER, 16);
    tileRef.current = L.tileLayer(MAP_PROVIDERS.esri.url, { attribution: MAP_PROVIDERS.esri.attribution, maxNativeZoom: 19, maxZoom: 19 }).addTo(map);
    map.on('click', (event) => {
      const next = [...pointsFromGeoJson(valueRef.current), [event.latlng.lng, event.latlng.lat]];
      onChange(polygonFromPoints(next));
    });
    mapRef.current = map;
    setTimeout(() => map.invalidateSize(), 50);
    return () => { map.remove(); mapRef.current = null; };
  }, []);

  useEffect(() => { const map = mapRef.current; const selected = MAP_PROVIDERS[provider]; if (!map || !selected) return; if (tileRef.current) tileRef.current.remove(); tileRef.current = L.tileLayer(selected.url, { attribution: selected.attribution, maxNativeZoom: selected.maxNativeZoom, maxZoom: 19 }).addTo(map); map.setMaxZoom(19); setZoomStatus('Imagery uses the latest available provider tiles; zoom level depends on coverage in this area.'); setTimeout(() => map.invalidateSize(), 50); }, [provider]);

  useEffect(() => {
    const map = mapRef.current; if (!map) return;
    markers.current.forEach(marker => marker.remove()); markers.current = [];
    if (line.current) line.current.remove();
    points.forEach((point, index) => {
      const marker = L.marker([point[1], point[0]], { draggable: true, icon: L.divIcon({ className: 'plot-pin', html: '<span></span>', iconSize: [16, 16], iconAnchor: [8, 8] }) }).addTo(map);
      marker.bindTooltip(String(index + 1), { permanent: true, direction: 'top', className: 'plot-point-label' });
      marker.on('dragend', event => {
        const pos = event.target.getLatLng(); const next = points.map((p, i) => i === index ? [pos.lng, pos.lat] : p);
        onChange(polygonFromPoints(next));
      });
      markers.current.push(marker);
    });
    if (points.length > 1) line.current = L.polygon(points.map(([lon, lat]) => [lat, lon]), { color: '#e5b85c', weight: 3, fillColor: '#dbe7a8', fillOpacity: .28 }).addTo(map);
    if (points.length >= 3) map.fitBounds(L.latLngBounds(points.map(([lon, lat]) => [lat, lon])), { padding: [30, 30] });
  }, [value]);

  const showReference = (lat, lon, label, accuracy) => { const map = mapRef.current; locationMarker.current?.remove(); accuracyCircle.current?.remove(); map?.setView([lat, lon], 19); locationMarker.current = L.marker([lat, lon], { draggable: true }).addTo(map).bindPopup(label).openPopup(); if (accuracy) accuracyCircle.current = L.circle([lat, lon], { radius: accuracy, color: accuracy > 100 ? '#b87942' : '#52794e', fillOpacity: .1 }).addTo(map); map?.once('zoomend', () => setZoomStatus(map.getZoom() < 19 ? 'Satellite zoom is limited in this area. Please zoom as much as possible and confirm the boundary manually.' : 'Satellite detail is set to the highest available planner zoom.')); };
  const locate = async () => { setStatus('Finding your current location…'); try { const position = await getCurrentLocation(); showReference(position.lat, position.lon, 'Your current location', position.accuracy); locationMarker.current.on('dragend', event => { const p = event.target.getLatLng(); onLocation?.({ latitude: p.lat, longitude: p.lng, accuracy_meters: position.accuracy, source: 'manual-correction' }); }); onLocation?.({ latitude: position.lat, longitude: position.lon, accuracy_meters: position.accuracy, source: 'browser-geolocation' }); setStatus(position.accuracy > 100 ? 'Location accuracy is low. Please zoom and adjust the map manually before selecting your plot.' : 'Location updated. Please confirm your plot on the satellite map.'); } catch (error) { setStatus(error.message.includes('denied') ? 'Location permission was denied. Please allow location or search/select your plot manually.' : 'Could not get accurate location. Please try again or select manually.'); } };
  const search = async (event) => { event.preventDefault(); if (!query.trim()) return; setStatus('Searching…'); try { const result = await searchLocation(query); showReference(result.lat, result.lon, `Searched location: ${result.label.split(',').slice(0, 2).join(',')}`); onLocation?.({ latitude: result.lat, longitude: result.lon, source: 'manual-search' }); setStatus(`Map centered near ${result.label.split(',').slice(0, 2).join(',')}. Now confirm the actual plot boundary.`); } catch (error) { setStatus(error.message.includes('not found') ? 'Location not found. Try adding village, district, and state.' : 'Location search is temporarily unavailable. Please move the map manually.'); } };
  const clear = () => onChange(polygonFromPoints([]));
  const undo = () => onChange(polygonFromPoints(points.slice(0, -1)));
  return <div className="satellite-picker">
    <div className="map-toolbar"><form onSubmit={search}><Search size={16}/><input value={query} onChange={e => setQuery(e.target.value)} placeholder="Search village, landmark, or farm location" aria-label="Search village, landmark, or farm location"/><button type="submit">Search</button></form><Button type="button" variant="secondary" onClick={locate}><LocateFixed size={16}/> Use my current location</Button></div>
    <div className="map-source-row"><label>Satellite source<select value={provider} onChange={e => setProvider(e.target.value)}><option value="esri">Esri World Imagery</option><option value="hybrid">Esri imagery + labels</option><option value="map">OpenStreetMap map</option></select></label><span>{zoomStatus}</span></div>
    <div ref={host} className="satellite-map" role="application" aria-label="Satellite map for selecting plot boundary" />
    <div className="map-actions"><span><MapPin size={15}/> Click satellite imagery to add points · drag pins to edit</span><div><button type="button" className="text-link" onClick={undo} disabled={!points.length}><RotateCcw size={15}/> Undo</button><button type="button" className="text-link danger" onClick={clear} disabled={!points.length}><Trash2 size={15}/> Clear</button></div></div>
    <div className="map-preview"><strong>{points.length >= 3 ? areaLabel(polygonAreaSqM(points)) : 'Area preview appears after 3 points'}</strong><span>{status}</span></div><p className="imagery-disclaimer">Satellite images may not be live. Use the latest available imagery from the selected provider and confirm the boundary manually.</p>
  </div>;
}
