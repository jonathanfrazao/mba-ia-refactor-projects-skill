const logger = require('./logger');

function errorHandler(err, req, res, next) {
    logger.error({ err: err.message, stack: err.stack }, 'Unhandled error');
    res.status(500).json({ error: 'Internal Server Error' });
}

module.exports = { errorHandler };
