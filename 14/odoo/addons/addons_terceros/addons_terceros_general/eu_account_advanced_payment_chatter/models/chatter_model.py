from odoo import models, fields

class AccountAdvancedPayment(models.Model):
	_name = 'account.advanced.payment'
	_inherit = ['account.advanced.payment', 'mail.thread']

	name = fields.Char(track_visibility="always",)
	
	
		