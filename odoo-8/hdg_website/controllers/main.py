# -*- coding: utf-8 -*-
import base64


from openerp import SUPERUSER_ID
from openerp import http
from openerp.tools.translate import _
from openerp.http import request
from openerp import addons
from openerp.addons.website.controllers.main import Website

# Import  requested_module
from openerp import conf
import imp
import math


class WebsiteHomePageInherit(addons.website.controllers.main.Website):
    @http.route('/', type='http', auth='public', website=True)
    def home(self, **kw):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        units_model = env['product.product']
        units = units_model.search([('sale_ok', '=', True)])
        shop_menu = env['website.menu'].search([('name', '=', 'Shop')])
        contact_us = env['website.menu'].search([('name', '=', 'Contact us')])
        shop_menu.unlink()
        contact_us.unlink()
        units_no = len(units)
        items_no = units_no / 4.00
        items = int(math.ceil(items_no))
        if items > 1 :
            more_than_one = True
            return request.website.render("website.homepage", {
                'units': units,
                'items': items,
                'units_no': units_no,
                'more_than_one': more_than_one,
            })
        else:
            items = 1
        return request.website.render("website.homepage", {
            'units': units,
            'items': items,
            'units_no': units_no,
        })

    @http.route('/property', methods=['POST'], type='http', auth="public", website=True)
    def property(self, **post):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        form_fields = ['name', 'property_type', 'min_beds', 'max_beds', 'min_price', 'max_price']
        search_fields = {}
        for field in form_fields:
            if post.get(field):
                search_fields[field] = post.get(field)
        if not search_fields:
            properties = env['product.product'].search([('sale_ok', '=', True)])
        else:
            fields = []
            for key, value in search_fields.iteritems():
                if key == 'min_price':
                    fields.append(('list_price', '>=', value))
                elif key == 'max_price':
                    fields.append(('list_price', '<=', value))
                elif key == 'min_beds':
                    fields.append(('bed_rooms', '>=', value))
                elif key == 'max_beds':
                    fields.append(('bed_rooms', '<=', value))
                elif key == 'name':
                    fields.append((key, 'like', '%'+value+'%'))
                else:
                    fields.append((key, "=", value))
            print fields
            properties = env['product.product'].search(fields)
        properties_no = len(properties)
        items_no = properties_no / 9.00
        items = int(math.ceil(items_no))
        list_items_no = properties_no / 4.00
        list_items = int(math.ceil(list_items_no))
        more_than_one = False
        more_than_one_list = False
        if items > 1 :
            more_than_one = True
        else:
            items = 1
        if list_items > 1:
            more_than_one_list = True
        else:
            items = 1
        return request.website.render("website.property", {
            'properties': properties,
            'properties_no': properties_no,
            'items': items,
            'more_than_one': more_than_one,
            'list_items': list_items,
            'more_than_one_list': more_than_one_list,
        })


    @http.route('/property_details/<model("product.product"):property>', type='http', auth="public", website=True)
    def property_details(self, property):
        return request.render("website.property_details", {
            'property': property,
        })



class leads(http.Controller):
    @http.route(['/page/website.contact_us', '/page/contact_us'], type='http', auth="public", website=True)
    def contact(self, **kwargs):
        values = {}
        for field in ['name', 'phone', 'email', 'description']:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())
        return request.website.render("website.contact_us", values)

    def create_lead(self, request, values, kwargs):
        """ Allow to be overrided """
        cr, context = request.cr, request.context
        # create new customer:
        def create_partner(self, request, values, kwargs):
            """ Allow to be overrided """
            cr, context = request.cr, request.context
            values['email'] = kwargs['email']
            return request.registry['res.partner'].create(cr, SUPERUSER_ID, values, context=dict(context, mail_create_nosubscribe=True))
        values['email_from'] = kwargs['email']
        partner_id = create_partner(self, request, values, kwargs)
        values['partner_id'] = partner_id
        return request.registry['crm.lead'].create(cr, SUPERUSER_ID, values,context=dict(context, mail_create_nosubscribe=True))

    def preRenderThanks(self, values, kwargs):
        """ Allow to be overrided """
        return {
            '_values': values,
            '_kwargs': kwargs,
        }

    def get_leads_response(self, values, kwargs):
        values = self.preRenderThanks(values, kwargs)
        return request.website.render(kwargs.get("view_callback", "hdg_website.leads_thanks"), values)

    @http.route(['/crm/leads'], type='http', auth="public", website=True)
    def leads(self, **kwargs):
        def dict_to_str(title, dictvar):
            ret = "\n\n%s" % title
            for field in dictvar:
                ret += "\n%s" % field
            return ret

        _TECHNICAL = ['show_info', 'view_from', 'view_callback']  # Only use for behavior, don't stock it
        _BLACKLIST = ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'user_id', 'active']  # Allow in description
        _REQUIRED = ['name']  # Could be improved including required from model

        post_file = []  # List of file to add to ir_attachment once we have the ID
        post_description = []  # Info to add after the message
        values = {}

        values['medium_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID,'crm.crm_medium_website')
        values['section_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID,'website.salesteam_website_sales')

        for field_name, field_value in kwargs.items():
            if hasattr(field_value, 'filename'):
                post_file.append(field_value)
            elif field_name in request.registry['crm.lead']._fields and field_name not in _BLACKLIST:
                values[field_name] = field_value
            elif field_name not in _TECHNICAL:  # allow to add some free fields or blacklisted field like ID
                post_description.append("%s: %s" % (field_name, field_value))

        if "name" not in kwargs and values.get("contact_name"):  # if kwarg.name is empty, it's an error, we cannot copy the contact_name
            values["name"] = values.get("contact_name")
        # fields validation : Check that required field from model crm_lead exists
        error = set(field for field in _REQUIRED if not values.get(field))

        if error:
            values = dict(values, error=error, kwargs=kwargs.items())
            return request.website.render(kwargs.get("view_from", "website.leads"), values)

        # description is required, so it is always already initialized

        lead_id = self.create_lead(request, dict(values, user_id=False), kwargs)
        values.update(lead_id=lead_id)
        if lead_id:
            for field_value in post_file:
                attachment_value = {
                    'name': field_value.filename,
                    'res_name': field_value.filename,
                    'res_model': 'crm.lead',
                    'res_id': lead_id,
                    'datas': base64.encodestring(field_value.read()),
                    'datas_fname': field_value.filename,
                }
                request.registry['ir.attachment'].create(request.cr, SUPERUSER_ID, attachment_value,context=request.context)

        return self.get_leads_response(values, kwargs)

    ### Contact Agent Form
    @http.route(['/property_details/<model("product.product"):property>'], type='http', auth="public", website=True)
    def contact(self, **kwargs):
        values = {}
        for field in ['name', 'phone', 'email', 'description']:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())
        return request.website.render("website.property_details", values)

    def create_lead(self, request, values, kwargs):
        """ Allow to be overrided """
        cr, context = request.cr, request.context

        # create new customer:
        def create_partner(self, request, values, kwargs):
            """ Allow to be overrided """
            cr, context = request.cr, request.context
            values['email'] = kwargs['email']
            return request.registry['res.partner'].create(cr, SUPERUSER_ID, values,
                                                          context=dict(context, mail_create_nosubscribe=True))
        values['email_from'] = kwargs['email']
        partner_id = create_partner(self, request, values, kwargs)
        values['partner_id'] = partner_id
        return request.registry['crm.lead'].create(cr, SUPERUSER_ID, values,
                                                   context=dict(context, mail_create_nosubscribe=True))

    def preRenderThanks(self, values, kwargs):
        """ Allow to be overrided """
        return {
            '_values': values,
            '_kwargs': kwargs,
        }

    def get_leads_response(self, values, kwargs):
        values = self.preRenderThanks(values, kwargs)
        return request.website.render(kwargs.get("view_callback", "hdg_website.leads_thanks"), values)

    @http.route(['/crm/leads'], type='http', auth="public", website=True)
    def leads(self, **kwargs):
        def dict_to_str(title, dictvar):
            ret = "\n\n%s" % title
            for field in dictvar:
                ret += "\n%s" % field
            return ret

        _TECHNICAL = ['show_info', 'view_from', 'view_callback']  # Only use for behavior, don't stock it
        _BLACKLIST = ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'user_id',
                      'active']  # Allow in description
        _REQUIRED = ['name']  # Could be improved including required from model

        post_file = []  # List of file to add to ir_attachment once we have the ID
        post_description = []  # Info to add after the message
        values = {}

        values['medium_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID,
                                                                                'crm.crm_medium_website')
        values['section_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID,
                                                                                 'website.salesteam_website_sales')

        for field_name, field_value in kwargs.items():
            if hasattr(field_value, 'filename'):
                post_file.append(field_value)
            elif field_name in request.registry['crm.lead']._fields and field_name not in _BLACKLIST:
                values[field_name] = field_value
            elif field_name not in _TECHNICAL:  # allow to add some free fields or blacklisted field like ID
                post_description.append("%s: %s" % (field_name, field_value))

        if "name" not in kwargs and values.get(
                "contact_name"):  # if kwarg.name is empty, it's an error, we cannot copy the contact_name
            values["name"] = values.get("contact_name")
        # fields validation : Check that required field from model crm_lead exists
        error = set(field for field in _REQUIRED if not values.get(field))

        if error:
            values = dict(values, error=error, kwargs=kwargs.items())
            return request.website.render(kwargs.get("view_from", "website.leads"), values)

        # description is required, so it is always already initialized

        lead_id = self.create_lead(request, dict(values, user_id=False), kwargs)
        values.update(lead_id=lead_id)
        if lead_id:
            for field_value in post_file:
                attachment_value = {
                    'name': field_value.filename,
                    'res_name': field_value.filename,
                    'res_model': 'crm.lead',
                    'res_id': lead_id,
                    'datas': base64.encodestring(field_value.read()),
                    'datas_fname': field_value.filename,
                }
                request.registry['ir.attachment'].create(request.cr, SUPERUSER_ID, attachment_value,
                                                         context=request.context)
        return self.get_leads_response(values, kwargs)

class Claims(http.Controller):
    # Electricity Claims
    @http.route(['/page/after_sales/elect'], type='http', auth="public", website=True)
    def contact1(self, **kwargs):
        values = {}
        for field in ['name', 'phone', 'email', 'description']:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())
        return request.website.render("website.elect_claims", values)

    def create_elect_claim(self, request, values, kwargs):
        """ Allow to be overrided """
        cr, context = request.cr, request.context

        # create new customer:
        def create_partner(self, request, values, kwargs):
            """ Allow to be overrided """
            cr, context = request.cr, request.context
            values['email'] = kwargs['email']
            return request.registry['res.partner'].create(cr, SUPERUSER_ID, values,
                                                          context=dict(context, mail_create_nosubscribe=True))
        values['email_from'] = kwargs['email']
        partner_id = create_partner(self, request, values, kwargs)
        values['partner_id'] = partner_id
        values['claim_type'] = 'elect'
        return request.registry['crm.claim'].create(cr, SUPERUSER_ID, values,
                                                   context=dict(context, mail_create_nosubscribe=True))

    def preRenderThanks(self, values, kwargs):
        """ Allow to be overrided """
        return {
            '_values': values,
            '_kwargs': kwargs,
        }

    def get_elect_claims_response(self, values, kwargs):
        values = self.preRenderThanks(values, kwargs)
        return request.website.render(kwargs.get("view_callback", "hdg_website.leads_thanks"), values)

    @http.route(['/crm/elect/claims'], type='http', auth="public", website=True)
    def elect_claims(self, **kwargs):
        def dict_to_str(title, dictvar):
            ret = "\n\n%s" % title
            for field in dictvar:
                ret += "\n%s" % field
            return ret

        _TECHNICAL = ['show_info', 'view_from', 'view_callback']  # Only use for behavior, don't stock it
        _BLACKLIST = ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'user_id',
                      'active']  # Allow in description
        _REQUIRED = ['name']  # Could be improved including required from model

        post_file = []  # List of file to add to ir_attachment once we have the ID
        post_description = []  # Info to add after the message
        values = {}

        values['medium_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID,
                                                                                'crm.crm_medium_website')
        values['section_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID,
                                                                                 'website.salesteam_website_sales')

        for field_name, field_value in kwargs.items():
            if hasattr(field_value, 'filename'):
                post_file.append(field_value)
            elif field_name in request.registry['crm.claim']._fields and field_name not in _BLACKLIST:
                values[field_name] = field_value
            elif field_name not in _TECHNICAL:  # allow to add some free fields or blacklisted field like ID
                post_description.append("%s: %s" % (field_name, field_value))

        if "name" not in kwargs and values.get(
                "contact_name"):  # if kwarg.name is empty, it's an error, we cannot copy the contact_name
            values["name"] = values.get("contact_name")
        # fields validation : Check that required field from model crm_lead exists
        error = set(field for field in _REQUIRED if not values.get(field))

        if error:
            values = dict(values, error=error, kwargs=kwargs.items())
            return request.website.render(kwargs.get("view_from", "website.leads"), values)

        # description is required, so it is always already initialized

        claim_id = self.create_elect_claim(request, dict(values, user_id=False), kwargs)
        values.update(lead_id=claim_id)
        if claim_id:
            for field_value in post_file:
                attachment_value = {
                    'name': field_value.filename,
                    'res_name': field_value.filename,
                    'res_model': 'crm.claim',
                    'res_id': claim_id,
                    'datas': base64.encodestring(field_value.read()),
                    'datas_fname': field_value.filename,
                }
                request.registry['ir.attachment'].create(request.cr, SUPERUSER_ID, attachment_value,
                                                         context=request.context)
        return self.get_elect_claims_response(values, kwargs)

    # Water Claims
    @http.route(['/page/after_sales/water'], type='http', auth="public", website=True)
    def contact(self, **kwargs):
        values = {}
        for field in ['name', 'phone', 'email', 'description']:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())
        return request.website.render("website.water_claims", values)

    def create_water_claim(self, request, values, kwargs):
        """ Allow to be overrided """
        cr, context = request.cr, request.context

        # create new customer:
        def create_partner(self, request, values, kwargs):
            """ Allow to be overrided """
            cr, context = request.cr, request.context
            values['email'] = kwargs['email']
            return request.registry['res.partner'].create(cr, SUPERUSER_ID, values,
                                                          context=dict(context, mail_create_nosubscribe=True))

        values['email_from'] = kwargs['email']
        partner_id = create_partner(self, request, values, kwargs)
        values['partner_id'] = partner_id
        values['claim_type'] = 'water'
        return request.registry['crm.claim'].create(cr, SUPERUSER_ID, values,
                                                    context=dict(context, mail_create_nosubscribe=True))

    def preRenderThanks(self, values, kwargs):
        """ Allow to be overrided """
        return {
            '_values': values,
            '_kwargs': kwargs,
        }

    def get_water_claims_response(self, values, kwargs):
        values = self.preRenderThanks(values, kwargs)
        return request.website.render(kwargs.get("view_callback", "hdg_website.leads_thanks"), values)

    @http.route(['/crm/water/claims'], type='http', auth="public", website=True)
    def water_claims(self, **kwargs):
        def dict_to_str(title, dictvar):
            ret = "\n\n%s" % title
            for field in dictvar:
                ret += "\n%s" % field
            return ret

        _TECHNICAL = ['show_info', 'view_from', 'view_callback']  # Only use for behavior, don't stock it
        _BLACKLIST = ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'user_id',
                      'active']  # Allow in description
        _REQUIRED = ['name']  # Could be improved including required from model

        post_file = []  # List of file to add to ir_attachment once we have the ID
        post_description = []  # Info to add after the message
        values = {}

        values['medium_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID,
                                                                                'crm.crm_medium_website')
        values['section_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID,
                                                                                 'website.salesteam_website_sales')

        for field_name, field_value in kwargs.items():
            if hasattr(field_value, 'filename'):
                post_file.append(field_value)
            elif field_name in request.registry['crm.claim']._fields and field_name not in _BLACKLIST:
                values[field_name] = field_value
            elif field_name not in _TECHNICAL:  # allow to add some free fields or blacklisted field like ID
                post_description.append("%s: %s" % (field_name, field_value))

        if "name" not in kwargs and values.get(
                "contact_name"):  # if kwarg.name is empty, it's an error, we cannot copy the contact_name
            values["name"] = values.get("contact_name")
        # fields validation : Check that required field from model crm_lead exists
        error = set(field for field in _REQUIRED if not values.get(field))

        if error:
            values = dict(values, error=error, kwargs=kwargs.items())
            return request.website.render(kwargs.get("view_from", "website.leads"), values)

        # description is required, so it is always already initialized

        claim_id = self.create_water_claim(request, dict(values, user_id=False), kwargs)
        values.update(lead_id=claim_id)
        if claim_id:
            for field_value in post_file:
                attachment_value = {
                    'name': field_value.filename,
                    'res_name': field_value.filename,
                    'res_model': 'crm.claim',
                    'res_id': claim_id,
                    'datas': base64.encodestring(field_value.read()),
                    'datas_fname': field_value.filename,
                }
                request.registry['ir.attachment'].create(request.cr, SUPERUSER_ID, attachment_value,
                                                         context=request.context)
        return self.get_water_claims_response(values, kwargs)


