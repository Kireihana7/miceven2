# -*- coding: utf-8 -*-

from odoo import api, fields, models  


class CropsTasksTemplate(models.Model):
	_name = 'crops.tasks.template'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'task_id'

	task_id = fields.Many2one(
		'project.task',
		string="Task",
		required=False,
		tracking=True
	)
	crop_id = fields.Many2one(
		'farmer.location.crops',
		string="Crop",
		required=True,
		tracking=True
	)
	animal_ids = fields.One2many(
		'crops.animals',
		'crops_tasks_template_id',
		string="Animals",
		required=True,
		tracking=True
	)
	fleet_ids = fields.One2many(
		'crops.fleet',
		'crops_tasks_template_id',
		string="Fleets",
		required=True,
		tracking=True
	)
	equipment_ids = fields.Many2many(
		'maintenance.equipment',
		string='Equipments',
		required=True,
		tracking=True
	)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


