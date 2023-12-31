# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Jupical Technologies(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api


class HREmployee(models.Model):

    _inherit = 'hr.employee'
    _description = "Generate employee sequence id"

    emp_id = fields.Char("Employee Id")


    def button_generate_emp_id(self):
        for rec in self:
            pass
    @api.model
    def create(self, values):
        if values['company_id']:
            code_seq=self.env['res.company'].search([('id','=',values['company_id'])],limit=1).company_emp_sequence
            values['emp_id'] = code_seq.next_by_code(code_seq.code)
        return super(HREmployee, self).create(values)

class HREmployeePublic(models.Model):

    _inherit = 'hr.employee.public'
    _description = "Generate employee sequence id"

    emp_id = fields.Char("Employee Id")

   


class ResCompany(models.Model):

    _inherit = 'res.company'


    company_emp_sequence=fields.Many2one('ir.sequence',string="Secuencia de empleados de la compañia")