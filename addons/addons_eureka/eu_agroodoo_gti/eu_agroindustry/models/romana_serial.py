# -*- coding: utf-8 -*-

import requests
from odoo import models, fields, _
from odoo.exceptions import UserError

class RomanaSerial(models.Model):
    _name = 'romana.serial'
    _description ="Configuración del Puerto Serial"
    _inherit= ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre del Aparato",tracking=True,required=True)
    puerto = fields.Char(string="Puerto",tracking=True,required=True)
    timeout = fields.Char(string="Tiempo de Espera",tracking=True,required=True)
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,invisible=True,tracking=True)
    bits_per_second = fields.Selection([
        ('75','75'),
        ('110','110'),
        ('134','134'),
        ('150','150'),
        ('300','300'),
        ('600','600'),
        ('1200','1200'),
        ('2400','2400'),
        ('4800','4800'),
        ('7200','7200'),
        ('9600','9600'),
        ('14400','14400'),
        ('19200','19200'),
        ('38400','38400'),
        ('57600','57600'),
        ('115200','115200'),
        ('128000','128000'),
    ], string='Bits por Segundo', index=True, tracking=True, default='9600',required=True)
    weight_url = fields.Char("URL de la balanza")
    state = fields.Selection([
        ('abierto', 'Abierto'),
        ('bloqueado', 'Bloqueado'),
        ], string='Estatus', readonly=True, copy=False, index=True, tracking=True, default='abierto')

    def bloquear(self):
        for rec in self:
            rec.state = 'bloqueado'

    def desbloquear(self):
        for rec in self:
            rec.state = 'abierto'

    def get_weight(self):
        self.ensure_one()

        response = requests.post(self.weight_url, json={
            "port": self.puerto,
            "timeout": self.timeout,
            "baudRate": self.bits_per_second,
        })

        result = response.json()

        if result["type"] == "error":
            raise UserError(result["result"])

        return float("".join(c for c in result["result"] if c.isnumeric()) or 0)

    def action_test(self):
        raise UserError(self.get_weight())