# -*- coding: utf-8 -*-



{
    'name': "school",
    'sequence': 0,
    'summary': "School Managment System",
    'description': "School Managment System",
    'author': "Mo ZAki",
    'version': '0.1',
    'depends': ['base', 'mail', 'project', 'hr'],
    'data': [
        'security/secuirty.xml',
        'security/ir.model.access.csv',
        'reports/students_templates.xml',
        'reports/student_report.xml',
        'reports/time_slot_templates.xml',
        'reports/time_slot_report.xml',
        'data/data.xml',
        'data/ir_sequence.xml',
        'data/ir_cron.xml',
        'views/student.xml',
        'views/courses.xml',
        'views/skills.xml',
        'views/teacher.xml',
        'views/classroom.xml',
        'views/time_slot.xml',
        'views/level.xml',
        'views/optional_courses.xml',
        'views/employee.xml',
        'views/student_stage.xml',
        'wizard/student_fees_update_wizard.xml',
        'wizard/student_report_wizard.xml',
        'wizard/time_slot_wizard.xml',
    ],
    'installable': True,
    'application': True,
}
