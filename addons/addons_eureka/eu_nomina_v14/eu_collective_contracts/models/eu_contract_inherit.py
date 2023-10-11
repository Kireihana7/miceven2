# -*- coding: utf-8 -*-


from odoo import models, fields,api

class EuHrContract(models.Model):
    _inherit="hr.contract"
    
    parent_collect_contract_id=fields.Many2one('hr.collective.contracts',string="Contrato Colectivo")
    
