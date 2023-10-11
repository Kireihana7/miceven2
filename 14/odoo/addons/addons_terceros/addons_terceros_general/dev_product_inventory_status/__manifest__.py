# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
{
    'name': 'Product Inventory Status Notification',
    'version': '14.0.1.0',
    'sequence': 1,
    'category': 'Warehouse',
    'description':
        """ 
        This Apps add below functionality into odoo 
        
        1.This module helps you send specify user Product Inventory Status mail.

odoo inventory Status
odoo product inventory
odoo product inventory status
odoo notify inventory status
odoo status inventory notification
odoo inventory status notification

odoo app allow to send Product Inventory Status mail notification to specify user, product inventory,inventory Status,notify inventory status,status inventory notification, product inventory, stock status, product status , warehouse product stock status, location inventory status

        
    """,
    'summary': 'odoo app allow to send Product Inventory Status mail notification to specify user, product inventory,inventory Status,notify inventory status,status inventory notification, product inventory, stock status, product status , warehouse product stock status, location inventory status', 
    'depends': ['sale_management','stock'],
    'data': [
        
        'data/product_inventory_cron.xml',
        'report/product_report_menu.xml',
        'data/inventory_mail_template.xml',
        'report/product_report_template.xml',
        'views/res_config_views.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':15.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
