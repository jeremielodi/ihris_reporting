const dotEnv = require('dotenv');
const express = require('express');
const path = require('path');

const app = express();
configureEnvironmentVariables();
const PORT = process.env.WEB_CLIENT_PORT || 3000;

// Serve static files from the Vue dist directory
app.use(express.static(path.join(__dirname, './dist')));

// Handle SPA - Redirect all other routes to index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, './dist', 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});

/**
 * @function configureEnvironmentVariables
 *
 * @description
 * Uses dotenv to add environmental variables from the .env.* file to the
 * process object.  If the NODE_ENV system variable is not set, the function
 * defaults to 'production'
 */
function configureEnvironmentVariables() {
    // if the process NODE_ENV is not set, default to production.
    process.env.NODE_ENV = process.env.NODE_ENV || 'development';
    // decode the file path for the environmental variables.
    const dotfile = path.resolve(__dirname, '.env');
    // load the environmental variables into process using the dotenv module
    dotEnv.config({ path: dotfile });
}
