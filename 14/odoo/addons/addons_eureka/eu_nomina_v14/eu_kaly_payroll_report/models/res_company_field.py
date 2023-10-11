
from odoo import models, fields, api

class ResCompanyField(models.Model):
    _inherit = "res.company"

    num_patronal = fields.Char(string="Número Patronal")
    law_represent = fields.Many2one("res.partner", string="Representante Legal")
    date_seguro_register = fields.Date('Fecha de registro seguro social')

class ResCompanyWizard(models.TransientModel):
    _inherit = 'hr.config.company.wiz'

    law_represent = fields.Many2one("res.partner", string="Representante Legal", default=lambda self: self.env.company.law_represent)
    date_seguro_register = fields.Date('Fecha de registro seguro social', default=lambda self: self.env.company.date_seguro_register)
    num_patronal = fields.Char(string="Número Patronal", default=lambda self: self.env.company.num_patronal)



    def configurar(self):
        super().configurar()
        
        compania=self.env.company

        if self.law_represent:
            compania.law_represent=self.law_represent
        
        if self.date_seguro_register:
            compania.date_seguro_register=self.date_seguro_register
        
        if self.num_patronal:
            compania.num_patronal = self.num_patronal