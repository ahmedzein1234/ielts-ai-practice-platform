import { expect, test } from '@playwright/test';

test.describe('Component Testing Suite', () => {
    test.describe('UI Components', () => {
        test('should test Button component variants', async ({ page }) => {
            console.log('🔍 Testing Button component...');

            // Create a test page with all button variants
            await page.setContent(`
        <html>
          <head>
            <link rel="stylesheet" href="/_next/static/css/app/layout.css">
          </head>
          <body>
            <div class="p-8 space-y-4">
              <button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
                Default Button
              </button>
              <button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2">
                Outline Button
              </button>
              <button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-secondary text-secondary-foreground hover:bg-secondary/80 h-10 px-4 py-2">
                Secondary Button
              </button>
            </div>
          </body>
        </html>
      `);

            const buttons = await page.locator('button').all();
            console.log(`📊 Found ${buttons.length} buttons`);

            // Test button visibility and styling
            for (let i = 0; i < buttons.length; i++) {
                const button = buttons[i];
                await expect(button).toBeVisible();

                const computedStyle = await button.evaluate(el => {
                    const style = window.getComputedStyle(el);
                    return {
                        display: style.display,
                        visibility: style.visibility,
                        opacity: style.opacity,
                        backgroundColor: style.backgroundColor,
                        color: style.color,
                        borderRadius: style.borderRadius,
                        padding: style.padding
                    };
                });

                console.log(`🎨 Button ${i + 1} styles:`, computedStyle);

                // Basic style assertions
                expect(computedStyle.display).toBe('inline-flex');
                expect(computedStyle.visibility).toBe('visible');
                expect(parseFloat(computedStyle.opacity)).toBeGreaterThan(0);
            }
        });

        test('should test LoadingSpinner component', async ({ page }) => {
            console.log('🔍 Testing LoadingSpinner component...');

            await page.setContent(`
        <html>
          <head>
            <link rel="stylesheet" href="/_next/static/css/app/layout.css">
          </head>
          <body>
            <div class="flex flex-col items-center justify-center space-y-2">
              <div class="animate-spin rounded-full border-2 border-gray-300 border-t-blue-600 w-6 h-6"></div>
              <p class="text-sm text-muted-foreground animate-pulse">Loading...</p>
            </div>
          </body>
        </html>
      `);

            const spinner = page.locator('.animate-spin');
            const text = page.locator('p');

            await expect(spinner).toBeVisible();
            await expect(text).toBeVisible();

            const spinnerStyle = await spinner.evaluate(el => {
                const style = window.getComputedStyle(el);
                return {
                    animation: style.animation,
                    borderStyle: style.borderStyle,
                    borderRadius: style.borderRadius
                };
            });

            console.log('🎨 Spinner styles:', spinnerStyle);

            // Check animation is applied
            expect(spinnerStyle.animation).toContain('spin');
            expect(spinnerStyle.borderRadius).toBe('50%');
        });

        test('should test Card component', async ({ page }) => {
            console.log('🔍 Testing Card component...');

            await page.setContent(`
        <html>
          <head>
            <link rel="stylesheet" href="/_next/static/css/app/layout.css">
          </head>
          <body>
            <div class="rounded-lg border bg-card text-card-foreground shadow-sm">
              <div class="flex flex-col space-y-1.5 p-6">
                <h3 class="text-2xl font-semibold leading-none tracking-tight">Card Title</h3>
                <p class="text-sm text-muted-foreground">Card description</p>
              </div>
              <div class="p-6 pt-0">
                <p>Card content goes here</p>
              </div>
            </div>
          </body>
        </html>
      `);

            const card = page.locator('.rounded-lg.border');
            const title = page.locator('h3');
            const description = page.locator('p');

            await expect(card).toBeVisible();
            await expect(title).toBeVisible();
            await expect(description).toBeVisible();

            const cardStyle = await card.evaluate(el => {
                const style = window.getComputedStyle(el);
                return {
                    borderRadius: style.borderRadius,
                    borderStyle: style.borderStyle,
                    backgroundColor: style.backgroundColor,
                    boxShadow: style.boxShadow
                };
            });

            console.log('🎨 Card styles:', cardStyle);

            // Check card styling
            expect(cardStyle.borderRadius).toBe('8px');
            expect(cardStyle.borderStyle).toBe('solid');
        });
    });

    test.describe('Form Components', () => {
        test('should test Input component', async ({ page }) => {
            console.log('🔍 Testing Input component...');

            await page.setContent(`
        <html>
          <head>
            <link rel="stylesheet" href="/_next/static/css/app/layout.css">
          </head>
          <body>
            <div class="space-y-4 p-8">
              <div>
                <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70" for="email">Email</label>
                <input class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" id="email" type="email" placeholder="Enter your email">
              </div>
              <div>
                <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70" for="password">Password</label>
                <input class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" id="password" type="password" placeholder="Enter your password">
              </div>
            </div>
          </body>
        </html>
      `);

            const inputs = await page.locator('input').all();
            const labels = await page.locator('label').all();

            console.log(`📊 Found ${inputs.length} inputs and ${labels.length} labels`);

            // Test input functionality
            for (let i = 0; i < inputs.length; i++) {
                const input = inputs[i];
                const label = labels[i];

                await expect(input).toBeVisible();
                await expect(label).toBeVisible();

                // Test input interaction
                await input.click();
                await input.fill('test value');

                const value = await input.inputValue();
                expect(value).toBe('test value');

                // Test focus styles
                await input.focus();
                const focusedStyle = await input.evaluate(el => {
                    const style = window.getComputedStyle(el);
                    return {
                        outline: style.outline,
                        borderColor: style.borderColor
                    };
                });

                console.log(`🎨 Input ${i + 1} focused styles:`, focusedStyle);
            }
        });

        test('should test Select component', async ({ page }) => {
            console.log('🔍 Testing Select component...');

            await page.setContent(`
        <html>
          <head>
            <link rel="stylesheet" href="/_next/static/css/app/layout.css">
          </head>
          <body>
            <div class="p-8">
              <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70" for="test-select">Test Select</label>
              <select class="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50" id="test-select">
                <option value="">Select an option</option>
                <option value="option1">Option 1</option>
                <option value="option2">Option 2</option>
                <option value="option3">Option 3</option>
              </select>
            </div>
          </body>
        </html>
      `);

            const select = page.locator('select');
            const label = page.locator('label');

            await expect(select).toBeVisible();
            await expect(label).toBeVisible();

            // Test select functionality
            await select.selectOption('option2');
            const selectedValue = await select.inputValue();
            expect(selectedValue).toBe('option2');

            // Test all options are present
            const options = await select.locator('option').all();
            expect(options.length).toBe(4);
        });
    });

    test.describe('Layout Components', () => {
        test('should test responsive layout', async ({ page }) => {
            console.log('🔍 Testing responsive layout...');

            const viewports = [
                { width: 375, height: 667, name: 'Mobile' },
                { width: 768, height: 1024, name: 'Tablet' },
                { width: 1920, height: 1080, name: 'Desktop' }
            ];

            for (const viewport of viewports) {
                console.log(`📱 Testing ${viewport.name} layout...`);

                await page.setViewportSize(viewport);
                await page.setContent(`
          <html>
            <head>
              <link rel="stylesheet" href="/_next/static/css/app/layout.css">
            </head>
            <body>
              <div class="container mx-auto px-4">
                <header class="py-6">
                  <nav class="flex items-center justify-between">
                    <div class="text-xl font-bold">Logo</div>
                    <div class="hidden md:flex space-x-4">
                      <a href="#" class="hover:text-primary">Home</a>
                      <a href="#" class="hover:text-primary">About</a>
                      <a href="#" class="hover:text-primary">Contact</a>
                    </div>
                    <button class="md:hidden">Menu</button>
                  </nav>
                </header>
                <main class="py-8">
                  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <div class="p-6 border rounded-lg">Card 1</div>
                    <div class="p-6 border rounded-lg">Card 2</div>
                    <div class="p-6 border rounded-lg">Card 3</div>
                  </div>
                </main>
              </div>
            </body>
          </html>
        `);

                const layoutCheck = await page.evaluate(() => {
                    const body = document.body;
                    const computedStyle = window.getComputedStyle(body);

                    return {
                        hasContent: body.textContent?.trim().length > 0,
                        isVisible: computedStyle.display !== 'none',
                        hasOverflow: body.scrollHeight > body.clientHeight,
                        hasHorizontalScroll: body.scrollWidth > body.clientWidth,
                        containerWidth: document.querySelector('.container')?.clientWidth || 0
                    };
                });

                console.log(`📊 ${viewport.name} layout check:`, layoutCheck);

                expect(layoutCheck.hasContent).toBeTruthy();
                expect(layoutCheck.isVisible).toBeTruthy();

                // Check responsive behavior
                if (viewport.name === 'Mobile') {
                    expect(layoutCheck.hasHorizontalScroll).toBeFalsy();
                }
            }
        });

        test('should test grid system', async ({ page }) => {
            console.log('🔍 Testing grid system...');

            await page.setContent(`
        <html>
          <head>
            <link rel="stylesheet" href="/_next/static/css/app/layout.css">
          </head>
          <body>
            <div class="container mx-auto p-8">
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div class="bg-blue-100 p-4 rounded">Item 1</div>
                <div class="bg-green-100 p-4 rounded">Item 2</div>
                <div class="bg-red-100 p-4 rounded">Item 3</div>
                <div class="bg-yellow-100 p-4 rounded">Item 4</div>
                <div class="bg-purple-100 p-4 rounded">Item 5</div>
                <div class="bg-pink-100 p-4 rounded">Item 6</div>
              </div>
            </div>
          </body>
        </html>
      `);

            const gridItems = await page.locator('.grid > div').all();
            expect(gridItems.length).toBe(6);

            // Test grid responsiveness
            const viewports = [
                { width: 375, height: 667, name: 'Mobile' },
                { width: 768, height: 1024, name: 'Tablet' },
                { width: 1920, height: 1080, name: 'Desktop' }
            ];

            for (const viewport of viewports) {
                await page.setViewportSize(viewport);

                const gridLayout = await page.evaluate(() => {
                    const grid = document.querySelector('.grid');
                    if (!grid) return null;

                    const computedStyle = window.getComputedStyle(grid);
                    return {
                        display: computedStyle.display,
                        gridTemplateColumns: computedStyle.gridTemplateColumns,
                        gap: computedStyle.gap
                    };
                });

                console.log(`📊 ${viewport.name} grid layout:`, gridLayout);

                expect(gridLayout?.display).toBe('grid');
                expect(gridLayout?.gap).toBe('16px');
            }
        });
    });

    test.describe('Interactive Components', () => {
        test('should test hover and focus states', async ({ page }) => {
            console.log('🔍 Testing hover and focus states...');

            await page.setContent(`
        <html>
          <head>
            <link rel="stylesheet" href="/_next/static/css/app/layout.css">
          </head>
          <body>
            <div class="p-8 space-y-4">
              <button class="bg-blue-500 hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 text-white px-4 py-2 rounded">
                Interactive Button
              </button>
              <a href="#" class="text-blue-500 hover:text-blue-600 hover:underline focus:ring-2 focus:ring-blue-500">
                Interactive Link
              </a>
              <input class="border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 px-3 py-2 rounded" placeholder="Interactive Input">
            </div>
          </body>
        </html>
      `);

            const button = page.locator('button');
            const link = page.locator('a');
            const input = page.locator('input');

            // Test hover states
            await button.hover();
            const buttonHoverStyle = await button.evaluate(el => {
                const style = window.getComputedStyle(el);
                return {
                    backgroundColor: style.backgroundColor
                };
            });

            console.log('🎨 Button hover style:', buttonHoverStyle);

            // Test focus states
            await input.focus();
            const inputFocusStyle = await input.evaluate(el => {
                const style = window.getComputedStyle(el);
                return {
                    borderColor: style.borderColor,
                    outline: style.outline
                };
            });

            console.log('🎨 Input focus style:', inputFocusStyle);

            // Test link hover
            await link.hover();
            const linkHoverStyle = await link.evaluate(el => {
                const style = window.getComputedStyle(el);
                return {
                    color: style.color,
                    textDecoration: style.textDecoration
                };
            });

            console.log('🎨 Link hover style:', linkHoverStyle);
        });

        test('should test animation components', async ({ page }) => {
            console.log('🔍 Testing animation components...');

            await page.setContent(`
        <html>
          <head>
            <link rel="stylesheet" href="/_next/static/css/app/layout.css">
          </head>
          <body>
            <div class="p-8 space-y-4">
              <div class="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
              <div class="animate-pulse bg-blue-500 w-8 h-8 rounded"></div>
              <div class="animate-bounce bg-green-500 w-8 h-8 rounded"></div>
              <div class="animate-ping bg-red-500 w-8 h-8 rounded-full"></div>
            </div>
          </body>
        </html>
      `);

            const animations = await page.locator('[class*="animate-"]').all();
            expect(animations.length).toBe(4);

            for (let i = 0; i < animations.length; i++) {
                const animation = animations[i];
                await expect(animation).toBeVisible();

                const animationStyle = await animation.evaluate(el => {
                    const style = window.getComputedStyle(el);
                    return {
                        animation: style.animation,
                        animationDuration: style.animationDuration,
                        animationIterationCount: style.animationIterationCount
                    };
                });

                console.log(`🎨 Animation ${i + 1} style:`, animationStyle);

                // Check that animation is applied
                expect(animationStyle.animation).toBeTruthy();
                expect(animationStyle.animationDuration).toBeTruthy();
            }
        });
    });
});
