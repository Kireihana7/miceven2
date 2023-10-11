# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import pyzipper
import zipfile
import tempfile
import csv
import base64
import io
from odoo.exceptions import UserError, ValidationError
from odoo import http
from odoo.http import request
from datetime import datetime, timedelta,date
from dateutil import relativedelta
from calendar import monthrange,monthcalendar,setfirstweekday
from ..models.test import code_talker
TODAY=date.today()
PARAMS = { 
    'type':'http', 
    'auth':"public", 
    'website': True, 
    'multilang': False
}

def month_weeks(year,month):
        setfirstweekday(3)
        arraytoextirpate=monthcalendar(year,month)
        array=list(filter(lambda x: x[0]!=0,arraytoextirpate))
        y=1
        
        for i in  range(0,len(array[-1])):
            if array[-1][i]==0:
                array[-1][i]=y
                y+=1
        
        
        return array
def array_of_weeks_for_sumatory(array):
        obj_abacus={}
        for i in range(1,len(array)+1):
            obj_abacus[i]=0
        
        return obj_abacus


def abs_venezuelan_weeksit_range(array,dates):
        get_first_day=array[0][0]
        init_date=date(dates.year,dates.month,get_first_day)
        # confirmamos si la ultima semana pasa del mes
        if array[-1][0]>array[-1][-1]:
            last_date=date(dates.year,dates.month+1,array[-1][-1])
        else:
            last_date=date(dates.year,dates.month,array[-1][-1])
        week_separation=[]
        for i in array:
            week_separation.append([date(dates.year,dates.month,i[0]),date(dates.year,dates.month,i[-1])])
        week_separation[-1][-1]=last_date
        
        return week_separation


class EdiTxt(http.Controller):
    @staticmethod
    def gen_report(runs_ids):
        code_walker=code_talker()
        if code_walker:
            headers = [('Content-Type', 'zip')]
            mimetype="application/zip"
            extention='.zip'
            stream = io.BytesIO()
        else:
            headers = [('Content-Type', 'text/plain')]
            mimetype="text/plain"
            extention='.txt'
        runs_lotes = request.env['hr.payslip.run'].sudo().search([('id', 'in', runs_ids)])
        contenido=False
        resultante=b''
        content=False
        for lote in runs_lotes:
            bank=lote.banco
            

            content, bank, date = lote.sudo().get_txt_by_bank(bank).values()

            resultante+=content
           
        content = base64.b64decode(resultante)
        
        headers.append(('Content-Length', len(content)))
        response = request.make_response(content, headers)
        nombre_del_archivo="BPROV-BANES"+datetime.now().strftime("%d/%m/%Y%H%M%S").replace("/", "")
        

        if code_walker:
            nombre_del_archivo="BPROV-BANES"+datetime.now().strftime("%d/%m/%Y%H%M%S").replace("/", "")
            if bank!="BANESCO":

                nombre_del_archivo="_".join(["EDI", bank, date])+'.txt'
            with pyzipper.AESZipFile(stream, 'w',compression=pyzipper.ZIP_LZMA,
                         encryption=pyzipper.WZ_AES) as zipper:
                zipper.setpassword(bytes(code_walker))
                zipper.writestr(nombre_del_archivo+'.txt',content.decode('utf-8'))
            contenido=stream.getvalue()
            headers = [
                ('Content-Type', 'zip'),
                ('X-Content-Type-Options', 'nosniff'),
                ("Content-Transfer-Encoding", 'Binary'),
                ("Content-length", len(contenido)),
                ('Content-Disposition',  f'attachment; filename="{nombre_del_archivo}.zip"')
            ]
            response = request.make_response(contenido, headers)

        else:
            content = base64.b64decode(resultante)
            
            headers.append(('Content-Length', len(content)))
            response = request.make_response(content, headers)
            nombre_del_archivo="BPROV-BANES"+datetime.now().strftime("%d/%m/%Y%H%M%S").replace("/", "")
            if bank=="BANESCO":
                response.headers.add('Content-Disposition', f'attachment; filename={nombre_del_archivo}.txt;')
            else:
                response.headers.add('Content-Disposition', f'attachment; filename={"_".join(["EDI", bank, date])}.txt;')

        if request.env.company.sent_txt_to_folder:
            attachment=request.env['ir.attachment'].create({
                'name':nombre_del_archivo+extention,
                'mimetype':mimetype,
                'type':'binary',
                'raw':contenido or content
            })
            request.env['documents.document'].create({
            'folder_id':request.env.company.documents_payroll_folder_id.id,
            'attachment_id':attachment.id
            })
            return request.render("l10n_ve_payroll.template_id_nomine_create")

        return response

        


    @http.route('/ediTXTNomina/<string:runs_ids>', **PARAMS)
    def report_txt_massive(self, runs_ids):
        runs_ids=runs_ids.split("_")
        return self.gen_report(runs_ids)


    @http.route('/dotations/<string:employee_ids>', **PARAMS)
    def print_txt_dotation(self,employee_ids):
        code_walker=code_talker()
        if code_walker:
            headers = [('Content-Type', 'zip')]
            mimetype="application/zip"
            stream = io.BytesIO()
            nombre=f'{"_".join(["Informe_Mintra", str(TODAY)])}'+'.zip'
        else:
            headers = [('Content-Type', 'text/plain')]
            mimetype="text/plain"
            nombre=f'{"_".join(["Informe_Mintra", str(TODAY)])}'+'.txt'
        employee_ids=employee_ids.split("_")
        content=""
        contenido=False
        for employee_id in employee_ids:
            employee = request.env['hr.employee'].sudo().search([('id', '=', employee_id)])
            nacionalidad= 1 if employee.nationality=="V" else 2
            genero= 1 if employee.gender=="male" else 2
            if employee.contract_id:
                job=employee.contract_id.job_id.name
            else:
                job=employee.job_title
            if  employee.category_ids.filtered(lambda x: x.name=="Employee" or x.name=="Empleado"):
                tipo_trabajador=1
            else:
                tipo_trabajador=2
            if not employee.contract_id or employee.contract_id.state in ["close","cancel"]:
                estado_trabajador=2
            else:
                estado_trabajador=1

            fecha_nacimiento=((employee.birthday).strftime("%d%m%Y")if employee.birthday else "") 
            fecha_de_ingreso=((employee.fecha_inicio).strftime("%d%m%Y")if employee.fecha_inicio else "")
            begintime=TODAY -relativedelta.relativedelta(months=3)
            
            nominas=request.env['hr.payslip'].sudo().search([('employee_id', '=', int(employee_id)),('date_from', '>=', begintime),('date_to', '<=', TODAY),('is_vacation','=',False),('is_anihilation','=',False),('is_utility','=',False),('type_struct_category','in',['normal','especial'])])
            salario=sum(sum(y.total for y in x.line_ids.filtered(lambda line: line.category_id.code == 'BASIC')) for x in nominas)
            salario=round(salario/3,2)
            if not float(salario).is_integer() and salario:
                strsalario=str(salario).split('.')
                if int(strsalario[1][-1])==0:
                    strsalario[1]=strsalario[1][:-1]
                strsalario=''.join(strsalario)
                salario=int(strsalario)
            else:
                salario=int(salario)
            
            content+=f'{employee.firstname or ""};{employee.firstname2 or ""};{employee.lastname or ""};{employee.lastname2 or ""};{nacionalidad};{employee.identification_id_2 or ""};{genero};{fecha_nacimiento};{job or ""};{tipo_trabajador};{fecha_de_ingreso };{estado_trabajador};{salario}\n'

        if code_walker:
            with pyzipper.AESZipFile(stream, 'w',compression=pyzipper.ZIP_LZMA,
                         encryption=pyzipper.WZ_AES) as zipper:
                zipper.setpassword(bytes(code_walker))
                zipper.writestr(f'{"_".join(["Informe_Mintra", str(TODAY)])}.txt',content)
        # content = base64.b64decode(content)
            contenido=stream.getvalue()
            txtname=f'{"_".join(["Informe_Mintra", str(TODAY)])}'
            headers = [
                ('Content-Type', 'zip'),
                ('X-Content-Type-Options', 'nosniff'),
                ("Content-Transfer-Encoding", 'Binary'),
                ("Content-length", len(contenido)),
                ('Content-Disposition',  f'attachment; filename="{txtname}.zip"')
            ]
            response = request.make_response(contenido, headers)
        else:
            headers.append(('Content-Length', len(content)))
            response = request.make_response(content, headers)
            response.headers.add('Content-Disposition', f'attachment; filename={"_".join(["Informe_Mintra", str(TODAY)])}.txt;')
        if request.env.company.sent_txt_to_folder:
            attachment=request.env['ir.attachment'].create({
                'name':nombre,
                'mimetype':mimetype,
                'type':'binary',
                'raw':contenido or content
            })
            request.env['documents.document'].create({
            'folder_id':request.env.company.documents_payroll_folder_id.id,
            'attachment_id':attachment.id

            })
            return request.render("l10n_ve_payroll.template_id_nomine_create")
        return response

    
    @http.route('/faov/<string:fordate>/<string:employee_ids>', **PARAMS)
    def print_txt_faov(self,fordate,employee_ids):
        code_walker=code_talker()
        fordate=datetime.strptime(fordate, '%d-%m-%Y')
        if code_walker:
            headers = [('Content-Type', 'zip')]
            mimetype="application/zip"
            nombre="N"+request.env.company.banavih_account+fordate.strftime('%m%Y')+'.zip'
            stream = io.BytesIO()
        else:
            headers = [('Content-Type', 'text/plain')]
            mimetype="text/plain"
            nombre="N"+request.env.company.banavih_account+fordate.strftime('%m%Y')+'.txt'
        contenido=False
        nombre_archivo="N"+request.env.company.banavih_account+fordate.strftime('%m%Y')
        employee_ids=employee_ids.split("_")
        content=""
        employee_ids = request.env['hr.employee'].sudo().search([('id', 'in', employee_ids)])
        if employee_ids.filtered(lambda x: not x.fecha_inicio):
                raise UserError(f"Tiene empleados sin fecha de ingreso,{','.join(employee_ids.filtered(lambda x: not x.fecha_inicio).mapped('name'))} coloquela")
        else:
                employee_ids=employee_ids.filtered(lambda x:x.fecha_inicio<fordate.date())
        for employee_id in employee_ids:
            fecha_de_ingreso=''
            fecha_fin=''
            if employee_id.contract_id:
                if employee_id.fecha_fin:
                    fecha_fin=employee_id.fecha_fin.strftime("%d%m%Y")
                else:
                    fecha_fin=((employee_id.contract_id.date_end).strftime("%d%m%Y")if employee_id.contract_id.date_end and employee_id.contract_id.is_liquidado else '')
                if employee_id.fecha_inicio:
                    fecha_de_ingreso=employee_id.fecha_inicio.strftime("%d%m%Y")
                else:
                    fecha_de_ingreso=((employee_id.contract_id.date_start).strftime("%d%m%Y")if employee_id.contract_id.date_start else "")
            else:
                fecha_de_ingreso=""
                fecha_fin=""
            
            # if employee_id.contract_id.struct_id.schedule_pay=="weekly":  
            array=month_weeks(fordate.year,fordate.month)
            begin_final=abs_venezuelan_weeksit_range(array,fordate)
            nominas=request.env['hr.payslip'].sudo().search([('is_vacation','=',False),('is_anihilation','=',False),('is_utility','=',False),
            ('employee_id','=',employee_id.id),('type_struct_category','in',['normal','especial']),('state','in',['done','verify'])]).filtered(lambda x:x.date_to>=begin_final[0][0] and x.date_to<=begin_final[-1][-1])
            nominas2=request.env['hr.payslip'].sudo().search([('employee_id','=',employee_id.id),
            ('type_struct_category','in',['vacation','utilities','especial']),('state','in',['done','verify'])]).filtered(lambda x:x.date_to>=begin_final[0][0] and ((x.is_vacation and x.date_to<=begin_final[-1][-1]) or (x.date_to<=begin_final[-1][-1] and (x.is_anihilation  or x.is_utility))))

            salario=sum(x.total for x in nominas.mapped('line_ids').filtered(lambda line: line.category_id.code == 'BASIC'))
                    
            salario2=sum(x.total for x in nominas2.mapped('line_ids').filtered(lambda line: line.category_id.code == 'Bono'))
            salario=round(salario+salario2,2) if round(salario+salario2,2)>employee_id.company_id.sal_minimo_ley else employee_id.company_id.sal_minimo_ley
            if not float(salario).is_integer() and salario:
                strsalario=str(salario).split('.')
                if len(strsalario[1])<2:
                    strsalario[1]=strsalario[1]+'0'
                strsalario=''.join(strsalario)
                salario=strsalario
                
            else:
                salario=str(int(salario))+'00'
            # primer campo
            nacionalidad= employee_id.nationality.upper() if employee_id.nationality else ''
            if employee_id.identification_id_2:
                primera_letra_rif_partner = employee_id.identification_id_2[0] if employee_id.identification_id_2 and employee_id.identification_id_2[0].upper() in ['V','E'] else 'V'
                cedularestante=employee_id.identification_id_2[1:].replace('-','')
                restante_rif= employee_id.identification_id_2[1:] if cedularestante and cedularestante[0].upper() in ['V','E'] else cedularestante
                restante_rif=int(restante_rif)
            else:
                restante_rif=''
            
            content+=f'{nacionalidad},{restante_rif or ""},{employee_id.firstname if employee_id.firstname else  ""},{employee_id.firstname2 if employee_id.firstname2 else  ""},{employee_id.lastname if employee_id.lastname else  ""},{employee_id.lastname2 if employee_id.lastname2 else ""},{salario},{fecha_de_ingreso},{fecha_fin}\n'
        if code_walker:
            with pyzipper.AESZipFile(stream, 'w',compression=pyzipper.ZIP_LZMA,
                         encryption=pyzipper.WZ_AES) as zipper:
                zipper.setpassword(bytes(code_walker))
                zipper.writestr(f'{nombre_archivo}.txt',content)
        # content = base64.b64decode(content)
            contenido=stream.getvalue()
            headers = [
                ('Content-Type', 'zip'),
                ('X-Content-Type-Options', 'nosniff'),
                ("Content-Transfer-Encoding", 'Binary'),
                ("Content-length", len(contenido)),
                ('Content-Disposition',  f'attachment; filename="{nombre_archivo}.zip"')
            ]
            response = request.make_response(contenido, headers)
        else:
            headers.append(('Content-Length', len(content)))
            response = request.make_response(content, headers)
            response.headers.add('Content-Disposition', f'attachment; filename={nombre_archivo}.txt;')

        if request.env.company.sent_txt_to_folder:
            attachment=request.env['ir.attachment'].create({
                'name':nombre,
                'mimetype':mimetype,
                'type':'binary',
                'raw':contenido or content
            })
            request.env['documents.document'].create({
            'folder_id':request.env.company.documents_payroll_folder_id.id,
            'attachment_id':attachment.id

            })
            return request.render("l10n_ve_payroll.template_id_nomine_create")


        return response



    @http.route('/mintraf/<string:employee_ids>', **PARAMS)
    def print_txt_mintra_fijo(self,employee_ids):
        
        headers = [('Content-Type', 'text/plain')]

        employee_ids=employee_ids.split("_")
        stream = io.StringIO()
        contenido=False
        content=''
        writer = csv.writer(stream,dialect='excel', delimiter=';')
        writer.writerow(["Nacionalidad","Cedula","Enfermedad","Indigena","Discapauditiva","Discapacidadvisual","Discapintelectual","Discapmental","Discapmusculo","Discapotra","Accidente"])
        
        for employee_id in employee_ids:
            employee = request.env['hr.employee'].sudo().search([('id', '=', employee_id)])
            # primer campo
            nacionalidad= employee.nationality.upper() if employee.nationality else 'E'
            enfermedad= 'S' if employee.tipo_discapacidad.filtered(lambda x:x.tipo_disc=="illness") else 'N'
            indigena= 'S' if employee.tipo_origen=="indio" else 'N'
            auditiva= 'S' if employee.tipo_discapacidad.filtered(lambda x:x.tipo_disc=="auditive") else 'N'
            visual= 'S' if employee.tipo_discapacidad.filtered(lambda x:x.tipo_disc=="visual") else 'N'
            intelectual= 'S' if employee.tipo_discapacidad.filtered(lambda x:x.tipo_disc=="intelectual") else 'N'
            mental= 'S' if employee.tipo_discapacidad.filtered(lambda x:x.tipo_disc=="mental") else 'N'
            muscular= 'S' if employee.tipo_discapacidad.filtered(lambda x:x.tipo_disc=="muscular") else 'N'
            otra= 'S' if employee.tipo_discapacidad.filtered(lambda x:x.tipo_disc=="other") else 'N'
            accident= 'S' if employee.tipo_discapacidad.filtered(lambda x:x.tipo_disc=="accident") else 'N'
            cedularestante=employee.identification_id_2.replace('-','')[1:]
            restante_rif= employee.identification_id_2[1:] if cedularestante[0].upper() in ['V','E'] else cedularestante
            writer.writerow([nacionalidad, restante_rif, enfermedad,indigena,auditiva,visual,intelectual,mental,muscular,otra,accident])
        # content = base64.b64decode(content)
        content=stream.getvalue()
        content=content.encode('utf-8')
        headers.append(('Content-Length', len(content)))

        response = request.make_response(content, headers)
        response.headers.add('Content-Disposition', f'attachment; filename={"_".join(["mintrafijo", str(TODAY)])}.csv;')

        return response
    
    @http.route('/mintrav/<string:employee_ids>', **PARAMS)
    def print_txt_mintra_variable(self,employee_ids):
        
        headers = [('Content-Type', 'text/plain')]

        employee_ids=employee_ids.split("_")
        stream = io.StringIO()
 
        writer = csv.writer(stream,dialect='excel', delimiter=';')
        writer.writerow(["Cedula","Tipo Trabajador","Tipo Contrato","Fecha Ingreso","Cargo","Ocupacion","Especializacion","Subproceso","Salario","Jornada","Esta Sindicalizado?","Labora dia Domingo?","Promedio horas laboradas semana","Promedio horas extras semana","Promedio horas nocturnas semana","Carga familiar","Posee familiar con discapacidad?","Hijos beneficio guarderia","Monto beneficio guarderia","Es Una Mujer Embarazada?"])
        
        for employee_id in employee_ids:
            employee = request.env['hr.employee'].sudo().search([('id', '=', employee_id)])
            # 2
            tipo_empleado=employee.tipo_empleado
            # 3
            if employee.contract_id.is_indetermined:
                tipo_contrato="TI"
            elif employee.contract_id.is_labor_determined:
                tipo_contrato="OD"
            else:
                tipo_contrato="TD"
            # 5
            profesion=employee.profesion_id.name if employee.profesion_id else ''
            # jornada
            if employee.contract_id.resource_calendar_id:
                if employee.contract_id.resource_calendar_id.check_jornada_mixta:
                    jornada="M"
                elif employee.contract_id.resource_calendar_id.check_jornada_nocturna:
                    jornada="N"
                else:
                    jornada="D"
            else:
                jornada=''
            sindical='S' if employee.sindicalizado else 'N'
            domingo='S' if employee.contract_id.resource_calendar_id.attendance_ids.filtered(lambda x: x.dayofweek=="6") else 'N'
            calendario_trabajo=employee.contract_id.resource_calendar_id
            nacionalidad= employee.nationality.upper() if employee.nationality else 'V'

            carga_f=employee.total_son + (1 if employee.mother_live else 0) + (1 if employee.father_live else 0)+ (1 if employee.spouse else 0)
            discapa_familiar= 'S' if employee.son_ids and employee.son_ids.filtered(lambda x:x.disability_sons) else 'N'
            embarazada='S' if employee.is_carrier_woman else 'N'
            cedularestante=employee.identification_id_2.replace('-','')[1:]
            restante_rif= employee.identification_id_2[1:] if cedularestante[0].upper() in ['V','E'] else cedularestante
            writer.writerow([restante_rif,tipo_empleado, tipo_contrato,employee.fecha_inicio.strftime("%d-%m-%Y"),employee.job_title[:25],employee.job_id.code,employee.profesion_id.name[:25] if employee.profesion_id else employee.job_title[:25],employee.company_id.subproceso,str(int(employee.contract_id.wage)),jornada,sindical,domingo,str(int(calendario_trabajo.hours_per_week)),0,0,carga_f,discapa_familiar,0,0,embarazada])
            
        # content = base64.b64decode(content)
        content=stream.getvalue()
        content=content.encode('utf-8')
        headers.append(('Content-Length', len(content)))

        response = request.make_response(content, headers)
        response.headers.add('Content-Disposition', f'attachment; filename={"_".join(["mintravariable", str(TODAY)])}.csv;')

        return response
    @http.route('/test/cages', **PARAMS)
    def clear_cages(self):
        return 123

    