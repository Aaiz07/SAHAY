import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SAHAY – Disaster Response Resource Allocator',
  description:
    'AI-powered crisis triage engine for Indian municipalities – multilingual distress signal processing, geospatial routing, and 112/RapidSOS dispatch.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          crossOrigin="anonymous"
        />
      </head>
      <body className="min-h-screen" style={{ background: 'var(--bg-primary)' }}>
        {children}
      </body>
    </html>
  );
}
