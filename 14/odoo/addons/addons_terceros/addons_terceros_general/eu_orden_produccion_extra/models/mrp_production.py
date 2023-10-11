# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models

class MrpProduction(models.Model):
	_inherit = 'mrp.production'

class StockMove(models.Model):
	_inherit = 'stock.move'

class StockMoveLine(models.Model):
	_inherit = 'stock.move.line'