# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models
from datetime import datetime,date
from dateutil import relativedelta
from odoo.exceptions import UserError

class Employee(models.Model):
    _inherit = 'hr.employee'
    
    commodities=fields.Many2many('hr.commodities',string="Comodidades",tracking=True)


    def write(self,vals):
        res = super().write(vals)
        if vals.get("commodities") and self.commodities:
            for  comodity in vals.get("commodities"):
                ids=[]
                for y in comodity[-1:]:
                    ids=[int(x) for x in y]
                    # raise UserError (ids)
                    comodities=self.env['hr.commodities'].sudo().search([('id','in',ids)])
                    for id in comodities:
                        self.message_post(body=f"Se le asigno [{id.name}] a este trabajador")
                        id.message_post(body=f"Al trabajador [{self.name}] se le asigno este activo")
        return res

class EmployeePublic(models.Model):
    _inherit = 'hr.employee.public'
    

    commodities=fields.Many2many('hr.commodities',string="Comodidades",tracking=True)
