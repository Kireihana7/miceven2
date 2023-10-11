from odoo import fields, models,api,_
from odoo.exceptions import UserError
from datetime import date,datetime
from odoo.tools.misc import format_date
from calendar import monthrange
from xlrd import open_workbook
import base64

TODAY = date.today()
class HrActTasaIntPresWiz(models.TransientModel):
    
    _name="act_tasa_int_pres_wiz"


    archivo =fields.Binary( string="Archivo XLS",required=True)


    def readed(self):

        # LEEEMOS EL ARCHIVOOOOOOO
        file_data = base64.b64decode(self.archivo)
        wb = open_workbook(file_contents=file_data)
        page=wb.sheet_by_index(0)
        # nos paramos en el punto inicial
        data_storm=[]
        auxiliar_year=1
        data_line=[]
        for i in range(0,page.nrows-8-3):
            # obtenemos el año por el cual transitamos
            if str(page.cell_value(i+8,0)).isdigit() and int(page.cell_value(i+8,0))!=auxiliar_year:
                auxiliar_year=int(page.cell_value(i+8,0))
                data_storm.append(data_line)
                data_line=[]
            elif not str(page.cell_value(i+8,0)).isdigit() and page.cell_value(i+8,0)!=False:
                data_line.append([auxiliar_year,page.cell_value(i+8,0),page.cell_value(i+8,5)])



        raise UserError(data_storm)



