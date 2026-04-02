import { test, expect } from '@playwright/test';
import data from '../../tests/mock/user.json';
import { login, sleep, fillPassword } from './helpers';

export default function user() {
    test.describe('user', () => {
        test('invalid empty form shows invalid message', async ({ page }) => {
            await login(page);
            await page.getByTestId('manage').click();
            await page.goto('/#/manage/user_registry');
            await page.getByTestId('addButton').click();
            await page.getByTestId('submitButton').click();

            await expect(page.locator('#firstname')).toHaveClass(/p-invalid/);
            await expect(page.locator('.p-toast-message-error')).toBeVisible();
        });

        test('shows validation only after submit', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/user_registry');
            await page.getByTestId('addButton').click();

            await page.fill('#firstname', data.user_create.firstname);
            await page.fill('#lastname', data.user_create.lastname);
            await page.fill('#email', data.user_create.email);
            await page.fill('#username', data.user_create.username);
            await fillPassword(page, 'password', data.user_create.password);
            await page.getByTestId('accessLevel').click();
            await sleep(1000);
            // await page.getByText('DR Congo').click();
            await page.getByTestId('selectButton').click();
            await sleep(1500);
            await page.getByTestId('submitButton').click();
            await sleep(1000);
            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });

        test('shows edit user', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/user_registry');
            await sleep(2000);

            await page.getByTestId('userAction2').click();
            await page.getByText('Editer').click();

            await sleep(1000);

            await page.fill('#firstname', data.user_update.firstname);
            await page.getByTestId('submitButton').click();

            await sleep(1000);
            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });

        test('assign role', async ({ page }) => {
            await login(page);
            await sleep(1000);

            await page.goto('/#/manage/user_registry');
            await sleep(2000);

            await page.getByTestId('userAction2').click();
            await page.getByText('Rôles').click();
            await sleep(1000);
            await page.getByText('Super user').click();

            await page.getByTestId('submitButton').click();

            await sleep(1000);
            await expect(page.locator('.p-toast-message-success')).toBeVisible();
        });
    });
}
