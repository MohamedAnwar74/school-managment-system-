from odoo import fields, models


class HrEmployee(models.Model):
    # Traditional Inheritance / Extension / Class inheritance
    # _name = 'hr.employee' #not mandatory
    _inherit = 'hr.employee'

    national_id = fields.Char()
    passport_no = fields.Char()
    # work_email = fields.Char('Work Emails', compute="_compute_work_contact_details", store=True,
    #                          inverse='_inverse_work_contact_details')
