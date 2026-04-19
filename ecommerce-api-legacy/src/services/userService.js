const { run, all } = require('../database');
const userModel = require('../models/userModel');
const logger = require('../middlewares/logger');

async function deleteUser(id) {
    const enrollments = await all('SELECT id FROM enrollments WHERE user_id = ?', [id]);
    for (const enr of enrollments) {
        await run('DELETE FROM payments WHERE enrollment_id = ?', [enr.id]);
    }
    await run('DELETE FROM enrollments WHERE user_id = ?', [id]);
    const result = await userModel.remove(id);
    logger.info({ userId: id }, 'User and related records deleted');
    return result;
}

module.exports = { deleteUser };
