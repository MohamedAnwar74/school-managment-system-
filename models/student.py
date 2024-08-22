import base64
import io
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date
from odoo.addons.base.models.res_users import check_identity
import xlsxwriter


class SchoolStudent(models.Model):
    _name = "school.student"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'school.student'

    name = fields.Char(required=True, translate=True)
    ref = fields.Char(default='New')
    code = fields.Char("Student code")
    birth_date = fields.Date(string="Date Of Birth")
    age = fields.Integer(compute="calc_age", store=True, string="Student Age")
    gender = fields.Selection([
        ('m', 'Male'), ('f', 'Female')
    ])
    accepted = fields.Boolean(default=False)
    note = fields.Text()
    address = fields.Text()
    phone = fields.Integer(string="Phone_number")
    level_id = fields.Many2one('school.level', string='Level')
    image = fields.Binary()
    cv = fields.Binary()
    start_date = fields.Date(string="Join_Date")
    end_date = fields.Date(string="End_Date")

    login_time = fields.Datetime(default=fields.Datetime.today())
    fees = fields.Monetary('Student Fess', default=0)
    tax = fields.Monetary(compute="calc_tax")
    total_fees = fields.Monetary(readonly=True)
    company_id = fields.Many2one('res.company', store=True, string="Company",
                                 default=lambda self: self.env.user.company_id.id)
    # company_id = fields.Many2one('res.company', default=_get_default_company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    course_ids = fields.Many2many("school.courses", domain="[('is_open' , '=' ,True)]", string="Courses")

    skills_ids = fields.Many2many("school.skills")
    teacher_ids = fields.Many2many('school.teacher', string="Teachers Name")
    room_id = fields.Many2one('school.classroom')
    room_capacity = fields.Integer(related="room_id.capacity")
    # user_id = fields.Many2one('res.users', 'Responsible')
    excel_sheet = fields.Binary('Download Report')
    excel_sheet_name = fields.Char(string='Name', size=64)

    state = fields.Selection([
        ('applied', 'Applied'), ('first', 'First Interview'), ('second', 'Second Interview'),
        ('passed', 'Passed'), ('rejected', 'Rejected')
    ], default='applied')

    def check_required_skills(self):
        for rec in self:
            if rec.course_ids:
                required_skills = rec.course_ids.required_skills.ids
                student_skills = rec.skills_ids.ids

                missing_skills = list(set(required_skills) - set(student_skills))
                if missing_skills:
                    raise ValidationError("Missing required skills for course")

    @api.onchange('course_ids')
    def onchange_course_ids(self):
        if self.course_ids:
            skills = self.env['school.skills'].search([('id', 'in', self.course_ids.mapped('required_skills').ids)])
            return {
                'domain': {
                    'skills_ids': [('id', 'in', skills.ids)],
                }
            }
        else:
            return {
                'domain': {
                    'skills_ids': [],
                }
            }

    # Dynamic record stages
    # stage_id = fields.Many2one('school.student.stage', string='Stage')
    def _get_default_state(self):
        state = self.env.ref('school.stage_application', raise_if_not_found=False)
        return state if state and state.id else False

    stage_id = fields.Many2one('school.student.stage', 'State',
                               default=_get_default_state, group_expand='_read_group_stage_ids',
                               tracking=True,
                               help='Current state of the student')

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['school.student.stage'].search([], order=order)

    _sql_constraints = [
        ('code_unique', 'unique (code)', "code already exists")
    ]

    # @api.constrains("age")
    # def check_age(self):
    #     for rec in self:
    #         if rec.age < 7 or rec.age > 15:
    #             raise ValidationError("Age of student must be greater that 7 or less than 15")

    @api.onchange('level_id')
    def onchange_level_ids(self):
        for rec in self:
            if rec.level_id:
                rec.course_ids = rec.env['school.courses'].search([('level_id', 'in', rec.level_id.ids
                                                                    )])
                rec.teacher_ids = rec.env['school.teacher'].search([('level_id', 'in', rec.level_id.ids
                                                                     )])
            else:
                rec.course_ids = False
                rec.teacher_ids = False

    @api.depends("fees")
    def calc_tax(self):
        self.tax = self.fees * 0.20
        self.total_fees = self.fees + self.tax

    @api.depends("birth_date")
    def calc_age(self):
        for rec in self:
            if rec.birth_date:
                today = date.today()
                birth_date = rec.birth_date
                rec.age = today.year - birth_date.year

            else:
                rec.age = 0

    @check_identity
    def change_state(self):
        if self.state == 'applied':
            self.state = 'first'
        elif self.state == 'first':
            self.state = 'second'
        elif self.state in ['passed', 'rejected']:
            self.state = 'applied'

    def set_passed(self):
        self.state = 'passed'

    def set_rejected(self):
        self.state = 'rejected'

    def wizard_open(self):
        return {
            'name': 'Update Student Fees',
            'type': 'ir.actions.act_window',
            'res_model': 'student.fees.update.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_student_id': self.id}
        }

    def show_courses(self):
        print(self.course_ids.ids[0])
        return {
            'name': ('My Courses'),
            'view_mode': 'form',
            'res_model': 'school.courses',
            'res_id': self.course_ids.ids[0],
            'type': 'ir.actions.act_window',
        }

    def test_status(self):
        # print(self.env['school.student'].search([('accepted', '!=', False)]))

        rec = self.env['school.student'].search([('accepted', '=', True)])
        rec.state = 'passed'

    # ORM Methods
    # CRUD operations
    # Create: self.env['model.name'].create(vals_dict) // self.env['model.name'].create({'name':'Ahmed', 'age': 22})
    # Read: self.env['model.name'].search([('any_field','any_operator','any_value')])
    # // self.env['model.name'].browse(id or list_ids) -- static domain [('id','=', any_int)]
    # Update: self.env['model.name'].write(vals_dict) -- only updated fields
    # Delete: self.env['model.name'].unlink()

    # def action(self):
    #
    #     # 1) Search => run on domain ,return record id or  list of record id
    #
    #     # searched_course = self.env['school.courses'].search([('is_open', '=', False)])
    #     # print(searched_course)
    #
    #     # searched_course = self.env['school.courses'].search([('is_open', '=', False)])
    #     # for rec in searched_course:
    #     #     rec.name = "not_open"
    #
    #     # print(self.env.context)  # return dictionary
    #
    #     # search_count() => return count  of record id
    #     # searched_course_count = self.env['school.courses'].search_count([])
    #     # print(searched_course_count)
    #
    #     # limit and offset
    #
    #     # limit_coursed = self.env['school.courses'].search([], limit=1, offset=2)
    #     # print(limit_coursed)
    #
    #     # 2) browse => run on id or ids , return recordset or list of record set
    #     # browsed_courses = self.env['school.courses'].browse(searched_course)
    #     # print(browsed_courses)
    #
    #     # 3) filtered() => run on function and return record ids
    #     # filtered_courses = searched_course.filtered('lambda x: x.id < 3')
    #     # print(filtered_courses)
    #
    #     # 4) mapped() => return list of ids
    #     for rec in self:
    #         mapped_courses = rec.course_ids.mapped('is_open')
    #         print(mapped_courses)
    #     return True
    #
    #     # course_open = course_open.sorted(key='id', reverse=True)
    #     # print(course_open)

    @api.model
    # doesnt have id already depend on model
    def create(self, vals):
        # res = super(SchoolStudent, self).create(vals)
        # if res.ref == 'New':
        #     if self.env['ir.sequence'].search([('code', '=', 'student.sequence')]):
        #         res.ref = self.env['ir.sequence'].next_by_code('student.sequence') + '-' + str(res.stage_id.name) or _(
        #             'New')
        # return res
        student = super(SchoolStudent, self).create(vals)
        student.check_required_skills()
        return student
        # print(f"before assignment{vals}")
        # vals.update({
        #     'fees': 1000
        # })
        # print(f"after assignment{vals}")
        # # res = super(SchoolStudent, self).create(vals)
        # # return res
        # return super(SchoolStudent, self).create(vals)

    # res is object

    # def write(self, vals):
    #     result = super(SchoolStudent, self).write(vals)
    #     self._check_required_skills()
    #     return result

    #     # from beginning i have id of object
    #     vals.update({
    #         'accepted': True
    #     })
    #
    #     res = super(SchoolStudent, self).write(vals)
    #     # print(res)
    #     # print(vals)  # dictionary of field I have updated it
    #
    #     # obj1.name = 'some value'
    #     # obj1.age = 30
    #
    #     # obj1.write({
    #     #     'name': 'some value',
    #     #     'level': 3,
    #     # })
    #
    #     return res

    # res here is boolean
    # Be careful not to fall in an infinite loop by calling write() inside itself

    def unlink(self):
        for rec in self:
            if rec.accepted == True:
                raise ValidationError("you cannot delete this record")

            return super(SchoolStudent, rec).unlink()

    @api.depends('name', 'state')
    def name_get(self):
        return_list = []
        for rec in self:
            return_list.append((rec.id, "%s (%s)" % (rec.name, rec.state)))
        return return_list

    @api.model
    def default_get(self, fields_list=[]):
        print(fields_list)

        res = super(SchoolStudent, self).default_get(fields_list)
        res['fees'] = 1000
        print(res)
        return res
