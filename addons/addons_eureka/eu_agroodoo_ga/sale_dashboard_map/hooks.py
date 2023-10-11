

def sale_dashboard_map_prepared(cr, registry):
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/Colombia.json?origen=module&code=CO' "
               "WHERE code = 'CO';")
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/Mexico.json?origen=module&code=MX' "
               "WHERE code = 'MX';")
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/USA.json?origen=module&code=US' "
               "WHERE code = 'US';")
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/Ecuador.json?origen=module&code=EC' "
               "WHERE code = 'EC';")
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/Guatemala.json?origen=module&code=GT' "
               "WHERE code = 'GT';")
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/España.json?origen=module&code=ES' "
               "WHERE code = 'ES';")
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/Brazil.json?origen=module&code=BR' "
               "WHERE code = 'BR';")
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/Italia.json?origen=module&code=IT' "
               "WHERE code = 'IT';")
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/Peru.json?origen=module&code=PE' "
               "WHERE code = 'PE';")
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/Chile.json?origen=module&code=CL' "
               "WHERE code = 'CL';")
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/Canada.json?origen=module&code=CA' "
               "WHERE code = 'CA';")
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/Venezuela.json?origen=module&code=VE' "
               "WHERE code = 'VE';")
    cr.execute("UPDATE res_country "
               "SET map_url = '/sale_dashboard_map/static/src/maps/Panama.json?origen=module&code=PA' "
               "WHERE code = 'PA';")

