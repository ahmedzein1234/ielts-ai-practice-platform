#!/usr/bin/env node

/**
 * IELTS AI Platform - MCP Integration Test Script
 * 
 * This script tests the MCP integration setup and verifies all connections
 * are working properly before deployment.
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Test configuration
const TEST_CONFIG = {
  projectName: 'ielts-ai-platform',
  supabaseProjectId: 'zzvskbvqtglzonftpikf',
  services: [
    { name: 'api', port: 8000 },
    { name: 'scoring', port: 8001 },
    { name: 'exam-generator', port: 8006 },
    { name: 'ocr', port: 8002 },
    { name: 'speech', port: 8003 },
    { name: 'ai-tutor', port: 8001 },
    { name: 'worker', port: 8004 }
  ]
};

// Utility functions
const log = {
  info: (msg) => console.log(`[INFO] ${msg}`),
  success: (msg) => console.log(`[SUCCESS] ${msg}`),
  warning: (msg) => console.log(`[WARNING] ${msg}`),
  error: (msg) => console.log(`[ERROR] ${msg}`),
  debug: (msg) => process.env.DEBUG && console.log(`[DEBUG] ${msg}`)
};

// Execute command and return promise
function executeCommand(command, args = [], options = {}) {
  return new Promise((resolve, reject) => {
    log.debug(`Executing: ${command} ${args.join(' ')}`);
    
    const child = spawn(command, args, {
      stdio: 'pipe',
      shell: true,
      ...options
    });
    
    let stdout = '';
    let stderr = '';
    
    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });
    
    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });
    
    child.on('close', (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
      } else {
        reject(new Error(`Command failed with exit code ${code}: ${stderr}`));
      }
    });
    
    child.on('error', (error) => {
      reject(error);
    });
  });
}

// Test Railway MCP Integration
async function testRailwayMCP() {
  log.info('Testing Railway MCP integration...');
  
  try {
    // Test Railway CLI installation
    const railwayVersion = await executeCommand('railway', ['--version']);
    log.success(`Railway CLI installed: ${railwayVersion.stdout.trim()}`);
    
    // Test Railway authentication
    const railwayAuth = await executeCommand('railway', ['whoami']);
    log.success('Railway authentication successful');
    
    // Test Railway projects list
    const railwayProjects = await executeCommand('railway', ['projects']);
    log.success('Railway projects accessible');
    
    log.success('Railway MCP integration test passed');
    return true;
  } catch (error) {
    log.error(`Railway MCP integration test failed: ${error.message}`);
    return false;
  }
}

// Test Cloudflare MCP Integration
async function testCloudflareMCP() {
  log.info('Testing Cloudflare MCP integration...');
  
  try {
    // Test Wrangler CLI installation
    const wranglerVersion = await executeCommand('wrangler', ['--version']);
    log.success(`Wrangler CLI installed: ${wranglerVersion.stdout.trim()}`);
    
    // Test Cloudflare authentication
    const cloudflareAuth = await executeCommand('wrangler', ['whoami']);
    log.success('Cloudflare authentication successful');
    
    // Test Cloudflare Pages projects
    const cloudflareProjects = await executeCommand('wrangler', ['pages', 'project', 'list']);
    log.success('Cloudflare Pages projects accessible');
    
    log.success('Cloudflare MCP integration test passed');
    return true;
  } catch (error) {
    log.error(`Cloudflare MCP integration test failed: ${error.message}`);
    return false;
  }
}

// Test Supabase Integration
async function testSupabaseIntegration() {
  log.info('Testing Supabase integration...');
  
  try {
    // Test Supabase CLI installation
    const supabaseVersion = await executeCommand('supabase', ['--version']);
    log.success(`Supabase CLI installed: ${supabaseVersion.stdout.trim()}`);
    
    // Test Supabase authentication
    const supabaseAuth = await executeCommand('supabase', ['login']);
    log.success('Supabase authentication successful');
    
    // Test Supabase project access
    const supabaseProjects = await executeCommand('supabase', [
      'projects', 'list',
      '--access-token', process.env.SUPABASE_ACCESS_TOKEN || 'test'
    ]);
    log.success('Supabase projects accessible');
    
    log.success('Supabase integration test passed');
    return true;
  } catch (error) {
    log.error(`Supabase integration test failed: ${error.message}`);
    return false;
  }
}

// Test Environment Variables
async function testEnvironmentVariables() {
  log.info('Testing environment variables...');
  
  const requiredEnvVars = [
    'RAILWAY_TOKEN',
    'CLOUDFLARE_API_TOKEN',
    'SUPABASE_ANON_KEY',
    'SUPABASE_SERVICE_ROLE_KEY',
    'OPENAI_API_KEY',
    'ANTHROPIC_API_KEY',
    'OPENROUTER_API_KEY'
  ];
  
  const missingVars = [];
  
  for (const envVar of requiredEnvVars) {
    if (!process.env[envVar]) {
      missingVars.push(envVar);
    } else {
      log.success(`${envVar} is set`);
    }
  }
  
  if (missingVars.length > 0) {
    log.error(`Missing environment variables: ${missingVars.join(', ')}`);
    return false;
  }
  
  log.success('All environment variables are set');
  return true;
}

// Test Project Structure
async function testProjectStructure() {
  log.info('Testing project structure...');
  
  const requiredPaths = [
    'services/api',
    'services/scoring',
    'services/exam-generator',
    'services/ocr',
    'services/speech',
    'services/ai-tutor',
    'workers',
    'apps/web',
    'supabase'
  ];
  
  const missingPaths = [];
  
  for (const path of requiredPaths) {
    if (!fs.existsSync(path)) {
      missingPaths.push(path);
    } else {
      log.success(`Path exists: ${path}`);
    }
  }
  
  if (missingPaths.length > 0) {
    log.error(`Missing project paths: ${missingPaths.join(', ')}`);
    return false;
  }
  
  log.success('Project structure is valid');
  return true;
}

// Test Service Configurations
async function testServiceConfigurations() {
  log.info('Testing service configurations...');
  
  const services = TEST_CONFIG.services;
  const failedServices = [];
  
  for (const service of services) {
    try {
      // Check if service directory exists
      const servicePath = service.name === 'worker' ? 'workers' : `services/${service.name}`;
      
      if (!fs.existsSync(servicePath)) {
        failedServices.push(`${service.name} (directory missing)`);
        continue;
      }
      
      // Check for Dockerfile
      const dockerfilePath = path.join(servicePath, 'Dockerfile');
      if (!fs.existsSync(dockerfilePath)) {
        failedServices.push(`${service.name} (Dockerfile missing)`);
        continue;
      }
      
      // Check for requirements.txt or package.json
      const requirementsPath = path.join(servicePath, 'requirements.txt');
      const packagePath = path.join(servicePath, 'package.json');
      
      if (!fs.existsSync(requirementsPath) && !fs.existsSync(packagePath)) {
        failedServices.push(`${service.name} (dependencies file missing)`);
        continue;
      }
      
      log.success(`Service configured: ${service.name}`);
    } catch (error) {
      failedServices.push(`${service.name} (${error.message})`);
    }
  }
  
  if (failedServices.length > 0) {
    log.error(`Failed service configurations: ${failedServices.join(', ')}`);
    return false;
  }
  
  log.success('All service configurations are valid');
  return true;
}

// Test Frontend Configuration
async function testFrontendConfiguration() {
  log.info('Testing frontend configuration...');
  
  try {
    const webPath = 'apps/web';
    
    // Check if web directory exists
    if (!fs.existsSync(webPath)) {
      throw new Error('Web directory missing');
    }
    
    // Check for package.json
    const packagePath = path.join(webPath, 'package.json');
    if (!fs.existsSync(packagePath)) {
      throw new Error('package.json missing');
    }
    
    // Check for next.config.js
    const nextConfigPath = path.join(webPath, 'next.config.js');
    if (!fs.existsSync(nextConfigPath)) {
      throw new Error('next.config.js missing');
    }
    
    // Test npm install
    process.chdir(webPath);
    await executeCommand('npm', ['install']);
    log.success('Frontend dependencies installed');
    
    // Test build
    await executeCommand('npm', ['run', 'build']);
    log.success('Frontend build successful');
    
    process.chdir('../..');
    
    log.success('Frontend configuration test passed');
    return true;
  } catch (error) {
    log.error(`Frontend configuration test failed: ${error.message}`);
    return false;
  }
}

// Test Supabase Schema
async function testSupabaseSchema() {
  log.info('Testing Supabase schema...');
  
  try {
    const schemaPath = 'supabase/schema.sql';
    
    if (!fs.existsSync(schemaPath)) {
      throw new Error('Schema file missing');
    }
    
    const schemaContent = fs.readFileSync(schemaPath, 'utf8');
    
    // Check for required tables
    const requiredTables = [
      'users',
      'speaking_sessions',
      'writing_submissions',
      'reading_tests',
      'listening_tests',
      'user_progress'
    ];
    
    const missingTables = [];
    
    for (const table of requiredTables) {
      if (!schemaContent.includes(`CREATE TABLE.*${table}`)) {
        missingTables.push(table);
      }
    }
    
    if (missingTables.length > 0) {
      throw new Error(`Missing tables: ${missingTables.join(', ')}`);
    }
    
    log.success('Supabase schema is valid');
    return true;
  } catch (error) {
    log.error(`Supabase schema test failed: ${error.message}`);
    return false;
  }
}

// Main test function
async function runAllTests() {
  log.info('🚀 Starting MCP Integration Tests...');
  
  const tests = [
    { name: 'Environment Variables', fn: testEnvironmentVariables },
    { name: 'Project Structure', fn: testProjectStructure },
    { name: 'Service Configurations', fn: testServiceConfigurations },
    { name: 'Frontend Configuration', fn: testFrontendConfiguration },
    { name: 'Supabase Schema', fn: testSupabaseSchema },
    { name: 'Railway MCP', fn: testRailwayMCP },
    { name: 'Cloudflare MCP', fn: testCloudflareMCP },
    { name: 'Supabase Integration', fn: testSupabaseIntegration }
  ];
  
  const results = [];
  
  for (const test of tests) {
    try {
      const result = await test.fn();
      results.push({ name: test.name, passed: result });
    } catch (error) {
      log.error(`Test ${test.name} failed with error: ${error.message}`);
      results.push({ name: test.name, passed: false, error: error.message });
    }
  }
  
  // Print summary
  console.log('\n📊 Test Results Summary:');
  console.log('========================');
  
  const passedTests = results.filter(r => r.passed);
  const failedTests = results.filter(r => !r.passed);
  
  console.log(`✅ Passed: ${passedTests.length}/${results.length}`);
  console.log(`❌ Failed: ${failedTests.length}/${results.length}`);
  
  if (passedTests.length > 0) {
    console.log('\n✅ Passed Tests:');
    passedTests.forEach(test => {
      console.log(`  - ${test.name}`);
    });
  }
  
  if (failedTests.length > 0) {
    console.log('\n❌ Failed Tests:');
    failedTests.forEach(test => {
      console.log(`  - ${test.name}${test.error ? `: ${test.error}` : ''}`);
    });
  }
  
  // Overall result
  const allPassed = failedTests.length === 0;
  
  if (allPassed) {
    log.success('🎉 All tests passed! MCP integration is ready for deployment.');
    console.log('\n🚀 Ready to deploy: npm run deploy');
  } else {
    log.error('❌ Some tests failed. Please fix the issues before deployment.');
    console.log('\n🔧 Fix the failed tests and run again: npm run test');
  }
  
  return allPassed;
}

// CLI interface
async function main() {
  if (process.argv.includes('--help') || process.argv.includes('-h')) {
    console.log(`
IELTS AI Platform - MCP Integration Test Script

Usage:
  node scripts/test-mcp-integration.js [options]

Options:
  --help, -h          Show this help message
  --verbose           Enable verbose logging
  --debug             Enable debug logging

Environment Variables Required:
  RAILWAY_TOKEN              Railway API token
  CLOUDFLARE_API_TOKEN       Cloudflare API token
  SUPABASE_ANON_KEY          Supabase anonymous key
  SUPABASE_SERVICE_ROLE_KEY  Supabase service role key
  OPENAI_API_KEY            OpenAI API key
  ANTHROPIC_API_KEY         Anthropic API key
  OPENROUTER_API_KEY        OpenRouter API key

Example:
  node scripts/test-mcp-integration.js --verbose
    `);
    return;
  }
  
  // Set debug mode
  if (process.argv.includes('--debug')) {
    process.env.DEBUG = 'true';
  }
  
  const success = await runAllTests();
  process.exit(success ? 0 : 1);
}

// Run the script
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  runAllTests,
  testRailwayMCP,
  testCloudflareMCP,
  testSupabaseIntegration,
  testEnvironmentVariables,
  testProjectStructure,
  testServiceConfigurations,
  testFrontendConfiguration,
  testSupabaseSchema
};
