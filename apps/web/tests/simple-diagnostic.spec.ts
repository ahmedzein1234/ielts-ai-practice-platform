import { expect, test } from '@playwright/test';

test.describe('Simple Frontend Diagnostic', () => {
    test('should check basic page loading', async ({ page }) => {
        console.log('🔍 Starting simple diagnostic...');

        // Navigate to the homepage
        await page.goto('/');
        console.log('✅ Navigated to homepage');

        // Wait for the page to load
        await page.waitForLoadState('domcontentloaded');
        console.log('✅ DOM content loaded');

        // Get the page title
        const title = await page.title();
        console.log('📄 Page title:', title);

        // Get the page URL
        const url = page.url();
        console.log('🔗 Page URL:', url);

        // Check if the page has any content
        const bodyText = await page.textContent('body');
        console.log('📝 Body text length:', bodyText?.length || 0);
        console.log('📝 Body text preview:', bodyText?.substring(0, 200));

        // Check for basic HTML structure
        const htmlStructure = await page.evaluate(() => {
            return {
                hasHtml: !!document.documentElement,
                hasHead: !!document.head,
                hasBody: !!document.body,
                bodyChildren: document.body.children.length,
                bodyInnerHTML: document.body.innerHTML.substring(0, 500),
                bodyClassName: document.body.className,
                bodyStyle: window.getComputedStyle(document.body).backgroundColor
            };
        });

        console.log('🏗️ HTML structure:', htmlStructure);

        // Take a screenshot
        await page.screenshot({ path: 'simple-diagnostic.png', fullPage: true });
        console.log('📸 Screenshot saved as simple-diagnostic.png');

        // Basic assertions
        expect(title).toBeTruthy();
        expect(bodyText).toBeTruthy();
        expect(htmlStructure.hasBody).toBeTruthy();
    });

    test('should check for React and Next.js', async ({ page }) => {
        console.log('🔍 Checking for React and Next.js...');

        await page.goto('/');
        await page.waitForLoadState('domcontentloaded');

        const reactCheck = await page.evaluate(() => {
            return {
                hasReact: typeof window !== 'undefined' && window.React,
                hasNextData: !!document.getElementById('__NEXT_DATA__'),
                hasNextRoot: !!document.getElementById('__next'),
                scripts: Array.from(document.querySelectorAll('script')).map(s => s.src || 'inline'),
                stylesheets: Array.from(document.querySelectorAll('link[rel="stylesheet"]')).map(l => l.href)
            };
        });

        console.log('⚛️ React check:', reactCheck);

        // Check for console errors
        const consoleErrors: string[] = [];
        page.on('console', msg => {
            if (msg.type() === 'error') {
                consoleErrors.push(msg.text());
            }
        });

        await page.waitForTimeout(3000);
        console.log('❌ Console errors:', consoleErrors);
    });

    test('should check CSS loading', async ({ page }) => {
        console.log('🔍 Checking CSS loading...');

        await page.goto('/');
        await page.waitForLoadState('domcontentloaded');

        const cssCheck = await page.evaluate(() => {
            const body = document.body;
            const computedStyle = window.getComputedStyle(body);

            return {
                backgroundColor: computedStyle.backgroundColor,
                color: computedStyle.color,
                fontFamily: computedStyle.fontFamily,
                fontSize: computedStyle.fontSize,
                hasTailwindClasses: body.className.includes('bg-') || body.innerHTML.includes('bg-'),
                cssVariables: {
                    background: getComputedStyle(body).getPropertyValue('--background'),
                    foreground: getComputedStyle(body).getPropertyValue('--foreground'),
                    primary: getComputedStyle(body).getPropertyValue('--primary')
                }
            };
        });

        console.log('🎨 CSS check:', cssCheck);
    });
});
