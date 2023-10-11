# -*- coding: utf-8 -*-

from . import models
from . import wizard
from odoo import api, SUPERUSER_ID
import requests

def _insert_default_crop_types(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    crop_data = requests.get('https://crop-monitoring.eos.com/backend/crop-type/?api_key=apk.85114272aff12e873f3d9d209cb1717bbf3e3b53e30d8e6db3c2aefeea3a2661&format=json')
    crop_data = crop_data.json()

    # crop_names = []
    for i, crop in enumerate(crop_data):
        crop_dic = crop_data[i]

        default_id = (crop_dic['id'])
        name_en = (crop_dic['name_en'])
        name_uk = (crop_dic['name_uk'])    
        name_ru = (crop_dic['name_ru'])
        name_pt = (crop_dic['name_pt'])
        name_es = (crop_dic['name_es'])
        name_fr = (crop_dic['name_fr'])
        name_en = (crop_dic['name_en'])
        color = (crop_dic['color'])
        maturities = (crop_dic['maturities'])

        # Insertando datos:
        env['farmer.location.crops'].create({
            'name': name_es,
            'default_id': default_id,
            'name_en': name_en,
            'name_uk': name_uk,    
            'name_ru': name_ru,
            'name_pt': name_pt,
            'name_es': name_es,
            'name_fr': name_fr,
            'name_en': name_en,
            'color': color,
        })

        crop_id = env['farmer.location.crops'].search([])[-1].id
        
        if(len(maturities) > 0):
            for j, maturity in enumerate(maturities):
                maturity_dic = maturities[j]

                default_id = maturity_dic['id']
                name = maturity_dic['name']

                env['farmer.location.crops.maturities'].create({
                    'crop_id': crop_id,
                    'default_id': default_id,
                    'name': name,                        
                })


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: