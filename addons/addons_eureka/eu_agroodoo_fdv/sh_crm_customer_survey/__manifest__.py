# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "CRM Survey Management",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "14.0.3",
    "license": "OPL-1",
    "category": "Marketing",
    "summary": "Customer Survey Management, User Survey,customer Feedback, Perform Market Search,Customer Survey In Lead, Customer Survey In Pipeline,Survey For Feedback, Client Survey Send Email,take survey,manage surveys,Customers Survey Odoo",
    "description": """Customer Surveys are a method of getting consumer feedback to help companies measure satisfaction, perform market research. Our module will provide a customer survey from the CRM(lead/opportunity/pipeline). We provide two different ways to manage surveys first is just send a survey form on customer's emails and filled by customer and the second way is the employee will visit the customer and ask survey questions answers will be filled by the employee of the company on behalf of the customer. One more important feature is easy to pause and resume the incomplete survey form.""",
    "depends": [
        'survey',
        'eu_sales_visit',
    ],
    "data": [
        'views/res_visit_view.xml',
        'views/res_config_settings.xml',
    ],
    "images": ["static/description/background.png",],           
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": "35",
    "currency": "EUR"
}
