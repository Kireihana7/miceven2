# -*- coding: utf-8 -*-
import re

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    #Columns
    rif = fields.Char(string='RIF', required=True)
    currency_id_ref = fields.Many2one('res.currency',string="Monedas de las Retenciones",default=lambda self: self.env['res.currency'].search(['|',('name', '=', 'VES'),('name', '=', 'VEF')], limit=1))

    @api.constrains('rif')
    def _check_rif(self):
        formate = (r"[VJG]{1}[-]{1}[0-9]{9}")
        form_rif = re.compile(formate)
        records = self.env['res.company']
        rif_exist = records.search_count([('rif', '=', self.rif),('id', '!=', self.id)])
        for company in self:
            if not form_rif.match(company.rif):
                raise ValidationError(("El formato del RIF es incorrecto por favor introduzca un RIF de la forma J-123456789 (utilice solo las letras V, J y G)"))
            elif rif_exist > 0:
                raise ValidationError(("Ya existe un registro con este RIF"))
            else:
                return True
