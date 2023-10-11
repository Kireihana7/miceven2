# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64

from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import UserError
<<<<<<< HEAD
from odoo.osv import expression
=======
from odoo.modules.module import get_module_resource
from odoo.tools import formatLang


class LunchProductCategory(models.Model):
    """ Category of the product such as pizza, sandwich, pasta, chinese, burger... """
    _name = 'lunch.product.category'
    _inherit = 'image.mixin'
    _description = 'Lunch Product Category'

    @api.model
    def _default_image(self):
        image_path = get_module_resource('lunch', 'static/img', 'lunch.png')
        return base64.b64encode(open(image_path, 'rb').read())

    name = fields.Char('Product Category', required=True, translate=True)
    company_id = fields.Many2one('res.company')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    topping_label_1 = fields.Char('Extra 1 Label', required=True, default='Extras')
    topping_label_2 = fields.Char('Extra 2 Label', required=True, default='Beverages')
    topping_label_3 = fields.Char('Extra 3 Label', required=True, default='Extra Label 3')
    topping_ids_1 = fields.One2many('lunch.topping', 'category_id', domain=[('topping_category', '=', 1)])
    topping_ids_2 = fields.One2many('lunch.topping', 'category_id', domain=[('topping_category', '=', 2)])
    topping_ids_3 = fields.One2many('lunch.topping', 'category_id', domain=[('topping_category', '=', 3)])
    topping_quantity_1 = fields.Selection([
        ('0_more', 'None or More'),
        ('1_more', 'One or More'),
        ('1', 'Only One')], 'Extra 1 Quantity', default='0_more', required=True)
    topping_quantity_2 = fields.Selection([
        ('0_more', 'None or More'),
        ('1_more', 'One or More'),
        ('1', 'Only One')], 'Extra 2 Quantity', default='0_more', required=True)
    topping_quantity_3 = fields.Selection([
        ('0_more', 'None or More'),
        ('1_more', 'One or More'),
        ('1', 'Only One')], 'Extra 3 Quantity', default='0_more', required=True)
    product_count = fields.Integer(compute='_compute_product_count', help="The number of products related to this category")
    active = fields.Boolean(string='Active', default=True)
    image_1920 = fields.Image(default=_default_image)

    def _compute_product_count(self):
        product_data = self.env['lunch.product'].read_group([('category_id', 'in', self.ids)], ['category_id'], ['category_id'])
        data = {product['category_id'][0]: product['category_id_count'] for product in product_data}
        for category in self:
            category.product_count = data.get(category.id, 0)

    @api.model
    def create(self, vals):
        for topping in vals.get('topping_ids_2', []):
            topping[2].update({'topping_category': 2})
        for topping in vals.get('topping_ids_3', []):
            topping[2].update({'topping_category': 3})
        return super(LunchProductCategory, self).create(vals)

    def write(self, vals):
        for topping in vals.get('topping_ids_2', []):
            topping_values = topping[2]
            if topping_values:
                topping_values.update({'topping_category': 2})
        for topping in vals.get('topping_ids_3', []):
            topping_values = topping[2]
            if topping_values:
                topping_values.update({'topping_category': 3})
        return super(LunchProductCategory, self).write(vals)

    def toggle_active(self):
        """ Archiving related lunch product """
        res = super().toggle_active()
        Product = self.env['lunch.product'].with_context(active_test=False)
        all_products = Product.search([('category_id', 'in', self.ids)])
        all_products._sync_active_from_related()
        return res

class LunchTopping(models.Model):
    """"""
    _name = 'lunch.topping'
    _description = 'Lunch Extras'

    name = fields.Char('Name', required=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    price = fields.Float('Price', digits='Account', required=True)
    category_id = fields.Many2one('lunch.product.category', ondelete='cascade')
    topping_category = fields.Integer('Topping Category', help="This field is a technical field", required=True, default=1)

    def name_get(self):
        currency_id = self.env.company.currency_id
        res = dict(super(LunchTopping, self).name_get())
        for topping in self:
            price = formatLang(self.env, topping.price, currency_obj=currency_id)
            res[topping.id] = '%s %s' % (topping.name, price)
        return list(res.items())
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe


class LunchProduct(models.Model):
    """ Products available to order. A product is linked to a specific vendor. """
    _name = 'lunch.product'
    _description = 'Lunch Product'
    _inherit = 'image.mixin'
    _order = 'name'
    _check_company_auto = True

    name = fields.Char('Product Name', required=True, translate=True)
    category_id = fields.Many2one('lunch.product.category', 'Product Category', check_company=True, required=True)
    description = fields.Html('Description', translate=True)
    price = fields.Float('Price', digits='Account', required=True)
    supplier_id = fields.Many2one('lunch.supplier', 'Vendor', check_company=True, required=True)
    active = fields.Boolean(default=True)

    company_id = fields.Many2one('res.company', related='supplier_id.company_id', readonly=False, store=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    new_until = fields.Date('New Until')
    is_new = fields.Boolean(compute='_compute_is_new')

    favorite_user_ids = fields.Many2many('res.users', 'lunch_product_favorite_user_rel', 'product_id', 'user_id', check_company=True)
    is_favorite = fields.Boolean(compute='_compute_is_favorite', inverse='_inverse_is_favorite')

    last_order_date = fields.Date(compute='_compute_last_order_date')

    product_image = fields.Image(compute='_compute_product_image')
    # This field is used only for searching
    is_available_at = fields.Many2one('lunch.location', 'Product Availability', compute='_compute_is_available_at', search='_search_is_available_at')

    @api.depends('image_128', 'category_id.image_128')
    def _compute_product_image(self):
        for product in self:
            product.product_image = product.image_128 or product.category_id.image_128

    @api.depends('new_until')
    def _compute_is_new(self):
        today = fields.Date.context_today(self)
        for product in self:
            if product.new_until:
                product.is_new = today <= product.new_until
            else:
                product.is_new = False

    @api.depends_context('uid')
    @api.depends('favorite_user_ids')
    def _compute_is_favorite(self):
        for product in self:
            product.is_favorite = self.env.user in product.favorite_user_ids

    @api.depends_context('uid')
    def _compute_last_order_date(self):
        all_orders = self.env['lunch.order'].search([
            ('user_id', '=', self.env.user.id),
            ('product_id', 'in', self.ids),
        ])
        mapped_orders = defaultdict(lambda: self.env['lunch.order'])
        for order in all_orders:
            mapped_orders[order.product_id] |= order
        for product in self:
            if not mapped_orders[product]:
                product.last_order_date = False
            else:
                product.last_order_date = max(mapped_orders[product].mapped('date'))

    def _compute_is_available_at(self):
        """
            Is available_at is always false when browsing it
            this field is there only to search (see _search_is_available_at)
        """
        for product in self:
            product.is_available_at = False

    def _search_is_available_at(self, operator, value):
        supported_operators = ['in', 'not in', '=', '!=']

        if not operator in supported_operators:
            return expression.TRUE_DOMAIN

        if isinstance(value, int):
            value = [value]

        if operator in expression.NEGATIVE_TERM_OPERATORS:
            return expression.AND([[('supplier_id.available_location_ids', 'not in', value)], [('supplier_id.available_location_ids', '!=', False)]])

        return expression.OR([[('supplier_id.available_location_ids', 'in', value)], [('supplier_id.available_location_ids', '=', False)]])

    def _sync_active_from_related(self):
        """ Archive/unarchive product after related field is archived/unarchived """
        return self.filtered(lambda p: (p.category_id.active and p.supplier_id.active) != p.active).toggle_active()

    def _sync_active_from_related(self):
        """ Archive/unarchive product after related field is archived/unarchived """
        return self.filtered(lambda p: (p.category_id.active and p.supplier_id.active) != p.active).toggle_active()

    def toggle_active(self):
<<<<<<< HEAD
        invalid_products = self.filtered(lambda product: not product.active and not product.category_id.active)
        if invalid_products:
            raise UserError(_("The following product categories are archived. You should either unarchive the categories or change the category of the product.\n%s", '\n'.join(invalid_products.category_id.mapped('name'))))
        invalid_products = self.filtered(lambda product: not product.active and not product.supplier_id.active)
        if invalid_products:
            raise UserError(_("The following suppliers are archived. You should either unarchive the suppliers or change the supplier of the product.\n%s", '\n'.join(invalid_products.supplier_id.mapped('name'))))
=======
        if self.filtered(lambda product: not product.active and not product.category_id.active):
            raise UserError(_("The product category is archived. The user have to unarchive the category or change the category of the product."))
        if self.filtered(lambda product: not product.active and not product.supplier_id.active):
            raise UserError(_("The product supplier is archived. The user have to unarchive the supplier or change the supplier of the product."))
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        return super().toggle_active()

    def _inverse_is_favorite(self):
        """ Handled in the write() """
        return

    def write(self, vals):
        if 'is_favorite' in vals:
            if vals.pop('is_favorite'):
                commands = [(4, product.id) for product in self]
            else:
                commands = [(3, product.id) for product in self]
            self.env.user.write({
                'favorite_lunch_product_ids': commands,
            })

        if not vals:
            return True
        return super().write(vals)
