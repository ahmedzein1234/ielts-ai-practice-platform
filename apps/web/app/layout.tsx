import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ThemeProvider } from '@/components/providers/theme-provider';
import { Toaster } from '@/components/ui/toaster';
import { QueryProvider } from '@/components/providers/query-provider';
import { AuthProvider } from '@/components/providers/auth-provider';
import { SupabaseProvider } from '@/components/providers/supabase-provider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'IELTS AI Practice Platform',
  description: 'Master IELTS with AI-powered practice tests, real-time feedback, and personalized learning.',
  keywords: ['IELTS', 'AI', 'practice', 'English', 'test', 'preparation', 'speaking', 'writing', 'listening', 'reading'],
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
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
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
      </body>
    </html>
  );
}
