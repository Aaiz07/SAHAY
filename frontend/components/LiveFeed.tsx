'use client';

import { motion } from 'framer-motion';
import DispatchButton from './DispatchButton';

export interface Incident {
  id: number;
  text: string;
  translated_text: string | null;
  emergency_type: string | null;
  severity: string | null;
  location: string | null;
  lat: number | null;
  lng: number | null;
  casualties: number;
  timestamp: string;
  priority_score: number;
}

interface LiveFeedProps {
  incidents: Incident[];
  loading: boolean;
}

function SeverityBadge({ severity }: { severity: string | null }) {
  const label = severity ?? 'N/A';
  const classes: Record<string, string> = {
    HIGH: 'bg-red-600 text-white',
    MEDIUM: 'bg-yellow-500 text-black',
    LOW: 'bg-green-600 text-white',
  };
  const cls = classes[label] ?? 'bg-gray-600 text-white';
  return (
    <span className={`text-xs font-bold px-2 py-0.5 rounded ${cls}`}>{label}</span>
  );
}

function TypeBadge({ type }: { type: string | null }) {
  return (
    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-700 text-white">
      {type ?? 'UNKNOWN'}
    </span>
  );
}

export default function LiveFeed({ incidents, loading }: LiveFeedProps) {
  return (
    <div className="glass-card flex flex-col h-full overflow-hidden">
      <div className="px-4 py-3 border-b border-white/10 flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
        <h2 className="text-sm font-semibold text-white uppercase tracking-widest">
          Live Distress Feed
        </h2>
        <span className="ml-auto text-xs text-gray-400">{incidents.length} signals</span>
      </div>

      <div className="flex-1 overflow-y-auto feed-scroll p-3 space-y-3">
        {loading && (
          <p className="text-center text-gray-400 text-sm mt-8">Loading signals…</p>
        )}
        {!loading && incidents.length === 0 && (
          <p className="text-center text-gray-500 text-sm mt-8">No incidents yet.</p>
        )}
        {incidents.map((inc, i) => (
          <motion.div
            key={inc.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="rounded-lg p-3 bg-white/5 border border-white/10 space-y-2"
          >
            {/* Badges row */}
            <div className="flex flex-wrap gap-1.5 items-center">
              <SeverityBadge severity={inc.severity} />
              <TypeBadge type={inc.emergency_type} />
              {inc.casualties > 0 && (
                <span className="text-xs px-2 py-0.5 rounded bg-orange-700 text-white font-semibold">
                  {inc.casualties} casualties
                </span>
              )}
              <span className="ml-auto text-xs text-gray-400">
                #{inc.id} · score {inc.priority_score.toFixed(1)}
              </span>
            </div>

            {/* Original text */}
            <p className="text-xs text-gray-400 leading-relaxed line-clamp-2">{inc.text}</p>

            {/* Translated text (if different) */}
            {inc.translated_text && inc.translated_text !== inc.text && (
              <p className="text-xs text-gray-300 leading-relaxed border-l-2 border-blue-500 pl-2 line-clamp-2">
                {inc.translated_text}
              </p>
            )}

            {/* Location */}
            {inc.location && (
              <p className="text-xs text-gray-400">
                📍 <span className="text-gray-300">{inc.location}</span>
              </p>
            )}

            <DispatchButton incident={inc} />
          </motion.div>
        ))}
      </div>
    </div>
  );
}
