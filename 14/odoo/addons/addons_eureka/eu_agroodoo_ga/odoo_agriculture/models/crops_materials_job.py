# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, RedirectWarning, UserError

class CropsMaterialsJob(models.Model):
	_name = 'crops.materials.job'
	_rec_name = 'product_id'

	internal_type = fields.Selection([
			('material', 'Material'),
			('labour', 'Labour'),
			('equipment', 'Equipment'),
			('overhead', 'Overhead'),
			('hired_service', 'Hired Service')
		],
		string="Type",
		required=True,
		tracking=True
	)
	
	crop_id = fields.Many2one(
		'farmer.location.crops',
		string="Crops",
		required=True,
		tracking=True
	)

	job_type_id = fields.Many2one(
		'job.type',
		string='Job Type',
		required=True,
		tracking=True
	)

	product_id = fields.Many2one(
		'product.product',
		string='Product',
		# domain=[('product_tmpl_id.is_agriculture','=', True)],
		required=True,
		tracking=True
	)
	
	vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')

	partner_id = fields.Many2one(
		'res.partner',
		string='Vendor',
		# required=True,
		tracking=True
	)

	uom_id = fields.Many2one(
		'uom.uom',
		string='Unit of Measure',
		# required=True,
		tracking=True
	)

	quantity = fields.Float(
		string='Quantity',
		default=1,
		# required=True,
		tracking=True
	)

	qty_available = fields.Float(
		string='On Hand',
		related=('product_id.qty_available'),
		readonly=True,
		required=True,
		tracking=True
	)

	internal_note = fields.Text(
		string='Description',
		tracking=True
	)

	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.uom_id = self.product_id.uom_id.id
			self.internal_note = self.product_id.name
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: