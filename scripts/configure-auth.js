#!/usr/bin/env node

/**
 * 🔐 Supabase Authentication Configuration
 * Helps configure authentication settings for the IELTS AI Platform
 */

console.log('🔐 Supabase Authentication Configuration\n');

console.log('📋 Authentication Setup Steps:\n');

console.log('1. 🔗 Site URL Configuration:');
console.log('   • Go to: https://supabase.com/dashboard/project/zzvskbvqtglzonftpikf/auth/settings');
console.log('   • Set Site URL to: https://ielts-frontend-bkgqbaxdn-ahmedzein1234s-projects.vercel.app');
console.log('   • Click "Save"\n');

console.log('2. 🔄 Redirect URLs:');
console.log('   • Add these redirect URLs:');
console.log('     - https://ielts-frontend-bkgqbaxdn-ahmedzein1234s-projects.vercel.app/auth/callback');
console.log('     - https://ielts-frontend-bkgqbaxdn-ahmedzein1234s-projects.vercel.app/login');
console.log('     - https://ielts-frontend-bkgqbaxdn-ahmedzein1234s-projects.vercel.app/register');
console.log('     - http://localhost:3000/auth/callback (for local development)');
console.log('     - http://localhost:3000/login (for local development)');
console.log('     - http://localhost:3000/register (for local development)\n');

console.log('3. 🔧 Email Settings:');
console.log('   • Enable "Enable email confirmations"');
console.log('   • Set confirmation email template');
console.log('   • Test email delivery\n');

console.log('4. 🛡️ Security Settings:');
console.log('   • Enable "Enable email confirmations"');
console.log('   • Set minimum password length to 8');
console.log('   • Enable "Enable phone confirmations" (optional)\n');

console.log('5. 📧 Email Templates:');
console.log('   • Customize confirmation email template');
console.log('   • Add your branding and messaging\n');

console.log('✅ Authentication will be ready once these steps are completed!\n');

console.log('🚀 Next steps:');
console.log('• Test sign-up flow');
console.log('• Test sign-in flow');
console.log('• Test password reset');
console.log('• Deploy and test on production');
