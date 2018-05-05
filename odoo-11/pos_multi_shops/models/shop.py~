# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from lxml import etree

class Shop(models.Model):
	_name = 'shop'

	name = fields.Char(string='shop')
	user_ids = fields.One2many('res.users', 'shop_id', string='Users', store=True)
	product_ids = fields.One2many('product.product', 'shop_id', string='Products', store=True)
	journal_ids = fields.One2many('account.journal', 'shop_id', string='Journals', store=True)
	image = fields.Binary('Image')
	pos_ids = fields.One2many('pos.config', 'shop_id', string='Points Of Sale', store=True)

class AccountJournalInherit(models.Model):
	_inherit = 'account.journal'

	shop_id = fields.Many2one('shop', string='Shop')

class ResUsersInherit(models.Model):
	_inherit = 'res.users'

	shop_id = fields.Many2one('shop', string='Shop')
	shop_ids = fields.Char()	

class PosConfigInherit(models.Model):
	_inherit = "pos.config"

	shop_id = fields.Many2one('shop', string='Shop')

class PosOrderInherit(models.Model):
	_inherit = "pos.order"
	
	# method to get shop id by default
	def _get_shop_id(self):
		current_user = self.env['res.users'].search([('id', '=', self.env.uid)])
		if current_user.shop_id:
			return current_user.shop_id.id

	shop_id = fields.Many2one('shop', string='Shop', default=_get_shop_id)

class PosOrderLineInherit(models.Model):
	_inherit = "pos.order.line"
	
	# add domain on products based on current user shop id
	@api.model
	def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
		res = super(PosOrderLineInherit, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(res['arch'])
		current_user = self.env['res.users'].search([('id', '=', self.env.uid)])
		for node in doc.xpath("//field[@name='product_id']"):
			node.set('domain', "[('shop_id', '=',"+current_user.shop_id.id+")]")
		res['arch'] = etree.tostring(doc)
		return res

class ProductProductInherit(models.Model):
	_inherit = 'product.template'

	# method to get shop id by default
	def _get_shop_id(self):
		current_user = self.env['res.users'].search([('id', '=', self.env.uid)])
		if current_user.shop_id:
			return current_user.shop_id.id

	shop_id = fields.Many2one('shop', string='Shop', default=_get_shop_id)
