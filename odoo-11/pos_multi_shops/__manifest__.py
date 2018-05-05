# -*- coding: utf-8 -*-
{
    'name': 'Pos Multi Shops',
    'author': "Eman Taha",
    'category': 'Point Of Sale',
    'sequence': 20,
    'summary': 'Pos Multi Shops',
    'depends': ['product','point_of_sale'],
    'data': [
        'security/shop_security.xml',
        'security/ir.model.access.csv',
        'views/shop_views.xml',
        'views/product_views.xml',
        'views/pos_config_views.xml',
        'views/pos_order_views.xml',
        'views/account_journal_views.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'price': 79.99,
    'currency': 'EUR',
}