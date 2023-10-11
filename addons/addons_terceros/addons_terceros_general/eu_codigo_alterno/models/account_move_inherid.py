from odoo import models, fields, api

class InheritCodigoAlternoAccountMove(models.Model):
    _inherit ='account.move'

    alternate_code = fields.Char(string="Codigo Alterno" )



    @api.onchange('alternate_code','partner_shipping_id')

    def _onchange_alternate_code(self):
        for rec in self:
            if rec.alternate_code:
                rec.partner_id= self.env['res.partner'].search([('alternate_code', '=' , rec.alternate_code)])
                
        pass


    @api.model
    def create(self,vals):
        res=super().create(vals)
        for rec in res:
            code=rec.alternate_code
            if code and not rec.partner_id:
                rec.partner_id= self.env['res.partner'].search([('alternate_code', '=' , code)])
        return  res
