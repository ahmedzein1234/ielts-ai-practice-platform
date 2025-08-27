import { expect, test } from '@playwright/test';

test.describe('White Page Diagnostic Tests', () => {
    test('should diagnose white page issue', async ({ page }) => {
        console.log('🔍 Starting white page diagnostic...');

        // Navigate to the homepage
        await page.goto('/');
        console.log('✅ Navigated to homepage');

        // Wait for initial load
        await page.waitForLoadState('domcontentloaded');
        console.log('✅ DOM content loaded');

        // Check if page is completely white
        const bodyBackground = await page.evaluate(() => {
            const body = document.body;
            const computedStyle = window.getComputedStyle(body);
            return {
                backgroundColor: computedStyle.backgroundColor,
                color: computedStyle.color,
                innerHTML: body.innerHTML,
                textContent: body.textContent,
                childrenCount: body.children.length
            };
        });

        console.log('📊 Page analysis:', bodyBackground);

        // Check for common white page causes
        const diagnostics = await page.evaluate(() => {
            const errors = [];
            const warnings = [];

            // Check for React hydration errors
            const reactErrors = document.querySelectorAll('[data-react-error]');
            if (reactErrors.length > 0) {
                errors.push(`React hydration errors: ${reactErrors.length}`);
            }

            // Check for JavaScript errors
            const scripts = document.querySelectorAll('script');
            const failedScripts = Array.from(scripts).filter(script => {
                return script.src && !script.complete;
            });

            if (failedScripts.length > 0) {
                errors.push(`Failed script loads: ${failedScripts.length}`);
            }

            // Check for CSS issues
            const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
            const failedStylesheets = Array.from(stylesheets).filter(link => {
                return link.href && !link.sheet;
            });

            if (failedStylesheets.length > 0) {
                errors.push(`Failed stylesheet loads: ${failedStylesheets.length}`);
            }

            // Check for Next.js specific issues
            const nextData = document.getElementById('__NEXT_DATA__');
            if (!nextData) {
                warnings.push('Next.js data not found');
            }

            // Check for React root
            const reactRoot = document.getElementById('__next');
            if (!reactRoot) {
                errors.push('React root not found');
            }

            return { errors, warnings };
        });

        console.log('🔍 Diagnostics:', diagnostics);

        // Take a screenshot for visual inspection
        await page.screenshot({ path: 'white-page-diagnostic.png', fullPage: true });
        console.log('📸 Screenshot saved as white-page-diagnostic.png');

        // Check console for errors
        const consoleMessages: string[] = [];
        page.on('console', msg => {
            consoleMessages.push(`${msg.type()}: ${msg.text()}`);
        });

        // Wait a bit more to capture any delayed errors
        await page.waitForTimeout(3000);

        console.log('📝 Console messages:', consoleMessages);

        // Basic assertions
        expect(bodyBackground.childrenCount).toBeGreaterThan(0);
        expect(bodyBackground.textContent).toBeTruthy();

        // If we have errors, fail the test with details
        if (diagnostics.errors.length > 0) {
            throw new Error(`White page caused by: ${diagnostics.errors.join(', ')}`);
        }
    });

    test('should check for build issues', async ({ page }) => {
        console.log('🔍 Checking for build issues...');

        await page.goto('/');

        // Check for 404 errors
        const failedRequests: string[] = [];
        page.on('response', response => {
            if (response.status() === 404) {
                failedRequests.push(response.url());
            }
        });

        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(2000);

        console.log('❌ Failed requests (404):', failedRequests);

        // Check for JavaScript bundle issues
        const jsErrors = await page.evaluate(() => {
            const errors = [];

            // Check if main JavaScript bundles are loaded
            const scripts = Array.from(document.querySelectorAll('script[src]'));
            const mainScripts = scripts.filter(script =>
                script.src.includes('chunk') ||
                script.src.includes('main') ||
                script.src.includes('app')
            );

            if (mainScripts.length === 0) {
                errors.push('No main JavaScript bundles found');
            }

            return errors;
        });

        console.log('🔍 JavaScript bundle analysis:', jsErrors);

        if (jsErrors.length > 0) {
            throw new Error(`Build issues detected: ${jsErrors.join(', ')}`);
        }
    });

    test('should verify component rendering', async ({ page }) => {
        console.log('🔍 Verifying component rendering...');

        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Check for specific React components
        const componentChecks = await page.evaluate(() => {
            const checks = {
                hasHeader: !!document.querySelector('header'),
                hasMain: !!document.querySelector('main'),
                hasFooter: !!document.querySelector('footer'),
                hasNavigation: !!document.querySelector('nav'),
                hasHeroSection: !!document.querySelector('h1'),
                hasButtons: document.querySelectorAll('button').length,
                hasLinks: document.querySelectorAll('a').length,
                hasImages: document.querySelectorAll('img').length
            };

            return checks;
        });

        console.log('📊 Component rendering check:', componentChecks);

        // Basic component presence checks
        expect(componentChecks.hasHeader).toBeTruthy();
        expect(componentChecks.hasHeroSection).toBeTruthy();
        expect(componentChecks.hasButtons).toBeGreaterThan(0);
        expect(componentChecks.hasLinks).toBeGreaterThan(0);
    });
});

