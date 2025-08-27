import { ErrorBoundary } from '@/components/error-boundary';
import { AuthProvider } from '@/components/providers/auth-provider';
import { QueryProvider } from '@/components/providers/query-provider';
import { SupabaseProvider } from '@/components/providers/supabase-provider';
import { ThemeProvider } from '@/components/providers/theme-provider';
import { Toaster } from '@/components/ui/toaster';
import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import Script from 'next/script';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'IELTS AI Practice Platform',
  description: 'Master IELTS with AI-powered practice tests, real-time feedback, and personalized learning. Achieve your target band score faster than ever before.',
  keywords: ['IELTS', 'AI', 'practice', 'English', 'test', 'preparation', 'speaking', 'writing', 'listening', 'reading', 'band score', 'academic', 'general training'],
  authors: [{ name: 'IELTS AI Platform' }],
  creator: 'IELTS AI Platform',
  publisher: 'IELTS AI Platform',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://ielts-ai.com'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: 'IELTS AI Practice Platform',
    description: 'Master IELTS with AI-powered practice tests, real-time feedback, and personalized learning.',
    url: 'https://ielts-ai.com',
    siteName: 'IELTS AI Platform',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'IELTS AI Practice Platform',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'IELTS AI Practice Platform',
    description: 'Master IELTS with AI-powered practice tests, real-time feedback, and personalized learning.',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'IELTS AI',
  },
  other: {
    'mobile-web-app-capable': 'yes',
    'apple-mobile-web-app-capable': 'yes',
    'apple-mobile-web-app-status-bar-style': 'default',
    'apple-mobile-web-app-title': 'IELTS AI',
    'msapplication-TileColor': '#3b82f6',
    'msapplication-config': '/browserconfig.xml',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: '#3b82f6',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" href="/icons/icon-192x192.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#3b82f6" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="IELTS AI" />
        <meta name="msapplication-TileColor" content="#3b82f6" />
        <meta name="msapplication-TileImage" content="/icons/icon-144x144.png" />

        {/* Preconnect to external domains for performance */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link rel="preconnect" href="https://zzvskbvqtglzonftpikf.supabase.co" />
        <link rel="preconnect" href="https://ielts-api-gateway-production.up.railway.app" />

        {/* DNS prefetch for better performance */}
        <link rel="dns-prefetch" href="//fonts.googleapis.com" />
        <link rel="dns-prefetch" href="//zzvskbvqtglzonftpikf.supabase.co" />
        <link rel="dns-prefetch" href="//ielts-api-gateway-production.up.railway.app" />
      </head>
      <body className={inter.className}>
        <ErrorBoundary>
          <ThemeProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
          >
            <QueryProvider>
              <SupabaseProvider>
                <AuthProvider>
                  {children}
                  <Toaster />
                </AuthProvider>
              </SupabaseProvider>
            </QueryProvider>
          </ThemeProvider>
        </ErrorBoundary>

        {/* Service Worker Registration */}
        <Script
          id="sw-registration"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js')
                    .then(function(registration) {
                      console.log('SW registered: ', registration);
                    })
                    .catch(function(registrationError) {
                      console.log('SW registration failed: ', registrationError);
                    });
                });
              }
            `,
          }}
        />

        {/* Performance Monitoring */}
        <Script
          id="performance-monitoring"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              // Performance monitoring
              window.addEventListener('load', function() {
                setTimeout(function() {
                  const perfData = performance.getEntriesByType('navigation')[0];
                  const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
                  const domContentLoaded = perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart;
                  
                  console.log('Page Load Time:', loadTime + 'ms');
                  console.log('DOM Content Loaded:', domContentLoaded + 'ms');
                  
                  // Send performance data to analytics
                  if (typeof gtag !== 'undefined') {
                    gtag('event', 'timing_complete', {
                      name: 'load',
                      value: loadTime
                    });
                  }
                }, 0);
              });
            `,
          }}
        />

        {/* Google Analytics */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
          strategy="afterInteractive"
        />
        <Script
          id="google-analytics"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'GA_MEASUREMENT_ID', {
                page_title: document.title,
                page_location: window.location.href,
              });
            `,
          }}
        />
      </body>
    </html>
  );
}
