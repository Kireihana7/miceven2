# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _, tools
from datetime import datetime
from odoo.exceptions import Warning, UserError,ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    sale_order_limit = fields.Integer(
        string='Limite de Productos en Pedidos de Ventas',
    )