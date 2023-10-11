# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
from ast import literal_eval
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    # Loyalty Fields


    # product Expiry report
    mailsend_check = fields.Boolean(string="Send Mail")
    email_notification_days = fields.Integer(string="Expiry Alert Days")
    res_user_ids = fields.Many2many('res.users', string='Users')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param_obj = self.env['ir.config_parameter'].sudo()
        res_user_ids = param_obj.sudo().get_param('eu_expiry_report_alerts_and_email.res_user_ids')
        if res_user_ids:
            res.update({
                'res_user_ids': literal_eval(res_user_ids),
            })
        res.update({
            'mailsend_check': self.env['ir.config_parameter'].sudo().get_param('eu_expiry_report_alerts_and_email.mailsend_check'),
            'email_notification_days': int(param_obj.sudo().get_param('eu_expiry_report_alerts_and_email.email_notification_days')),
        })

        IrDefault = self.env['ir.default'].sudo()
        return res

    def set_values(self):
        param_obj = self.env['ir.config_parameter'].sudo()

        param_obj.sudo().set_param('eu_expiry_report_alerts_and_email.mailsend_check', self.mailsend_check)
        param_obj.sudo().set_param('eu_expiry_report_alerts_and_email.res_user_ids', self.res_user_ids.ids)
        param_obj.sudo().set_param('eu_expiry_report_alerts_and_email.email_notification_days', self.email_notification_days)
        IrDefault = self.env['ir.default'].sudo()
        return super(ResConfigSettings, self).set_values()

    # @api.model
    # def load_loyalty_config_settings(self):
    #     record = {}

    #     min_order_value = self.env['ir.config_parameter'].sudo().search(
    #         [('key', '=', 'eu_expiry_report_alerts_and_email.min_order_value')])
    #     if min_order_value:
    #         record['min_order_value'] = min_order_value.value

    #     point_calculation = self.env['ir.config_parameter'].sudo().search(
    #         [('key', '=', 'eu_expiry_report_alerts_and_email.point_calculation')])
    #     if point_calculation:
    #         record['point_calculation'] = point_calculation.value

    #     exclude_tax = self.env['ir.config_parameter'].sudo().search(
    #         [('key', '=', 'eu_expiry_report_alerts_and_email.exclude_tax')])
    #     if exclude_tax:
    #         record['exclude_tax'] = exclude_tax.value

    #     amount_per_point = self.env['ir.config_parameter'].sudo().search(
    #         [('key', '=', 'eu_expiry_report_alerts_and_email.amount_per_point')])
    #     if amount_per_point:
    #         record['amount_per_point'] = amount_per_point.value

    #     enable_customer_referral = self.env['ir.config_parameter'].sudo().search(
    #         [('key', '=', 'eu_expiry_report_alerts_and_email.enable_customer_referral')])
    #     if enable_customer_referral:
    #         record['enable_customer_referral'] = enable_customer_referral.value

    #     referral_event = self.env['ir.config_parameter'].sudo().search(
    #         [('key', '=', 'eu_expiry_report_alerts_and_email.referral_event')])
    #     if referral_event:
    #         record['referral_event'] = referral_event.value

    #     referral_point_calculation = self.env['ir.config_parameter'].sudo().search(
    #         [('key', '=', 'eu_expiry_report_alerts_and_email.referral_point_calculation')])
    #     if referral_point_calculation:
    #         record['referral_point_calculation'] = referral_point_calculation.value

    #     enable_loyalty = self.env['ir.config_parameter'].sudo().search(
    #         [('key', '=', 'eu_expiry_report_alerts_and_email.enable_loyalty')])
    #     if enable_loyalty:
    #         record['enable_loyalty'] = enable_loyalty.value

    #     exclude_category = self.env['ir.config_parameter'].sudo().search(
    #         [('key', '=', 'eu_expiry_report_alerts_and_email.exclude_category')])
    #     if exclude_category:
    #         record['exclude_category'] = literal_eval(exclude_category.value)
    #     return [record]
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
