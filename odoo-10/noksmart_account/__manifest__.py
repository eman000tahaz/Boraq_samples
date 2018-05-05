# -*- coding: utf-8 -*-
{
    'name': 'Noksmart Accounting',
    'version': '1.0.1',
    'Author': "Eman Taha",
    'category': 'Accounting',
    'sequence': 20,
    'summary': 'Noksmart Accounting',
    'depends': ['account'],
    'data': [
        'views/account_views.xml',
        'wizard/account_report_trial_balance_view.xml',
        'views/report_trialbalance.xml',
        'views/noksmart_account_report.xml',
        'wizard/account_report_statement_view.xml',
        'views/report_account_statement.xml',
    ],
    'demo': [
    ],
    'qweb': [],
    'installable': True,
    'application': True,
}
