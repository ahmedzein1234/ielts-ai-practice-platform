#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const requiredMcpServers = [
  'filesystem',
  'github',
  'openrouter',
  'postgres',
  'redis',
  's3',
  'browser',
  'playwright',
  'lighthouse',
  'axe',
  'stripe',
  'ffmpeg',
  'stt',
  'ocr',
  'scoring',
  'deploy'
];

function validateMcpConfig() {
  const mcpConfigPath = path.join(__dirname, '../../cursor/mcp.json');
  
  if (!fs.existsSync(mcpConfigPath)) {
    console.error('❌ MCP configuration file not found at cursor/mcp.json');
    process.exit(1);
  }

  try {
    const mcpConfig = JSON.parse(fs.readFileSync(mcpConfigPath, 'utf8'));
    const configuredServers = Object.keys(mcpConfig.mcpServers || {});
    
    const missingServers = requiredMcpServers.filter(
      server => !configuredServers.includes(server)
    );
    
    if (missingServers.length > 0) {
      console.error('❌ Missing required MCP servers:', missingServers.join(', '));
      process.exit(1);
    }
    
    console.log('✅ All required MCP servers are configured');
    
    // Validate environment variables
    const missingEnvVars = [];
    
    for (const [serverName, config] of Object.entries(mcpConfig.mcpServers)) {
      if (config.env) {
        for (const [envKey, envValue] of Object.entries(config.env)) {
          if (envValue.startsWith('env:') && !process.env[envValue.slice(4)]) {
            missingEnvVars.push(`${envValue.slice(4)} (for ${serverName})`);
          }
        }
      }
    }
    
    if (missingEnvVars.length > 0) {
      console.warn('⚠️  Missing environment variables:', missingEnvVars.join(', '));
      console.warn('   Some MCP servers may not function correctly');
    }
    
  } catch (error) {
    console.error('❌ Error reading MCP configuration:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  validateMcpConfig();
}

module.exports = { validateMcpConfig };
