# -*- coding: utf-8 -*-

from odoo import models

class HrDepartment(models.Model):
    _name = "hr.department"
    _inherit = ["hr.department", "image.mixin"]