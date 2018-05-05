# -*- coding: utf-8 -*-
{
    'name': 'Noksmart Reports',
    'version': '1.0.1',
    'category': 'Reports',
    'sequence': 20,
    'summary': 'Noksmart Reports',
    'depends': ['account', 'report', 'sale', 'purchase'],
    'data': [
        'views/report_invoice.xml',
        'views/report_saleorder.xml',
        'views/report_purchase_order.xml',
        'views/report_purchase_quotation.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'Author': "Eman Taha"
}
