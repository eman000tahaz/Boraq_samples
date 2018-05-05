from odoo import api, fields, models, _


class AccountAccountInherit(models.Model):
    _inherit = 'account.account'

    parent_id = fields.Many2one('account.account', 'Parent Account')
    child_ids = fields.One2many('account.account', 'parent_id', 'Children')
    code = fields.Char(string='Code', required=False, help="The journal entries of this journal will be named using this prefix.")


    @api.model
    def create(self, vals):
        if vals['code'] == False:
        	if vals['parent_id'] != False:
        		parent_acc = self.env['account.account'].search([('id', '=', vals['parent_id'])])
        		if parent_acc.parent_id:
        			if parent_acc.child_ids:
        				ids=[]
        				for child in parent_acc.child_ids:
        					ids.append(child.id)
        				last_child_acc = self.env['account.account'].search([('id', 'in', ids)], order='id desc', limit=1)
        				vals['code'] = str(int(last_child_acc.code)+1)	
        			else:
        				vals['code'] = parent_acc.code +str(1)
        		else:
        			if parent_acc.child_ids:
        				ids=[]
        				for child in parent_acc.child_ids:
        					ids.append(child.id)
        				last_child_acc = self.env['account.account'].search([('id', 'in', ids)], order='id desc', limit=1)
        				vals['code'] = str(int(last_child_acc.code)+100000)	
        			else:
        				vals['code'] = str(int(parent_acc.code)+100000)
        	else:
        		accounts_last_id = self.env['account.account'].search([('parent_id', '=', False)], order='id desc', limit=1)
        		if not accounts_last_id:
        			vals['code'] = str(1000000000)
        		else:
        			vals['code'] = str(int(accounts_last_id.code)+1000000000)
        return super(AccountAccountInherit, self).create(vals)