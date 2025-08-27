import { expect, test } from '@playwright/test';

test.describe('IELTS AI Platform Homepage', () => {
    test('should load homepage without white page', async ({ page }) => {
        // Navigate to the homepage
        await page.goto('/');

        // Wait for the page to load completely
        await page.waitForLoadState('networkidle');

        // Check if the page has content (not white)
        const bodyText = await page.textContent('body');
        expect(bodyText).toBeTruthy();

        // Check for specific elements that should be present
        await expect(page.locator('h1')).toBeVisible();
        await expect(page.locator('text=Master IELTS with')).toBeVisible();

        // Check for navigation elements
        await expect(page.locator('text=Sign In')).toBeVisible();
        await expect(page.locator('text=Get Started')).toBeVisible();
    });

    test('should display all main sections', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Check for hero section
        await expect(page.locator('text=AI-Powered IELTS Preparation')).toBeVisible();

        // Check for features section
        await expect(page.locator('text=Complete IELTS Preparation')).toBeVisible();
        await expect(page.locator('text=Speaking')).toBeVisible();
        await expect(page.locator('text=Writing')).toBeVisible();
        await expect(page.locator('text=Listening')).toBeVisible();
        await expect(page.locator('text=Reading')).toBeVisible();

        // Check for testimonials
        await expect(page.locator('text=What Our Students Say')).toBeVisible();

        // Check for CTA section
        await expect(page.locator('text=Ready to Ace Your IELTS?')).toBeVisible();
    });

    test('should handle navigation correctly', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Test navigation links
        const signInLink = page.locator('a[href="/login"]');
        const getStartedLink = page.locator('a[href="/register"]');

        await expect(signInLink).toBeVisible();
        await expect(getStartedLink).toBeVisible();

        // Test that links are clickable
        await expect(signInLink).toBeEnabled();
        await expect(getStartedLink).toBeEnabled();
    });

    test('should be responsive on mobile', async ({ page }) => {
        // Set mobile viewport
        await page.setViewportSize({ width: 375, height: 667 });

        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Check that content is still visible on mobile
        await expect(page.locator('h1')).toBeVisible();
        await expect(page.locator('text=Master IELTS with')).toBeVisible();
    });

    test('should not have JavaScript errors', async ({ page }) => {
        const consoleErrors: string[] = [];

        page.on('console', msg => {
            if (msg.type() === 'error') {
                consoleErrors.push(msg.text());
            }
        });

        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Wait a bit more for any delayed errors
        await page.waitForTimeout(2000);

        // Check for console errors
        expect(consoleErrors).toHaveLength(0);
    });

    test('should load all images and assets', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Check for failed image loads
        const failedRequests: string[] = [];

        page.on('response', response => {
            if (response.status() >= 400 && response.url().includes('localhost')) {
                failedRequests.push(response.url());
            }
        });

        await page.waitForTimeout(3000);

        // Should not have failed requests
        expect(failedRequests).toHaveLength(0);
    });

    test('should have proper meta tags', async ({ page }) => {
        await page.goto('/');

        // Check for important meta tags
        const title = await page.title();
        expect(title).toContain('IELTS AI');

        // Check for viewport meta tag
        const viewport = await page.locator('meta[name="viewport"]');
        await expect(viewport).toBeVisible();
    });

    test('should handle animations without breaking', async ({ page }) => {
        await page.goto('/');
        await page.waitForLoadState('networkidle');

        // Wait for animations to complete
        await page.waitForTimeout(5000);

        // Check that page is still functional after animations
        await expect(page.locator('h1')).toBeVisible();
        await expect(page.locator('text=Start Free Trial')).toBeVisible();
    });
});

