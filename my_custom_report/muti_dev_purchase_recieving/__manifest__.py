# -*- coding: utf-8 -*-
{
    'name': "MUTI DEV PURCHASE RECIEVING REPORT TEMPLATE",

    'summary': """
        PURCHASE RECIEVING REPORT TEMPLATE FOR MC AND SP""",

    'description': """
        Purchase recieving report for SP and MC"
    """,
    "author": "Joshua M. Mission",
    'website': "http://www.mutigroup.com",

    'category': 'Custom',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock','odoo_muti_custom','stock_picking_invoice_link'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'reports/muti_dev_purchase_recieving_report.xml',
        'reports/muti_dev_purchase_recieving_report_sp.xml'
    ],
    
    
    'application': True,
    'installable': True,
    'auto_install': False,
}