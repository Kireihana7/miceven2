# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import traceback
class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    @api.model
    def _name_search(self, name, args = None, operator = "ilike", limit = 50, name_get_uid = None):
        res=super()._name_search(name, args = None, operator = "ilike", limit = 50, name_get_uid = None)
        tres=1/0
        return res    
class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'


    @api.model
    def _name_search(self, name, args = None, operator = "ilike", limit = 50, name_get_uid = None):
        res=super()._name_search(name, args = None, operator = "ilike", limit = 50, name_get_uid = None)
        tres=1/0
        return res        