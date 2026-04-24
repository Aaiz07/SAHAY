'use client';

import dynamic from 'next/dynamic';

// Leaflet must not be rendered on the server (no window object)
const MapInner = dynamic(() => import('./MapInner'), { ssr: false });

export interface IncidentMarker {
  id: number;
  lat: number;
  lng: number;
  emergency_type: string | null;
  severity: string | null;
  location: string | null;
  casualties: number;
}

export interface ResourceMarker {
  id: string;
  type: string;
  city: string;
  lat: number;
  lng: number;
}

interface MapProps {
  incidents: IncidentMarker[];
  resources: ResourceMarker[];
}

export default function Map(props: MapProps) {
  return <MapInner {...props} />;
}
