# -*- coding: utf-8 -*-
# from odoo import http


# class EuShippingRecord(http.Controller):
#     @http.route('/eu_shipping_record/eu_shipping_record/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/eu_shipping_record/eu_shipping_record/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('eu_shipping_record.listing', {
#             'root': '/eu_shipping_record/eu_shipping_record',
#             'objects': http.request.env['eu_shipping_record.eu_shipping_record'].search([]),
#         })

#     @http.route('/eu_shipping_record/eu_shipping_record/objects/<model("eu_shipping_record.eu_shipping_record"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('eu_shipping_record.object', {
#             'object': obj
#         })
