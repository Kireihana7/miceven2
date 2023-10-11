# -*- coding: utf-8 -*-

from odoo import api, fields, models  


class CropsIncident(models.Model):
	_name = 'crops.incident'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	crop_id = fields.Many2one(
		'farmer.location.crops',
		string='Crop',
		required=True,
		tracking=True
	)
	task_id = fields.Many2one(
		'project.task',
		string='Task',
		required=False,
		tracking=True
	)
	name = fields.Char(
		string='Name',
		required=True,
		tracking=True
	)
	datetime = fields.Datetime(
		string='Datetime',
		required=True,
		tracking=True
	)
	location_id = fields.Many2one(
		'res.partner',
		string='Location',
		required=True,
		tracking=True
	)
	description = fields.Char(
		string='Description',
		required=True,
		tracking=True
	)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


