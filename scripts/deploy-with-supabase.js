#!/usr/bin/env node

/**
 * 🚀 Deploy IELTS AI Platform with Supabase
 * Deploys the updated application with database and authentication
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Deploying IELTS AI Platform with Supabase...\n');

// Check if we're in the right directory
if (!fs.existsSync('apps/web/package.json')) {
  console.log('❌ Please run this script from the project root directory');
  process.exit(1);
}

async function buildFrontend() {
  console.log('📦 Building frontend application...');
  
  try {
    execSync('cd apps/web && npm run build', { stdio: 'inherit' });
    console.log('✅ Frontend build successful');
    return true;
  } catch (error) {
    console.log('❌ Frontend build failed');
    return false;
  }
}

async function deployToVercel() {
  console.log('\n⚡ Deploying to Vercel...');
  
  try {
    // Check if Vercel CLI is installed
    try {
      execSync('vercel --version', { stdio: 'pipe' });
    } catch {
      console.log('📥 Installing Vercel CLI...');
      execSync('npm install -g vercel', { stdio: 'inherit' });
    }
    
    // Deploy to Vercel
    console.log('🚀 Deploying to Vercel...');
    execSync('cd apps/web && vercel --prod', { stdio: 'inherit' });
    
    console.log('✅ Vercel deployment successful');
    return true;
  } catch (error) {
    console.log('❌ Vercel deployment failed');
    return false;
  }
}

async function checkEnvironmentVariables() {
  console.log('\n🔍 Checking environment variables...');
  
  const envPath = path.join('apps/web', '.env.local');
  
  if (!fs.existsSync(envPath)) {
    console.log('⚠️  .env.local not found in apps/web/');
    console.log('Please create it with your Supabase credentials:\n');
    console.log('NEXT_PUBLIC_SUPABASE_URL=https://zzvskbvqtglzonftpikf.supabase.co');
    console.log('NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here');
    console.log('NEXT_PUBLIC_API_URL=https://ielts-api-gateway-production.up.railway.app\n');
    return false;
  }
  
  const envContent = fs.readFileSync(envPath, 'utf8');
  
  if (!envContent.includes('NEXT_PUBLIC_SUPABASE_URL') || 
      !envContent.includes('NEXT_PUBLIC_SUPABASE_ANON_KEY')) {
    console.log('⚠️  Missing required environment variables');
    return false;
  }
  
  console.log('✅ Environment variables found');
  return true;
}

async function runDeployment() {
  console.log('🎯 Starting deployment process...\n');
  
  const steps = [
    { name: 'Environment Variables', fn: checkEnvironmentVariables },
    { name: 'Frontend Build', fn: buildFrontend },
    { name: 'Vercel Deployment', fn: deployToVercel }
  ];
  
  for (const step of steps) {
    console.log(`\n📋 Step: ${step.name}`);
    const success = await step.fn();
    
    if (!success) {
      console.log(`\n❌ Deployment failed at: ${step.name}`);
      console.log('Please fix the issue and try again.');
      process.exit(1);
    }
  }
  
  console.log('\n🎉 Deployment completed successfully!');
  console.log('\n📋 Next steps:');
  console.log('1. Test the deployed application');
  console.log('2. Create your first user account');
  console.log('3. Test all IELTS features');
  console.log('4. Monitor performance and usage');
  
  console.log('\n🔗 Your application should be available at:');
  console.log('https://ielts-frontend-bkgqbaxdn-ahmedzein1234s-projects.vercel.app');
}

// Run deployment
runDeployment().catch(console.error);
