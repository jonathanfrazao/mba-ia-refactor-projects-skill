const pino = require('pino');
const settings = require('../config/settings');

module.exports = pino({ level: settings.logLevel });
