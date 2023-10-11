

from pyexpat import model

from odoo import models, api, fields

class ResPartnerBank(models.Model) :
    _inherit = "res.partner.bank"

    tipo_de_cuenta = fields.Selection(String='Tipo de Cuenta',selection=[
                                    ('corriente','Corriente'),
                                    ('ahorro','Ahorro'),
                                    ('nomina','Nómina')
        ]
    )