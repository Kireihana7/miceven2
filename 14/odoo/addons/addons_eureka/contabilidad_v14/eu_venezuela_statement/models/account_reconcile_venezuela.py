# -*- coding: utf-8 -*-
import tempfile
import binascii
import xlrd
from odoo.exceptions import Warning,UserError
from odoo import models, fields, exceptions, api, _
import time
from datetime import date, datetime
import io
import logging
import csv
from odoo.tools import translate
_logger = logging.getLogger(__name__)
from odoo.tools.misc import file_open, mute_logger

try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class AccountReconcileVenezuela(models.TransientModel):
    _name = "account.reconcile.venezuela"

    file = fields.Binary('Archivo',required=True)
    date = fields.Date(string='Fecha del Extracto',default=fields.Date.context_today)
    journal_id = fields.Many2one('account.journal', string="Diario del Extracto",domain="[('type', '=', 'bank')]")
    bank_option = fields.Selection(
        [
        ('0102','Banco de Venezuela - 0102'),
        ('0105','Banco Mercantil - 0105'),
        ('0108','Banco Provincial - 0108'),
        ('0114','BanCaribe - 0114'),
        ('0115','Banco Exterior - 0115'),
        ('0172','Bancamiga - 0172'),
        ('0174','BanPlus - 0174'),
        ('BANPA','Banesco Panamá'),
        ('BANCU','Banesco Custodia'),
        ],
        string='Banco Origen', 
        required=True)


    def import_account(self):
        contador = 0
        statement = self.env['account.bank.statement'].create({
            'date': self.date,
            'name': self.date,
            'journal_id':self.journal_id.id,
        })
        # Si el Banco no es VENEZUELA, BANCARIBE, BANESCO PANAMÁ
        # Esto es por el tipo de Formato, aquí van los .xlsx
        if self.bank_option not in ('0114','0102'):
            fp = tempfile.NamedTemporaryFile(delete=False,suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            res = {}
            try:
                workbook = xlrd.open_workbook(fp.name)
                sheet = workbook.sheet_by_index(0)
            except Exception:
                raise Warning(_("El formato del archivo no corresponde a un .xlsx"))
            
            
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    contador += 1
                    # Banco Mercantil
                    if self.bank_option == '0105':
                        if line[5] not in ('SF','SI'):
                            values={
                                "date": datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(float(line[3])) - 2),
                                "amount": float(line[7]) if line[5] == 'NC' else -float(line[7]),
                                "ref": line[4],
                                "payment_ref": line[6],
                                #"manual_currency_exchange_rate":self.tasa_del_dia if self.tasa_del_dia != 0 else self.env.company.currency_id.parent_id.rate,
                            }
                            lines = [(0,0,values)]
                            statement.write({'line_ids':lines})
                    # Banco Exterior
                    if self.bank_option == '0115' and contador > 1:
                        values={
                            "date": datetime.strptime(line[1], "%d/%m/%y"),
                            "amount": float(line[3].replace('.','').replace(',','.')) if line[4] == '+' else -float(line[3].replace('.','').replace(',','.')),
                            "ref": line[2],
                            "payment_ref": line[0],
                            #"manual_currency_exchange_rate":self.tasa_del_dia if self.tasa_del_dia != 0 else self.env.company.currency_id.parent_id.rate,
                        }
                        lines = [(0,0,values)]
                        statement.write({'line_ids':lines})
                    # Banco Provincial
                    if self.bank_option == '0108' and line[0] != '':
                        fecha = ''
                        if line[0].find('\xa0'):
                            fecha = datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(float(line[0])) - 2)
                        else:
                            fecha = datetime.strptime(line[0][1:], "%d-%m-%Y") 
                        values={
                            "date": fecha,
                            "amount": float(line[5].replace('.','').replace(',','.')),
                            "ref": line[3],
                            "payment_ref": line[4],
                            #"manual_currency_exchange_rate":self.tasa_del_dia if self.tasa_del_dia != 0 else self.env.company.currency_id.parent_id.rate,
                        }
                        lines = [(0,0,values)]
                        statement.write({'line_ids':lines})
                    # Bancamiga
                    if self.bank_option == '0172' and contador > 3:
                        values={
                            "date": datetime.strptime(line[1][1:], "%d/%m/%y"),
                            "amount": -float(line[4]) if float(line[4]) != 0 else float(line[5]),
                            "ref": line[2][1:],
                            "payment_ref": line[3],
                            #"manual_currency_exchange_rate":self.tasa_del_dia if self.tasa_del_dia != 0 else self.env.company.currency_id.parent_id.rate,
                        }
                        lines = [(0,0,values)]
                        statement.write({'line_ids':lines})
                    # BanPlus
                    if self.bank_option == '0174' and line[0] != '':
                        values={
                            "date": datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(float(line[0])) - 2),
                            "amount": -float(line[3]) if line[3] != '' else float(line[4]),
                            "ref": line[1][1:],
                            "payment_ref": line[2],
                            #"manual_currency_exchange_rate":self.tasa_del_dia if self.tasa_del_dia != 0 else self.env.company.currency_id.parent_id.rate,
                        }
                        lines = [(0,0,values)]
                        statement.write({'line_ids':lines})
                    # Banesco Panamá
                    if self.bank_option == 'BANPA' and line[6] != '':
                        values={
                            "date": datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(float(line[0])) - 2),
                            "amount": -float(line[4]) if line[5] == '' else float(line[5]),
                            "ref": line[1],
                            "payment_ref": line[2],
                            #"manual_currency_exchange_rate":self.tasa_del_dia if self.tasa_del_dia != 0 else self.env.company.currency_id.parent_id.rate,
                        }
                        lines = [(0,0,values)]
                        statement.write({'line_ids':lines})
                    # Banesco Custodia
                    if self.bank_option == 'BANCU' and contador > 1:
                        amount = line[3]
                        if all(c in str(line[3]) for c in ',.'):
                            amount = float(str(line[3]).replace('.','').replace(',','.')) if line[4] == '+' else -float(str(line[3]).replace('.','').replace(',','.'))
                        else:
                            amount = float(str(line[3])) if line[4] == '+' else -float(str(line[3]))
                        values={
                            "date": datetime.strptime(line[0], "%d/%m/%Y"),
                            "amount": amount,
                            "ref": line[2],
                            "payment_ref": line[1],
                            #"manual_currency_exchange_rate":self.tasa_del_dia if self.tasa_del_dia != 0 else self.env.company.currency_id.parent_id.rate,
                        }
                        lines = [(0,0,values)]
                        statement.write({'line_ids':lines})
        
        # Si el Banco es VENEZUELA, BANCARIBE, BANESCO PANAMÁ
        # Esto es porque el tipo de archivo para estos bancos es .csv
        if self.bank_option in ('0114','0102'):
            #try:
            csv_data = base64.b64decode(self.file)
            data_file = io.StringIO(csv_data.decode("ISO-8859-1"))
            data_file.seek(0)
            file_reader = []
            values = {}
            csv_reader = csv.reader(data_file, delimiter=';')
            file_reader.extend(csv_reader)
            # Bancoexcept:
            #    raise UserError(_("Archivo Inválido!"))
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                #vals = dict(zip(field))
                if field:
                    if i <= 0:
                        continue
                    else:
                        # Banco de Venezuela
                        if self.bank_option == '0102':
                            values={
                                "date": datetime.strptime(field[0][:10], "%d/%m/%Y"),
                                "amount": float(field[8].replace('.','').replace(',','.')),
                                "ref": field[1],
                                "payment_ref": field[2],
                                #"manual_currency_exchange_rate":self.tasa_del_dia if self.tasa_del_dia != 0 else self.env.company.currency_id.parent_id.rate,
                            }
                            lines = [(0,0,values)]
                            statement.write({'line_ids':lines})
                        # BanCaribe
                        if self.bank_option == '0114':
                            values={
                                "date": datetime.strptime(field[0], "%d/%m/%Y"),
                                "amount": float(field[4].replace('.','').replace(',','.')) if field[3] == 'C' else -float(field[4].replace('.','').replace(',','.')),
                                "ref": field[1],
                                "payment_ref": field[2],
                                #"manual_currency_exchange_rate":self.tasa_del_dia if self.tasa_del_dia != 0 else self.env.company.currency_id.parent_id.rate,
                            }
                            lines = [(0,0,values)]
                            statement.write({'line_ids':lines})
                        

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': statement.id,
            'views': [(False, 'form')],
            #'target': 'new',
        }
