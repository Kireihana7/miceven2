# -*- coding: utf-8 -*-
# from odoo import http


# class EuReport(http.Controller):
#     @http.route('/eu_report/eu_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/eu_report/eu_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('eu_report.listing', {
#             'root': '/eu_report/eu_report',
#             'objects': http.request.env['eu_report.eu_report'].search([]),
#         })

#     @http.route('/eu_report/eu_report/objects/<model("eu_report.eu_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('eu_report.object', {
#             'object': obj
#         })
