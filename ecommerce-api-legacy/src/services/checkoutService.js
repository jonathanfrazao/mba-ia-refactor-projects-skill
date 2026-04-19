const courseModel = require('../models/courseModel');
const userModel = require('../models/userModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const auditModel = require('../models/auditModel');
const logger = require('../middlewares/logger');

async function processCheckout({ userName, email, password, courseId, cardNumber }) {
    const course = await courseModel.findActiveById(courseId);
    if (!course) throw new Error('Curso não encontrado');

    // Stub: replace with real payment gateway integration using settings.paymentGatewayKey
    const status = cardNumber.startsWith('4') ? 'PAID' : 'DENIED';
    if (status === 'DENIED') throw new Error('Pagamento recusado');

    let user = await userModel.findByEmail(email);
    const userId = user
        ? user.id
        : await userModel.create(userName, email, password || '123456');

    const enrollmentId = await enrollmentModel.create(userId, courseId);
    await paymentModel.create(enrollmentId, course.price, status);
    await auditModel.log(`Checkout curso ${courseId} por ${userId}`);

    logger.info({ courseId, userId, enrollmentId }, 'Checkout completed');
    return { enrollmentId };
}

module.exports = { processCheckout };
