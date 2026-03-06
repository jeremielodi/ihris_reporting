import { test, expect } from '@playwright/test';
import data from '../../tests/mock/job_type.json';
import { login, sleep } from './helpers';

export default function jobType() {
    test.describe('job_type', () => {
        test('invalid empty form shows invalid message', async ({ page }) => {
            await login(page);
            await page.getByTestId('manage').click();
            await page.goto('/#/manage/job_type_registry');
            await page.getByTestId('addButton').click();
            await page.getByTestId('submitButton').click();

            await expect(page.locator('#name')).toHaveClass(/p-invalid/);
            await expect(page.locator('.p-toast-message-error')).toBeVisible();
        });

        test('shows validation only after submit', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/job_type_registry');
            await page.getByTestId('addButton').click();

            await page.fill('#name', data.job_type.name);
            await page.fill('#code', data.job_type.code);
            await page.fill('#description', data.job_type.description);

            await page.getByTestId('submitButton').click();
            await sleep(1000);

            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });

        test('shows edit job_type', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/job_type_registry');
            await sleep(2000);

            await page.getByTestId('jobTypeAction1').click();
            await page.getByText('Editer').click();

            await sleep(1000);

            await page.fill('#description', data.job_type_update.description);
            await page.getByTestId('submitButton').click();

            await sleep(1000);
            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });

        test('should import job_types', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/job_type_registry');
            await sleep(2000);

            await page.getByTestId('importButton').click();

            let fileContent = 'code,name,description\n';
            fileContent += data.job_type_bulk.map((cls) => `${cls.code},${cls.name},${cls.description}`).join('\n');

            const filePath = 'temp_job_type_import.csv';
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
