# -*- coding: utf-8 -*-
{
    "name": "Sale Order Approval Check Lists",
    "version": "13.0.1.0.1",
    "category": "sales",
    "author": "Odoo Tools",
    "website": "corpoeureka.com",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "sale",'sale_management',
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/sale_order.xml",
        "views/check_company_list.xml",
        "data/data.xml"
    ],
    "qweb": [
        
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to make sure a sale order is ready for the next stage",
    "description": """
    
""",
    "images": [
        "static/description/main.png"
    ],
}