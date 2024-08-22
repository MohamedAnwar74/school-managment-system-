import base64
import io
import xlsxwriter
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class StudentReportWizard(models.TransientModel):
    _name = 'student.report.wizard'

    student_ids = fields.Many2many('school.student')
    type = fields.Selection([
        ('xls', 'XLS'),
        ('pdf', 'PDF')
    ], string="Report Type", default="xls", required=True)
    excel_sheet = fields.Binary('Download Report')
    excel_sheet_name = fields.Char(string='Name', size=64)
    pdf_report = fields.Binary('Download PDF Report')
    pdf_report_name = fields.Char('PDF Report Name')

    def get_report_data(self):
        data = []
        for line in self.student_ids:
            data.append({
                'name': line.name,
                'date': line.birth_date,
                'age': line.age,
                'gender': dict(line._fields['gender'].selection).get(line.gender),
                'level': line.level_id.name,
                'course': ','.join(line.course_ids.mapped('name')),
                'teacher': ','.join(line.teacher_ids.mapped('name')),
            })

        return data

    def print_student_excel(self):
        data = self.get_report_data()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Students Report')

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
        worksheet.merge_range(row, col, row + 1, col + 18, "Students Report", format3)
        row += 1
        col = 0
        worksheet.merge_range(row + 1, col, row + 2, col + 2, 'Student Name', format3)
        worksheet.merge_range(row + 1, col + 3, row + 2, col + 5, 'date', format3)
        worksheet.merge_range(row + 1, col + 6, row + 2, col + 7, 'Age', format3)
        worksheet.merge_range(row + 1, col + 8, row + 2, col + 10, 'Gender', format3)
        worksheet.merge_range(row + 1, col + 11, row + 2, col + 12, 'Level', format3)
        worksheet.merge_range(row + 1, col + 13, row + 2, col + 15, 'Course', format3)
        worksheet.merge_range(row + 1, col + 16, row + 2, col + 18, 'Teacher', format3)
        row += 1

        for line in data:
            worksheet.merge_range(row + 3, col, row + 3, col + 2, line['name'], bold2)
            worksheet.merge_range(row + 3, col + 3, row + 3, col + 5, line['date'].strftime('%Y-%m-%d'), bold2)
            worksheet.merge_range(row + 3, col + 6, row + 3, col + 7, line['age'], bold2)
            worksheet.merge_range(row + 3, col + 8, row + 3, col + 10, line['gender'], bold2)
            worksheet.merge_range(row + 3, col + 11, row + 3, col + 12, line['level'], bold2)
            worksheet.merge_range(row + 3, col + 13, row + 3, col + 15, line['course'], bold2)
            worksheet.merge_range(row + 3, col + 16, row + 3, col + 18, line['teacher'], bold2)
            row += 1
        row += 3

        # Close workbook and retrieve Excel file as bytes
        workbook.close()
        output.seek(0)
        self.excel_sheet = base64.encodebytes(output.read())
        self.excel_sheet_name = f"Students_Report.xlsx"

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/student.report.wizard/{self.id}/excel_sheet/Students_Report.xlsx?download=true',
            'target': 'self',
        }

    def action_print_pdf(self):

        return {
            'type': 'ir.actions.report',
            'name': 'School Students Reports',
            'model': 'school.student',
            'report_type': 'qweb-pdf',
            'report_name': 'school.school_student_template_view',
            'report_file': 'school.school_student_template_view',
            'print_report_name': "School Students Reports",
            'context': {'active_ids': self.student_ids.ids}  # list of ids
        }

    def action_print_report(self):
        if self.type == 'pdf':
            return self.action_print_pdf()
        else:
            return self.print_student_excel()
