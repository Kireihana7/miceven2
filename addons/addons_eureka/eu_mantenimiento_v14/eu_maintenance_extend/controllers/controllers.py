# -*- coding: utf-8 -*-
# from odoo import http


# class EuMaintenanceExtend(http.Controller):
#     @http.route('/eu_maintenance_extend/eu_maintenance_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/eu_maintenance_extend/eu_maintenance_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('eu_maintenance_extend.listing', {
#             'root': '/eu_maintenance_extend/eu_maintenance_extend',
#             'objects': http.request.env['eu_maintenance_extend.eu_maintenance_extend'].search([]),
#         })

#     @http.route('/eu_maintenance_extend/eu_maintenance_extend/objects/<model("eu_maintenance_extend.eu_maintenance_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('eu_maintenance_extend.object', {
#             'object': obj
#         })
