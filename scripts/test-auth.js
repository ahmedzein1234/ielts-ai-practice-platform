#!/usr/bin/env node

/**
 * 🧪 Supabase Authentication Test Script
 * Tests the authentication flow and database connection
 */

const { createClient } = require('@supabase/supabase-js');

console.log('🧪 Testing Supabase Authentication...\n');

// Check if environment variables are set
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.log('❌ Environment variables not found!');
  console.log('Please create apps/web/.env.local with your Supabase credentials.\n');
  console.log('Example:');
  console.log('NEXT_PUBLIC_SUPABASE_URL=https://zzvskbvqtglzonftpikf.supabase.co');
  console.log('NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key_here\n');
  process.exit(1);
}

console.log('✅ Environment variables found');
console.log(`URL: ${supabaseUrl}`);
console.log(`Key: ${supabaseAnonKey.substring(0, 20)}...\n`);

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function testConnection() {
  console.log('🔗 Testing database connection...');
  
  try {
    // Test basic connection
    const { data, error } = await supabase
      .from('users')
      .select('count')
      .limit(1);
    
    if (error) {
      console.log('❌ Database connection failed:', error.message);
      return false;
    }
    
    console.log('✅ Database connection successful');
    return true;
  } catch (err) {
    console.log('❌ Connection error:', err.message);
    return false;
  }
}

async function testAuth() {
  console.log('\n🔐 Testing authentication...');
  
  try {
    // Test auth state
    const { data: { session }, error } = await supabase.auth.getSession();
    
    if (error) {
      console.log('❌ Auth test failed:', error.message);
      return false;
    }
    
    console.log('✅ Authentication system working');
    console.log(`Session: ${session ? 'Active' : 'None'}`);
    return true;
  } catch (err) {
    console.log('❌ Auth error:', err.message);
    return false;
  }
}

async function testStorage() {
  console.log('\n📁 Testing storage buckets...');
  
  try {
    // Test storage buckets
    const { data: buckets, error } = await supabase.storage.listBuckets();
    
    if (error) {
      console.log('❌ Storage test failed:', error.message);
      return false;
    }
    
    console.log('✅ Storage system working');
    console.log('Available buckets:', buckets.map(b => b.name).join(', '));
    return true;
  } catch (err) {
    console.log('❌ Storage error:', err.message);
    return false;
  }
}

async function runTests() {
  console.log('🚀 Running Supabase tests...\n');
  
  const tests = [
    { name: 'Database Connection', fn: testConnection },
    { name: 'Authentication', fn: testAuth },
    { name: 'Storage', fn: testStorage }
  ];
  
  const results = [];
  
  for (const test of tests) {
    console.log(`\n📋 Running: ${test.name}`);
    const result = await test.fn();
    results.push({ name: test.name, passed: result });
  }
  
  console.log('\n📊 Test Results:');
  console.log('================');
  
  results.forEach(result => {
    const status = result.passed ? '✅ PASS' : '❌ FAIL';
    console.log(`${status} ${result.name}`);
  });
  
  const allPassed = results.every(r => r.passed);
  
  if (allPassed) {
    console.log('\n🎉 All tests passed! Supabase is ready to use.');
    console.log('\n🚀 Next steps:');
    console.log('1. Deploy to Vercel with environment variables');
    console.log('2. Test the full application');
    console.log('3. Create your first user account');
  } else {
    console.log('\n⚠️  Some tests failed. Please check your configuration.');
  }
}

// Run tests
runTests().catch(console.error);
