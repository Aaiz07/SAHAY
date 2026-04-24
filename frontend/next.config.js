/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Leaflet CSS is imported in the Map component; allow it
  transpilePackages: ['leaflet', 'react-leaflet'],
};

module.exports = nextConfig;
