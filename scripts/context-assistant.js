#!/usr/bin/env node

/**
 * 🧠 Context Assistant for IELTS AI Platform
 * Provides intelligent assistance for deployment and development
 */

const fs = require('fs');
const path = require('path');

class ContextAssistant {
    constructor() {
        this.projectRoot = process.cwd();
        this.context = this.loadProjectContext();
    }

    loadProjectContext() {
        const context = {
            project: {
                name: 'IELTS AI Platform',
                type: 'microservices',
                architecture: 'FastAPI + Next.js + PostgreSQL + Redis',
                services: ['api', 'scoring', 'speech', 'ocr', 'ai-tutor'],
                frontend: 'Next.js with TypeScript and Tailwind CSS'
            },
            deployment: {
                recommended: 'Railway + Vercel + Supabase',
                cost: '$80-175/month',
                complexity: 'Medium'
            },
            features: {
                speaking: 'Real-time recording and scoring',
                writing: 'Essay writing with AI feedback',
                listening: 'Audio playback and comprehension',
                reading: 'Passage analysis and questions',
                aiTutor: 'Personalized learning paths',
                analytics: 'Progress tracking and insights'
            }
        };

        return context;
    }

    analyzeProjectStructure() {
        console.log('🔍 Analyzing project structure...');

        const structure = {
            services: [],
            frontend: null,
            config: [],
            scripts: []
        };

        // Check services
        const servicesDir = path.join(this.projectRoot, 'services');
        if (fs.existsSync(servicesDir)) {
            const services = fs.readdirSync(servicesDir);
            structure.services = services.filter(service =>
                fs.statSync(path.join(servicesDir, service)).isDirectory()
            );
        }

        // Check frontend
        const webDir = path.join(this.projectRoot, 'apps', 'web');
        if (fs.existsSync(webDir)) {
            structure.frontend = 'Next.js';
        }

        // Check config files
        const configFiles = ['docker-compose.yml', 'package.json', 'requirements.txt'];
        structure.config = configFiles.filter(file =>
            fs.existsSync(path.join(this.projectRoot, file))
        );

        // Check scripts
        const scriptsDir = path.join(this.projectRoot, 'scripts');
        if (fs.existsSync(scriptsDir)) {
            structure.scripts = fs.readdirSync(scriptsDir);
        }

        return structure;
    }

    generateDeploymentPlan() {
        console.log('📋 Generating deployment plan...');

        const plan = {
            phase1: {
                name: 'Backend Setup',
                steps: [
                    'Create Railway account and project',
                    'Deploy API Gateway service',
                    'Deploy Scoring service',
                    'Deploy AI Tutor service',
                    'Configure environment variables'
                ],
                estimatedTime: '30 minutes'
            },
            phase2: {
                name: 'Database Setup',
                steps: [
                    'Create Supabase project',
                    'Configure PostgreSQL database',
                    'Set up authentication',
                    'Create storage buckets',
                    'Configure real-time subscriptions'
                ],
                estimatedTime: '20 minutes'
            },
            phase3: {
                name: 'Frontend Deployment',
                steps: [
                    'Connect GitHub repository to Vercel',
                    'Configure build settings',
                    'Set environment variables',
                    'Deploy frontend application',
                    'Test all features'
                ],
                estimatedTime: '15 minutes'
            },
            phase4: {
                name: 'Integration & Testing',
                steps: [
                    'Test API endpoints',
                    'Verify database connections',
                    'Test real-time features',
                    'Configure custom domains',
                    'Set up monitoring'
                ],
                estimatedTime: '25 minutes'
            }
        };

        return plan;
    }

    provideRecommendations() {
        console.log('💡 Providing recommendations...');

        return {
            performance: [
                'Use Redis caching for frequently accessed data',
                'Implement CDN for static assets',
                'Optimize database queries with proper indexing',
                'Use connection pooling for database connections'
            ],
            security: [
                'Enable HTTPS for all services',
                'Implement rate limiting on API endpoints',
                'Use environment variables for sensitive data',
                'Set up proper CORS configuration',
                'Implement input validation and sanitization'
            ],
            monitoring: [
                'Set up Railway monitoring for backend services',
                'Configure Vercel analytics for frontend',
                'Use Supabase dashboard for database monitoring',
                'Implement error tracking with Sentry',
                'Set up automated health checks'
            ],
            scaling: [
                'Railway auto-scales based on traffic',
                'Vercel provides global CDN and edge functions',
                'Supabase handles database scaling automatically',
                'Consider implementing caching strategies',
                'Monitor resource usage and optimize accordingly'
            ]
        };
    }

    generateTroubleshootingGuide() {
        console.log('🔧 Generating troubleshooting guide...');

        return {
            commonIssues: {
                'Port conflicts': {
                    description: 'Services trying to use the same port',
                    solution: 'Use different ports or kill conflicting processes',
                    command: 'netstat -ano | findstr :8000'
                },
                'Environment variables': {
                    description: 'Missing or incorrect environment variables',
                    solution: 'Check Railway/Vercel dashboard and verify all variables are set',
                    command: 'railway variables'
                },
                'Database connection': {
                    description: 'Cannot connect to Supabase database',
                    solution: 'Verify DATABASE_URL and ensure SSL is enabled',
                    command: 'Check Supabase dashboard for connection string'
                },
                'CORS errors': {
                    description: 'Frontend cannot access backend APIs',
                    solution: 'Update CORS origins in FastAPI services',
                    command: 'Check ALLOWED_ORIGINS in service configs'
                }
            },
            debugCommands: {
                'Check service status': 'railway status',
                'View logs': 'railway logs',
                'Redeploy service': 'railway up',
                'Check environment': 'railway variables',
                'Test API endpoint': 'curl http://localhost:8000/health'
            }
        };
    }

    generateContextReport() {
        const structure = this.analyzeProjectStructure();
        const plan = this.generateDeploymentPlan();
        const recommendations = this.provideRecommendations();
        const troubleshooting = this.generateTroubleshootingGuide();

        const report = {
            timestamp: new Date().toISOString(),
            project: this.context.project,
            structure,
            deploymentPlan: plan,
            recommendations,
            troubleshooting,
            nextSteps: [
                'Run the MCP deployment script',
                'Set up environment variables',
                'Test all services locally',
                'Deploy to production',
                'Monitor and optimize'
            ]
        };

        return report;
    }

    saveContextReport() {
        const report = this.generateContextReport();
        const reportPath = path.join(this.projectRoot, 'context-report.json');

        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
        console.log('📄 Context report saved to context-report.json');

        return reportPath;
    }

    displaySummary() {
        const report = this.generateContextReport();

        console.log('\n🎯 IELTS AI Platform - Context Summary');
        console.log('=====================================\n');

        console.log('📊 Project Overview:');
        console.log(`  • Name: ${report.project.name}`);
        console.log(`  • Architecture: ${report.project.architecture}`);
        console.log(`  • Services: ${report.structure.services.join(', ')}`);
        console.log(`  • Frontend: ${report.structure.frontend || 'Not found'}\n`);

        console.log('🚀 Deployment Plan:');
        Object.entries(report.deploymentPlan).forEach(([phase, details]) => {
            console.log(`  • ${details.name}: ${details.estimatedTime}`);
        });
        console.log('');

        console.log('💡 Key Recommendations:');
        console.log('  • Use Railway for backend services');
        console.log('  • Use Vercel for frontend deployment');
        console.log('  • Use Supabase for database and auth');
        console.log('  • Implement proper monitoring');
        console.log('');

        console.log('🔧 Next Steps:');
        report.nextSteps.forEach((step, index) => {
            console.log(`  ${index + 1}. ${step}`);
        });
        console.log('');
    }
}

// Run the context assistant
const assistant = new ContextAssistant();
assistant.displaySummary();
assistant.saveContextReport();

console.log('✅ Context analysis completed!');
console.log('📄 Detailed report saved to context-report.json');
