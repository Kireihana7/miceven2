# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _,exceptions
from odoo.exceptions import ValidationError

class Employee(models.Model):
    _inherit = "hr.employee"
    _description = "Employee measures"
    
    zapatos = fields.Integer(string='Talla de los zapatos', size=2)
    pantalon = fields.Integer(string='Talla de pantalon', size=2)
    camisa = fields.Selection([
        ('s','S'),
        ('m','M'),
        ('l','L'),
        ('xl','XL'),
        ], string='Talla de la camisa')
    estatura = fields.Float("Estatura", size=2)
    peso = fields.Float(string='Peso Kg.')
    braga = fields.Selection([
        ('s','S'),
        ('m','M'),
        ('l','L'),
        ('xl','XL'),
        ], string='Talla de la braga')

class EmployeePublic(models.Model):
    _inherit = "hr.employee.public"
    _description = "Employee measures"
    
    zapatos = fields.Integer(string='Talla de los zapatos', size=2)
    pantalon = fields.Integer(string='Talla de pantalon', size=2)
    camisa = fields.Selection([
        ('s','S'),
        ('m','M'),
        ('l','L'),
        ('xl','XL'),
        ], string='Talla de la camisa')
    estatura = fields.Float("Estatura", size=2)
    peso = fields.Float(string='Peso Kg.')
    braga = fields.Selection([
        ('s','S'),
        ('m','M'),
        ('l','L'),
        ('xl','XL'),
        ], string='Talla de la braga')
    
    







    