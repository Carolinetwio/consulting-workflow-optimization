# -*- coding: utf-8 -*-
{
    'name': "Consulting Workflow Optimization",

    'summary': """
        This module optimizes several points in the timesheet workflow
    """,

    'description': """
        This module optimizes several points in the timesheet workflow
    """,

    'author': "twio.tech AG",
    'website': "https://www.twio.tech",
    'license': 'OPL-1',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'sale_timesheet',
    ],

    # always loaded
    'data': [
        'views/project_task_views.xml',
    ],
}
