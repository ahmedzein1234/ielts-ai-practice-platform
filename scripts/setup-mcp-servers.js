#!/usr/bin/env node

/**
 * MCP Servers Setup Script
 * Installs and configures the required MCP servers for IELTS AI Platform
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const log = {
  info: (msg) => console.log(`🔵 [INFO] ${msg}`),
  success: (msg) => console.log(`✅ [SUCCESS] ${msg}`),
  warning: (msg) => console.log(`⚠️  [WARNING] ${msg}`),
  error: (msg) => console.log(`❌ [ERROR] ${msg}`)
};

// Required MCP servers for optimized deployment
const MCP_SERVERS = [
  {
    name: 'Railway MCP',
    package: '@jason-tan-swe/railway-mcp',
    description: 'Railway platform integration for backend deployment'
  },
  {
    name: 'Cloudflare Wrangler MCP',
    package: '@cloudflare/wrangler-mcp',
    description: 'Cloudflare Pages deployment and management'
  },
  {
    name: 'Supabase MCP',
    package: '@modelcontextprotocol/server-supabase',
    description: 'Supabase database, auth, and storage integration'
  },
  {
    name: 'GitHub MCP',
    package: '@modelcontextprotocol/server-github',
    description: 'GitHub repository management'
  },
  {
    name: 'OpenRouter MCP',
    package: '@modelcontextprotocol/server-openrouter',
    description: 'AI model access for IELTS features'
  },
  {
    name: 'PostgreSQL MCP',
    package: '@modelcontextprotocol/server-postgres',
    description: 'Direct database access for development'
  },
  {
    name: 'Filesystem MCP',
    package: '@modelcontextprotocol/server-filesystem',
    description: 'Local filesystem operations'
  },
  {
    name: 'Playwright MCP',
    package: '@modelcontextprotocol/server-playwright',
    description: 'End-to-end testing and browser automation'
  }
];

// CLI tools required for deployment
const CLI_TOOLS = [
  {
    name: 'Wrangler CLI',
    package: 'wrangler',
    description: 'Cloudflare CLI tool'
  },
  {
    name: 'Railway CLI',
    package: '@railway/cli',
    description: 'Railway CLI tool'
  },
  {
    name: 'Supabase CLI',
    package: 'supabase',
    description: 'Supabase CLI tool'
  }
];

function executeCommand(command, description) {
  try {
    log.info(description);
    execSync(command, { stdio: 'inherit' });
    return true;
  } catch (error) {
    log.error(`Failed: ${error.message}`);
    return false;
  }
}

function checkIfInstalled(packageName) {
  try {
    execSync(`npm list -g ${packageName}`, { stdio: 'pipe' });
    return true;
  } catch (error) {
    return false;
  }
}

async function installMCPServers() {
  log.info('🚀 Installing MCP servers...\n');

  for (const server of MCP_SERVERS) {
    if (checkIfInstalled(server.package)) {
      log.success(`${server.name} is already installed`);
      continue;
    }

    const success = executeCommand(
      `npm install -g ${server.package}`,
      `Installing ${server.name}...`
    );

    if (success) {
      log.success(`${server.name} installed successfully`);
    } else {
      log.error(`Failed to install ${server.name}`);
    }
    console.log('');
  }
}

async function installCLITools() {
  log.info('🛠️  Installing CLI tools...\n');

  for (const tool of CLI_TOOLS) {
    if (checkIfInstalled(tool.package)) {
      log.success(`${tool.name} is already installed`);
      continue;
    }

    const success = executeCommand(
      `npm install -g ${tool.package}`,
      `Installing ${tool.name}...`
    );

    if (success) {
      log.success(`${tool.name} installed successfully`);
    } else {
      log.error(`Failed to install ${tool.name}`);
    }
    console.log('');
  }
}

function validateEnvironmentVariables() {
  log.info('🔍 Validating environment variables...\n');

  const requiredEnvVars = [
    'RAILWAY_TOKEN',
    'CLOUDFLARE_API_TOKEN',
    'CLOUDFLARE_ACCOUNT_ID',
    'SUPABASE_URL',
    'SUPABASE_ANON_KEY',
    'SUPABASE_SERVICE_ROLE_KEY',
    'GITHUB_PERSONAL_ACCESS_TOKEN',
    'OPENROUTER_API_KEY'
  ];

  const missing = [];
  const present = [];

  for (const envVar of requiredEnvVars) {
    if (process.env[envVar]) {
      present.push(envVar);
      log.success(`${envVar} is set`);
    } else {
      missing.push(envVar);
      log.warning(`${envVar} is not set`);
    }
  }

  console.log('');

  if (missing.length > 0) {
    log.warning('Missing environment variables:');
    missing.forEach(env => console.log(`   • ${env}`));
    console.log('\n📝 Please add these to your .env file or environment.');
    console.log('   See env.example for reference values.\n');
  }

  return missing.length === 0;
}

function createMCPConfigValidation() {
  log.info('📋 Validating MCP configuration...\n');

  const configPath = path.resolve('mcp-config.json');
  
  if (!fs.existsSync(configPath)) {
    log.error('mcp-config.json not found!');
    return false;
  }

  try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    
    if (!config.mcpServers) {
      log.error('Invalid MCP configuration: missing mcpServers');
      return false;
    }

    const configuredServers = Object.keys(config.mcpServers);
    log.success(`MCP configuration found with ${configuredServers.length} servers:`);
    
    configuredServers.forEach(server => {
      console.log(`   • ${server}`);
    });

    return true;
  } catch (error) {
    log.error(`Invalid MCP configuration: ${error.message}`);
    return false;
  }
}

function printSetupSummary() {
  console.log('\n' + '='.repeat(60));
  console.log('🎯 MCP Setup Summary');
  console.log('='.repeat(60));
  
  console.log('\n✅ Installed MCP Servers:');
  MCP_SERVERS.forEach(server => {
    console.log(`   • ${server.name}`);
  });

  console.log('\n🛠️  Installed CLI Tools:');
  CLI_TOOLS.forEach(tool => {
    console.log(`   • ${tool.name}`);
  });

  console.log('\n🚀 Next Steps:');
  console.log('   1. Set up environment variables (see env.example)');
  console.log('   2. Configure API tokens for each platform');
  console.log('   3. Run: npm run deploy');
  
  console.log('\n📚 Documentation:');
  console.log('   • Railway: https://docs.railway.app');
  console.log('   • Cloudflare: https://developers.cloudflare.com/pages');
  console.log('   • Supabase: https://supabase.com/docs');
  console.log('');
}

async function main() {
  console.log('🎯 IELTS AI Platform - MCP Setup\n');

  try {
    // Install MCP servers
    await installMCPServers();

    // Install CLI tools
    await installCLITools();

    // Validate configuration
    const configValid = createMCPConfigValidation();
    
    // Validate environment variables
    const envValid = validateEnvironmentVariables();

    // Print summary
    printSetupSummary();

    if (!configValid || !envValid) {
      log.warning('Setup completed with warnings. Please address the issues above.');
      process.exit(1);
    } else {
      log.success('🎉 MCP setup completed successfully!');
    }

  } catch (error) {
    log.error(`Setup failed: ${error.message}`);
    process.exit(1);
  }
}

// Run setup
if (require.main === module) {
  main();
}

module.exports = {
  installMCPServers,
  installCLITools,
  validateEnvironmentVariables,
  createMCPConfigValidation
};