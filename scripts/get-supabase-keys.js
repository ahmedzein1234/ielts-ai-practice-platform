#!/usr/bin/env node

/**
 * 🔑 Supabase Keys Helper Script
 * Helps you find and configure your Supabase API keys
 */

console.log('🔑 Supabase API Keys Configuration\n');

console.log('📋 To get your Supabase anon key:');
console.log('1. Go to: https://supabase.com/dashboard/project/zzvskbvqtglzonftpikf/settings/api-keys');
console.log('2. Copy the "anon public" key (starts with eyJ...)');
console.log('3. Create apps/web/.env.local with the following content:\n');

console.log('📄 Create apps/web/.env.local with:');
console.log('```');
console.log('# Supabase Configuration');
console.log('NEXT_PUBLIC_SUPABASE_URL=https://zzvskbvqtglzonftpikf.supabase.co');
console.log('NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here');
console.log('');
console.log('# API Configuration');
console.log('NEXT_PUBLIC_API_URL=https://ielts-api-gateway-production.up.railway.app');
console.log('');
console.log('# Development Configuration');
console.log('NODE_ENV=development');
console.log('```\n');

console.log('⚠️  Important:');
console.log('• Replace "your_anon_key_here" with your actual anon key');
console.log('• Never commit .env.local to git (it\'s already in .gitignore)');
console.log('• For Vercel deployment, add these as environment variables in Vercel dashboard\n');

console.log('🚀 Next steps:');
console.log('1. Create the .env.local file');
console.log('2. Test locally with: npm run dev');
console.log('3. Deploy to Vercel with environment variables');
