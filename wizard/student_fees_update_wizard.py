from odoo import fields, models, api
from odoo.exceptions import ValidationError


class StudentFessUpdateWizard(models.TransientModel):
    _name = "student.fees.update.wizard"
    student_id = fields.Many2one('school.student')
    fees = fields.Float()

    def update_student_fees(self):
        self.student_id.fees = self.fees
