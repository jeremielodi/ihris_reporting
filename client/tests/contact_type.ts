import { test, expect } from '@playwright/test';
import data from '../../tests/mock/contact_type.json';
import { login, sleep } from './helpers';

export default function contactType() {
    test.describe('contact_type', () => {
        test('invalid empty form shows invalid message', async ({ page }) => {
            await login(page);
            await page.getByTestId('manage').click();
            await page.goto('/#/manage/contact_type_registry');
            await page.getByTestId('addButton').click();
            await page.getByTestId('submitButton').click();

            await expect(page.locator('#name')).toHaveClass(/p-invalid/);
            await expect(page.locator('.p-toast-message-error')).toBeVisible();
        });

        test('shows validation only after submit', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/contact_type_registry');
            await page.getByTestId('addButton').click();

            await page.fill('#name', data.contact_type.name);
            await page.fill('#code', data.contact_type.code);
            await page.getByTestId('submitButton').click();
            await sleep(1000);

            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });

        test('shows edit contact_type', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/contact_type_registry');
            await sleep(2000);

            await page.getByTestId('contactTypeAction1').click();
            await page.getByText('Editer').click();

            await sleep(1000);

            await page.fill('#name', data.contact_type_update.name);
            await page.getByTestId('submitButton').click();

            await sleep(1000);
            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });
    });
}
