import { test, expect } from '@playwright/test';

const testUserName = 'ihris';
const testPassword = 'admin';

export default function Login() {
    test.describe('Login', () => {
        test('shows validation only after submit', async ({ page }) => {
            await page.goto('/#/auth/login');
            const errorMsg = page.locator('.text-pink-800');
            // No error initially
            await expect(errorMsg).toBeHidden();
            // Submit with empty fields
            await page.getByTestId('submit').click();
            // Now error appears
            await expect(errorMsg).toBeVisible();
            // Inputs should be marked invalid (PrimeVue adds p-invalid class)
            await expect(page.locator('#username')).toHaveClass(/p-invalid/);
            // Password input is inside component; select the real input
            await expect(page.locator('input[type="password"]')).toHaveClass(/p-invalid/);
        });

        test('invalid credentials shows 401 message', async ({ page }) => {
            await page.goto('/#/auth/login');

            await page.fill('#username', 'wrong');
            await page.locator('input[type="password"]').fill('wrong');
            await page.getByTestId('submit').click();
            await expect(page.locator('.text-pink-800')).toBeVisible();

            // Should not store token
            const token = await page.evaluate(() => localStorage.getItem('_ihris_token'));
            expect(token).toBeNull();
        });

        test('successful login stores token and redirects', async ({ page }) => {
            await page.goto('/#/auth/login');

            await page.fill('#username', testUserName);

            // PrimeVue Password: the actual input is inside; this selector is robust:
            const pwd = page.locator('input[type="password"]');
            await pwd.fill(testPassword);

            await page.getByTestId('submit').click();

            // Your code does window.location='/' so URL should be home
            await expect(page).toHaveURL(/\/$/);

            // Check localStorage
            const token = await page.evaluate(() => localStorage.getItem('_ihris_token'));
            const isDefined = token !== null && token !== undefined;
            expect(isDefined).toBeTruthy();

            const uname = await page.evaluate(() => localStorage.getItem('_ihris_username'));
            expect(uname).toBe('ihris');
        });

    });

}