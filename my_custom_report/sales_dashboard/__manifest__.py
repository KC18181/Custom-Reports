# -*- coding: utf-8 -*-
{
    'name': "MUTI Sales Dashboard",

    'summary': """
        Sales Dashboard Report""",

    'description': """
        Sales Dashboard Report.
    """,

    'author': "Divo",
    'website': "http://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale', 'report_xlsx','res_area_code'],

    # always loaded
    'data': [
        'security/sales_security.xml',
        'security/sd_ir_rule.xml',
        'security/ir.model.access.csv',
        'views/sales_cash_cron_view.xml',
        'views/sales_credit_cron_view.xml',
        'views/branch_cron_view.xml',
        'views/brand_cron_view.xml',
        'views/company_cron_view.xml',
        'views/category_cron_view.xml',
        'views/customer_cron_view.xml',
        'views/usage_cron_view.xml',
        'views/description_cron_view.xml',
        'views/outlet_cron_view.xml',
        'views/area_cron_view.xml',
        'views/service_cron_view.xml',
        'views/type_cron_view.xml',
        'views/sales_views.xml',
        'views/sales_wizard.xml',
        'views/sales_list_view.xml',
        'views/sales_cash.xml',
        'views/sales_credit.xml',
        'views/holiday_non_operation.xml',
        'views/sales_branch_wizard.xml',
        'views/sales_branch_list.xml',
        'views/sales_summary_cron.xml',
        'views/sales_summary_list.xml',
        'views/sidecar_config.xml',
        'views/target_cpmrp_config.xml',
        'views/sales_gm_wizard.xml',
        'views/sd_menu.xml'
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
