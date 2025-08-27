/** @type {import('next').NextConfig} */
const nextConfig = {
  // Development debugging
  reactStrictMode: true,
  productionBrowserSourceMaps: true,

  images: {
    domains: ['localhost', 'ielts-ai-platform.s3.amazonaws.com'],
    formats: ['image/webp', 'image/avif'],
  },

  // Enhanced debugging in development
  experimental: {
    instrumentationHook: true,
    serverComponentsExternalPackages: ['@prisma/client'],
  },

  // Docker support
  output: 'standalone',
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=31536000; includeSubDomains',
          },
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://cdn.vercel.com",
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: https: blob:",
              "media-src 'self' blob:",
              "connect-src 'self' ws: wss: https://api.ielts-ai.com",
              "frame-ancestors 'none'",
            ].join('; '),
          },
        ],
      },
    ];
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/:path*',
      },
      {
        source: '/speech/:path*',
        destination: 'http://localhost:8002/:path*',
      },
      {
        source: '/ocr/:path*',
        destination: 'http://localhost:8003/:path*',
      },
      {
        source: '/scoring/:path*',
        destination: 'http://localhost:8005/:path*',
      },
    ];
  },
  webpack: (config, { dev, isServer }) => {
    // Enhanced source maps for debugging
    if (dev) {
      config.devtool = 'eval-source-map'
    }

    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }

    // Add debugging plugins
    if (dev) {
      config.plugins.push(
        new (require('webpack')).DefinePlugin({
          'process.env.NODE_ENV': JSON.stringify('development'),
          'process.env.DEBUG': JSON.stringify('*'),
        })
      )
    }

    return config;
  },
};

module.exports = nextConfig;
