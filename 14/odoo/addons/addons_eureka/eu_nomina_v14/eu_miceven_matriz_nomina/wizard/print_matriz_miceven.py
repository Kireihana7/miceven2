# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError
import re
import requests

class PrintMatrizNomina(models.TransientModel):
    _name = 'print.matriz.nomina'
    _description = "Imprimir reporte matriz"


    def payrun_get(self):
        return self.env['hr.payslip.run'].search([('id','=',self._context.get('active_id'))])

    payslip_run = fields.Many2one("hr.payslip.run",default=payrun_get)

    

   
    def remove_accents(self, text):
        text_normalizing_map = {
            'À': 'A',
            'Á': 'A',
            'Â': 'A',
            'Ã': 'A',
            'Ä': 'A',
            'È': 'E',
            'É': 'E',
            'Ê': 'E',
            'Ë': 'E',
            'Í': 'I',
            'Ì': 'I',
            'Î': 'I',
            'Ï': 'I',
            'Ù': 'U',
            'Ú': 'U',
            'Û': 'U',
            'Ü': 'U',
            'Ò': 'O',
            'Ó': 'O',
            'Ô': 'O',
            'Õ': 'O',
            'Ö': 'O',
            'Ñ': 'N',
            'Ç': 'C',
            'ª': 'A',
            'º': 'O',
            '§': 'S',
            '³': '3',
            '²': '2',
            '¹': '1',
            'à': 'a',
            'á': 'a',
            'â': 'a',
            'ã': 'a',
            'ä': 'a',
            'è': 'e',
            'é': 'e',
            'ê': 'e',
            'ë': 'e',
            'í': 'i',
            'ì': 'i',
            'î': 'i',
            'ï': 'i',
            'ù': 'u',
            'ú': 'u',
            'û': 'u',
            'ü': 'u',
            'ò': 'o',
            'ó': 'o',
            'ô': 'o',
            'õ': 'o',
            'ö': 'o',
            'ñ': 'n',
            'ç': 'c'
        }        
        list_text = list(text)
        for index, i in enumerate(list_text):
            val = text_normalizing_map.get(i)
            if(val):
                list_text[index] = val
        return "".join(list_text)

    def naming_convencion(self):
        templ = self.env.ref("eu_miceven_matriz_nomina.nomina_matrix")
        payslip_run=self.env['hr.payslip.run'].search([('id','=',self._context.get('active_id'))])
        if not payslip_run.slip_ids:
            raise UserError("Elija un lote con nominas")
        
        chunk = lambda l, n: [l[i:i + n] for i in range(0, len(l), n)]
        to_float = lambda value: "{:.2f}".format(float(str(value or 0).replace(",", ".")))
        run = payslip_run
        valid_line = lambda items: "".join(map(str.upper, items))
        for slip in run.slip_ids:
            data = self.env['mail.render.mixin']._render_template(templ.body_html, 'hr.payslip', [slip.id], add_context={
                # "columns": lambda lines: "  ".join([
                #     "".join([line.name[:15].ljust(15, "."), ": ", to_float(line.value)[:4].ljust(4)]) for line in lines
                # ]).center(80),
                # "chunk": chunk,
                # "formatLang": lambda v: formatLang(self.env, v),
                # "to_float": to_float,
                # "align": lambda lista: (" " * (80 - len("".join(lista)))).join(lista).upper(),
                # "kilos": lambda lista: "  ".join([(text[0][:19] + ":" + str(text[1]).rjust(6)).center(20).upper() for text in chunk(lista, 2)]).center(80),
                # "get_date": lambda fecha: [fecha.strftime("%d-%m-%Y"), fecha.strftime("%X")] if fecha else [""] * 2,
                # "fformat": lambda char: to_float(char),
                # "fixed_columns": lambda columns: "".join(valid_line(item).ljust(80 // len(item)) for item in chunk(list(map(str, columns)), 2)),
                # "valid_line": valid_line,
            })

            name = data[slip.id]
        
            return self.remove_accents(name)

        # requests.post("http://192.168.21.113/Impresora/index.php", json={
        #     "text": re.sub('<[^<]+?>', '', self.name),
        # })        

        # requests.post("http://192.168.21.113/Matriz/index.php", json={
        #     "text": re.sub('<[^<]+?>', '', name),
        # })
        
            # requests.post("http://200.8.185.150:8081/Matriz/index.php", json={
            #     "text": re.sub('<[^<]+?>', '', name),
            # })
    name = fields.Html( default=naming_convencion)



    def action_print_matriz_miceven(self):
        templ = self.env.ref("eu_miceven_matriz_nomina.nomina_matrix")
        payslip_run=self.env['hr.payslip.run'].search([('id','=',self._context.get('active_id'))])
        if not payslip_run.slip_ids:
            raise UserError("Elija un lote con nominas")
        
        chunk = lambda l, n: [l[i:i + n] for i in range(0, len(l), n)]
        to_float = lambda value: "{:.2f}".format(float(str(value or 0).replace(",", ".")))
        run = payslip_run
        valid_line = lambda items: "".join(map(str.upper, items))
        for slip in run.slip_ids:
            data = self.env['mail.render.mixin']._render_template(templ.body_html, 'hr.payslip', [slip.id], add_context={
                # "columns": lambda lines: "  ".join([
                #     "".join([line.name[:15].ljust(15, "."), ": ", to_float(line.value)[:4].ljust(4)]) for line in lines
                # ]).center(80),
                # "chunk": chunk,
                # "formatLang": lambda v: formatLang(self.env, v),
                # "to_float": to_float,
                # "align": lambda lista: (" " * (80 - len("".join(lista)))).join(lista).upper(),
                # "kilos": lambda lista: "  ".join([(text[0][:19] + ":" + str(text[1]).rjust(6)).center(20).upper() for text in chunk(lista, 2)]).center(80),
                # "get_date": lambda fecha: [fecha.strftime("%d-%m-%Y"), fecha.strftime("%X")] if fecha else [""] * 2,
                # "fformat": lambda char: to_float(char),
                # "fixed_columns": lambda columns: "".join(valid_line(item).ljust(80 // len(item)) for item in chunk(list(map(str, columns)), 2)),
                # "valid_line": valid_line,
            })

            name = data[slip.id]
        
            # return self.remove_accents(name)

        # requests.post("http://192.168.21.113/Impresora/index.php", json={
        #     "text": re.sub('<[^<]+?>', '', self.name),
        # })        192.168.21.131

            # requests.post("http://localhost/Matriz/index.php", json={
            #     "text": re.sub('<[^<]+?>', '', name),
            # })
        
            requests.post("http://200.8.185.150:8081/Matriz/index.php", json={
                "text": re.sub('<[^<]+?>', '', name),
            })

    def _print_matriz_miceven(self):
        templ = self.env.ref("eu_miceven_matriz_nomina.nomina_matrix")
        payslip_run=self.env['hr.payslip.run'].search([('id','=',self._context.get('active_id'))])
        if not payslip_run.slip_ids:
            raise UserError("Elija un lote con nominas")
        
        chunk = lambda l, n: [l[i:i + n] for i in range(0, len(l), n)]
        to_float = lambda value: "{:.2f}".format(float(str(value or 0).replace(",", ".")))
        run = payslip_run
        valid_line = lambda items: "".join(map(str.upper, items))
        for slip in run.slip_ids:
            data = self.env['mail.render.mixin']._render_template(templ.body_html, 'hr.payslip', [slip.id], add_context={
                # "columns": lambda lines: "  ".join([
                #     "".join([line.name[:15].ljust(15, "."), ": ", to_float(line.value)[:4].ljust(4)]) for line in lines
                # ]).center(80),
                # "chunk": chunk,
                # "formatLang": lambda v: formatLang(self.env, v),
                # "to_float": to_float,
                # "align": lambda lista: (" " * (80 - len("".join(lista)))).join(lista).upper(),
                # "kilos": lambda lista: "  ".join([(text[0][:19] + ":" + str(text[1]).rjust(6)).center(20).upper() for text in chunk(lista, 2)]).center(80),
                # "get_date": lambda fecha: [fecha.strftime("%d-%m-%Y"), fecha.strftime("%X")] if fecha else [""] * 2,
                # "fformat": lambda char: to_float(char),
                # "fixed_columns": lambda columns: "".join(valid_line(item).ljust(80 // len(item)) for item in chunk(list(map(str, columns)), 2)),
                # "valid_line": valid_line,
            })

            name = data[slip.id]
        
            # return self.remove_accents(name)

        # requests.post("http://192.168.21.113/Impresora/index.php", json={
        #     "text": re.sub('<[^<]+?>', '', self.name),
        # })        

            # requests.post("http://192.168.21.131/Matriz/index.php", json={
            #     "text": re.sub('<[^<]+?>', '', name),
            # })
        
            requests.post("http://200.8.185.150:8081/Matriz/index.php", json={
                "text": re.sub('<[^<]+?>', '', name),
            })