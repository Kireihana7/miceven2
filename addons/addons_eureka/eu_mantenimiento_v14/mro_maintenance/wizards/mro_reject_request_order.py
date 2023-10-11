# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MroRequestOrderReject(models.TransientModel):
    _name = 'mro.request.order.reject'
    _description = 'Reject Request from Order'

    reject_reason = fields.Text(_('Reject Reason'), required=True)


    def reject_request_order(self):
        order_id = self.env.context.get('active_id', False)
        request_obj = self.env['mro.request']
        if order_id:
            order = self.env['mro.order'].browse(order_id)
            order.write({'state': 'cancel'})
            order.write({'reject_reason': self.reject_reason})
            request = request_obj.search([('name', '=', order.request_id.name)])
            if request:
                request.write({'reject_reason': self.reject_reason})
                request.action_reject()
                current_user_id = order.write_uid or order.create_uid
                if current_user_id.partner_id.email and order.request_id.requested_by.partner_id.email:
                    self.sudo().request_rejection_mail_send(current_user_id.partner_id.email, order.request_id.requested_by.partner_id.email)
        return True

    def request_rejection_mail_send(self, email_from, email_to):
        mail_obj = self.env['mail.mail']
        order_id = self._context.get('active_id', False)
        order = self.env['mro.order'].browse(order_id)
        subject = 'Maintenance Rejection: '+ str(order.request_id.name)
        mail_data = {
                    'subject': subject,
                    'body_html': order.reject_reason,
                    'email_from': email_from,
                    'email_to': email_to,
                    }
        mail_id = mail_obj.create(mail_data)
        mail_id.send()
        return True
