from odoo import fields, models


class SchoolSkills(models.Model):
    _name = "school.skills"
    _description = "school.skills"

    name = fields.Char()
    Reference_record = fields.Reference([('school.student', 'student'), ('school.courses', 'courses')]
                                        , String="Record")

    course_ids = fields.Many2many('school.courses')


