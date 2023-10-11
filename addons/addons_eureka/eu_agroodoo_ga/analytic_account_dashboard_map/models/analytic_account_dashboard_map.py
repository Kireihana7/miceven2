from odoo import api, fields, models, _
from odoo.http import request
from odoo.exceptions import UserError, ValidationError

class AnalyticAccountDashboadMap(models.Model):
    _inherit = 'account.analytic.account'

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
        land_division = args[2]
        measures = args[3]
        country_code = args[4]
        farmer = args[5]
        company_id = self.get_current_company_value()
                
        lj_res_country = 'LEFT JOIN res_country ON res_country.id = res_country_state.country_id'
        lj_agriculture_fincas = 'LEFT JOIN agriculture_fincas ON agriculture_fincas.state_id = res_country_state.id'
        res_country_filter = '''
            WHERE res_country.code = \''''+country_code+'''\'
        '''

        data = []

        sql = f'''
            SELECT 
                agriculture_fincas.id AS finca_id,
                res_country_state.name AS country_state,
                COUNT(agriculture_fincas.id) AS farm_count
            FROM res_country_state 

            {lj_res_country}
            {lj_agriculture_fincas}

            {res_country_filter}
            GROUP BY country_state, agriculture_fincas.id
        '''

        if measures == '1': # <------- Quantity of elements
            # Filtrar por Fincas:
            if land_division == 'farm':
                sql = f'''
                    SELECT 
                        agriculture_fincas.id AS finca_id,
                        res_country_state.name AS country_state,
                        COUNT(agriculture_fincas.id) AS farm_count,
                        agriculture_fincas.parcel_count AS parcel_count
                    FROM res_country_state 

                    {lj_res_country}
                    {lj_agriculture_fincas} 

                    {res_country_filter}
                    GROUP BY country_state, agriculture_fincas.id, parcel_count
                '''

            # Filtrar por Parcelas:
            if land_division == 'parcel':
                sql = f'''
                    SELECT 
                        agriculture_fincas.id AS finca_id,
                        res_country_state.name AS country_state,
                        COUNT(agriculture_parcelas.id) AS parcel_count
                    FROM res_country_state 

                    {lj_res_country}
                    {lj_agriculture_fincas} 
                    LEFT JOIN agriculture_parcelas ON agriculture_parcelas.finca_id = agriculture_fincas.id
                    
                    {res_country_filter}
                    GROUP BY country_state, agriculture_fincas.id
                '''            

            # Filtrar por Tablones:
            if land_division == 'tablon':
                sql = f'''
                    SELECT 
                        agriculture_fincas.id AS finca_id,
                        res_country_state.name AS country_state,
                        COUNT(agriculture_tablon.id) AS tablon_count
                    FROM res_country_state 

                    {lj_res_country}
                    {lj_agriculture_fincas} 
                    LEFT JOIN agriculture_parcelas ON agriculture_parcelas.finca_id = agriculture_fincas.id
                    LEFT JOIN agriculture_tablon ON agriculture_tablon.parcel_id = agriculture_parcelas.id
                
                    {res_country_filter}
                    GROUP BY country_state, agriculture_fincas.id
                '''   
        elif measures == '0': # <------- Analytic Entries

            lj_analytic_line = 'LEFT JOIN account_analytic_line ON account_analytic_line.finca_id = agriculture_fincas.id'
            analytic_line_date_filter = f'AND account_analytic_line.date BETWEEN \'{from_date}\' AND \'{to_date}\''

            # Filtrar por Fincas:
            if land_division == 'farm':
                sql = f'''
                    SELECT 
                        agriculture_fincas.id AS finca_id,
                        res_country_state.name AS country_state,
                        SUM(account_analytic_line.amount) as amount_total_farm
                    FROM res_country_state 

                    {lj_res_country}
                    {lj_agriculture_fincas} 
                    {lj_analytic_line}

                    {res_country_filter}
                    {analytic_line_date_filter}
                    GROUP BY country_state, agriculture_fincas.id
                '''

            # Filtrar por Parcelas:
            if land_division == 'parcel':
                sql = f'''
                    SELECT 
                        agriculture_fincas.id AS finca_id,
                        res_country_state.name AS country_state,
                        SUM(account_analytic_line.amount) as amount_total_farm
                    FROM res_country_state 

                    {lj_res_country}
                    {lj_agriculture_fincas} 
                    {lj_analytic_line}
                
                    {res_country_filter}
                    {analytic_line_date_filter}
                    GROUP BY country_state, agriculture_fincas.id
                '''

                self._cr.execute(sql)
                farms = self._cr.dictfetchall()
                if len(farms) > 0:
                    i = 0
                    for farm in farms:
                        finca_id = farm['finca_id']
                        amount_total_parcel = 0
                        if finca_id:
                            sql_parcel = '''
                                SELECT 
                                    id
                                FROM agriculture_parcelas 
                                WHERE finca_id = \''''+str(finca_id)+'''\'
                            '''
                            self._cr.execute(sql_parcel)
                            parcels = self._cr.dictfetchall()

                            if len(parcels) > 0:
                                j = 0
                                for parcel in parcels:
                                    parcel_id = parcel['id']
                                    if parcel_id:
                                        sql_parcel_amount = '''
                                            SELECT 
                                                SUM(amount) as amount_parcel
                                            FROM account_analytic_line 
                                            WHERE parcel_id = \''''+str(parcel_id)+'''\'
                                        '''                        
                                        self._cr.execute(sql_parcel_amount)
                                        amount_total_result = self._cr.dictfetchall()
                                        if len(amount_total_result) > 0:
                                            for line in amount_total_result:
                                                if line['amount_parcel']:
                                                    amount_total_parcel += line['amount_parcel']
                                    j += 1             

                            farm['amount_total_parcel'] = amount_total_parcel
                        i += 1 

                # Retornando datos:
                # return farms
                data = farms                                   

            # Filtrar por Tablones:
            if land_division == 'tablon':
                sql = f'''
                    SELECT 
                        agriculture_fincas.id AS finca_id,
                        res_country_state.name AS country_state,
                        SUM(account_analytic_line.amount) as amount_total_farm
                    FROM res_country_state

                    {lj_res_country}
                    {lj_agriculture_fincas} 
                    {lj_analytic_line}
                
                    {res_country_filter}
                    {analytic_line_date_filter}
                    GROUP BY country_state, agriculture_fincas.id
                '''

                self._cr.execute(sql)
                farms = self._cr.dictfetchall()
                if len(farms) > 0:
                    i = 0
                    for farm in farms:
                        finca_id = farm['finca_id']
                        amount_total_parcel = 0
                        amount_total_tablon = 0
                        
                        if finca_id:
                            sql_parcel = '''
                                SELECT 
                                    id
                                FROM agriculture_parcelas 
                                WHERE finca_id = \''''+str(finca_id)+'''\'
                            '''
                            self._cr.execute(sql_parcel)
                            parcels = self._cr.dictfetchall()

                            if len(parcels) > 0:
                                j = 0
                                for parcel in parcels:
                                    parcel_id = parcel['id']
                                    if parcel_id:
                                        sql_parcel_amount = '''
                                            SELECT 
                                                SUM(amount) as amount_parcel
                                            FROM account_analytic_line 
                                            WHERE parcel_id = \''''+str(parcel_id)+'''\'
                                        '''                        
                                        self._cr.execute(sql_parcel_amount)
                                        amount_total_result = self._cr.dictfetchall()
                                        if len(amount_total_result) > 0:
                                            for line in amount_total_result:
                                                if line['amount_parcel']:
                                                    amount_total_parcel += line['amount_parcel']
                                        
                                        # Tablones:
                                        sql_tablon = '''
                                            SELECT 
                                                id
                                            FROM agriculture_tablon 
                                            WHERE parcel_id = \''''+str(parcel_id)+'''\'
                                        '''                                        
                                        self._cr.execute(sql_tablon)
                                        tablones = self._cr.dictfetchall()
                                        if len(tablones) > 0:
                                            for tablon in tablones:
                                                tablon_id = tablon['id']
                                                if tablon_id:
                                                    sql_tablon_amount = '''
                                                        SELECT 
                                                            SUM(amount) as amount_tablon
                                                        FROM account_analytic_line 
                                                        WHERE tablon_id = \''''+str(tablon_id)+'''\'
                                                    '''                        
                                                    self._cr.execute(sql_tablon_amount)
                                                    amount_total_result_tablon = self._cr.dictfetchall()
                                                    if len(amount_total_result_tablon) > 0:
                                                        for line in amount_total_result_tablon:
                                                            if line['amount_tablon']:
                                                                amount_total_tablon += line['amount_tablon']                                                    

                                    j += 1             

                            farm['amount_total_parcel'] = amount_total_parcel
                            farm['amount_total_tablon'] = amount_total_tablon
                        i += 1 

                # Retornando datos:
                # return farms
                data = farms         

        self._cr.execute(sql)
        record = self._cr.dictfetchall()
        data = record

        x = []
        if len(data) > 0:
            i = 0
            for dict_item in data:
                for key in dict_item:
                    if key == 'finca_id':
                        if dict_item[key] is not None:
                            # data.pop(i)
                            x.append(dict_item)
                i += 1
        # raise UserError(_(data))

        # Verificando el farmer:
        result = []
        if farmer != 'all':
            for line in x:
                finca_id = line['finca_id']
                sql_finca_partner = f'''
                    SELECT 
                        *
                    FROM finca_partner_rel 

                    WHERE finca_id = {finca_id}
                    AND partner_id = {farmer}
                '''
                self._cr.execute(sql_finca_partner)
                result_finca_partner = self._cr.dictfetchall()
                if len(result_finca_partner) > 0:
                    result.append(line)
        else:
            result = x
            
        return result
        # return record

    def load_data_region(self, *args):

        # from_date = args[0]
        # to_date = args[1]
        # state = args[2]
        # measures = args[3]
        # region = args[4]
        # sale_person = args[5]
        # company_id = self.get_current_company_value()
        # sale_person_c = 'AND true '
        # if not sale_person == 'all':
        #     sale_person_c = 'AND so.user_id = '+sale_person
        # # sql = '''
        # #                 SELECT rc.name AS country, SUM(so.'''+measures+''') AS amount 
        # #                 FROM sale_order AS so LEFT JOIN res_partner AS rp ON so.partner_id = rp.id 
        # #                 LEFT JOIN res_country AS rc ON rp.country_id = rc.id 
        # #                 WHERE TO_DATE(TO_CHAR(so.date_order, 'YYYY-MM-DD'), 'YYYY-MM-DD') >= \''''+from_date+'''\' and TO_DATE(TO_CHAR(so.date_order, 'YYYY-MM-DD'), 'YYYY-MM-DD') <= \''''+to_date+'''\'
        # #                 AND so.state = \''''+state+'''\' 
        # #                 AND so.company_id in ''' + str(tuple(company_id)) + '''
        # #                 '''+sale_person_c+'''
        # #                 GROUP BY country 
        # #                 ORDER BY amount 
        # # '''
        # sql = '''
        #                 SELECT 
        #                     res_country_state.name AS country_state, 
        #                     COUNT(agriculture_fincas.id) AS amount 
        #                 FROM agriculture_fincas 
        #                 LEFT JOIN res_country_state ON agriculture_fincas.state_id = res_country_state.id 
        #                 LEFT JOIN res_country ON agriculture_fincas.country_id = res_country.id 
        #                 WHERE res_country.code = \''''+region+'''\' 
        #                 GROUP BY country_state 
        #                 ORDER BY amount 
        # '''        
        # self._cr.execute(sql)
        # record = self._cr.dictfetchall()
        # # return record
        # return 'Aldana'

        # ======================================================================= #
        # ======================================================================= #
        # ======================================================================= #

        from_date = args[0]
        to_date = args[1]
        land_division = args[2]
        measures = args[3]
        country_code = args[4]
        sale_person = args[5]
        company_id = self.get_current_company_value()
        farmer = 'AND true '
        if not sale_person == 'all':
            farmer = 'AND so.user_id = ' + sale_person

        # sql = '''
        #                 SELECT 
        #                     res_country_state.name AS country_state, 
        #                     COUNT(agriculture_fincas.id) AS amount 
        #                 FROM agriculture_fincas 
        #                 LEFT JOIN res_country_state ON agriculture_fincas.state_id = res_country_state.id 
        #                 LEFT JOIN res_country ON agriculture_fincas.country_id = res_country.id 
        #                 WHERE res_country.code = \''''+country_code+'''\' 
        #                 GROUP BY country_state 
        #                 ORDER BY amount 
        # '''

        sql = '''
            SELECT 
                res_country_state.name AS country_state,
                COUNT(agriculture_fincas.id) AS farm_count,
                agriculture_fincas.parcel_count AS parcel_count
            FROM res_country_state 

            LEFT JOIN res_country ON res_country.id = res_country_state.country_id
            LEFT JOIN agriculture_fincas ON agriculture_fincas.state_id = res_country_state.id 

            WHERE res_country.code = \''''+country_code+'''\'
            GROUP BY country_state, parcel_count
        '''

        if measures == '1':
            # Filtrar por Fincas:
            if land_division == 'farm':
                sql = '''
                    SELECT 
                        res_country_state.name AS country_state,
                        COUNT(agriculture_fincas.id) AS farm_count,
                        agriculture_fincas.parcel_count AS parcel_count
                    FROM res_country_state 

                    LEFT JOIN res_country ON res_country.id = res_country_state.country_id
                    LEFT JOIN agriculture_fincas ON agriculture_fincas.state_id = res_country_state.id 

                    WHERE res_country.code = \''''+country_code+'''\'
                    GROUP BY country_state, parcel_count
                '''

            # Filtrar por Parcelas:
            if land_division == 'Parcels':
                sql = '''
                    SELECT 
                        res_country_state.name AS country_state,
                        COUNT(agriculture_parcelas.id) AS parcel_count
                    FROM res_country_state 

                    LEFT JOIN res_country ON res_country.id = res_country_state.country_id
                    LEFT JOIN agriculture_fincas ON agriculture_fincas.state_id = res_country_state.id 
                    LEFT JOIN agriculture_parcelas ON agriculture_parcelas.finca_id = agriculture_fincas.id
                    
                    WHERE res_country.code = \''''+country_code+'''\'
                    GROUP BY country_state
                '''            

            # Filtrar por Tablones:
            if land_division == 'Parcels':
                sql = '''
                    SELECT 
                        res_country_state.name AS country_state,
                        COUNT(agriculture_tablon.id) AS tablon_count
                    FROM res_country_state 

                    LEFT JOIN res_country ON res_country.id = res_country_state.country_id
                    LEFT JOIN agriculture_fincas ON agriculture_fincas.state_id = res_country_state.id 
                    LEFT JOIN agriculture_parcelas ON agriculture_parcelas.finca_id = agriculture_fincas.id
                    LEFT JOIN agriculture_tablon ON agriculture_tablon.parcel_id = agriculture_parcelas.id
                
                    WHERE res_country.code = \''''+country_code+'''\'
                    GROUP BY country_state
                '''                        

        self._cr.execute(sql)
        record = self._cr.dictfetchall()
        return record        
        

    def get_all_farmers(self):
        # company_id = self.get_current_company_value()
        
        # sql = '''
        #     SELECT ru.id as id, rp.name as name 
        #     FROM sale_order AS so 
        #     LEFT JOIN res_users AS ru ON so.user_id = ru.id
        #     LEFT JOIN res_partner AS rp ON ru.partner_id = rp.id
        #     WHERE so.company_id in ''' + str(tuple(company_id)) + '''
        #     GROUP BY ru.id, rp.name
        # '''

        company_id = self.env.company.id

        sql = '''
            SELECT *
            FROM res_partner 
            WHERE is_farmer = true
        '''

        self._cr.execute(sql)
        record = self._cr.dictfetchall()
        return record
        # return 'Test'


