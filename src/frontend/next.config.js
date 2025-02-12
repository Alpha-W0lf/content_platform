/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() { // Add this rewrites configuration
    return [
      {
        source: '/projects/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/projects/:path*`,
      },
      {
        source: '/health',
        destination: `${process.env.NEXT_PUBLIC_API_URL}/health`,
      },
    ];
  },
}

module.exports = nextConfig
