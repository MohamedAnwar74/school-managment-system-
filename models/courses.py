from odoo import fields, models


class SchoolCourses(models.Model):
    _name = "school.courses"
    _description = "school.courses"

    name = fields.Char('Course Name')
    is_open = fields.Boolean()
    # start_date = fields.Date()
    # End_date = fields.Date()
    student_ids = fields.Many2many("school.student")
    teacher_id = fields.Many2one('school.teacher', string="Teachers")
    required_skills = fields.Many2many('school.skills')
    level_id = fields.Many2one('school.level', string='Level')
    time_slot_ids = fields.One2many('school.time.slot', 'course_id', string='Time Slots')

    def crate_course(self):
        course = self.env['school.courses'].create({
            # name of course
            'name': 'new Course 1',
            'is_open': True
        })
        for a in range(4):
            course.student_ids = [(0, 0, {
                # name of student
                'name': 'New Student ' + str(a)
            })]

    def remove_x2many(self):
        to_remove = []
        students = self.student_ids.filtered(lambda x: x.state == 'rejected')
        for a in students:
            to_remove.append((2, a.id))
        self.write({'student_ids': to_remove})
