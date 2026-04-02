import { test, expect } from '@playwright/test';
import data from '../../tests/mock/grade.json';
import { login, sleep } from './helpers';

export default function grade() {
    test.describe('grade', () => {
        test('invalid empty form shows invalid message', async ({ page }) => {
            await login(page);
            await page.getByTestId('manage').click();
            await page.goto('/#/manage/grade_registry');
            await page.getByTestId('addButton').click();
            await page.getByTestId('submitButton').click();

            await expect(page.locator('#name')).toHaveClass(/p-invalid/);
            await expect(page.locator('.p-toast-message-error')).toBeVisible();
        });

        test('shows validation only after submit', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/grade_registry');
            await page.getByTestId('addButton').click();

            await page.fill('#name', data.grade.name);

            await page.getByTestId('submitButton').click();
            await sleep(1000);

            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });

        test('shows edit grade', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/grade_registry');
            await sleep(2000);

            await page.getByTestId('gradeAction1').click();
            await page.getByText('Editer').click();

            await sleep(1000);

            await page.fill('#name', data.grade_update.name);
            await page.getByTestId('submitButton').click();

            await sleep(1000);
            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });

        test('should import grades', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/grade_registry');
            await sleep(2000);

            await page.getByTestId('importButton').click();

            let fileContent = 'name\n';
            fileContent += data.grades_bulk.map((cls) => `${cls.name}`).join('\n');

            const filePath = 'temp_grade_import.csv';

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
