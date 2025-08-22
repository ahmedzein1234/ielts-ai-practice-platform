#!/usr/bin/env node

const http = require('http');
const https = require('https');

const healthEndpoints = [
  { name: 'API Gateway', url: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/health/' },
  { name: 'Speech Service', url: process.env.SPEECH_SERVICE_URL || 'http://localhost:8002/health' },
  { name: 'OCR Service', url: process.env.OCR_SERVICE_URL || 'http://localhost:8003/health' },
  // { name: 'Scoring Service', url: process.env.SCORING_SERVICE_URL || 'http://localhost:8005/health' },
];

async function checkHealth(endpoint) {
  return new Promise((resolve) => {
    const url = new URL(endpoint.url);
    const client = url.protocol === 'https:' ? https : http;
    
    const req = client.request(url, { timeout: 5000 }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          resolve({
            name: endpoint.name,
            status: res.statusCode === 200 ? 'healthy' : 'unhealthy',
            statusCode: res.statusCode,
            response: response
          });
        } catch (error) {
          resolve({
            name: endpoint.name,
            status: res.statusCode === 200 ? 'healthy' : 'unhealthy',
            statusCode: res.statusCode,
            response: data
          });
        }
      });
    });
    
    req.on('error', (error) => {
      resolve({
        name: endpoint.name,
        status: 'error',
        error: error.message
      });
    });
    
    req.on('timeout', () => {
      req.destroy();
      resolve({
        name: endpoint.name,
        status: 'timeout',
        error: 'Request timed out'
      });
    });
    
    req.end();
  });
}

async function checkAllHealth() {
  console.log('🔍 Checking MCP server health...\n');
  
  const results = await Promise.all(
    healthEndpoints.map(endpoint => checkHealth(endpoint))
  );
  
  let allHealthy = true;
  
  for (const result of results) {
    const statusIcon = result.status === 'healthy' ? '✅' : '❌';
    console.log(`${statusIcon} ${result.name}: ${result.status}`);
    
    if (result.status !== 'healthy') {
      allHealthy = false;
      if (result.error) {
        console.log(`   Error: ${result.error}`);
      }
      if (result.statusCode) {
        console.log(`   Status Code: ${result.statusCode}`);
      }
    }
  }
  
  console.log('\n' + (allHealthy ? '✅ All services are healthy' : '❌ Some services are unhealthy'));
  
  if (!allHealthy) {
    process.exit(1);
  }
}

if (require.main === module) {
  checkAllHealth();
}

module.exports = { checkAllHealth };
