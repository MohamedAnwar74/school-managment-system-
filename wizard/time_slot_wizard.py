import base64
import io
import xlsxwriter
from odoo import models, fields, api, _


class SchoolTimeSlot(models.TransientModel):
    _name = 'school.time.slot.wizard'

    type = fields.Selection([
        ('xls', 'XLS'),
        ('pdf', 'PDF')
    ], string="Report Type", default="xls", required=True)

    timeSlot_ids = fields.Many2many('school.time.slot')
    excel_sheet = fields.Binary('Download Report')
    excel_sheet_name = fields.Char(string='Name', size=64)

    def get_report_data(self):
        data = []
        for line in self.timeSlot_ids:
            data.append({
                'name': line.name,
                'start_date': line.start_time,
                'end_date': line.end_time,
                'room': line.room_id.room_name,
                'course': line.course_id.name,
                'teacher': line.teacher_id.name,
            })
        return data

    def print_timeslot_excel(self):
        data = self.get_report_data()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('TimeSlots Report')

        bold = workbook.add_format(
            {'bold': False, 'align': 'center', 'border': 1})
        boldx = workbook.add_format(
            {'bold': False, 'num_format': '0.00', 'align': 'center', 'border': 0})
        bold2 = workbook.add_format(
            {'bold': False, 'align': 'center', 'border': 1})
        format3 = workbook.add_format({'font_name': 'Calibri',
                                       'border': 1,
                                       'font_size': 13,
                                       'align': 'center',
                                       'valign': 'vcenter',
                                       'font_color': 'black',
                                       'bg_color': '#ABAFB1', })
        format4 = workbook.add_format({'font_name': 'Calibri',
                                       'border': 1,
                                       'font_size': 13,
                                       'align': 'center',
                                       'valign': 'vcenter',
                                       'font_color': 'black',
                                       'bg_color': '#E9ECEF', })

        row = 0
        col = 0
        worksheet.merge_range(row, col, row + 1, col + 20, "TimeSlots Report", format3)
        row += 1
        col = 0
        worksheet.merge_range(row + 1, col, row + 2, col + 3, 'TimeSlot Name', format3)
        worksheet.merge_range(row + 1, col + 4, row + 2, col + 7, 'Start Time', format3)
        worksheet.merge_range(row + 1, col + 8, row + 2, col + 11, 'End Time', format3)
        worksheet.merge_range(row + 1, col + 12, row + 2, col + 14, 'Room', format3)
        worksheet.merge_range(row + 1, col + 15, row + 2, col + 17, 'Course', format3)
        worksheet.merge_range(row + 1, col + 18, row + 2, col + 20, 'Teacher', format3)
        row += 1

        for line in data:
            worksheet.merge_range(row + 3, col, row + 3, col + 3, line['name'], bold2)
            worksheet.merge_range(row + 3, col + 4, row + 3, col + 7, line['start_date'].strftime('%Y-%m-%d %H:%M:%S'),
                                  bold2)
            worksheet.merge_range(row + 3, col + 8, row + 3, col + 11, line['end_date'].strftime('%Y-%m-%d %H:%M:%S'),
                                  bold2)
            worksheet.merge_range(row + 3, col + 12, row + 3, col + 14, line['room'], bold2)
            worksheet.merge_range(row + 3, col + 15, row + 3, col + 17, line['course'], bold2)
            worksheet.merge_range(row + 3, col + 18, row + 3, col + 20, line['teacher'], bold2)
            row += 1
        row += 3
        workbook.close()
        output.seek(0)
        self.excel_sheet = base64.encodebytes(output.read())

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/school.time.slot.wizard/{self.id}/excel_sheet/TimeSlot_Report.xlsx?download=true',
            'target': 'self',
        }

    def action_print_pdf(self):

        return {
            'type': 'ir.actions.report',
            'name': 'School Timeslots Reports',
            'model': 'school.time.slot',
            'report_type': 'qweb-pdf',
            'report_name': 'school.school_timeslot_template_view',
            'report_file': 'school.school_timeslot_template_view',
            'print_report_name': "School TimeSlots Reports",
            'context': {'active_ids': self.timeSlot_ids.ids}  # list of ids
        }

    def action_print_report(self):
        if self.type == 'pdf':
            return self.action_print_pdf()
        else:
            return self.print_timeslot_excel()
