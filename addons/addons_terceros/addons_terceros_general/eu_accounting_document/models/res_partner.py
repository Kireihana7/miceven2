
from email.policy import default
from tokenize import String
from odoo import models, api,fields
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_view_estado_cuenta_cxc(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_account_moves_all")
        action['domain'] = [
            #('move_type', 'in', ('out_invoice', 'out_refund')),
            ('move_id.state', '=', 'posted'),
            ('partner_id', '=', self.id),
            ('account_id.user_type_id.type','=','receivable'),
        ]
        action['context'] = {'default_state':'posted', 'state':'posted'}
        return action
    
    def open_wizard_estado_cuenta(self):
        return {
            'name': "Estado de Cuenta",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'res.partner.account.client.state.wizard',
            'view_id': self.env.ref('eu_accounting_document.wizard_client_account_state_form').id,
            'target': 'new',
            'context': {'default_partner_id': self.id}
        }
            # , 'default_user_id': self.saleorder_ids.ids
    

