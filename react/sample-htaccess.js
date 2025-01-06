const fs = require('fs');
const path = require('path');

const source = path.join(__dirname, '.htaccess');
const destination = path.join(__dirname, 'build', '.htaccess');

fs.copyFile(source, destination, (err) => {
    if (err) {
        console.error('Failed to copy .htaccess file:', err);
    } else {
        console.log('.htaccess file copied to build directory');
    }
});
