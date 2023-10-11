from odoo import api, fields, models,_
from odoo.exceptions import UserError
import pdb
import datetime
from datetime import timedelta
from num2words import num2words 
from collections import defaultdict
from odoo.tools import float_is_zero
from odoo.tools.misc import formatLang, format_date, get_lang

class StockLandedCost(models.Model):
	_inherit="stock.landed.cost"

	display_complete = fields.Boolean(compute='_compute_display_complete')
