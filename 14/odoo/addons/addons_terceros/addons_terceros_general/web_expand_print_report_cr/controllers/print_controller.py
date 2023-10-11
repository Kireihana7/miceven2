# -*- encoding: utf-8 -*-

# Part of Odoo Module Developed by Candidroot Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

try:
    import json
except ImportError:
    import simplejson as json
    
import re
import io
from odoo import http, tools
from odoo.addons.web.controllers.main import ExportFormat,serialize_exception
from odoo.http import  request
from odoo.tools.misc import xlsxwriter


class ExcelExport(ExportFormat,http.Controller):
    _path = '/web/export/excel_export'
    
    @property
    def content_type(self):
        return 'text/csv;charset=utf8'

    def from_data(self, fields, rows):

        fp = io.BytesIO()
        workbook = xlsxwriter.Workbook(fp, {'in_memory': True})
        worksheet = workbook.add_worksheet('Sheet 1')
        
                  
        header_bold_style = workbook.add_format({'text_wrap': True, 'bold': True})
        header_style = workbook.add_format({'bold': True,'bg_color' : '#e9ecef'})
        base_style = workbook.add_format({'text_wrap': True})
        
        header_format = workbook.add_format()
        header_format.set_pattern(1)
        header_format.set_bg_color('#e9ecef')
        header_format.set_bold()
        header_format.set_text_wrap()
        
        ignore_index = []
        count = 0
        field_count = 0
        index_to_remove = []
        for fl in fields:
            if not fl.get('header_data_id') or not fl.get('header_name'):
                index_to_remove.append(field_count)
            field_count += 1
            
        removed_count = 0
        
        for ind in index_to_remove:
            ignore_index.append(ind)
            fields.pop(ind - removed_count)
            removed_count += 1
        
            
        for i, fieldname in enumerate(fields):
            if fieldname.get('header_data_id', False):
                field_name = fieldname.get('header_name', '')
                worksheet.write(0, i-count, field_name, header_bold_style)
                worksheet.set_column(0, i-count, 8000)
            else:
                # ignore_index.append(count)
                count += 1
                
        for row_index, row in enumerate(rows):
            count = 0
            is_header_group = False
            
            for cell_index, cell_value in enumerate(row):
                if cell_value.get('group_row'):
                    is_header_group = True
                    if cell_index == 0 and not cell_value.get('data'):
                        continue
                    else:
                        cellvalue = cell_value.get('data', '')
                        if isinstance(cellvalue, str):
                            cellvalue = re.sub("\r", " ", cellvalue)
                        if cellvalue is False: cellvalue = None
                        
                        if cell_value.get('padding-left') and cell_value.get('padding-left').find('px') != -1:
                            depth = int(cell_value.get('padding-left').split('px')[0])
                            cellvalue = '%s%s' % (' ' * int(depth/10), cellvalue)
                            worksheet.write(row_index + 1, count, cellvalue, header_format)
                        else:
                            worksheet.write(row_index + 1, count, cellvalue, header_format)
                        worksheet.set_column(row_index + 1, count, 8000)
                        
                        if cell_value.get('colspan') and int(cell_value.get('colspan')) > 1 and count == 0:
                            count += int(cell_value.get('colspan')) - 1
                            
                            for ir in range(count - (int(cell_value.get('colspan')) - 1) + 1,count):
                                worksheet.write(row_index + 1, ir, '', header_format)
                                worksheet.set_column(row_index + 1, ir, 8000)
                                
                               
                        elif cell_value.get('colspan'):
                            count += int(cell_value.get('colspan'))
                            for ir in range(count - (int(cell_value.get('colspan'))) + 1,count):
                                worksheet.write(row_index + 1, count, '', header_format)
                                worksheet.set_column(row_index + 1, count, 8000)
                            
                        else:
                            count += 1
                            for ir in range((count - 1) + 1,count):
                                worksheet.write(row_index + 1, count, '', header_format)
                                worksheet.set_column(row_index + 1, count, 8000)
                            
                            
                else:
                    if cell_index not in ignore_index:                    
                        if cell_index == 0 and not cell_value.get('data'):
                            continue
                        else:
                            cellvalue = cell_value.get('data', '')
                            if isinstance(cellvalue, str):
                                cellvalue = re.sub("\r", " ", cellvalue)
                            if cellvalue is False: cellvalue = None
                            worksheet.write(row_index + 1, count, cellvalue, base_style)
                            worksheet.set_column(row_index + 1, count, 8000)
                            
                            if cell_value.get('colspan') and int(cell_value.get('colspan')) > 1 and count == 0:
                                count += int(cell_value.get('colspan')) - 1
                            elif cell_value.get('colspan'):
                                count += int(cell_value.get('colspan'))
                            else:
                                count += 1
        workbook.close()
        return fp.getvalue()

    @http.route(_path,type='http', auth="user")
    @serialize_exception
    def index(self, data, token):
        data = json.loads(data)
        filename = "%s.%s" % (data.get('model'), 'xls')
        return request.make_response(
            self.from_data(data.get('headers', []), data.get('rows', [])),
                           headers=[('Content-Disposition', 'attachment; filename="%s"'% filename),
                                    ('Content-Type', self.content_type)
                                    ],
                                 cookies={'fileToken': token}
                                 )


class ListReportController(http.Controller):

    @http.route('/pdf/reports', type='http', auth='user', methods=['POST'], csrf=False)
    def get_list_report(self, **kw):
        data = json.loads(kw.get('data'))
        uid = data.get('uid', False)
        filename = "%s.%s" % (data.get('model'), 'pdf')
        pdf_content = self.from_data(uid, data.get('headers', []), data.get('rows', []),data.get('company_name',''))
        pdfhttpheaders = [('Content-Disposition', 'attachment; filename="%s"'% filename),('Content-Type', 'application/pdf'), ('Content-Length', len(pdf_content))]
        return request.make_response(pdf_content,headers=pdfhttpheaders)
    
    
    def from_data(self, uid, fields, rows, company_name):
        pdf_html = '<table class="table table-condensed" style="font-size:12px;">'
        if fields:
            pdf_html += '<thead style="font-size:12px;"><tr>'
            for head in fields:
                if head:
                    pdf_html += '<th>' + head.get('header_name') + '</th>'
                    
            pdf_html += '</tr></thead>'
            
        
        if rows:
            pdf_html += '<tbody  style="font-size:12px;">'
            is_previous_row_header = False
            for row in rows:
                pdf_html += '<tr>'
                bold_row = True if row[0].get('bold') else False
                for dt in row:
                    padding_left = dt.get('padding-left') if dt.get('padding-left') else '0px'
                    if dt.get('data') and len(dt.get('data')) >0 and dt.get('data')[0] == '$':
                        pdf_html += '<td colspan="%s">%s</td>'%(dt.get('colspan'),dt.get('data')[:-2])
                    elif bold_row:
                        pdf_html += '<td colspan="%s" style="background-color:rgba(233, 236, 239, 0.9);padding-left:%s">%s</td>'%(dt.get('colspan'),padding_left,dt.get('data'))
                    else:
                        pdf_html += '<td colspan="%s">%s</td>'%(dt.get('colspan'),dt.get('data'))
                pdf_html += '</tr>'
            pdf_html += '</tbody>'
            
        pdf_html_encoded = pdf_html.encode('utf-8')
        convert_data = request.env['print.pdf.report'].sudo().search([],limit=1).get_pdf(pdf_html_encoded.decode('utf-8'),company_name)
        
        return convert_data
        
