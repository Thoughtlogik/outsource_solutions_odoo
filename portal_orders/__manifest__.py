# -*- coding: utf-8 -*-
{
    'name': 'Portal Orders',
    'version': '0.1',
    'summary': 'Portal Orders',
    'depends': ['sale_management','hr','product','sale','crm','portal'],

    'data': [
        'security/ir.model.access.csv',
        'report/report_sale.xml',
        'data/sequence.xml',
        'views/sales_order_design_templates.xml',
        # 'views/popup_temp.xml',
        'views/order_backend.xml',
        # 'views/certification.xml',
        'views/new_certificate.xml',
        'views/inherit_crm.xml',
        'views/report.xml',


    ],
    'images': [],

    'assets': {
        'web.assets_frontend': [

            # 'portal_orders/static/src/scss/style.scss',
            'portal_orders/static/src/css/sales_order_design.css',
            'portal_orders/static/src/css/sales_order.css',
            'portal_orders/static/src/js/sales_order_portal.js',
            # 'portal_orders/static/src/js/sales_order.js',
            'portal_orders/static/src/js/xlsx.full.min.js',

        ]
    },

    'installable': True,
    'auto_install': False,
    'application': True,

}
