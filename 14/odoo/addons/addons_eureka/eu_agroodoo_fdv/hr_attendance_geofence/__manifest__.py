# -*- coding: utf-8 -*-
#################################################################################
# Author      : CFIS (<https://www.cfis.store/>)
# Copyright(c): 2017-Present CFIS.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://www.cfis.store/>
#################################################################################

{
    "name": "HR Attendance Geofence | Geo-Fencing | Geofencing | Geofence | Geolocation | Attendance Geolocation | Attendance Location Restriction",
    "summary": """
        The odoo Hr Attendance Manager / Administrators can use this module to create a virtual geographic boundary 
        for attendance locations, and employees can only check in and out within one of these Geofence areas.
    """,
    "version": "14.0.1",
    "description": """
        The odoo Hr Attendance Manager / Administrators can use this module to create a virtual geographic boundary 
        for attendance locations, and employees can only check in and out within one of these Geofence areas.
        HR Attendance Geofencing
        Geofencing
        Attendance Geofence          
    """,    
    "author": "CFIS",
    "maintainer": "CFIS",
    "license" :  "Other proprietary",
    "website": "https://www.cfis.store",
    "images": ["images/hr_attendance_geofence.png"],
    "category": "Sales",
    "depends": [
        "base",
        "hr_attendance",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/geolocation_data.xml",
        "views/assets.xml",
        "views/hr_attendance_geofence.xml",
        "views/hr_attendance_views.xml",
        "views/res_users.xml",
        "views/ir_sequence_geofence.xml"
    ],
    "qweb": [
        "static/src/xml/*.xml"
    ],    
    "installable": True,
    "application": True,
    "price"                 :  150.00,
    "currency"              :  "EUR",
    "pre_init_hook"         :  "pre_init_check",
    'uninstall_hook': 'uninstall_hook',
}
