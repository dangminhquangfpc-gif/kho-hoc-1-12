import type { NextConfig } from 'next';
const config: NextConfig = { poweredByHeader: false, experimental: { serverActions: { bodySizeLimit: '2mb' }, cpus: 2 } };
export default config;
