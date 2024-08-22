from odoo import models, fields, api


class SchoolClassroom(models.Model):
    _name = 'school.classroom'
    _rec_name = "room_name"

    room_name = fields.Char(string="Room")
    capacity = fields.Integer()

    level_ids = fields.Many2many('school.level')
    course_ids = fields.Many2many('school.courses')
    teacher_ids = fields.Many2many('school.teacher')
    time_slot_ids = fields.One2many('school.time.slot', 'room_id', string='Time Slots')

    @api.onchange('level_ids')
    def _onchange_level_ids(self):
        if self.level_ids:
            self.course_ids = self.env['school.courses'].search([('level_id', 'in', self.level_ids.ids
                                                                )])
            self.teacher_ids = self.env['school.teacher'].search([('level_id', 'in', self.level_ids.ids
                                                                   )])
        else:
            self.course_ids = False
            self.teacher_ids = False
