#!/usr/bin/env node

/**
 * 🗄️ Supabase Setup Script for IELTS AI Platform
 * Helps configure Supabase database and authentication
 */

const fs = require('fs');
const path = require('path');

console.log('🗄️ Setting up Supabase for IELTS AI Platform...\n');

// Supabase project details
const supabaseConfig = {
  projectId: 'zzvskbvqtglzonftpikf',
  projectName: 'IELTS CURSOR',
  url: 'https://zzvskbvqtglzonftpikf.supabase.co'
};

console.log('📋 Supabase Project Details:');
console.log(`  • Project ID: ${supabaseConfig.projectId}`);
console.log(`  • Project Name: ${supabaseConfig.projectName}`);
console.log(`  • URL: ${supabaseConfig.url}\n`);

console.log('🔧 Setup Steps:');
console.log('\n1. 📊 Database Schema:');
console.log('   • Go to your Supabase dashboard');
console.log('   • Navigate to SQL Editor');
console.log('   • Copy and paste the contents of supabase/schema.sql');
console.log('   • Execute the SQL to create tables and policies\n');

console.log('2. 🔑 Environment Variables:');
console.log('   • Copy your Supabase anon key from the API Keys section');
console.log('   • Create a .env.local file in apps/web/ with:');
console.log('     NEXT_PUBLIC_SUPABASE_URL=https://zzvskbvqtglzonftpikf.supabase.co');
console.log('     NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here\n');

console.log('3. 🔐 Authentication:');
console.log('   • Go to Authentication > Settings');
console.log('   • Configure your site URL: https://ielts-frontend-bkgqbaxdn-ahmedzein1234s-projects.vercel.app');
console.log('   • Add redirect URLs for authentication\n');

console.log('4. 📁 Storage:');
console.log('   • Storage buckets will be created automatically by the schema');
console.log('   • audio-recordings: for speaking practice audio files');
console.log('   • writing-images: for handwritten text images\n');

console.log('5. 🚀 Deploy:');
console.log('   • Run: npm run build');
console.log('   • Deploy to Vercel with the new environment variables\n');

console.log('✅ Supabase setup instructions completed!');
console.log('\n📚 Next steps:');
console.log('  • Execute the database schema in Supabase');
console.log('  • Configure environment variables');
console.log('  • Test authentication flow');
console.log('  • Deploy the updated application\n');

// Create a quick reference file
const setupGuide = `
# Supabase Setup Guide

## Project Details
- Project ID: ${supabaseConfig.projectId}
- Project Name: ${supabaseConfig.projectName}
- URL: ${supabaseConfig.url}

## Environment Variables
Create apps/web/.env.local with:
\`\`\`
NEXT_PUBLIC_SUPABASE_URL=${supabaseConfig.url}
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here
NEXT_PUBLIC_API_URL=https://ielts-api-gateway-production.up.railway.app
\`\`\`

## Database Schema
Execute supabase/schema.sql in your Supabase SQL Editor

## Authentication
Configure site URL and redirect URLs in Supabase Auth settings

## Storage
Storage buckets are created automatically by the schema
`;

fs.writeFileSync('SUPABASE_SETUP.md', setupGuide);
console.log('📄 Setup guide saved to SUPABASE_SETUP.md');
