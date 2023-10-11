# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

<<<<<<< HEAD
from werkzeug.exceptions import NotFound

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv import expression

from odoo.addons.account.controllers.portal import PortalAccount
from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.addons.project.controllers.portal import ProjectCustomerPortal


class PortalProjectAccount(PortalAccount, ProjectCustomerPortal):
=======
from odoo import http, _
from odoo.http import request
from odoo.osv import expression

from odoo.addons.account.controllers import portal
from odoo.addons.hr_timesheet.controllers.portal import TimesheetCustomerPortal


class PortalAccount(portal.PortalAccount):
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    def _invoice_get_page_view_values(self, invoice, access_token, **kwargs):
        values = super()._invoice_get_page_view_values(invoice, access_token, **kwargs)
        domain = request.env['account.analytic.line']._timesheet_get_portal_domain()
        domain = expression.AND([
            domain,
            request.env['account.analytic.line']._timesheet_get_sale_domain(
                invoice.mapped('line_ids.sale_line_ids'),
                request.env['account.move'].browse([invoice.id])
            )
        ])
        values['timesheets'] = request.env['account.analytic.line'].sudo().search(domain)
        values['is_uom_day'] = request.env['account.analytic.line'].sudo()._is_timesheet_encode_uom_day()
        return values

<<<<<<< HEAD
    @http.route([
        '/my/tasks/<task_id>/orders/invoices',
        '/my/tasks/<task_id>/orders/invoices/page/<int:page>'],
        type='http', auth="user", website=True)
    def portal_my_tasks_invoices(self, task_id=None, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        task = request.env['project.task'].search([('id', '=', task_id)])
        if not task:
            return NotFound()

        domain = [('id', 'in', task.sale_order_id.invoice_ids.ids)]
        values = self._prepare_my_invoices_values(page, date_begin, date_end, sortby, filterby, domain=domain)

        # pager
        pager = portal_pager(**values['pager'])

        # content according to pager and archive selected
        invoices = values['invoices'](pager['offset'])
        request.session['my_invoices_history'] = invoices.ids[:100]

        values.update({
            'invoices': invoices,
            'pager': pager,
        })

        return request.render("account.portal_my_invoices", values)
=======

class CustomerPortal(portal.CustomerPortal):
    def _order_get_page_view_values(self, order, access_token, **kwargs):
        values = super(CustomerPortal, self)._order_get_page_view_values(order, access_token, **kwargs)
        domain = request.env['account.analytic.line']._timesheet_get_portal_domain()
        domain = expression.AND([
            domain,
            request.env['account.analytic.line']._timesheet_get_sale_domain(
                order.mapped('order_line'),
                order.invoice_ids
            )
        ])
        values['timesheets'] = request.env['account.analytic.line'].sudo().search(domain)
        values['is_uom_day'] = request.env['account.analytic.line'].sudo()._is_timesheet_encode_uom_day()
        return values
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe


class SaleTimesheetCustomerPortal(TimesheetCustomerPortal):

    def _get_searchbar_inputs(self):
        searchbar_inputs = super()._get_searchbar_inputs()
        searchbar_inputs.update(
<<<<<<< HEAD
            so={'input': 'so', 'label': _('Search in Sales Order')},
            sol={'input': 'sol', 'label': _('Search in Sales Order Item')},
            invoice={'input': 'invoice', 'label': _('Search in Invoice')})
=======
            sol={'input': 'sol', 'label': _('Search in Sales Order Item')},
            sol_id={'input': 'sol_id', 'label': _('Search in Sales Order Item ID')},
            invoice={'input': 'invoice_id', 'label': _('Search in Invoice ID')})
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        return searchbar_inputs

    def _get_searchbar_groupby(self):
        searchbar_groupby = super()._get_searchbar_groupby()
<<<<<<< HEAD
        searchbar_groupby.update(
            so={'input': 'so', 'label': _('Sales Order')},
            sol={'input': 'sol', 'label': _('Sales Order Item')},
            invoice={'input': 'invoice', 'label': _('Invoice')})
=======
        searchbar_groupby.update(sol={'input': 'sol', 'label': _('Sales Order Item')})
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        return searchbar_groupby

    def _get_search_domain(self, search_in, search):
        search_domain = super()._get_search_domain(search_in, search)
        if search_in in ('sol', 'all'):
            search_domain = expression.OR([search_domain, [('so_line', 'ilike', search)]])
<<<<<<< HEAD
        if search_in in ('so', 'all'):
            search_domain = expression.OR([search_domain, [('so_line.order_id.name', 'ilike', search)]])
        if search_in in ('invoice', 'all'):
            invoices = request.env['account.move'].sudo().search([('name', 'ilike', search)])
            domain = request.env['account.analytic.line']._timesheet_get_sale_domain(invoices.mapped('invoice_line_ids.sale_line_ids'), invoices)
=======
        if search_in in ('sol_id', 'invoice_id'):
            search = int(search) if search.isdigit() else 0
        if search_in == 'sol_id':
            search_domain = expression.OR([search_domain, [('so_line.id', '=', search)]])
        if search_in == 'invoice_id':
            invoice = request.env['account.move'].browse(search)
            domain = request.env['account.analytic.line']._timesheet_get_sale_domain(invoice.mapped('invoice_line_ids.sale_line_ids'), invoice)
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            search_domain = expression.OR([search_domain, domain])
        return search_domain

    def _get_groupby_mapping(self):
        groupby_mapping = super()._get_groupby_mapping()
<<<<<<< HEAD
        groupby_mapping.update(
            sol='so_line',
            so='order_id',
            invoice='timesheet_invoice_id')
        return groupby_mapping

    def _get_searchbar_sortings(self):
        searchbar_sortings = super()._get_searchbar_sortings()
        searchbar_sortings.update(
            sol={'label': _('Sales Order Item'), 'order': 'so_line'})
        return searchbar_sortings

    def _task_get_page_view_values(self, task, access_token, **kwargs):
        values = super()._task_get_page_view_values(task, access_token, **kwargs)
        values['so_accessible'] = False
        try:
            if task.sale_order_id and self._document_check_access('sale.order', task.sale_order_id.id):
                values['so_accessible'] = True
                title = _('Quotation') if task.sale_order_id.state in ['draft', 'sent'] else _('Sales Order')
                values['task_link_section'].append({
                    'access_url': task.sale_order_id.get_portal_url(),
                    'title': title,
                })
        except (AccessError, MissingError):
            pass

        moves = request.env['account.move']
        invoice_ids = task.sale_order_id.invoice_ids
        if invoice_ids and request.env['account.move'].check_access_rights('read', raise_exception=False):
            moves = request.env['account.move'].search([('id', 'in', invoice_ids.ids)])
            values['invoices_accessible'] = moves.ids
            if moves:
                if len(moves) == 1:
                    task_invoice_url = moves.get_portal_url()
                    title = _('Invoice')
                else:
                    task_invoice_url = f'/my/tasks/{task.id}/orders/invoices'
                    title = _('Invoices')
                values['task_link_section'].append({
                    'access_url': task_invoice_url,
                    'title': title,
                })
        return values

    @http.route(['/my/timesheets', '/my/timesheets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_timesheets(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='sol', **kw):
=======
        groupby_mapping.update(sol='so_line')
        return groupby_mapping

    @http.route(['/my/timesheets', '/my/timesheets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_timesheets(self, page=1, sortby=None, filterby=None, search=None, search_in='all', groupby='sol', **kw):
        if search and search_in and search_in in ('sol_id', 'invoice_id') and not search.isdigit():
            search = '0'
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        return super().portal_my_timesheets(page, sortby, filterby, search, search_in, groupby, **kw)
