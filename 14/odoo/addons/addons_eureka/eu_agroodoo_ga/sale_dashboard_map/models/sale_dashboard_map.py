from odoo import api, fields, models, _
from odoo.http import request

class SaleDashboadMap(models.Model):
    _inherit = 'sale.order'

    def get_current_company_value(self):
        cookies_cids = [int(r) for r in request.httprequest.cookies.get('cids').split(",")] \
            if request.httprequest.cookies.get('cids') \
            else [request.env.user.company_id.id]
        for company_id in cookies_cids:
            if company_id not in self.env.user.company_ids.ids:
                cookies_cids.remove(company_id)
        if not cookies_cids:
            cookies_cids = [self.env.company.id]
        if len(cookies_cids) == 1:
            cookies_cids.append(0)
        return cookies_cids

    def load_data_country(self, *args):

        from_date = args[0]
        to_date = args[1]
        state = args[2]
        measures = args[3]
        country_code = args[4]
        sale_person = args[5]
        company_id = self.get_current_company_value()
        sale_person_c = 'AND true '
        if not sale_person == 'all':
            sale_person_c = 'AND so.user_id = ' + sale_person
        sql = '''
                        SELECT rcs.name AS country_state, SUM(so.'''+measures+''') AS amount 
                        FROM sale_order AS so LEFT JOIN res_partner AS rp ON so.partner_id = rp.id 
                        LEFT JOIN res_country_state AS rcs ON rp.state_id = rcs.id 
                        LEFT JOIN res_country AS rc ON rp.country_id = rc.id 
                        WHERE rc.code = \''''+country_code+'''\' 
                        AND TO_DATE(TO_CHAR(so.date_order, 'YYYY-MM-DD'), 'YYYY-MM-DD') >= \''''+from_date+'''\' and TO_DATE(TO_CHAR(so.date_order, 'YYYY-MM-DD'), 'YYYY-MM-DD') <= \''''+to_date+'''\'
                        AND so.state = \''''+state+'''\' 
                        AND so.company_id in ''' + str(tuple(company_id)) + ''' 
                        '''+sale_person_c+''' 
                        GROUP BY country_state 
                        ORDER BY amount 
        '''
        self._cr.execute(sql)
        record = self._cr.dictfetchall()
        return record

    def load_data_region(self, *args):

        from_date = args[0]
        to_date = args[1]
        state = args[2]
        measures = args[3]
        region = args[4]
        sale_person = args[5]
        company_id = self.get_current_company_value()
        sale_person_c = 'AND true '
        if not sale_person == 'all':
            sale_person_c = 'AND so.user_id = '+sale_person
        sql = '''
                        SELECT rc.name AS country, SUM(so.'''+measures+''') AS amount 
                        FROM sale_order AS so LEFT JOIN res_partner AS rp ON so.partner_id = rp.id 
                        LEFT JOIN res_country AS rc ON rp.country_id = rc.id 
                        WHERE TO_DATE(TO_CHAR(so.date_order, 'YYYY-MM-DD'), 'YYYY-MM-DD') >= \''''+from_date+'''\' and TO_DATE(TO_CHAR(so.date_order, 'YYYY-MM-DD'), 'YYYY-MM-DD') <= \''''+to_date+'''\'
                        AND so.state = \''''+state+'''\' 
                        AND so.company_id in ''' + str(tuple(company_id)) + '''
                        '''+sale_person_c+'''
                        GROUP BY country 
                        ORDER BY amount 
        '''
        self._cr.execute(sql)
        record = self._cr.dictfetchall()
        return record

    def get_all_vendor(self):
        company_id = self.get_current_company_value()
        sql = '''
            SELECT ru.id as id, rp.name as name 
            FROM sale_order AS so 
            LEFT JOIN res_users AS ru ON so.user_id = ru.id
            LEFT JOIN res_partner AS rp ON ru.partner_id = rp.id
            WHERE so.company_id in ''' + str(tuple(company_id)) + '''
            GROUP BY ru.id, rp.name
        '''
        self._cr.execute(sql)
        record = self._cr.dictfetchall()
        return record


