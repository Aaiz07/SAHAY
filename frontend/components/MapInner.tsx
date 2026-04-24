'use client';

import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import type { IncidentMarker, ResourceMarker } from './Map';

// Fix Leaflet's default icon paths when bundled by webpack/Next.js
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

const redIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

const blueIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-blue.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

function RecenterMap({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView([lat, lng], map.getZoom());
  }, [lat, lng, map]);
  return null;
}

interface MapInnerProps {
  incidents: IncidentMarker[];
  resources: ResourceMarker[];
}

export default function MapInner({ incidents, resources }: MapInnerProps) {
  const center: [number, number] = [12.9716, 77.5946]; // Bengaluru

  return (
    <MapContainer
      center={center}
      zoom={6}
      style={{ height: '100%', width: '100%', borderRadius: '12px' }}
      className="z-0"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <RecenterMap lat={center[0]} lng={center[1]} />

      {incidents.map((inc) => (
        <Marker key={`inc-${inc.id}`} position={[inc.lat, inc.lng]} icon={redIcon}>
          <Popup>
            <div className="text-sm">
              <p className="font-bold text-red-600">
                {inc.emergency_type ?? 'UNKNOWN'} – {inc.severity ?? 'N/A'}
              </p>
              <p>📍 {inc.location ?? 'Unknown location'}</p>
              {inc.casualties > 0 && <p>🚨 Casualties: {inc.casualties}</p>}
            </div>
          </Popup>
        </Marker>
      ))}

      {resources.map((res) => (
        <Marker key={`res-${res.id}`} position={[res.lat, res.lng]} icon={blueIcon}>
          <Popup>
            <div className="text-sm">
              <p className="font-bold text-blue-600">{res.type}</p>
              <p>📍 {res.city}</p>
              <p className="text-gray-500 text-xs">ID: {res.id}</p>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
