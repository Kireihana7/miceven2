# -*- coding: utf-8 -*-
#######################################################
# 
#   CorpoEureka - Innovation First!
#
#   Copyright (C) 2021-TODAY CorpoEureka (<https://www.corpoeureka.com>)
#   Author: CorpoEureka (<https://www.corpoeureka.com>)
#
#   This software and associated files (the "Software") may only be used (executed,
#   modified, executed after modifications) if you have pdurchased a vali license
#   from the authors, typically via Odoo Apps, or if you have received a written
#   agreement from the authors of the Software (see the COPYRIGHT file).
#
#   You may develop Odoo modules that use the Software as a library (typically
#   by depending on it, importing it and using its resources), but without copying
#   any source code or material from the Software. You may distribute those
#   modules under the license of your choice, provided that this license is
#   compatible with the terms of the Odoo Proprietary License (For example:
#   LGPL, MIT, or proprietary licenses similar to this one).
#
#   It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#   or modified copies of the Software.
#
#   The above copyright notice and this permission notice must be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#   IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#   DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#   ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.

#   Responsable CorpoEureka: Jose Mazzei y José Ñeri (aunque si mas hizo mazzei)
##########################################################################-
{
    "name" : "Secondary UoMs",
    "author" : "CorpoEureka",
    "website": "https://www.corpoeureka.com",
    "category": "Inventory",
    "summary": "",
    "description": """
    This app allow to show more UOMs, with this, you can use multi UOM in Inventory, Sale, Purchase, Accounting
    """,
    "version":"14.0.1.0",
    "depends" : [
                    "stock",
                    "sale",
                    "sale_management",
                    "account",
                    "purchase",
                ],
    "application" : True,
    "data" : [
            "security/secondary_unit_group.xml",
            "views/product_template_custom.xml",
            "views/product_custom.xml",
            "views/sale_order_view.xml",
            "views/purchase_order_view.xml",
            "views/stock_picking_view.xml",
            "views/stock_quants_secondary_views.xml",
            "views/account_invoice_view.xml",
            "views/stock_scrap_view.xml",
            ],
    "auto_install":False,
    "installable" : True,
}
