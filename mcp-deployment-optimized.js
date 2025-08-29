#!/usr/bin/env node

/**
 * IELTS AI Platform - Optimized MCP Deployment Script
 * 
 * Streamlined deployment using Railway (backend) + Cloudflare Pages (frontend) + Supabase (database)
 * Proper MCP protocol implementation with JSON-RPC 2.0
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  projectName: 'ielts-ai-platform',
  supabaseProjectId: 'zzvskbvqtglzonftpikf',
  services: [
    { name: 'api', port: 8000, path: 'services/api' },
    { name: 'scoring', port: 8001, path: 'services/scoring' },
    { name: 'exam-generator', port: 8006, path: 'services/exam-generator' },
    { name: 'ocr', port: 8002, path: 'services/ocr' },
    { name: 'speech', port: 8003, path: 'services/speech' },
    { name: 'ai-tutor', port: 8001, path: 'services/ai-tutor' },
    { name: 'worker', port: 8004, path: 'workers' }
  ],
  mcpConfig: null
};

// Utility functions
const log = {
  info: (msg) => console.log(`🔵 [INFO] ${msg}`),
  success: (msg) => console.log(`✅ [SUCCESS] ${msg}`),
  warning: (msg) => console.log(`⚠️  [WARNING] ${msg}`),
  error: (msg) => console.log(`❌ [ERROR] ${msg}`),
  debug: (msg) => process.env.DEBUG && console.log(`🐛 [DEBUG] ${msg}`)
};

// Load MCP configuration
function loadMCPConfig() {
  try {
    CONFIG.mcpConfig = JSON.parse(fs.readFileSync('mcp-config.json', 'utf8'));
    log.success('MCP configuration loaded');
    return CONFIG.mcpConfig;
  } catch (error) {
    log.error(`Failed to load MCP config: ${error.message}`);
    throw error;
  }
}

// Execute command with proper error handling
function executeCommand(command, args = [], options = {}) {
  return new Promise((resolve, reject) => {
    log.debug(`Executing: ${command} ${args.join(' ')}`);
    
    const child = spawn(command, args, {
      stdio: ['pipe', 'pipe', 'pipe'],
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
        resolve({ stdout, stderr, code });
      } else {
        reject(new Error(`Command failed with exit code ${code}: ${stderr}`));
      }
    });
    
    child.on('error', (error) => {
      reject(error);
    });
  });
}

// MCP Server Manager
class MCPServerManager {
  constructor() {
    this.servers = new Map();
    this.config = loadMCPConfig();
  }

  async startServer(name, config) {
    log.info(`Starting ${name} MCP server...`);
    
    return new Promise((resolve, reject) => {
      const env = { ...process.env };
      
      // Substitute environment variables
      Object.keys(config.env).forEach(key => {
        const value = config.env[key];
        if (value.startsWith('${') && value.endsWith('}')) {
          const envVar = value.slice(2, -1);
          env[key] = process.env[envVar];
        } else {
          env[key] = value;
        }
      });

      const child = spawn(config.command, config.args, { env });
      
      child.stdout.on('data', (data) => {
        log.debug(`[${name}] ${data.toString().trim()}`);
      });

      child.stderr.on('data', (data) => {
        log.debug(`[${name}] ERROR: ${data.toString().trim()}`);
      });

      child.on('spawn', () => {
        this.servers.set(name, child);
        log.success(`${name} MCP server started`);
        resolve(child);
      });

      child.on('error', (error) => {
        log.error(`Failed to start ${name} MCP server: ${error.message}`);
        reject(error);
      });
    });
  }

  async sendMCPCommand(serverName, method, params = {}) {
    const server = this.servers.get(serverName);
    if (!server) {
      throw new Error(`${serverName} MCP server not running`);
    }

    return new Promise((resolve, reject) => {
      const id = Date.now();
      const request = {
        jsonrpc: '2.0',
        id,
        method,
        params
      };

      log.debug(`Sending MCP command to ${serverName}: ${JSON.stringify(request)}`);

      server.stdin.write(JSON.stringify(request) + '\n');

      const timeout = setTimeout(() => {
        reject(new Error(`MCP command timeout for ${serverName}`));
      }, 30000);

      server.stdout.once('data', (data) => {
        clearTimeout(timeout);
        try {
          const response = JSON.parse(data.toString());
          if (response.error) {
            reject(new Error(`MCP Error: ${response.error.message}`));
          } else {
            resolve(response.result);
          }
        } catch (error) {
          // Fallback for non-JSON responses
          resolve(data.toString().trim());
        }
      });
    });
  }

  async stopAllServers() {
    for (const [name, server] of this.servers) {
      log.info(`Stopping ${name} MCP server...`);
      server.kill('SIGTERM');
    }
    this.servers.clear();
  }
}

// Railway Deployment Manager
class RailwayDeployment {
  constructor(mcpManager) {
    this.mcp = mcpManager;
    this.serviceUrls = new Map();
  }

  async deployServices() {
    log.info('🚂 Deploying backend services to Railway...');

    for (const service of CONFIG.services) {
      try {
        log.info(`Deploying ${service.name} service...`);
        
        // Use Railway MCP to deploy service
        const result = await this.mcp.sendMCPCommand('railway', 'deploy', {
          serviceName: service.name,
          path: service.path,
          port: service.port
        });

        const serviceUrl = `https://${service.name}-${CONFIG.projectName}.railway.app`;
        this.serviceUrls.set(service.name, serviceUrl);
        
        log.success(`${service.name} deployed: ${serviceUrl}`);
      } catch (error) {
        log.error(`Failed to deploy ${service.name}: ${error.message}`);
        throw error;
      }
    }

    return this.serviceUrls;
  }

  async setEnvironmentVariables(serviceName, variables) {
    log.info(`Setting environment variables for ${serviceName}...`);
    
    try {
      await this.mcp.sendMCPCommand('railway', 'setEnvVars', {
        serviceName,
        variables
      });
      log.success(`Environment variables set for ${serviceName}`);
    } catch (error) {
      log.error(`Failed to set environment variables: ${error.message}`);
      throw error;
    }
  }
}

// Cloudflare Pages Deployment Manager
class CloudflareDeployment {
  constructor(mcpManager) {
    this.mcp = mcpManager;
  }

  async deployFrontend() {
    log.info('☁️  Deploying frontend to Cloudflare Pages...');

    try {
      // Build the Next.js application
      log.info('Building Next.js application...');
      const buildPath = path.resolve('apps/web');
      
      await executeCommand('npm', ['run', 'build'], { 
        cwd: buildPath 
      });

      // Deploy to Cloudflare Pages using MCP
      const result = await this.mcp.sendMCPCommand('cloudflare', 'deployPages', {
        projectName: CONFIG.projectName,
        directory: 'out',
        branch: 'main'
      });

      const frontendUrl = `https://${CONFIG.projectName}.pages.dev`;
      log.success(`Frontend deployed: ${frontendUrl}`);
      
      return frontendUrl;
    } catch (error) {
      log.error(`Frontend deployment failed: ${error.message}`);
      throw error;
    }
  }

  async setEnvironmentVariables(variables) {
    log.info('Setting Cloudflare Pages environment variables...');
    
    try {
      await this.mcp.sendMCPCommand('cloudflare', 'setEnvVars', {
        projectName: CONFIG.projectName,
        variables
      });
      log.success('Cloudflare Pages environment variables set');
    } catch (error) {
      log.error(`Failed to set Cloudflare environment variables: ${error.message}`);
      throw error;
    }
  }
}

// Supabase Integration Manager
class SupabaseIntegration {
  constructor(mcpManager) {
    this.mcp = mcpManager;
  }

  async setupDatabase() {
    log.info('🗄️  Setting up Supabase database...');

    try {
      // Apply database migrations
      await this.mcp.sendMCPCommand('supabase', 'migrate', {
        projectId: CONFIG.supabaseProjectId
      });

      // Setup storage buckets
      const buckets = ['ielts-uploads', 'audio-recordings', 'documents', 'user-avatars'];
      for (const bucket of buckets) {
        try {
          await this.mcp.sendMCPCommand('supabase', 'createBucket', {
            name: bucket,
            public: false
          });
          log.success(`Created storage bucket: ${bucket}`);
        } catch (error) {
          log.warning(`Bucket ${bucket} might already exist`);
        }
      }

      log.success('Supabase setup completed');
    } catch (error) {
      log.error(`Supabase setup failed: ${error.message}`);
      throw error;
    }
  }
}

// Main Deployment Orchestrator
class OptimizedDeploymentOrchestrator {
  constructor() {
    this.mcpManager = new MCPServerManager();
    this.railway = new RailwayDeployment(this.mcpManager);
    this.cloudflare = new CloudflareDeployment(this.mcpManager);
    this.supabase = new SupabaseIntegration(this.mcpManager);
  }

  async checkPrerequisites() {
    log.info('Checking deployment prerequisites...');
    
    const requiredEnvVars = [
      'RAILWAY_TOKEN',
      'CLOUDFLARE_API_TOKEN', 
      'CLOUDFLARE_ACCOUNT_ID',
      'SUPABASE_ANON_KEY',
      'SUPABASE_SERVICE_ROLE_KEY',
      'OPENAI_API_KEY',
      'ANTHROPIC_API_KEY',
      'OPENROUTER_API_KEY'
    ];

    const missing = requiredEnvVars.filter(env => !process.env[env]);
    if (missing.length > 0) {
      throw new Error(`Missing environment variables: ${missing.join(', ')}`);
    }

    log.success('All prerequisites satisfied');
  }

  async startMCPServers() {
    log.info('🚀 Starting MCP servers...');
    
    const serverPromises = Object.entries(this.mcpManager.config.mcpServers).map(
      ([name, config]) => this.mcpManager.startServer(name, config)
    );

    await Promise.all(serverPromises);
    log.success('All MCP servers started');
  }

  async deploy() {
    try {
      log.info('🎯 Starting optimized IELTS AI Platform deployment...\n');

      // Step 1: Prerequisites
      await this.checkPrerequisites();

      // Step 2: Start MCP servers
      await this.startMCPServers();

      // Step 3: Setup Supabase
      await this.supabase.setupDatabase();

      // Step 4: Deploy backend services
      const serviceUrls = await this.railway.deployServices();

      // Step 5: Configure environment variables for frontend
      const frontendEnvVars = {
        NEXT_PUBLIC_SUPABASE_URL: `https://${CONFIG.supabaseProjectId}.supabase.co`,
        NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY,
        NEXT_PUBLIC_API_URL: serviceUrls.get('api'),
        NEXT_PUBLIC_AI_TUTOR_URL: serviceUrls.get('ai-tutor'),
        NEXT_PUBLIC_SCORING_URL: serviceUrls.get('scoring'),
        NEXT_PUBLIC_SPEECH_URL: serviceUrls.get('speech'),
        NEXT_PUBLIC_OCR_URL: serviceUrls.get('ocr'),
        NEXT_PUBLIC_EXAM_GENERATOR_URL: serviceUrls.get('exam-generator')
      };

      await this.cloudflare.setEnvironmentVariables(frontendEnvVars);

      // Step 6: Deploy frontend
      const frontendUrl = await this.cloudflare.deployFrontend();

      // Step 7: Health checks
      await this.runHealthChecks(serviceUrls, frontendUrl);

      log.success('🎉 Deployment completed successfully!');
      this.printDeploymentSummary(serviceUrls, frontendUrl);

    } catch (error) {
      log.error(`Deployment failed: ${error.message}`);
      throw error;
    } finally {
      await this.mcpManager.stopAllServers();
    }
  }

  async runHealthChecks(serviceUrls, frontendUrl) {
    log.info('🏥 Running health checks...');

    // Check backend services
    for (const [serviceName, url] of serviceUrls) {
      try {
        const response = await fetch(`${url}/health`);
        if (response.ok) {
          log.success(`${serviceName} health check passed`);
        } else {
          log.warning(`${serviceName} health check failed`);
        }
      } catch (error) {
        log.warning(`${serviceName} health check failed: ${error.message}`);
      }
    }

    // Check frontend
    try {
      const response = await fetch(frontendUrl);
      if (response.ok) {
        log.success('Frontend health check passed');
      } else {
        log.warning('Frontend health check failed');
      }
    } catch (error) {
      log.warning(`Frontend health check failed: ${error.message}`);
    }
  }

  printDeploymentSummary(serviceUrls, frontendUrl) {
    console.log('\n📊 Deployment Summary:');
    console.log('='.repeat(50));
    console.log(`🌐 Frontend: ${frontendUrl}`);
    console.log('🚂 Backend Services:');
    
    for (const [serviceName, url] of serviceUrls) {
      console.log(`   • ${serviceName}: ${url}`);
    }
    
    console.log(`🗄️  Database: https://${CONFIG.supabaseProjectId}.supabase.co`);
    console.log('\n🎯 Next Steps:');
    console.log('1. Configure custom domain');
    console.log('2. Set up monitoring');
    console.log('3. Configure CI/CD pipeline');
    console.log('4. Test all functionality');
  }
}

// CLI interface
async function main() {
  if (process.argv.includes('--help') || process.argv.includes('-h')) {
    console.log(`
IELTS AI Platform - Optimized MCP Deployment Script

Usage:
  node mcp-deployment-optimized.js [options]

Options:
  --help, -h          Show this help message
  --debug             Enable debug logging

Environment Variables Required:
  RAILWAY_TOKEN              Railway API token
  CLOUDFLARE_API_TOKEN       Cloudflare API token  
  CLOUDFLARE_ACCOUNT_ID      Cloudflare account ID
  SUPABASE_ANON_KEY          Supabase anonymous key
  SUPABASE_SERVICE_ROLE_KEY  Supabase service role key
  OPENAI_API_KEY            OpenAI API key
  ANTHROPIC_API_KEY         Anthropic API key
  OPENROUTER_API_KEY        OpenRouter API key

Example:
  DEBUG=true node mcp-deployment-optimized.js
    `);
    return;
  }

  const orchestrator = new OptimizedDeploymentOrchestrator();
  await orchestrator.deploy();
}

// Run the script
if (require.main === module) {
  main().catch(error => {
    console.error('💥 Deployment failed:', error.message);
    process.exit(1);
  });
}

module.exports = {
  OptimizedDeploymentOrchestrator,
  MCPServerManager,
  RailwayDeployment,
  CloudflareDeployment,
  SupabaseIntegration
};