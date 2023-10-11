# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models


# from dateutil.relativedelta import relativedelta
# from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
# from datetime import datetime, date, time, timedelta
# import time
# import pytz
# import os
# import re


class ResCountryStates(models.Model):
    _inherit = "res.country.state"
    _description = "Country States"

    res_state_ve_id = fields.Char('Id único de los estados de Venezuela')


class ResCountryCity(models.Model):
    _name = "res.country.city"
    _description = "Country City"

    res_country_state_id = fields.Char('Estate')
    name = fields.Char('City')
    is_capital = fields.Boolean('Is capital?')


class ResStateMunicipal(models.Model):
    _name = "res.state.municipal"
    _description = "State Municipal"

    ids_comp = fields.Char('id')
    res_country_state_id = fields.Char('Estate')
    name = fields.Char('Municipal')


class ResMunicipalParish(models.Model):
    _name = "res.municipal.parish"
    _description = "Municipal Parish"

    res_state_municipal_id = fields.Char('Municipio')
    name = fields.Char('Parish')
