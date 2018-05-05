# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError


class AccountReportStatement(models.TransientModel):
    _name = "account.report.statement"

    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    report_type = fields.Selection([('one', 'One Account'), ('all', 'ALL Accounts')], string='Report Type', required=True, default='all')
    account_id = fields.Many2one('account.account', string='Account', domain=[('parent_id', '!=', False)])

    @api.multi
    def print_report(self, data):
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        if self.report_type == 'one' and not self.account_id:
            raise ValidationError(_('Please choose one account ...'))
        if self.report_type == 'all':
            self.account_id = False
        data['form'] = self.read(['company_id', 'date_from', 'date_to', 'report_type', 'account_id'])[0]
        records = self.env[data['model']].browse(data.get('ids', []))
        return self.env['report'].get_action(records, 'noksmart_account.report_account_statement', data=data)