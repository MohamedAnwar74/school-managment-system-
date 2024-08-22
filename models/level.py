from odoo import models, fields,api


class SchoolLevel(models.Model):
    _name = "school.level"
    _description = "school.level"

    name = fields.Char(string="Level", required=True)
    course_ids = fields.One2many('school.courses', 'level_id', string='Courses')




