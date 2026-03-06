import { test, expect } from '@playwright/test';
import data from '../../tests/mock/classification.json';
import { login, sleep } from './helpers';

export default function Classification() {
    test.describe('Classification', () => {
        test('invalid empty form shows invalid message', async ({ page }) => {
            await login(page);
            await page.getByTestId('manage').click();
            await page.goto('/#/manage/classification_registry');
            await page.getByTestId('addButton').click();
            await page.getByTestId('submitButton').click();

            await expect(page.locator('#name')).toHaveClass(/p-invalid/);
            await expect(page.locator('.p-toast-message-error')).toBeVisible();
        });

        test('shows validation only after submit', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/classification_registry');
            await page.getByTestId('addButton').click();

            await page.fill('#name', data.classification.name);
            await page.fill('#code', data.classification.code);
            await page.fill('#description', data.classification.description);

            await page.getByTestId('submitButton').click();
            await sleep(1000);

            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });

        test('shows edit classification', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/classification_registry');
            await sleep(2000);

            await page.getByTestId('classifAction1').click();
            await page.getByText('Editer').click();

            await sleep(1000);

            await page.fill('#description', data.classification_update.description);
            await page.getByTestId('submitButton').click();

            await sleep(1000);
            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });

        test('should import classifications', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/classification_registry');
            await sleep(2000);

            await page.getByTestId('importButton').click();

            let fileContent = 'code,name,description\n';
            fileContent += data.classification_bulk.map((cls) => `${cls.code},${cls.name},${cls.description}`).join('\n');

            const filePath = 'temp_classification_import.csv';

            await page.setInputFiles('input[type="file"]', {
                name: filePath,
                mimeType: 'text/csv',
                buffer: Buffer.from(fileContent)
            });

            await page.getByTestId('submitImportButton').click();
            await sleep(1000);

            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });
    });
}
