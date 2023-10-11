# -*- coding: utf-8 -*-

from odoo import api, fields, models  


class CropsAnimals(models.Model):
	_name = 'crops.animals'
	_rec_name = 'partner_id'

	crops_tasks_template_id = fields.Many2one(
		'crops.tasks.template',
		string="Crops Tasks Template",
		tracking=True
	)
	task_id = fields.Many2one(
		'project.task',
		string='Task',
		tracking=True
	)
	partner_id = fields.Many2one(
		'res.partner',
		string="Animal",
		required=True,
		tracking=True
	)
	start_date = fields.Date(
		string='Start Date',
		required=True,
		tracking=True
	)
	end_date = fields.Date(
		string='End Date',
		required=True,
		tracking=True
	)
	quantity = fields.Float(
		string='Quantity',
		required=True,
		tracking=True
	)
	description = fields.Text(
		string='Description',
		required=True,
		tracking=True
	)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


