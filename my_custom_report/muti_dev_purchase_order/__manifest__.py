# -*- coding: utf-8 -*-
{
    'name': "MUTI DEV PURCHASE ORDER",

    'summary': """
        PURCHASE ORDER REPORT """,

    'description': """
        Purchase Order Report"
    """,
    "author": "Joshua M. Mission",
    'website': "http://www.mutigroup.com",

    'category': 'Custom',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase','hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/muti_dev_purchase_order.xml',
        'reports/muti_dev_purchase_order_templates.xml',
        'reports/muti_dev_purchase_order_override.xml'
    ],
    
    
    'application': True,
    'installable': True,
    'auto_install': False,
}