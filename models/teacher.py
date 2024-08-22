from odoo import models, fields,api


class SchoolTeacher(models.Model):
    _name = "school.teacher"
    _description = "school.teacher"

    name = fields.Char(string="Teacher Name", required=True)
    title = fields.Char("teacher title")

    course_id = fields.Many2one('school.courses')
    level_id = fields.Many2one('school.level')
    # student_ids = fields.One2many('school.student', 'teacher_id', string="Students")

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = ['|', ('name', operator, name), ('title', operator, name)]
        return self._search(domain, limit=limit, access_rights_uid=name_get_uid)
