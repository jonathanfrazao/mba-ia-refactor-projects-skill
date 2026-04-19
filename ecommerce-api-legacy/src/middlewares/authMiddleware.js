const settings = require('../config/settings');

function requireAuth(req, res, next) {
    const authHeader = req.headers['authorization'];
    if (!authHeader || authHeader !== `Bearer ${settings.adminToken}`) {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    next();
}

module.exports = { requireAuth };
