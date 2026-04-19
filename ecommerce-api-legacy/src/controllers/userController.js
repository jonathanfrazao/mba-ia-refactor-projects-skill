const { deleteUser } = require('../services/userService');
const logger = require('../middlewares/logger');

async function removeUser(req, res) {
    const { id } = req.params;
    try {
        await deleteUser(id);
        res.json({ msg: 'Usuário e registros relacionados deletados.' });
    } catch (err) {
        logger.error({ err: err.message }, 'Delete user failed');
        res.status(500).json({ error: 'Internal Server Error' });
    }
}

module.exports = { removeUser };
