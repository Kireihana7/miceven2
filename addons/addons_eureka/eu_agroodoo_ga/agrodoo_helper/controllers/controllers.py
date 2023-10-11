# -*- coding: utf-8 -*-
# from odoo import http


# class AgrodooHelper(http.Controller):
#     @http.route('/agrodoo_helper/agrodoo_helper/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/agrodoo_helper/agrodoo_helper/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('agrodoo_helper.listing', {
#             'root': '/agrodoo_helper/agrodoo_helper',
#             'objects': http.request.env['agrodoo_helper.agrodoo_helper'].search([]),
#         })

#     @http.route('/agrodoo_helper/agrodoo_helper/objects/<model("agrodoo_helper.agrodoo_helper"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('agrodoo_helper.object', {
#             'object': obj
#         })
