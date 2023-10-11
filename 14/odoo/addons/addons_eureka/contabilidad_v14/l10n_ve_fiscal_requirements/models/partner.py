# -*- coding: utf-8 -*-
import re

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    rif = fields.Char(string="RIF", required=False)
    vd_rif = fields.Integer(string="Dígito Validador RIF",compute="_compute_vd_rif")
    cedula = fields.Char(string="Cédula o RIF",size=10,tracking=True,required=False)
    street = fields.Char(required=True)
    city = fields.Char(required=True)
    state_id = fields.Many2one(required=True)
    country_id = fields.Many2one(required=True)
    has_cedula = fields.Boolean("Tiene cédula?", default=True, tracking=True)
    residence_type = fields.Selection([('SR','Sin RIF'),
                                      ('R', 'Residenciado'),
                                      ('NR', 'No residenciado'),
                                      ('D', 'Domiciliado'),
                                      ('ND', 'No domiciliado')], help='This is the Supplier Type')

    @api.onchange('company_type','is_company')
    def onchange_company_type_re(self):
        for rec in self:
            if rec.is_company:
                rec.residence_type = 'D'
            else:
                rec.residence_type = 'R'
    
    # @api.constrains('rif')
    # def _check_rif(self):
    #     if self.rif:
    #         if self.is_company:
    #             formate = (r"[JG]{1}[-]{1}[0-9]{8}")
    #         else:
    #             formate = (r"[PVE]{1}[-]{1}[0-9]{8}")
    #         form_rif = re.compile(formate)
    #         records = self.env['res.partner']
    #         rif_exist = records.search_count([('cedula', '=', self.rif),('id', '!=', self.id)])
    #         for partner in self:
    #             if not form_rif.match(partner.cedula):
    #                 if self.is_company:
    #                     raise ValidationError(("El formato del RIF es incorrecto por favor introduzca un RIF de la forma J-123456789 (utilice solo las letras J y G)"))
    #                 else:
    #                     raise ValidationError(("El formato del RIF es incorrecto por favor introduzca un RIF de la forma V-123456789 (utilice solo las letras V y E)"))
    #             #verificar si no existe un registro con el mismo rif
    #             elif rif_exist > 0:
    #                 raise ValidationError(
    #                     ("Ya existe un registro con este rif"))
    #             else:
    #                 return True
    @api.onchange('rif','cedula')
    def _onchange_rif_to_vat(self):
        if self.cedula:
            self.vat = self.cedula
        if self.rif:
            self.vat = self.rif


    @api.constrains('cedula')
    def _check_cedula(self):
        if self.cedula:
            if self.cedula == 'CNP':
                return True

            formate = (r"[CJGPVE]{1}[-]{1}[0-9]{8}")
            form_ci = re.compile(formate)
            records = self.env['res.partner']
            cedula_exist = records.search_count([('cedula', '=', self.cedula),('id', '!=', self.id)])
            for partner in self:
                if not form_ci.match(partner.cedula):
                    raise ValidationError(("El formato de la cedula es incorrecto. Por favor introduzca una cédula de la forma V-12345678"))
                elif cedula_exist > 0:
                    raise ValidationError(("Ya existe un registro con este número de cédula"))
                else:
                    return True

    @api.depends('cedula')
    def _compute_vd_rif(self):
        for rec in self:
            rec.vd_rif= 0
            if rec.cedula and not rec.cedula == 'CNP':
                cedula = rec.cedula.replace('-','')
                base = {'V': 4, 'E': 8, 'J': 12, 'G': 20}
                oper = [0, 3, 2, 7, 6, 5, 4, 3, 2]
                val = 0
                for i in range(len(cedula[:9])):
                    val += base.get(cedula[0], 0) if i == 0 else oper[i] * int(cedula[i])
                digit = 11 - (val % 11)
                digit = digit if digit < 10 else 0
                rec.vd_rif = int(digit)

    @api.onchange("cedula", "vd_rif")
    def _onchange_cedula_vd_rif(self):
        for rec in self:
            if rec.cedula:
                rec.rif = rec.cedula + str(rec.vd_rif)
    
    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     args = args or []
    #     if name:
    #         # Be sure name_search is symetric to name_get
    #         name = name.split(' / ')[-1]
    #         args = ['|',('name', operator, name),('rif', operator, name)] + args
    #     return self._search(args, limit=limit, access_rights_uid=name_get_uid)