const testUserName = 'ihris';
const testPassword = 'admin';

async function login(page) {
    await page.goto('/#/auth/login');

    await page.fill('#username', testUserName);

    // PrimeVue Password: the actual input is inside; this selector is robust:
    const pwd = page.locator('input[type="password"]');
    await pwd.fill(testPassword);

    await page.getByTestId('submit').click();
}

async function fillPassword(page, id, password) {
    const pwd = await page.getByTestId(id).locator('input[type="password"]');
    return pwd.fill(password);
}

function sleep(time:number) {
    return new Promise(resolve => setTimeout(resolve, time));
}

export { login, sleep, fillPassword };