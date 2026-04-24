'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import dynamic from 'next/dynamic';
import LiveFeed, { type Incident } from '@/components/LiveFeed';

// Leaflet map – client-side only
const Map = dynamic(() => import('@/components/Map'), { ssr: false });

const RESOURCES = [
  { id: 'AMB-BLR-01', type: 'AMBULANCE',  city: 'Bengaluru', lat: 12.9716, lng: 77.5946 },
  { id: 'AMB-BLR-02', type: 'AMBULANCE',  city: 'Bengaluru', lat: 12.9352, lng: 77.6245 },
  { id: 'FIRE-BLR-01', type: 'FIRE_TRUCK', city: 'Bengaluru', lat: 12.9784, lng: 77.6408 },
  { id: 'AMB-HYD-01', type: 'AMBULANCE',  city: 'Hyderabad', lat: 17.3850, lng: 78.4867 },
  { id: 'FIRE-HYD-01', type: 'FIRE_TRUCK', city: 'Hyderabad', lat: 17.4126, lng: 78.4071 },
  { id: 'AMB-CHN-01', type: 'AMBULANCE',  city: 'Chennai',   lat: 13.0827, lng: 80.2707 },
  { id: 'AMB-PUN-01', type: 'AMBULANCE',  city: 'Pune',      lat: 18.5204, lng: 73.8567 },
];

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

export default function Dashboard() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [ingestText, setIngestText] = useState('');
  const [ingesting, setIngesting] = useState(false);
  const [ingestError, setIngestError] = useState('');

  const fetchIncidents = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/incidents`);
      if (res.ok) {
        const data: Incident[] = await res.json();
        setIncidents(data);
      }
    } catch {
      // backend not available in static preview – keep empty list
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchIncidents();
    const interval = setInterval(fetchIncidents, 15000);
    return () => clearInterval(interval);
  }, [fetchIncidents]);

  const handleIngest = async () => {
    if (!ingestText.trim()) return;
    setIngesting(true);
    setIngestError('');
    try {
      const res = await fetch(`${API_URL}/api/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: ingestText }),
      });
      if (res.ok) {
        setIngestText('');
        await fetchIncidents();
      } else {
        setIngestError('Failed to ingest signal. Is the backend running?');
      }
    } catch {
      setIngestError('Backend unreachable. Start the FastAPI server.');
    } finally {
      setIngesting(false);
    }
  };

  const mapIncidents = incidents
    .filter((i) => i.lat !== null && i.lng !== null)
    .map((i) => ({
      id: i.id,
      lat: i.lat as number,
      lng: i.lng as number,
      emergency_type: i.emergency_type,
      severity: i.severity,
      location: i.location,
      casualties: i.casualties,
    }));

  return (
    <main className="min-h-screen p-4 md:p-6" style={{ background: 'var(--bg-primary)' }}>
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6 flex flex-col sm:flex-row items-start sm:items-center gap-3"
      >
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            🚨 SAHAY
          </h1>
          <p className="text-xs text-gray-400 mt-0.5">
            Disaster Response Resource Allocator · Indian Municipalities
          </p>
        </div>
        <div className="sm:ml-auto flex items-center gap-2 text-xs text-gray-400">
          <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
          Live · {incidents.length} active incidents
        </div>
      </motion.header>

      {/* Ingest panel */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="glass-card p-4 mb-6"
      >
        <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">
          Ingest Distress Signal
        </h2>
        <div className="flex gap-2">
          <input
            className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
            placeholder="Paste multilingual distress text (Hindi / Tamil / English)…"
            value={ingestText}
            onChange={(e) => setIngestText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleIngest()}
          />
          <motion.button
            whileTap={{ scale: 0.97 }}
            onClick={handleIngest}
            disabled={ingesting || !ingestText.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg disabled:opacity-50 transition-colors"
          >
            {ingesting ? 'Processing…' : 'Analyze & Ingest'}
          </motion.button>
        </div>
        {ingestError && (
          <p className="text-xs text-red-400 mt-2">{ingestError}</p>
        )}
      </motion.section>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4" style={{ height: 'calc(100vh - 260px)', minHeight: '500px' }}>
        {/* Map – takes 2/3 width on large screens */}
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.15 }}
          className="lg:col-span-2 glass-card overflow-hidden"
          style={{ minHeight: '400px' }}
        >
          <div className="px-4 py-3 border-b border-white/10 flex items-center gap-2">
            <span className="text-sm font-semibold text-white uppercase tracking-widest">
              Incident Map
            </span>
            <span className="ml-auto text-xs text-gray-400">
              🔴 Distress signals &nbsp;|&nbsp; 🔵 Resources
            </span>
          </div>
          <div style={{ height: 'calc(100% - 48px)' }}>
            <Map incidents={mapIncidents} resources={RESOURCES} />
          </div>
        </motion.div>

        {/* Live feed – takes 1/3 width */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="lg:col-span-1"
        >
          <LiveFeed incidents={incidents} loading={loading} />
        </motion.div>
      </div>

      {/* Footer */}
      <footer className="mt-4 text-center text-xs text-gray-600">
        SAHAY v1.0 · AI-Enhanced Crisis Triage · Haversine Priority Routing ·{' '}
        <span className="text-gray-500">112 / RapidSOS Compatible</span>
      </footer>
    </main>
  );
}
