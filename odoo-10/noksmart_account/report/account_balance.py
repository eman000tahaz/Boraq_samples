# -*- coding: utf-8 -*-

import time
from odoo import api, models
from operator import itemgetter


class ReportTrialBalanceInherit(models.AbstractModel):
    _inherit = 'report.account.report_trialbalance'

    def _get_accounts(self, accounts, display_account):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

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
            if account.parent_id:
                res['parent'] = account.parent_id
            else:
                res['parent'] = False
            if account.child_ids:
                res['children'] = account.child_ids
            else:
                res['children'] = False
            if account.id in account_result.keys():
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            account_res.append(res)
            # if display_account == 'all':
            #     account_res.append(res)
            # if display_account == 'not_zero' and not currency.is_zero(res['balance']):
            #     account_res.append(res)
            # if display_account == 'movement' and (not currency.is_zero(res['debit']) or not currency.is_zero(res['credit'])):
            #     account_res.append(res)
        return account_res


    @api.model
    def render_html(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        display_account = data['form'].get('display_account')
        accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account)
        new_account_res = sorted(account_res, key=itemgetter('code'))

        final_accounts = []
        if data['form'].get('rep_view') == 'p_view':
            view = 'p'
            for account in new_account_res:  
                if account['parent'] == False:
                    temp_debit = account['debit']
                    temp_credit = account['credit']
                    temp_balance = account['balance']
                    if account['children']:
                        for f_child in account['children']:
                            f_c = [x for x in new_account_res if x['code'] == int(f_child.code)]
                            temp_debit += f_c[0]['debit']
                            temp_credit += f_c[0]['credit']
                            temp_balance += f_c[0]['balance']
                            if f_child.child_ids:
                                for s_child in f_child.child_ids:
                                    s_c = [y for y in new_account_res if y['code'] == int(s_child.code)]
                                    temp_debit += s_c[0]['debit']
                                    temp_credit += s_c[0]['credit']
                                    temp_balance += s_c[0]['balance']
                    account['debit'] = temp_debit
                    account['credit'] = temp_credit
                    account['balance'] = temp_balance
                    final_accounts.append(account)
        elif data['form'].get('rep_view') == 'c_view':
            view ='c'
            for account in new_account_res:
                if account['parent'] != False:
                    temp_debit = account['debit']
                    temp_credit = account['credit']
                    temp_balance = account['balance']
                    if account['children']:
                        for child in account['children']:
                            c = [z for z in new_account_res if z['code'] == int(child.code)]
                            temp_debit += c[0]['debit']
                            temp_credit += c[0]['credit']
                            temp_balance += c[0]['balance']
                    account['debit'] = temp_debit
                    account['credit'] = temp_credit
                    account['balance'] = temp_balance
                    final_accounts.append(account)
        elif data['form'].get('rep_view') == 't_view':
            view = 't'
            for account in new_account_res:
                if account['parent'] == False:
                    temp_debit = account['debit']
                    temp_credit = account['credit']
                    temp_balance = account['balance']
                    if account['children']:
                        for f_child in account['children']:
                            f_c = [x for x in new_account_res if x['code'] == int(f_child.code)]
                            temp_debit += f_c[0]['debit']
                            temp_credit += f_c[0]['credit']
                            temp_balance += f_c[0]['balance']
                            if f_child.child_ids:
                                for s_child in f_child.child_ids:
                                    s_c = [y for y in new_account_res if y['code'] == int(s_child.code)]
                                    temp_debit += s_c[0]['debit']
                                    temp_credit += s_c[0]['credit']
                                    temp_balance += s_c[0]['balance']
                    account['debit'] = temp_debit
                    account['credit'] = temp_credit
                    account['balance'] = temp_balance
                    final_accounts.append(account)
                elif account['parent'] != False:
                    temp_debit = account['debit']
                    temp_credit = account['credit']
                    temp_balance = account['balance']
                    if account['children']:
                        for child in account['children']:
                            c = [z for z in new_account_res if z['code'] == int(child.code)]
                            temp_debit += c[0]['debit']
                            temp_credit += c[0]['credit']
                            temp_balance += c[0]['balance']
                    account['debit'] = temp_debit
                    account['credit'] = temp_credit
                    account['balance'] = temp_balance
                    final_accounts.append(account)

        docargs = {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'view_t': view,
            'Accounts': final_accounts,
        }
        return self.env['report'].render('account.report_trialbalance', docargs)
