# -*- coding: utf-8 -*-

{
    "name" : "Purchase Tender Based on Supplier",
    "author": "Edge Technologies",
    "version" : "13.0.1.0",
    "live_test_url":'https://youtu.be/f98b49uiTaI',
    "images":["static/description/main_screenshot.png"],
    'summary': 'This app is created the to avoid problems of the customers during creating purchase order with multiple vendors. User can create purchase order with the choosen products.',
    "description": """ Purchase Tender helps customers to select the best quotation among all the purchase orders. Change quantities of selected quotation.
Odoo previous versions had Tender Bidding Procurement to choose Best Vendor/Supplier, so this app helps to choose best Request for proposal RFQ , this module helps to avoid problems of the customers during creating purchase order with multiple vendors. User can create purchase order with the chosen products and most suitable supplier from bid in tendering process by this Odoo ERP module
Tender Bidding for supplier
Bidding Procurement
supplier bidding

Tender Bidding Procurement for Best Supplier
Bidding process
Tender management  Bid Supplier Price Comparision
Request for Proposal RFP
RFP
bids for best supplier 
bidding process 
  supplier bidding process supplier tender bidding process

Procurement bidding process
tender Procurement process 
Procurement for supplier 
supplier Procurement
vendor Procurement
Procurement of vendors

   Choose Best Supplier On Tender
Tender Procurement for Best Supplier
Procurement for Best Supplier
Procurement Supplier
Supplier Procurement
 Best Supplier Purchase Tender
 tender Best Supplier
tendr requisition by supplier best supplier from tender process
purchase requisition with supplier purchase procurement process material purchase requisition supplier material requisition


 """,
    "license" : "OPL-1",
    "depends" : ['base','purchase','purchase_requisition','purchase_requisition_stock'],
    "data": [   
        'views/purchase_agreement_views.xml',
        'wizard/quantity_wizard_views.xml',
        'wizard/generate_views.xml',
        'data/data.xml',
        'security/ir.model.access.csv',
    ],
    "auto_install": False,
    "installable": True,
    "price": 58,
    "currency": 'EUR',
    "category" : "Purchase",
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
