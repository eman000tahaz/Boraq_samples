# -*- coding: utf-8 -*-

import time
from odoo import api, models
from operator import itemgetter


class ReportAccountStatementInherit(models.AbstractModel):
    _name = 'report.noksmart_account.report_account_statement'

    def _get_accounts(self, accounts):
    	account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"','')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
                   " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        ids = []
        row_zero = {'credit': 0.0, 'balance': 0.0, 'debit': 0.0}
        for row in self.env.cr.dictfetchall():
            current_id = row.pop('id')
            ids.append(current_id)
            account_result[current_id] = row
        for acc in accounts:
            if acc.id not in ids:
                account_result[acc.id] = row_zero
        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = int(account.code)
            res['name'] = account.name
            res['id'] = account.id
            if account.id in account_result.keys():
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            account_res.append(res)

       
        return account_res

    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        # report_type = data['form'].get('report_type')
        account = data['form'].get('account_id')
        date_from = data['form'].get('date_from')
        date_to = data['form'].get('date_to')
        if account:
        	accounts = docs if self.model == 'account.account' else self.env['account.account'].search([('id', '=', account[0])])
        else:
        	accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        account_res = self._get_accounts(accounts)
        new_account_res = sorted(account_res, key=itemgetter('code'))

        journal_res = []

        for acc in new_account_res:
        	if date_from and date_to:
        		arg = [('account_id', '=', acc['id']), ('date_maturity', '>=', date_from), ('date_maturity', '<=', date_to)]
        	elif date_from and not date_to:
   	     		arg = [('account_id', '=', acc['id']), ('date_maturity', '>=', date_from)]
   	     	elif date_to and not date_from:
   	     		arg = [('account_id', '=', acc['id']), ('date_maturity', '<=', date_to)]
   	     	else:
   	     		arg = [('account_id', '=', acc['id'])]
        	account_move_lines = self.env['account.move.line'].search(arg)
        	for line in account_move_lines:
        		res = {}
        		res['account_id'] = line.account_id.id
        		res['date'] = line.date_maturity
        		res['credit'] = line.credit
        		res['debit'] = line.debit
        		res['balance'] = line.debit - line.credit
        		res['name'] = line.name
        		res['move'] = line.move_id.id
        		res['desc'] = line.move_id.narration
        		journal_res.append(res)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts': new_account_res,
            'journals': journal_res,
        }
        return self.env['report'].render('noksmart_account.report_account_statement', docargs)