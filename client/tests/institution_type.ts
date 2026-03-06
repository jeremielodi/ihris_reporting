import { test, expect } from '@playwright/test';
import data from '../../tests/mock/institution_type.json';
import { login, sleep } from './helpers';

export default function contactType() {
    test.describe('institution_type', () => {
        test('invalid empty form shows invalid message', async ({ page }) => {
            await login(page);
            await page.getByTestId('manage').click();
            await page.goto('/#/manage/institution_type_registry');
            await page.getByTestId('addButton').click();
            await page.getByTestId('submitButton').click();

            await expect(page.locator('#name')).toHaveClass(/p-invalid/);
            await expect(page.locator('.p-toast-message-error')).toBeVisible();
        });

        test('shows validation only after submit', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/institution_type_registry');
            await page.getByTestId('addButton').click();

            await page.fill('#name', data.institution_type.name);
            await page.fill('#code', data.institution_type.code);
            await page.getByTestId('submitButton').click();
            await sleep(1000);

            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });

        test('shows edit institution_type', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/institution_type_registry');
            await sleep(2000);

            await page.getByTestId('institutionTypeAction1').click();
            await page.getByText('Editer').click();

            await sleep(1000);

            await page.fill('#code', data.institution_type_update.code);
            await page.getByTestId('submitButton').click();

            await sleep(1000);
            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });
    });
}
