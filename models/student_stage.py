from odoo import fields, models


class SchoolStudentStage(models.Model):
    _name = "school.student.stage"
    _order = 'sequence'

    name = fields.Char()
    sequence = fields.Integer(string='Sequence', default=1)

