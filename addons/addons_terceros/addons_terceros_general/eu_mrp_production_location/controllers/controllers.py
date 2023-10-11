# -*- coding: utf-8 -*-
# from odoo import http


# class MrpWorkorderComponentPercentage(http.Controller):
#     @http.route('/mrp_workorder_component_percentage/mrp_workorder_component_percentage/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mrp_workorder_component_percentage/mrp_workorder_component_percentage/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mrp_workorder_component_percentage.listing', {
#             'root': '/mrp_workorder_component_percentage/mrp_workorder_component_percentage',
#             'objects': http.request.env['mrp_workorder_component_percentage.mrp_workorder_component_percentage'].search([]),
#         })

#     @http.route('/mrp_workorder_component_percentage/mrp_workorder_component_percentage/objects/<model("mrp_workorder_component_percentage.mrp_workorder_component_percentage"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mrp_workorder_component_percentage.object', {
#             'object': obj
#         })
