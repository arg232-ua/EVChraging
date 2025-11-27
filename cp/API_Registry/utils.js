const crypto = require('crypto');

function generarCredencial() {
    return crypto.randomBytes(24).toString('hex'); 
}

module.exports = { generarCredencial };
