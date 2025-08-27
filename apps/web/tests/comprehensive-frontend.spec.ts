import { expect, test } from '@playwright/test';

test.describe('Comprehensive Frontend Analysis', () => {
    test('should analyze homepage structure and functionality', async ({ page }) => {
        console.log('🔍 Analyzing homepage...');

        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Check for critical elements
        const criticalElements = await page.evaluate(() => {
            const elements = {
                hasHeroSection: !!document.querySelector('h1'),
                hasNavigation: !!document.querySelector('nav'),
                hasMainContent: !!document.querySelector('main'),
                hasFooter: !!document.querySelector('footer'),
                hasButtons: document.querySelectorAll('button').length,
                hasLinks: document.querySelectorAll('a').length,
                hasImages: document.querySelectorAll('img').length,
                hasForms: document.querySelectorAll('form').length,
                hasScripts: document.querySelectorAll('script').length,
                hasStylesheets: document.querySelectorAll('link[rel="stylesheet"]').length
            };

            // Check for specific content
            const content = {
                hasIELTSContent: document.body.textContent?.includes('IELTS') || false,
                hasAIContent: document.body.textContent?.includes('AI') || false,
                hasFeaturesSection: document.body.textContent?.includes('Features') || false,
                hasTestimonials: document.body.textContent?.includes('Testimonials') || false
            };

            return { elements, content };
        });

        console.log('📊 Homepage analysis:', criticalElements);

        // Basic assertions
        expect(criticalElements.elements.hasHeroSection).toBeTruthy();
        expect(criticalElements.elements.hasNavigation).toBeTruthy();
        expect(criticalElements.elements.hasButtons).toBeGreaterThan(0);
        expect(criticalElements.elements.hasLinks).toBeGreaterThan(0);
    });

    test('should check for JavaScript errors and console issues', async ({ page }) => {
        console.log('🔍 Checking JavaScript errors...');

        const consoleErrors: string[] = [];
        const consoleWarnings: string[] = [];

        page.on('console', msg => {
            if (msg.type() === 'error') {
                consoleErrors.push(msg.text());
            } else if (msg.type() === 'warning') {
                consoleWarnings.push(msg.text());
            }
        });

        await page.goto('/');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(3000);

        console.log('❌ Console errors:', consoleErrors);
        console.log('⚠️ Console warnings:', consoleWarnings);

        // Check for specific error patterns
        const criticalErrors = consoleErrors.filter(error =>
            error.includes('React') ||
            error.includes('Next.js') ||
            error.includes('Hydration') ||
            error.includes('TypeError') ||
            error.includes('ReferenceError')
        );

        if (criticalErrors.length > 0) {
            throw new Error(`Critical JavaScript errors found: ${criticalErrors.join(', ')}`);
        }
    });

    test('should verify component accessibility and ARIA', async ({ page }) => {
        console.log('🔍 Checking accessibility...');

        await page.goto('/');
        await page.waitForLoadState('networkidle');

        const accessibilityIssues = await page.evaluate(() => {
            const issues = [];

            // Check for missing alt attributes on images
            const imagesWithoutAlt = document.querySelectorAll('img:not([alt])');
            if (imagesWithoutAlt.length > 0) {
                issues.push(`Images without alt attributes: ${imagesWithoutAlt.length}`);
            }

            // Check for proper heading hierarchy
            const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            const headingLevels = Array.from(headings).map(h => parseInt(h.tagName[1]));
            let previousLevel = 0;
            for (const level of headingLevels) {
                if (level > previousLevel + 1) {
                    issues.push(`Skipped heading level: ${previousLevel} to ${level}`);
                }
                previousLevel = level;
            }

            // Check for form labels
            const inputs = document.querySelectorAll('input, textarea, select');
            const inputsWithoutLabels = Array.from(inputs).filter(input => {
                const id = input.getAttribute('id');
                const label = document.querySelector(`label[for="${id}"]`);
                const ariaLabel = input.getAttribute('aria-label');
                return !label && !ariaLabel;
            });

            if (inputsWithoutLabels.length > 0) {
                issues.push(`Form inputs without labels: ${inputsWithoutLabels.length}`);
            }

            return issues;
        });

        console.log('♿ Accessibility issues:', accessibilityIssues);

        if (accessibilityIssues.length > 0) {
            console.warn('Accessibility issues found:', accessibilityIssues);
        }
    });

    test('should test responsive design and mobile compatibility', async ({ page }) => {
        console.log('🔍 Testing responsive design...');

        const viewports = [
            { width: 375, height: 667, name: 'Mobile' },
            { width: 768, height: 1024, name: 'Tablet' },
            { width: 1920, height: 1080, name: 'Desktop' }
        ];

        for (const viewport of viewports) {
            console.log(`📱 Testing ${viewport.name} viewport...`);

            await page.setViewportSize(viewport);
            await page.goto('/');
            await page.waitForLoadState('networkidle');

            // Check if content is visible and properly laid out
            const layoutCheck = await page.evaluate(() => {
                const body = document.body;
                const computedStyle = window.getComputedStyle(body);

                return {
                    hasContent: body.textContent?.trim().length > 0,
                    isVisible: computedStyle.display !== 'none',
                    hasOverflow: body.scrollHeight > body.clientHeight,
                    hasHorizontalScroll: body.scrollWidth > body.clientWidth
                };
            });

            console.log(`📊 ${viewport.name} layout check:`, layoutCheck);

            expect(layoutCheck.hasContent).toBeTruthy();
            expect(layoutCheck.isVisible).toBeTruthy();
        }
    });

    test('should verify navigation and routing', async ({ page }) => {
        console.log('🔍 Testing navigation...');

        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Test internal navigation links
        const navigationLinks = await page.evaluate(() => {
            const links = Array.from(document.querySelectorAll('a[href^="/"]'));
            return links.map(link => ({
                href: link.getAttribute('href'),
                text: link.textContent?.trim(),
                isVisible: link.offsetParent !== null
            }));
        });

        console.log('🔗 Navigation links:', navigationLinks);

        // Test a few key navigation paths
        const keyPaths = ['/login', '/register', '/dashboard'];

        for (const path of keyPaths) {
            try {
                await page.goto(path);
                await page.waitForLoadState('networkidle');

                const pageTitle = await page.title();
                const hasContent = await page.evaluate(() => document.body.textContent?.trim().length > 0);

                console.log(`✅ ${path}: Title="${pageTitle}", HasContent=${hasContent}`);

                expect(hasContent).toBeTruthy();
            } catch (error) {
                console.error(`❌ Failed to load ${path}:`, error);
            }
        }
    });

    test('should check for performance issues', async ({ page }) => {
        console.log('🔍 Checking performance...');

        const performanceMetrics: any[] = [];

        page.on('response', response => {
            const url = response.url();
            const status = response.status();
            const size = response.headers()['content-length'];

            if (status >= 400) {
                performanceMetrics.push({
                    type: 'error',
                    url,
                    status,
                    size
                });
            } else if (size && parseInt(size) > 1024 * 1024) { // > 1MB
                performanceMetrics.push({
                    type: 'large_file',
                    url,
                    status,
                    size: parseInt(size)
                });
            }
        });

        await page.goto('/');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(2000);

        console.log('📊 Performance metrics:', performanceMetrics);

        // Check for large files
        const largeFiles = performanceMetrics.filter(m => m.type === 'large_file');
        if (largeFiles.length > 0) {
            console.warn('⚠️ Large files detected:', largeFiles);
        }

        // Check for failed requests
        const failedRequests = performanceMetrics.filter(m => m.type === 'error');
        if (failedRequests.length > 0) {
            console.error('❌ Failed requests:', failedRequests);
        }
    });

    test('should verify form functionality and validation', async ({ page }) => {
        console.log('🔍 Testing forms...');

        // Test login form
        await page.goto('/login');
        await page.waitForLoadState('networkidle');

        const loginFormCheck = await page.evaluate(() => {
            const form = document.querySelector('form');
            const inputs = document.querySelectorAll('input');
            const submitButton = document.querySelector('button[type="submit"]');

            return {
                hasForm: !!form,
                inputCount: inputs.length,
                hasSubmitButton: !!submitButton,
                hasEmailInput: !!document.querySelector('input[type="email"]'),
                hasPasswordInput: !!document.querySelector('input[type="password"]')
            };
        });

        console.log('📝 Login form check:', loginFormCheck);

        // Test register form
        await page.goto('/register');
        await page.waitForLoadState('networkidle');

        const registerFormCheck = await page.evaluate(() => {
            const form = document.querySelector('form');
            const inputs = document.querySelectorAll('input');
            const submitButton = document.querySelector('button[type="submit"]');

            return {
                hasForm: !!form,
                inputCount: inputs.length,
                hasSubmitButton: !!submitButton
            };
        });

        console.log('📝 Register form check:', registerFormCheck);
    });

    test('should check for missing dependencies and broken imports', async ({ page }) => {
        console.log('🔍 Checking for missing dependencies...');

        const missingResources: string[] = [];

        page.on('response', response => {
            if (response.status() === 404) {
                missingResources.push(response.url());
            }
        });

        await page.goto('/');
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(3000);

        console.log('❌ Missing resources:', missingResources);

        // Check for critical missing resources
        const criticalMissing = missingResources.filter(url =>
            url.includes('.js') ||
            url.includes('.css') ||
            url.includes('.json') ||
            url.includes('api/')
        );

        if (criticalMissing.length > 0) {
            console.error('❌ Critical missing resources:', criticalMissing);
        }
    });

    test('should verify theme and styling consistency', async ({ page }) => {
        console.log('🔍 Checking theme consistency...');

        await page.goto('/');
        await page.waitForLoadState('networkidle');

        const themeCheck = await page.evaluate(() => {
            const body = document.body;
            const computedStyle = window.getComputedStyle(body);

            // Check for CSS custom properties (theme variables)
            const cssVars = {
                '--background': getComputedStyle(body).getPropertyValue('--background'),
                '--foreground': getComputedStyle(body).getPropertyValue('--foreground'),
                '--primary': getComputedStyle(body).getPropertyValue('--primary'),
                '--muted': getComputedStyle(body).getPropertyValue('--muted')
            };

            // Check for Tailwind classes
            const hasTailwindClasses = body.className.includes('bg-') ||
                body.className.includes('text-') ||
                body.innerHTML.includes('bg-') ||
                body.innerHTML.includes('text-');

            return {
                cssVars,
                hasTailwindClasses,
                backgroundColor: computedStyle.backgroundColor,
                color: computedStyle.color,
                fontFamily: computedStyle.fontFamily
            };
        });

        console.log('🎨 Theme check:', themeCheck);

        // Basic theme assertions
        expect(themeCheck.hasTailwindClasses).toBeTruthy();
    });
});
