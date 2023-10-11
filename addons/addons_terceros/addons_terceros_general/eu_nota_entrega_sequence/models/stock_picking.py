# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import  UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    

    nota_de_entrega = fields.Boolean(string="¿Es una nota de entrega?",default=False,tracking=True)
    sequence = fields.Char(
        string='Secuencia Nota de Entrega',
        copy=False,
        readonly=1,
        default=False,
        tracking=True,
    )

    def asignar_nota(self):
        for rec in self:
            sequence = False
            rec.nota_de_entrega = True
            if rec.nota_de_entrega and not rec.sequence and rec.picking_type_code == 'outgoing':
                sequence = self.env['ir.sequence'].next_by_code('picking.seq')
            else:
                raise UserError('No puedes asignar un secuencial a esta SU')
            rec.sequence = sequence

