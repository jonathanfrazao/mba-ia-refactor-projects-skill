const { all } = require('../database');

async function getFinancialReport() {
    const rows = await all(`
        SELECT
            c.id   AS course_id,
            c.title,
            u.name AS student_name,
            p.amount,
            p.status
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u ON u.id = e.user_id
        LEFT JOIN payments p ON p.enrollment_id = e.id
        ORDER BY c.id
    `);

    const coursesMap = {};
    for (const row of rows) {
        if (!coursesMap[row.course_id]) {
            coursesMap[row.course_id] = { course: row.title, revenue: 0, students: [] };
        }
        if (row.student_name) {
            if (row.status === 'PAID') {
                coursesMap[row.course_id].revenue += row.amount || 0;
            }
            coursesMap[row.course_id].students.push({
                student: row.student_name,
                paid: row.amount || 0,
            });
        }
    }

    return Object.values(coursesMap);
}

module.exports = { getFinancialReport };
