import base64
import io
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import xlsxwriter


class TimeSlot(models.Model):
    _name = 'school.time.slot'
    _description = 'Time Slot'

    name = fields.Char(string='Time Slot', required=True)
    room_id = fields.Many2one('school.classroom', string='Room', required=True)
    course_id = fields.Many2one('school.courses', string='Course', required=True)
    teacher_id = fields.Many2one('school.teacher', string='Teacher', required=True)
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time', required=True)
    excel_sheet = fields.Binary('Download Report')
    excel_sheet_name = fields.Char(string='Name', size=64)

    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.course_id = False
            self.teacher_id = False
            print(self.room_id.course_ids)
            print(self.room_id.teacher_ids)
            return {
                'domain': {
                    'course_id': [('id', 'in', self.room_id.course_ids.ids)],
                    'teacher_id': [('id', 'in', self.room_id.teacher_ids.ids)]
                }
            }
        else:
            return {
                'domain': {
                    'course_id': [],
                    'teacher_id': [],
                }
            }
    # @api.onchange('room_id')
    # def _onchange_room_id(self):
    #     if self.room_id:
    #         # Get the courses and teachers associated with the selected room
    #         courses = self.room_id.course_ids.ids
    #         teachers = self.room_id.teacher_ids.ids
    #         return {
    #             'domain': {
    #                 'course_id': [('id', 'in', courses)],
    #                 'teacher_id': [('id', 'in', teachers)],
    #             }
    #         }

    # @api.constrains('teacher_id', 'course_id', 'start_time', 'end_time')
    # def check_time_slot(self):
    #     for record in self:
    #         conflict_slots = self.env['school.time.slot'].search([
    #             ('id', '!=', record.id),
    #             ('teacher_id', '=', record.teacher_id.id),
    #             ('course_id', '=', record.course_id.id),
    #             ('start_time', '<', record.end_time),
    #             ('end_time', '>', record.start_time)
    #         ])
    #         if conflict_slots:
    #             raise ValidationError('You cannot schedule the same course in the same room at overlapping times.')

    @api.constrains('teacher_id', 'start_time', 'end_time')
    def check_teacher(self):
        for record in self:
            conflict_slots = self.env['school.time.slot'].search([
                ('id', '!=', record.id),
                ('teacher_id', '=', record.teacher_id.id),
                ('start_time', '<', record.end_time),
                ('end_time', '>', record.start_time)
            ])
            if conflict_slots:
                raise ValidationError('This teacher is already assigned to another course at the selected time.')

    @api.constrains('room_id', 'start_time', 'end_time')
    def check_room(self):
        for record in self:
            conflict_slots = self.env['school.time.slot'].search([
                ('id', '!=', record.id),
                ('room_id', '=', record.room_id.id),
                ('start_time', '<', record.end_time),
                ('end_time', '>', record.start_time)
            ])
            if conflict_slots:
                raise ValidationError('The room is already booked for another course at this time..')

    @api.constrains('course_id', 'start_time', 'end_time')
    def check_course(self):
        for record in self:
            conflict_slots = self.env['school.time.slot'].search([
                ('id', '!=', record.id),
                ('course_id', '=', record.course_id.id),
                ('start_time', '<', record.end_time),
                ('end_time', '>', record.start_time)
            ])
            if conflict_slots:
                raise ValidationError('This course is already scheduled in another room at the selected time.')

