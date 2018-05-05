# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountBalanceReportInherit(models.TransientModel):
	_inherit = "account.balance.report"

	rep_view = fields.Selection([('p_view', 'Parent View'),('c_view', 'Children View'),('t_view', 'Tree View')], string='View Type', default='t-view', required=True)

	def _print_report(self, data):
		data['form'].update(self.read(['rep_view'])[0])
		data = self.pre_print_report(data)
		records = self.env[data['model']].browse(data.get('ids', []))
		return self.env['report'].get_action(records, 'account.report_trialbalance', data=data)
