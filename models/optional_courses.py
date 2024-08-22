from odoo import models, fields


class SchoolOptionalCourses(models.Model):
    _name = 'school.courses.optional'
    _inherits = {'school.courses': 'course_id'}

    course_id = fields.Many2one('school.courses')
    code = fields.Char("Course Code")
