import logging

# from odoo.tools import email_split
from odoo import api, fields, models,_
from odoo.exceptions import  UserError
from datetime import datetime
import base64
import re
import random

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    acc_number = fields.Char(size=20) 

class AccountPaymentBatchHeader(models.Model):

    _name = 'account.batch.payment'
    _inherit= ['account.batch.payment','mail.thread', 'mail.activity.mixin']

    report_historical = fields.Char(string="Historico", track_visibility="always", invisible=True)
    acc_number  = fields.Many2one(related='journal_id.bank_account_id', string="N° Cuenta Bancaria del diario", readonly=True, store=True)
    file_generation_enabled = fields.Boolean(help="Whether or not this batch payment should display the 'Generate File' button instead of 'Print' in form view.", compute='_compute_file_generation_enabled')
    tiene_repetidos = fields.Boolean(string="Tiene repetidos",compute="_compute_tiene_repetidos")
    company_id = fields.Many2one('res.company', 'Compañía', required=True, index=True, default=lambda self: self.env.company)
    confirmado_por = fields.Many2one('res.users',string="Confirmado por",readonly=True,tracking=True)
    
    @api.depends('payment_ids')
    def _compute_tiene_repetidos(self):
        for rec in self:
            rec.tiene_repetidos = False
            contador = 0
            exist_partner_list = []
            for line in rec.payment_ids:
                if line.payment_id.partner_id.id in exist_partner_list:
                    contador += 1 
                exist_partner_list.append(line.payment_id.partner_id.id)  
            if contador > 0:
                rec.tiene_repetidos = True 
    # Botón para obtener TXT
    def apply_txt_payment(self):
        self.ensure_one()
        for rec in self:
            rec.report_historical = ('Ha impreso el TXT')         
        return {
            'type': 'ir.actions.act_url',
            'url': '/paymentTXTreports/%s' % self.id,
            'target': 'new',
            'res_id': self.id,
            }
    #Botón para obtener TXT Beneficiario
    def apply_txt_payment_bene(self):
        self.ensure_one()
        for rec in self:
            rec.report_historical = ('Ha impreso el TXT de Beneficiarios ')          
        return {
            'type': 'ir.actions.act_url',
            'url': '/paymentTXTreports_ingre/%s' % self.id,
            'target': 'new',
            'res_id': self.id,
                }
    def validate_batch_button(self):
        res = super(AccountPaymentBatchHeader, self).validate_batch_button()
        for rec in self:
            rec.confirmado_por = self.env.uid
        return res
    # Obtener Archivo TXT
    def act_getfile(self,batch):
        for header in batch:
            if header.journal_id.txt_payment == '0157':
                return self.bank_0157(batch)
            if header.journal_id.txt_payment == '0108':
                return self.bank_0108(batch)
            if header.journal_id.txt_payment == '0134':
                return self.bank_0134(batch)
            if header.journal_id.txt_payment == '0105':
                return self.bank_0105(batch)
            if header.journal_id.txt_payment == '0191':
                return self.bank_0191(batch)
            if header.journal_id.txt_payment == '0114':
                return self.bank_0114(batch)
            if header.journal_id.txt_payment == '0174':
                return self.bank_0174(batch)
            if header.journal_id.txt_payment == '0102':
                return self.bank_0102(batch)
            if header.journal_id.txt_payment == '0138':
                return self.bank_0138(batch)
            if header.journal_id.txt_payment == '0151':
                return self.bank_0151(batch)
            else: 
                raise UserError('No tiene definido un TXT para ese banco, por favor, contacte a su equipo de desarrollo')
        return False
    # Obtener Archivo TXT para Ingresar BENEFICIARIO
    def act_getfile_bene(self,batch):
        for header in batch:
            if header.journal_id.txt_payment == '0157':
                return self.bank_0157_bene(batch)
            else: 
                raise UserError('No tiene definido un TXT para ese banco, por favor, contacte a su equipo de desarrollo')
        return False

    # banco Fondo Comun
    def bank_0151(self, batch) :
        codigo_empresa= '021580'
        date = datetime.now().strftime("%Y/%m/%d %H/%M/%S").replace("/", "").replace(" ","")
        content = ''
        nombre_archivo = 'PRO'+ codigo_empresa + str(date) + '.txt'
        for header in batch:
            string_lote = batch.name.replace("/", "")
            num_lote = ''.join([i for i in string_lote if not i.isalpha()])
            last_num_lote = num_lote.zfill(12)
            print_date = datetime.now().strftime("%Y/%m/%d").replace("/", "")
            print_time = datetime.now().strftime("%H/%M/%S").replace("/", "")
            fecha_valor = header.date.strftime("%Y/%m/%d").replace("/", "")
            cero= '0'
            space=" "
            codigo_company= '021580'
            service_code = '000077' #valor fijo
            first_letter_rif = header.company_id.vat[0]
            rif = header.company_id.vat[2:]
            rest_rif = rif.zfill(9)
            content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                cero.zfill(6).ljust(6),
                print_date.ljust(8),
                print_time.ljust(6),
                fecha_valor.ljust(8),
                cero.zfill(6).ljust(6),
                cero.zfill(8).ljust(8),
                cero.zfill(6).ljust(6),
                codigo_company.ljust(6),
                service_code.ljust(6),
                space.ljust(3),
                batch.acc_number.acc_number[:22].zfill(22).ljust(22),
                space.ljust(3),
                cero.zfill(22).ljust(22),
                last_num_lote[:12].ljust(12),
                first_letter_rif.ljust(1),
                rest_rif[:9].ljust(9),
                cero.zfill(98).ljust(98),
            )
            count = 0
            for wh in header.payment_ids:
                if not wh.third_payment:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Beneficiario')
                    count = count + 1
                    num_registro = str(count)
                    primera_letra_rif = wh.partner_id.vat[0]
                    cedula = wh.partner_id.vat[2:]
                    if primera_letra_rif =='V':
                        cedula= cedula[:8]
                    elif primera_letra_rif =='J':
                        cedula= cedula[:9]
                    cedula_final  = cedula.zfill(10)
                    cero= '0'
                    monto_total = wh.amount
                    amount_cal = "{0:.2f}".format(monto_total)
                    total_amount = ''.join(amount_cal.split('.')).zfill(15)
                    credito = 'C'
                    description = " "
                    email = ''
                    if wh.partner_id.email :
                        email = wh.partner_id.email
                    concepto_del_pago = "08"
                    partner_name = (wh.partner_id.name).replace(",","").replace(".","")
                    replaces = {"ñ":"n","'":"","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    partner= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], partner_name)
                    content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        num_registro.zfill(6).ljust(6),
                        space.ljust(3),
                        wh.acc_number_partner.acc_number.ljust(20),
                        primera_letra_rif.ljust(1),
                        cedula_final[:10].ljust(10),
                        cero.zfill(5).ljust(5),
                        cero.zfill(5).ljust(5),
                        wh.ref[:10].zfill(10).ljust(10),
                        total_amount[:15].ljust(15),
                        credito.ljust(1),
                        cero.ljust(1),
                        partner[:40].ljust(40),
                        cero.ljust(1),
                        cero.zfill(3).ljust(3),
                        description.ljust(40),
                        cero.zfill(9).ljust(9),
                        email[:58].ljust(58),
                        concepto_del_pago.ljust(2)
                    )
                else:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner_autorizado.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Autorizado')
                    contador = contador + 1
                    num_registro = str(contador)
                    primera_letra_rif = wh.autorizado.autorizados.vat[0]
                    cedula = wh.autorizado.autorizados.vat[2:]
                    if primera_letra_rif =='V':
                        cedula= cedula[:8]
                    elif primera_letra_rif =='J':
                        cedula= cedula[:9]
                    cedula_final  = cedula.zfill(10)
                    cero= '0'
                    monto_total = wh.amount
                    amount_cal = "{0:.2f}".format(monto_total)
                    total_amount = ''.join(amount_cal.split('.')).zfill(15)
                    credito = 'C'
                    description = " "
                    email = ''
                    if  wh.autorizado.autorizados.email :
                        email = wh.autorizado.autorizados.email
                    concepto_del_pago = "08"
                    partner_name =( wh.autorizado.autorizados.name).replace(",","").replace(".","")
                    replaces = {"ñ":"n","'":"","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    partner= re.sub(r'[ñéóíáÑÉÍÓÁ,.]',lambda c: replaces[c.group(0)], partner_name)
                    content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        num_registro.zfill(6).ljust(6),
                        space.ljust(3),
                        wh.acc_number_partner_autorizado.acc_number.ljust(20),
                        primera_letra_rif.ljust(1),
                        cedula_final[:10].ljust(10),
                        cero.zfill(5).ljust(5),
                        cero.zfill(5).ljust(5),
                        wh.ref[:10].zfill(10).ljust(10),
                        total_amount[:15].ljust(15),
                        credito.ljust(1),
                        cero.ljust(1),
                        partner[:40].ljust(40),
                        cero.ljust(1),
                        cero.zfill(3).ljust(3),
                        description.ljust(40),
                        cero.zfill(9).ljust(9),
                        email.ljust(58),
                        concepto_del_pago.ljust(2)
                    )
            consecutivo = '999999'
            comp_name = (header.company_id.name).replace(",","").replace(".","")
            replaces = {"ñ":"n","'":"","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
            company= re.sub(r'[ñéóíáÑÉÍÓÁ,.]',lambda c: replaces[c.group(0)], comp_name)
            can = str(len(header.payment_ids)).zfill(6) 
            monto_total = sum(header.payment_ids.mapped('amount'))
            amount_cal = "{0:.2f}".format(monto_total)
            total_amount = ''.join(amount_cal.split('.')).zfill(15)
            valor_fijo_debito = '000001'
            filler = '0'
            space= ' '
            content += '%s%s%s%s%s%s%s%s%s%s\n'%(
                consecutivo.ljust(6),
                company[:40].ljust(40),
                can[:6].ljust(6),
                total_amount[:15].ljust(15),
                total_amount[:15].ljust(15),
                valor_fijo_debito.ljust(6),
                can[:6].ljust(6),
                filler[76:].zfill(76).ljust(76),
                space.ljust(50),
                filler[10:].zfill(10).ljust(10),
            )

        return base64.encodebytes(bytes(content, 'utf-8')),nombre_archivo
    # Banco plaza
    def bank_0138(self, batch):
        rs=''
        content = ''
        date = datetime.now().strftime("%d/%m/%y").replace("/", "")
        first_letter_rif = batch.company_id.rif[0]
        rest_rif = batch.company_id.rif[2:]
        nombre_archivo = 'PRO'+ str(first_letter_rif) + '00'+ str(rest_rif)+ str(date)+'01' +'.txt'
        for header in batch:
            for wh in header.payment_ids:
                if not wh.third_payment:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Beneficiario')
                    first_letter_comp_rif = header.company_id.rif[0]
                    rest_rif_comp = header.company_id.rif[2:]
                    rest_rif_comp = rest_rif_comp.zfill(11)

                    primera_letra_partner_rif = wh.partner_id.vat[0]
                    partner_restante_rif = wh.partner_id.vat[2:]
                    partner_restante_rif  = partner_restante_rif.zfill(11)
                    email = ''
                    if wh.partner_id.email :
                        email = wh.partner_id.email
                    cc = 'CC'
                    monto= (wh.amount)
                    amount_cal = "{0:.2f}".format(monto)
                    amount = rs.join(str(amount_cal).split('.')).zfill(17)
                    ref = (wh.name).replace("/","")
                    if not wh.partner_id.phone:
                        phone= '00000000000'
                    elif len(wh.partner_id.phone) > 11:
                        phone = '00000000000'
                    elif wh.partner_id.phone:
                        phone = wh.partner_id.phone
                    partner = wh.partner_id.name
                    content += '%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        first_letter_comp_rif.ljust(1),
                        rest_rif_comp[:11].ljust(11),
                        partner[:50].ljust(50),
                        primera_letra_partner_rif.ljust(1),
                        partner_restante_rif[:11].ljust(11),
                        email[:50].ljust(50),
                        cc.ljust(2),
                        batch.acc_number.acc_number.ljust(20),
                        amount[:17].ljust(17),
                        ref[:129].ljust(129),
                        phone.ljust(11)
                    )
                else:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner_autorizado.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Autorizado')
                    if not wh.autorizado.autorizados.vat:
                        raise UserError('No le tiene asignado una cedulo o rif al Autorizado')
                    first_letter_comp_rif = header.company_id.rif[0]
                    rest_rif_comp = header.company_id.rif[2:]
                    rest_rif_comp = rest_rif_comp.zfill(15)

                    primera_letra_partner_rif = wh.autorizado.autorizados.cedula[0]
                    partner_restante_rif = wh.autorizado.autorizados.cedula[2:]
                    partner_restante_rif = partner_restante_rif.zfill(11)
                    email = ''
                    if wh.autorizado.autorizados.email :
                        email = wh.autorizado.autorizados.email
                    if not wh.autorizado.autorizados.phone:
                        phone = '00000000000'
                    elif len(wh.autorizado.autorizados.phone) > 11:
                        phone = '00000000000'
                    elif wh.autorizado.autorizados.phone:
                        phone = wh.autorizado.autorizados.phone
                    partner = wh.autorizado.autorizados.name
                    content += '%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        first_letter_comp_rif.ljust(1),
                        rest_rif_comp[:11].ljust(11),
                        partner[:50].ljust(50),
                        primera_letra_partner_rif.ljust(1),
                        partner_restante_rif[:11].ljust(11),
                        email[:50].ljust(50),
                        cc.ljust(2),
                        wh.acc_number_partner_autorizado.acc_number.ljust(20),
                        amount[:17].ljust(17),
                        ref.ljust(129),
                        phone.ljust(11)
                    )
        return base64.encodebytes(bytes(content, 'utf-8')),nombre_archivo

    # Banco de Venezuela
    def bank_0102(self,batch):
        rs=','
        content = ''
        date = datetime.now().strftime("%d/%m/%Y").replace("/", "")
        nombre_archivo = 'PROVE_'+ str(date) +'.txt'
        for header in batch:
            if not batch.acc_number.acc_number:
                raise UserError('El diario no tiene configurado una Cuenta Bancaria')
            head = 'HEADER'
            string_lote = batch.name.replace("/", "")
            num_lote = ''.join([i for i in string_lote if not i.isalpha()])
            num_nego = '00654564'
            first_letter_rif = header.company_id.vat[0]
            rest_rif = header.company_id.vat[2:]
            if first_letter_rif == 'J':
                rest_rif = rest_rif[:9]
            fecha = datetime.now().strftime("%d/%m/%Y")
            content += '%s%s%s%s%s%s%s\n'%(
                head.ljust(8),
                num_lote.ljust(8),
                num_nego.ljust(8),
                first_letter_rif.ljust(1),
                rest_rif.ljust(9),
                fecha.ljust(10),
                fecha.ljust(10)
            )
            for wh in header.payment_ids:
                if not wh.third_payment:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Beneficiario')
                    ################### linea de debito##################
                    debito = 'DEBITO'
                    num_ref= wh.name.replace("/","").replace("-","").replace(".","")
                    num_ref = ''.join([i for i in num_ref if not i.isalpha()])
                    referencia = num_ref[-8:]
                    first_letter_rif = header.company_id.vat[0]
                    rest_rif = header.company_id.vat[2:]
                    if first_letter_rif == 'J':
                        rest_rif = rest_rif[:9]
                    name_comp = (header.company_id.name).replace(",","").replace(".","").replace("'","")
                    replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    company= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], name_comp)
                    date = header.date.strftime("%d/%m/%Y")
                    code = 'VEB40'
                    cero='00'
                    monto= (wh.amount)
                    amount_cal = "{0:.2f}".format(monto)
                    amount = rs.join(str(amount_cal).split('.')).zfill(18)
                    content += '%s%s%s%s%s%s%s%s%s%s\n'%(
                        debito.ljust(8),
                        referencia[:8].ljust(8),
                        first_letter_rif.ljust(1),
                        rest_rif[:9].ljust(9),
                        company[:35].ljust(35),
                        date.ljust(10),
                        cero.ljust(2),
                        batch.acc_number.acc_number.ljust(20),
                        amount[:18].ljust(18),
                        code.ljust(5)
                    )
                    ################### linea de credito##################
                    if not wh.partner_id.vat:
                        raise UserError(('El Contacto %s, no posee RIF asociado') % (wh.partner_id.name))
                    primera_letra_rif = wh.partner_id.vat[0]
                    restante_rif = wh.partner_id.vat[2:]
                    if primera_letra_rif =='V':
                        restante_rif= restante_rif[:8]
                    restante_rif  = restante_rif.zfill(9)
                    credit = 'CREDITO'
                    digit_cuenta = ''
                    digit_swift = ''
                    # if header.payment_ids.filtered( lambda y: y.tipo_de_cuenta == 'corriente'):
                    if wh.acc_number_partner.tipo_de_cuenta == 'corriente':
                        digit_cuenta = '00'
                        digit_swift = '10'
                    if wh.acc_number_partner.tipo_de_cuenta == 'ahorro':
                        digit_cuenta = '01'
                        digit_swift = '00'
                    email = ''
                    if wh.partner_id.email :
                        email = wh.partner_id.email
                    monto= (wh.amount)
                    amount_cal = "{0:.2f}".format(monto)
                    amount = rs.join(str(amount_cal).split('.')).zfill(18)
                    if not wh.acc_number_partner.code_swift:
                        raise UserError('Debe tener asignado el código Swift del banco')
                    partner_name = (wh.partner_id.name).replace(",","").replace(".","").replace("'","")
                    replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    partner= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], partner_name)
                    content += '%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        credit.ljust(8),
                        referencia[:8].ljust(8),
                        primera_letra_rif.ljust(1),
                        restante_rif[:9].ljust(9),
                        partner[:30].ljust(30),
                        digit_cuenta.ljust(2),
                        wh.acc_number_partner.acc_number.ljust(20),
                        amount[:18].ljust(18),
                        digit_swift.ljust(2),
                        wh.acc_number_partner.code_swift.ljust(19),
                        email[:50].ljust(50),
                    )
                    wh.ref = referencia[:8]
                else:
                    ###################linea de debito##################
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner_autorizado.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Autorizado')
                    debito = 'DEBITO'
                    num_ref= wh.name.replace("/","").replace("-","").replace(".","")
                    num_ref = ''.join([i for i in num_ref if not i.isalpha()])
                    referencia = num_ref[-8:]
                    first_letter_rif = header.company_id.vat[0]
                    rest_rif = header.company_id.vat[2:]
                    if first_letter_rif == 'J':
                        rest_rif = rest_rif[:9]
                    name_comp = (header.company_id.name).replace(",","").replace(".","").replace("'","")
                    replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    company= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], name_comp)
                    date = header.date.strftime("%d/%m/%Y")
                    code = 'VEB40'
                    cero='00'
                    monto= (wh.amount)
                    amount_cal = "{0:.2f}".format(monto)
                    amount = rs.join(str(amount_cal).split('.')).zfill(18)
                    content += '%s%s%s%s%s%s%s%s%s%s\n'%(
                        debito.ljust(8),
                        referencia.ljust(8),
                        first_letter_rif.ljust(1),
                        rest_rif[:9].ljust(9),
                        company[:35].ljust(35),
                        date.ljust(10),
                        cero.ljust(2),
                        batch.acc_number.acc_number.ljust(20),
                        amount[:18].ljust(18),
                        code.ljust(5)
                    )
                    ################### credito autorizado##################
                    if not wh.autorizado.autorizados.vat:
                        raise UserError(('El Contacto %s, no posee RIF asociado') % (wh.autorizado.autorizados.name))
                    primera_letra_rif = wh.autorizado.autorizados.cedula[0]
                    restante_rif = wh.autorizado.autorizados.cedula[2:]
                    if primera_letra_rif =='V':
                        restante_rif= restante_rif[:8]
                    restante_rif  = restante_rif.zfill(9)
                    credit = 'CREDITO'
                    digit_cuenta = ''
                    digit_swift = ''
                    if wh.acc_number_partner.tipo_de_cuenta == 'corriente':
                        digit_cuenta = '00'
                        digit_swift = '10'
                    if wh.acc_number_partner.tipo_de_cuenta == 'ahorro':
                        digit_cuenta = '01'
                        digit_swift = '00'
                    email = ''
                    if wh.autorizado.autorizados.email:
                       email =  wh.autorizado.autorizados.email
                    monto= (wh.amount)
                    amount_cal = "{0:.2f}".format(monto)
                    amount = rs.join(str(amount_cal).split('.')).zfill(18)
                    if not wh.acc_number_partner_autorizado.code_swift:
                        raise UserError('Debe tener asignado el código Swift del banco')
                    partner_name =( wh.autorizado.autorizados.name).replace(",","").replace(".","").replace("'","")
                    replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    partner= re.sub(r'[ñéóíáÑÉÍÓÁ,.]',lambda c: replaces[c.group(0)], partner_name)
                    content += '%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        credit.ljust(8),
                        referencia.ljust(8),
                        primera_letra_rif.ljust(1),
                        restante_rif[:9].ljust(9),
                        partner[:30].ljust(30),
                        digit_cuenta.ljust(2),
                        wh.acc_number_partner_autorizado.acc_number.ljust(20),
                        amount[:18].ljust(18),
                        digit_swift.ljust(2),
                        wh.acc_number_partner_autorizado.code_swift.ljust(19),
                        email[:50].ljust(50),
                    )
                    wh.ref = referencia[:8]

            total = 'TOTAL'
            can1 = str(len(header.payment_ids)).zfill(5)
            monto_total = sum(header.payment_ids.mapped('amount'))
            amount_cal = "{0:.2f}".format(monto_total)
            amount = rs.join(str(amount_cal).split('.')).zfill(18)
            content += '%s%s%s%s\n'%(
                total.ljust(8),
                can1.ljust(5),
                can1.ljust(5),
                amount[:18].ljust(18)
            )

        return base64.encodebytes(bytes(content, 'utf-8')),nombre_archivo

    # Banco del Sur Definición TXT
    def bank_0157(self,batch):
        r=''
        rs=''
        content = ''
        nombre_archivo = 'PAGO.txt'
        for header in batch:
            for wh in header.payment_ids:
                if not wh.third_payment:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Beneficiario')
                    primera_letra_rif = wh.partner_id.vat[0]
                    restante_rif = wh.partner_id.vat[2:]
                    if primera_letra_rif =='V':
                        restante_rif= restante_rif[:8]
                    if primera_letra_rif =='J':
                        restante_rif= restante_rif[:9]
                    restante_rif  = restante_rif.zfill(12)
                    cta_debito = header.journal_id.bank_account_id.acc_number[10:]
                    cta_debito = cta_debito.zfill(12)
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount_cal = rs.join(str(amount_cal).split('.'))
                    #amount_cal = rs.join(amount_cal.split('-'))
                    amount_cal = amount_cal.zfill(18)
                    content += '%s%s%s%s%s%s%s%s\n'%(
                        primera_letra_rif.ljust(1),
                        restante_rif.ljust(12),
                        cta_debito.ljust(12),
                        wh.acc_number_partner.acc_number.ljust(20),
                        datetime.strftime(header.date, '%d/%m/%Y').ljust(10),
                        rs.join(wh.name.split('/'))[12:].ljust(15),
                        amount_cal.ljust(18),
                        r.join(wh.communication or 'Sin circular').ljust(160),
                        )
                else:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner_autorizado.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Autorizado')
                    primera_letra_rif = wh.autorizado.autorizados.cedula[0]
                    restante_rif = wh.autorizado.autorizados.cedula[2:]
                    if primera_letra_rif =='V':
                        restante_rif= restante_rif[:8]
                    if primera_letra_rif =='J':
                        restante_rif= restante_rif[:9]
                    restante_rif  = restante_rif.zfill(12)
                    cta_debito = header.journal_id.bank_account_id.acc_number[10:]
                    cta_debito = cta_debito.zfill(12)
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount_cal = rs.join(str(amount_cal).split('.'))
                    #amount_cal = rs.join(amount_cal.split('-'))
                    amount_cal = amount_cal.zfill(18)
                    content += '%s%s%s%s%s%s%s%s\n'%(
                        primera_letra_rif.ljust(1),
                        restante_rif.ljust(12),
                        cta_debito.ljust(12),
                        wh.acc_number_partner_autorizado.acc_number.ljust(20),
                        datetime.strftime(header.date, '%d/%m/%Y').ljust(10),
                        rs.join(wh.name.split('/'))[12:].ljust(15),
                        amount_cal.ljust(18),
                        r.join(wh.communication or 'Sin circular').ljust(160),
                        )
        return base64.encodebytes(bytes(content, 'utf-8')),nombre_archivo

    # Banco Provicial Definición TXT
    def bank_0108(self,batch):
        r=''
        rs=''
        content = ''
        date = datetime.now().strftime("%d/%m/%Y %H/%M/%S").replace("/", "").replace(" ","")
        mismo_banco = False if len(batch.mapped('payment_ids').filtered(lambda line: (line.acc_number_partner and str(line.acc_number_partner.acc_number[:4]) != '0108') or (line.acc_number_partner_autorizado and str(line.acc_number_partner_autorizado.acc_number[:4]) != '0108'))) > 0 else True
        if mismo_banco:
            nombre_archivo = 'PAG-TXT PROV '+str(date)+'.txt'
        else:
            nombre_archivo = 'PAG-TXT OB '+str(date)+'.txt'
        for header in batch:
            for wh in header.payment_ids:
                if not wh.third_payment:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Beneficiario')
                    if not wh.partner_id.cedula:
                        raise UserError(('El Contacto %s, no posee RIF asociado') % (wh.partner_id.name))
                    primera_letra_rif = wh.partner_id.cedula[0]
                    rif = wh.partner_id.cedula[2:]
                    # if primera_letra_rif =='V':
                    #     restante_rif= restante_rif[:8]
                    # if primera_letra_rif =='J':
                    #     restante_rif= restante_rif[:9]
                    restante_rif  = rif.zfill(10)
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount_cal = rs.join(str(amount_cal).split('.'))
                    #amount_cal = rs.join(amount_cal.split('-'))
                    amount_cal = amount_cal.zfill(15)
                    # email = ''
                    # if wh.partner_id.email :
                    #     email = wh.partner_id.email
                    space = ' '
                    partner_name = (wh.partner_id.name).replace(",","").replace(".","")
                    replaces = {"ñ":"n","'":"","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    partner= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], partner_name)
                    code_ref = (wh.payment_id.name).replace("/", "").replace("-", "").replace(".", "")
                    newstring = ''.join([i for i in code_ref if not i.isalpha()])
                    new_code_ref = newstring[-8:].zfill(8)
                    content += '%s%s%s%s%s%s%s%s%s%s\n'%(
                        wh.acc_number_partner.acc_number.ljust(20),
                        space.ljust(1),
                        primera_letra_rif.ljust(1),
                        restante_rif[:10].ljust(10),
                        space.ljust(1),
                        amount_cal.ljust(15),
                        space.ljust(1),
                        new_code_ref[:8].ljust(8),
                        space.ljust(1),
                        partner,
                        # email.ljust(38),
                    )
                else:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner_autorizado.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Autorizado')
                    if not wh.autorizado.autorizados.cedula:
                        raise UserError('No le tiene asignado una cedula o un rif al Autorizado')
                    if not wh.autorizado.autorizados.cedula:
                        raise UserError(('El Contacto %s, no posee RIF asociado') % (wh.autorizado.autorizados.name))
                    primera_letra_rif = wh.autorizado.autorizados.cedula[0]
                    rif = wh.autorizado.autorizados.cedula[2:]
                    # if primera_letra_rif =='V':
                    #     restante_rif= restante_rif[:8]
                    # if primera_letra_rif =='J':
                    #     restante_rif= restante_rif[:9]
                    restante_rif  = rif.zfill(10)
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount_cal = rs.join(str(amount_cal).split('.'))
                    #amount_cal = rs.join(amount_cal.split('-'))
                    amount_cal = amount_cal.zfill(15)
                    # email = ''
                    # if wh.autorizado.autorizados.email :
                    #     email = wh.autorizado.autorizados.email
                    space = ' '
                    partner_name = (wh.autorizado.autorizados.name).replace(",","").replace(".","")
                    replaces = {"ñ":"n","'":"","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    partner= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], partner_name)
                    code_ref = (wh.payment_id.name).replace("/", "").replace("-", "").replace(".", "")
                    newstring = ''.join([i for i in code_ref if not i.isalpha()])
                    new_code_ref = newstring[-8:].zfill(8)
                    content += '%s%s%s%s%s%s%s%s%s%s\n'%(
                        wh.acc_number_partner_autorizado.acc_number.ljust(20),
                        space.ljust(1),
                        primera_letra_rif.ljust(1),
                        restante_rif[:10].ljust(10),
                        space.ljust(1),
                        amount_cal.ljust(15),
                        space.ljust(1),
                        new_code_ref[:8].ljust(8),
                        space.ljust(1),
                        partner,
                        # email.ljust(38),
                    )
        return base64.encodebytes(bytes(content, 'utf-8')),nombre_archivo
    # Banco Mercantil Definición TXT
    def bank_0105(self,batch):
        r=''
        rs=''
        content = ''
        nombre_archivo = 'BPI0001W.txt'
        for header in batch:
            if not batch.acc_number.acc_number:
                raise UserError('El diario no tiene configurado una Cuenta Bancaria')
            moneda = batch.currency_id.name
            code_swift = "BAMRVECA"
            if moneda == 'VEF':
                tipo_moneda = 'PROVE'
            if moneda == 'USD':
                tipo_moneda = 'PRODO'
            if moneda == 'EUR':
                tipo_moneda= 'PROEU'
            type_de_pago = '0000000062'
            first_letter_rif = header.company_id.vat[0]
            rest_rif = header.company_id.vat[2:]
            if first_letter_rif == 'J':
                rest_rif = rest_rif[:9]
            rest_rif = rest_rif.zfill(15)
            string_lote = batch.name.replace("/", "")
            num_lote = ''.join([i for i in string_lote if not i.isalpha()])
            last_num_lote = num_lote.zfill(15)
            can1 = str(len(header.payment_ids)).zfill(8)
            monto_total = sum(header.payment_ids.mapped('amount'))
            amount_cal = "{0:.2f}".format(monto_total)
            total_amount = rs.join(str(amount_cal).split('.')).zfill(17)
            date = header.date.strftime("%Y/%m/%d").replace("/", "") #AAAAMMDD
            reserved_area = "0000000"
            reserved_area2 = "0"
            num_serial = "00000000"
            response_code = "0000"
            fecha_proceso = "00000000"
            tipo_registro = "1"
            content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                tipo_registro[:1],
                code_swift.ljust(12),
                last_num_lote[:15].ljust(15),
                tipo_moneda[:5].ljust(5),
                type_de_pago[:10].ljust(10),
                first_letter_rif.ljust(1),
                rest_rif[:15].ljust(15),
                can1[:8].ljust(8),
                total_amount[:17].ljust(17),
                date[:8].ljust(8),
                batch.acc_number.acc_number[:20],
                reserved_area[:7].ljust(7),
                num_serial[:8].ljust(8),
                response_code[:4].ljust(4),
                fecha_proceso[:8].ljust(8),
                reserved_area2.zfill(261).ljust(261),
            )
            for wh in header.payment_ids:
                if not wh.third_payment:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Beneficiario')
                    primera_letra_rif = wh.partner_id.vat[0]
                    restante_rif = wh.partner_id.vat[2:]
                    if primera_letra_rif =='V':
                        restante_rif= restante_rif[:8]
                    if primera_letra_rif == 'J':
                        restante_rif= restante_rif[:9]
                    restante_rif  = restante_rif.zfill(15)
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount_cal = rs.join(str(amount_cal).split('.')).zfill(17)
                    num_ref = (wh.name).replace("/","").replace("-","").replace(".","")
                    ref = num_ref[-8:]
                    email = ''
                    if wh.partner_id.email :
                        email = wh.partner_id.email
                    tipo_de_pago = '0000000062'
                    tipo_registro = "2"
                    if wh.acc_number_partner.acc_number[:4] == '0105':
                        forma_pago = "1"
                    if wh.acc_number_partner.acc_number[:4] != '0105':
                        forma_pago = "3"
                    area_reservada12 = "000000000000" 
                    area_reservada = " "
                    area_reservada3 = "000000000000000"
                    area_reservada_3 = "000"
                    area_reservada4 = "0000000"
                    area_reservada35 = "0"
                    cliente_empresa = " "
                    response_code = "0000"
                    msj_respuesta = " "
                    payment_concept = " "
                    partner_name = (wh.partner_id.name).replace(",","").replace(".","").replace("'","")
                    replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    partner= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], partner_name)
                    content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        tipo_registro.ljust(1),
                        primera_letra_rif.ljust(1),
                        restante_rif[:15].ljust(15),
                        forma_pago.ljust(1),
                        area_reservada12.ljust(12),
                        area_reservada.ljust(15), 
                        area_reservada3[:15].ljust(15),
                        wh.acc_number_partner.acc_number.ljust(20),
                        amount_cal[:17].ljust(17),
                        cliente_empresa.ljust(16),
                        tipo_de_pago[:10].ljust(10),
                        area_reservada_3[:3].ljust(3),
                        partner[:60].ljust(60),
                        area_reservada4[:7].ljust(7),
                        ref[:8].ljust(8),
                        email[:50].ljust(50),
                        response_code[:4].ljust(4),
                        msj_respuesta.ljust(30),
                        payment_concept[:80].ljust(80),
                        area_reservada35.zfill(35)
                    )
                    wh.ref = ref[:8]
                else:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner_autorizado.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Autorizado')
                    if not wh.autorizado.autorizados.vat:
                        raise UserError('No le tiene asignado una cedulo o rif al Autorizado')
                    primera_letra_rif = wh.autorizado.autorizados.cedula[0]
                    restante_rif = wh.autorizado.autorizados.cedula[2:]
                    if primera_letra_rif =='V':
                        restante_rif= restante_rif[:8]
                    if primera_letra_rif =='J':
                        restante_rif= restante_rif[:9]
                    restante_rif  = restante_rif.zfill(15)
                    email = ''
                    if wh.autorizado.autorizados.email:
                       email =  wh.autorizado.autorizados.email
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount_cal = rs.join(str(amount_cal).split('.')).zfill(17)
                    num_ref = (wh.name).replace("/","").replace("-","").replace(".","")
                    ref = num_ref[-8:]
                    tipo_de_pago = '0000000062'
                    tipo_registro = "2"
                    if wh.acc_number_partner_autorizado.acc_number[:4] == '0105':
                        forma_pago = "1"
                    if wh.acc_number_partner_autorizado.acc_number[:4] != '0105':
                        forma_pago = "3"
                    area_reservada12 = "000000000000" 
                    area_reservada = " "
                    area_reservada3 = "000000000000000"
                    area_reservada_3 = "000"
                    area_reservada4 = "0000000"
                    area_reservada35 = "0"
                    cliente_empresa = " "
                    response_code = "0000"
                    msj_respuesta = " "
                    payment_concept = " "
                    partner_name =( wh.autorizado.autorizados.name).replace(",","").replace(".","").replace("'","")
                    replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    partner= re.sub(r'[ñéóíáÑÉÍÓÁ,.]',lambda c: replaces[c.group(0)], partner_name)
                    content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        tipo_registro.ljust(1),
                        primera_letra_rif.ljust(1),
                        restante_rif[:15].ljust(15),
                        forma_pago.ljust(1),
                        area_reservada12.ljust(12),
                        area_reservada.ljust(15),
                        area_reservada3[:15].ljust(15),
                        wh.acc_number_partner_autorizado.acc_number.ljust(20),
                        amount_cal[:17].ljust(17),
                        cliente_empresa.ljust(16),
                        tipo_de_pago[:10].ljust(10),
                        area_reservada_3[:3].ljust(3),
                        partner[:60].ljust(60),
                        area_reservada4[:7].ljust(7),
                        str(ref)[:8].ljust(8),
                        email[:50].ljust(50),
                        response_code[:4].ljust(4),
                        msj_respuesta.ljust(30),
                        payment_concept[:80].ljust(80),
                        area_reservada35.zfill(35)
                    )
                    wh.ref = ref[:8]
        return base64.encodebytes(bytes(content, 'utf-8')),nombre_archivo

    # Banco de Banplus
    def bank_0174(self,batch):
        r=''
        rs=''
        content = ''
        nombre_archivo = 'PAGO.txt'
        for header in batch:
            if not batch.acc_number.acc_number:
                raise UserError('El diario no tiene configurado una Cuenta Bancaria')
            rif = header.company_id.vat
            rest_rif = rif.replace("-", "")
            string_lote = batch.name.replace("/", "")
            num_lote = ''.join([i for i in string_lote if not i.isalpha()])
            can1 = len(header.payment_ids)
            monto_total = sum(header.payment_ids.mapped('amount'))
            amount_cal = "{0:.2f}".format(monto_total)
            total_amount = rs.join(str(amount_cal).split('.'))
            date = datetime.now().strftime("%Y/%m/%d").replace("/", "")
            punto_coma = ";"
            content += '%s%s%s%s%s%s%s%s%s%s%s\n'%(
                rest_rif[:12].ljust(12),
                punto_coma,
                batch.acc_number.acc_number[:20],
                punto_coma,
                str(can1),
                punto_coma,
                total_amount,
                punto_coma,
                date[:8].ljust(8),
                punto_coma,
                num_lote[:15].ljust(15),                               
            )
            for wh in header.payment_ids:
                if not wh.third_payment:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Beneficiario')
                    rif = wh.partner_id.vat
                    rest_rif = rif.replace("-", "")
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount_cal = rs.join(str(amount_cal).split('.'))
                    primera_letra_rif = wh.partner_id.vat[0]
                    if primera_letra_rif == "V":
                        tipo_documento = "01"
                    if  primera_letra_rif == "J":
                        tipo_documento = "04"
                    if  primera_letra_rif == "P":
                        tipo_documento = "02"
                    if  primera_letra_rif == "E":
                        tipo_documento = "08"
                    punto_coma = ";"
                    code_ref = (wh.payment_id.name).replace("/", "")
                    ejecucion = "SI"
                    email = ''
                    if wh.partner_id.email :
                        email = wh.partner_id.email
                    content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        tipo_documento,
                        punto_coma,
                        rest_rif[:9].ljust(9),
                        punto_coma,
                        wh.partner_id.name[:40].ljust(40),
                        punto_coma,
                        wh.acc_number_partner.acc_number[:20],
                        punto_coma,
                        amount_cal,
                        punto_coma,
                        code_ref[:15].ljust(15),
                        punto_coma,
                        email,
                        punto_coma,
                        ejecucion,
                    )
                else:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner_autorizado.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Autorizado')
                    rif = wh.autorizado.autorizados.vat
                    rest_rif = rif.replace("-", "")
                    
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount_cal = rs.join(str(amount_cal).split('.'))
                    #condicion de tipo de documento
                    primera_letra_rif = wh.autorizado.autorizados.cedula[0]
                    if primera_letra_rif == "V":
                        tipo_documento = "01"
                    if  primera_letra_rif == "J":
                        tipo_documento = "04"
                    if  primera_letra_rif == "P":
                        tipo_documento = "02"
                    if  primera_letra_rif == "E":
                        tipo_documento = "08"
                    punto_coma = ";"
                    code_ref = (wh.payment_id.name).replace("/", "")
                    ejecucion = "SI"
                    email = ''
                    if wh.autorizado.autorizados.email :
                        email = wh.autorizado.autorizados.email
                    content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                       tipo_documento,
                        punto_coma,
                        rest_rif[:9].ljust(9),
                        punto_coma,
                        wh.partner_id.name[:40].ljust(40),
                        punto_coma,
                        wh.acc_number_partner.acc_number[:20],
                        punto_coma,
                        amount_cal,
                        punto_coma,
                        code_ref[:15].ljust(15),
                        punto_coma,
                        email,
                        punto_coma,
                        ejecucion,
                    )
        return base64.encodebytes(bytes(content, 'utf-8')),nombre_archivo
    # Banco nacional de credito TXT
    def bank_0191(self,batch):
        r=''
        rs=''
        content = ''
        nombre_archivo = 'PAGO.txt'
        for header in batch:
            for wh in header.payment_ids:
                if not wh.third_payment:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Beneficiario')
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount = amount_cal.replace(".",",")
                    date = datetime.now().strftime("%d/%m/%Y")
                    ref = ''
                    if wh.ref:
                        ref = str(wh.ref)
                    code_ref = (wh.payment_id.name).replace("/", "").replace("-", "").replace(".", "")
                    newstring = ''.join([i for i in code_ref if not i.isalpha()])
                    new_code_ref = newstring[-10:].zfill(10)
                    email = ''
                    if wh.partner_id.email :
                        email = wh.partner_id.email
                    restante_rif = ''
                    if wh.partner_id.vat:
                        restante_rif = wh.partner_id.vat
                    partner = wh.partner_id.name
                    content += '%s%s%s%s%s%s%s%s%s\n'%(
                        date.ljust(10),
                        batch.acc_number.acc_number[:20],
                        wh.acc_number_partner.acc_number[:20],
                        amount.ljust(15),
                        ref[:60].ljust(60),
                        restante_rif[:10].ljust(10),
                        partner[:80].ljust(80),
                        email[:100].ljust(100),
                        new_code_ref[:10].ljust(10),
                    )
                else:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner_autorizado.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Autorizado')
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount = amount_cal.replace(".",",")
                    ref = ''
                    if wh.ref :
                        ref = str(wh.ref)
                    code_ref = (wh.payment_id.name).replace("/", "").replace("-", "").replace(".", "")
                    newstring = ''.join([i for i in code_ref if not i.isalpha()])
                    new_code_ref = newstring[-10:].zfill(10)
                    date = datetime.now().strftime("%d/%m/%Y")
                    email = ''
                    if  wh.autorizado.autorizados.email :
                        email = wh.autorizado.autorizados.email
                    restante_rif = ''
                    if wh.autorizado.autorizados.cedula:
                        restante_rif = wh.autorizado.autorizados.cedula
                    partner = wh.autorizado.autorizados.name
                    content += '%s%s%s%s%s%s%s%s%s\n'%(
                        date.ljust(10),
                        batch.acc_number.acc_number[:20],
                        wh.acc_number_partner_autorizado.acc_number[:20],
                        amount.ljust(15),
                        ref[:60].ljust(60),
                        restante_rif[:10].ljust(10),
                        partner[:80].ljust(80),
                        email[:100].ljust(100),
                        new_code_ref[:10].ljust(10),
                    )
        return base64.encodebytes(bytes(content, 'utf-8')),nombre_archivo

    # Bancaribe Ca  
    def bank_0114(self,batch):
        content = ''
        date = datetime.now().strftime("%d/%m/%y").replace("/", "")
        name = batch.name.replace("/","").replace(".","")
        batch_name = ''.join([i for i in name if not i.isalpha()])
        name_batch = batch_name[-6:]
        nombre_archivo = 'PAP-'+str(date)+'-'+ str(name_batch)+'.txt'
        for header in batch:
            for wh in header.payment_ids:
                if not wh.third_payment:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Beneficiario')
                    if not wh.acc_number_partner.tipo_de_cuenta:
                        raise UserError('Debe asignar un tipo cuenta para la cuenta del proveedor')
                    cedula_o_rif = wh.partner_id.vat
                    restante_rif = cedula_o_rif.replace("-", "")
                    amount_cal = "{0:.2f}".format(wh.amount)
                    code_archivo = "PAP"
                    un_slash = "/"
                    code_bank = wh.acc_number_partner.acc_number[:4]
                    cero = "0"
                    if wh.acc_number_partner.tipo_de_cuenta == 'corriente':
                        tipo_cuenta = "CTE"
                    if wh.acc_number_partner.tipo_de_cuenta == 'ahorro':
                        tipo_cuenta = "AH"
                    phone = ''
                    string = wh.payment_id.name.replace("/","").replace(".","").replace("-","")
                    lote_num = ''.join([i for i in string if not i.isalpha()])
                    num_lote = lote_num[-8:]
                    email = ''
                    if wh.partner_id.email : 
                        email = wh.partner_id.email
                    if wh.partner_id.phone : 
                        tel = (wh.partner_id.phone).replace("+","").replace("-","").replace(" ","")
                        phone = '0' + tel[9:]
                    content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        code_archivo,
                        un_slash,
                        un_slash,
                        cero.ljust(1),
                        un_slash,
                        code_bank.ljust(4),
                        un_slash,
                        wh.acc_number_partner.acc_number[:20],
                        un_slash,
                        tipo_cuenta,
                        un_slash,
                        cero.ljust(1),
                        un_slash,
                        amount_cal,
                        un_slash,
                        restante_rif.ljust(8),
                        un_slash,
                        wh.partner_id.name,
                        un_slash,
                        num_lote.ljust(8),
                        un_slash,
                        email,
                        un_slash,
                        phone[:11].ljust(11),
                        un_slash,
                        un_slash,
                    )
                else:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner_autorizado.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Autorizado')
                    if not wh.acc_number_partner_autorizado.tipo_de_cuenta:
                        raise UserError('Debe asignar un tipo cuenta para la cuenta del proveedor')
                    cedula_o_rif = wh.partner_id.vat
                    restante_rif = cedula_o_rif.replace("-", "")
                    amount_cal = "{0:.2f}".format(wh.amount)
                    code_archivo = "PAP"
                    un_slash = "/"
                    code_bank = wh.acc_number_partner_autorizado.acc_number[:4]
                    cero = "0"
                    if wh.acc_number_partner_autorizado.tipo_de_cuenta == 'corriente':
                        tipo_cuenta = "CTE"
                    if wh.acc_number_partner_autorizado.tipo_de_cuenta == 'ahorro':
                        tipo_cuenta = "AH"
                    string = wh.payment_id.name.replace("/","").replace("-","").replace(".","")
                    lote_num = ''.join([i for i in string if not i.isalpha()])
                    num_lote = lote_num[-8:]
                    email = ''
                    if  wh.autorizado.autorizados.email :
                       email =  wh.autorizado.autorizados.email
                    phone = ''
                    if  wh.autorizado.autorizados.phone :
                        tel = (wh.autorizado.autorizados.phone).replace("+","").replace("-","").replace(" ","")
                        phone =  '0' + tel[9:]
                    content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        code_archivo,
                        un_slash,
                        un_slash,
                        cero.ljust(1),
                        un_slash,
                        code_bank.ljust(4),
                        un_slash,
                        wh.acc_number_partner_autorizado.acc_number[:20],
                        un_slash,
                        tipo_cuenta,
                        un_slash,
                        cero.ljust(1),
                        un_slash,
                        amount_cal,
                        un_slash,
                        restante_rif.ljust(8),
                        un_slash,
                        wh.autorizado.autorizados.name,
                        un_slash,
                        num_lote.ljust(8),
                        un_slash,
                        email,
                        un_slash,
                        phone[:11].ljust(11),
                        un_slash,
                        un_slash,
                    )
        return base64.encodebytes(bytes(content, 'utf-8')),nombre_archivo
    # Banco Banesco Definición TXT
    def bank_0134(self,batch):
        rs=''
        content = ''
        date = datetime.now().strftime("%d/%m/%Y%H%M%S").replace("/", "")
        mismo_banco = False
        for lin in batch.mapped('payment_ids'):
            if not mismo_banco:
                mismo_banco = True if lin.acc_number_partner and lin.acc_number_partner.acc_number and str(lin.acc_number_partner.acc_number[:4]) != '0134' else False
                if mismo_banco:
                    break
                mismo_banco = True if lin.acc_number_partner_autorizado and lin.acc_number_partner_autorizado.acc_number and str(lin.acc_number_partner_autorizado.acc_number[:4]) != '0134' else False
        if mismo_banco:
            nombre_archivo = 'BPROV-BANES'+ ''+ str(date)+'.txt'    
        else:
            nombre_archivo = 'BPRO-BANES'+ ''+ str(date)+'.txt'
        for header in batch:
            count_batch = self.env['account.batch.payment'].search_count([('journal_id','=',header.journal_id.id),('id','!=',header.id),('date','=',header.date)]) + 1
            # la cabecera
            nom = 'HDRBANESCO        ED  95BPAYMULP'
            content += '%s\n'%(
                nom.ljust(32),
            )
            # segunda linea
            est = '01SCV'
            space = " "
            num = '9'
            # randomUpperLetter = chr(random.randint(ord('A'), ord('Z')))
            # randomUpperLetter2 = chr(random.randint(ord('A'), ord('Z')))
            randomUpperdigit = chr(random.randint(ord('0'), ord('9')))
            randomUpperdigit2 = chr(random.randint(ord('0'), ord('9')))
            letters = str(randomUpperdigit)+ str(randomUpperdigit2)
            date = datetime.now().strftime("%d%m%y").replace("/","")
            userdate = letters + str(date)+ str(count_batch)
            fecha = datetime.now().strftime("%Y%m%d%H%M%S").replace("/","")
            
            # fecha = header.date.strftime("%Y%m%d%H%M%S").replace("/", "")
            content += '%s%s%s%s%s%s%s\n'%(
                est.ljust(5),
                space.ljust(32),
                num.ljust(1),
                space.ljust(2),
                userdate.ljust(9),
                space.ljust(26),
                fecha.ljust(14)
            )

            for wh in header.payment_ids:
                if not wh.third_payment:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Beneficiario')
                        ############## DEBITO###########
                    num="02"
                    num_reg = (wh.name).replace("/","").replace(".","").replace("-","")
                    num_reg2 = ''.join([i for i in num_reg if not i.isalpha()])
                    num_restante = num_reg2[-8:].zfill(8)
                    space = " "
                    primera_letra_rif = header.company_id.rif[0]
                    restante_rif= header.company_id.rif[2:]
                    nom_empresa = (header.company_id.name).replace(",","").replace(".","").replace("'","")
                    replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    new_name = re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], nom_empresa)
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount_cal = rs.join(str(amount_cal).split('.'))
                    amount_cal = amount_cal.zfill(15)
                    ves = 'VES'
                    banesco = 'BANESCO'
                    fecha_pago = wh.date.strftime('%Y%m%d').replace("/","")
                    
                    content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        num.ljust(2),
                        num_restante.ljust(9),
                        space.ljust(21),
                        primera_letra_rif.ljust(1),
                        restante_rif.ljust(9),
                        space.ljust(7),
                        new_name[:32].ljust(32),
                        space.ljust(3),
                        amount_cal.ljust(15),
                        ves.ljust(3),
                        space,
                        batch.acc_number.acc_number.ljust(20),
                        space.ljust(14),
                        banesco.ljust(7),
                        space.ljust(4),
                        fecha_pago.ljust(8),
                    )
                    wh.ref = num_restante

                    ########## credito ##############
                    if not wh.partner_id.vat:
                        raise UserError(('El Contacto %s, no posee RIF asociado') % (wh.partner_id.name))
                    primera_letra_rif_partner = wh.partner_id.cedula[0] if not wh.partner_id.is_company else wh.partner_id.vat[0]
                    restante_rif = wh.partner_id.cedula[2:] if not wh.partner_id.is_company else wh.partner_id.vat[2:]
                    #restante_rif  = restante_rif.zfill(9)
                    num2="03"
                    num_reg = (wh.name).replace("/","").replace(".","").replace("-","")
                    num_reg2 = ''.join([i for i in num_reg if not i.isalpha()])
                    num_restante = num_reg2[-8:].zfill(8)
                    space = " "
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount_cal = rs.join(str(amount_cal).split('.'))
                    amount_cal = amount_cal.zfill(15)
                    ves1 = 'VES'
                    primeros_4_num_account = wh.acc_number_partner.acc_number[:4]
                    if primeros_4_num_account == '0134':
                        last_num = '42'
                    if primeros_4_num_account != '0134':
                        last_num = '425'
                    email = ''
                    if wh.partner_id.email :
                        email = wh.partner_id.email
                    partner_name = (wh.partner_id.name).replace(",","").replace(".","").replace("'","")
                    replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    partner= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], partner_name)
                    content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        num2.ljust(2),
                        num_restante.ljust(9),
                        space.ljust(21),
                        amount_cal.ljust(15),
                        ves1.ljust(3),
                        wh.acc_number_partner.acc_number.ljust(20),
                        space.ljust(10),
                        primeros_4_num_account.ljust(4),
                        space.ljust(10),
                        primera_letra_rif_partner.ljust(1),
                        restante_rif.ljust(9),
                        space.ljust(7),
                        partner[:45].ljust(45),
                        space.ljust(25),
                        email.ljust(40),
                        space.ljust(161),
                        last_num,
                    )
                else:
                    if not header.journal_id.bank_account_id.acc_number:
                        raise UserError('El diario no tiene configurado una Cuenta Bancaria')
                    if not  wh.acc_number_partner_autorizado.acc_number:
                        raise UserError('No le ha registrado Cuentas Bancarias al Autorizado')
                    if not wh.autorizado.autorizados.vat:
                        raise UserError('No tiene asignado una cedula o un rif al Autorizado')
                    
                    ############### debito #############
                    num="02"
                    num_reg = (wh.name).replace("/","").replace(".","").replace("-","")
                    num_reg2 = ''.join([i for i in num_reg if not i.isalpha()])
                    num_restante = num_reg2[-8:].zfill(8)
                    space = " "
                    primera_letra_rif = header.company_id.rif[0]
                    restante_rif= header.company_id.rif[2:]
                    nom_empresa = (header.company_id.name).replace(",","").replace(".","").replace("'","")
                    replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    company= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], nom_empresa)
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount_cal = rs.join(str(amount_cal).split('.'))
                    amount_cal = amount_cal.zfill(15)
                    ves = 'VES'
                    banesco = 'BANESCO'
                    fecha_pago = wh.date.strftime('%Y%m%d').replace("/","")
                    content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        num.ljust(2),
                        num_restante.ljust(9),
                        space.ljust(21),
                        primera_letra_rif.ljust(1),
                        restante_rif.ljust(9),
                        space.ljust(7),
                        company[:32].ljust(32),
                        space.ljust(3),
                        amount_cal.ljust(15),
                        ves.ljust(3),
                        space,
                        batch.acc_number.acc_number.ljust(20),
                        space.ljust(14),
                        banesco.ljust(7),
                        space.ljust(4),
                        fecha_pago.ljust(8),
                    )
                    wh.ref = num_restante

                    ########## credito ##############
                    if not wh.autorizado.autorizados.vat:
                        raise UserError(('El Contacto %s, no posee RIF asociado') % (wh.autorizado.autorizados.name))
                    primera_letra_rif_partner = wh.autorizado.autorizados.cedula[0] if not wh.autorizado.autorizados.is_company else wh.autorizado.autorizados.vat[0]
                    restante_rif = wh.autorizado.autorizados.cedula[2:] if not wh.autorizado.autorizados.is_company else wh.autorizado.autorizados.vat[2:]
                    #restante_rif  = restante_rif.zfill(9) if not wh.autorizado.autorizados.is_company else restante_rif.zfill(9)
                    amount_cal = "{0:.2f}".format(wh.amount)
                    amount_cal = rs.join(str(amount_cal).split('.'))
                    amount_cal = amount_cal.zfill(15)
                    primeros_4_num_account = wh.acc_number_partner_autorizado.acc_number[:4]
                    if primeros_4_num_account == '0134':
                        last_num = '42'
                    if primeros_4_num_account != '0134':
                        last_num = '425'
                    num2="03"
                    ves1 = 'VES'
                    num_reg = (wh.name).replace("/","").replace(".","").replace("-","")
                    num_reg2 = ''.join([i for i in num_reg if not i.isalpha()])
                    num_restante = num_reg2[-8:].zfill(8)
                    email = ''
                    if wh.autorizado.autorizados.email:
                        email = wh.autorizado.autorizados.email
                    partner_name = (wh.autorizado.autorizados.name).replace(",","").replace(".","").replace("'","")
                    replaces = {"ñ":"n","é":"e", "ó":"o","í":"i","á":"a","Ñ":"N","É":"E","Í":"I","Ó":"O","Á":"A" }
                    partner= re.sub(r'[ñéóíáÑÉÍÓÁ]',lambda c: replaces[c.group(0)], partner_name)
                    content += '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n'%(
                        num2.ljust(2),
                        num_restante.ljust(9),
                        space.ljust(21),
                        amount_cal.ljust(15),
                        ves1.ljust(3),
                        wh.acc_number_partner_autorizado.acc_number.ljust(20),
                        space.ljust(10),
                        primeros_4_num_account.ljust(4),
                        space.ljust(10),
                        primera_letra_rif_partner.ljust(1),
                        restante_rif.ljust(9),
                        space.ljust(7),
                        partner[:45].ljust(45),
                        space.ljust(25),
                        email.ljust(40),
                        space.ljust(161),
                        last_num,
                    )
            standard = '060000000000000'  
            standard2 = '0000000000000'
            can = str(len(header.payment_ids)).zfill(2)  
            can2 = str(len(header.payment_ids)).zfill(2)
            monto_total = sum(header.payment_ids.mapped('amount'))
            amount_cal = "{0:.2f}".format(monto_total)
            total_amount = rs.join(amount_cal.split('.')).zfill(15)  
            content += '%s%s%s%s%s\n'%(
                standard.ljust(15),
                can[:2].ljust(2),
                standard2.ljust(13),
                can2[:2].ljust(2),
                total_amount[:15].ljust(15)
            )
        return base64.encodebytes(bytes(content, 'utf-8')),nombre_archivo

    # Banco del Sur Definición INGRESO BENEFICIARIO
    def bank_0157_bene(self,batch):
        rs=''
        content = ''
        nombre_archivo = 'PAGO.txt'
        for header in batch:
            for wh in header.payment_ids:
                if not wh.partner_id.email:
                    raise UserError('No le ha registrado email/correo electronico al Beneficiario')
                if not wh.acc_number_partner.acc_number:
                    raise UserError("No le ha registrado Cuentas Bancarias al Beneficiario")
                primera_letra_rif = wh.partner_id.vat[0]
                restante_rif = wh.partner_id.vat[2:]
                restante_rif  = restante_rif.zfill(12)
                amount_cal = rs.join(str(wh.amount).split('.'))
                amount_cal = rs.join(amount_cal.split('-'))
                amount_cal = amount_cal.zfill(18)
                email = ''
                if wh.partner_id.email:
                    email = wh.partner_id.email
                content += '%s%s%s%s%s\n'%(
                    primera_letra_rif,
                    restante_rif,
                    wh.partner_id.name[:50].ljust(50),
                    wh.acc_number_partner.acc_number.ljust(20),
                    email[:50].ljust(50),
                    #wh.payment_id.journal_id.bank_account_id.acc_number,
                    #wh.payment_id.payment_date,
                    )
        return base64.encodebytes(bytes(content, 'utf-8')),nombre_archivo

    #No permitir eliminar un lote si no está en borrador
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError('No puede eliminar un pago por lote ya confirmado y/o conciliado')
        return super(AccountPaymentBatchHeader, self).unlink()


    def validate_batch_button(self):
        for rec in self:
            rec.message_post(body=_('Los Pagos han sido CONFIRMADOS por %s') % (self.env.user.name))
        return super(AccountPaymentBatchHeader, self).validate_batch_button()

    def validate_all_payment(self):
        for rec in self:
            rec.message_post(body=_('Los Pagos han sido CONFIRMADOS por %s') % (self.env.user.name))
            for pay in rec.payment_ids.filtered(lambda x: x.state=='draft'):
                pay.action_post()

    def unlink_all_payment(self):
        for rec in self:
            rec.message_post(body=_('Los Pagos han sido Desvinculados por %s') % (self.env.user.name))
            for pay in rec.payment_ids:
                pay.batch_payment_id = False

class AccountPaymentBatchDetail(models.Model):

    _inherit = 'account.payment'

    acc_number_partner = fields.Many2one('res.partner.bank',compute="_compute_account_accnumber",string="N° Cuenta Bancaria",readonly=False,domain="[('partner_id', '=', partner_id)]")
    acc_number_partner_autorizado = fields.Many2one('res.partner.bank',compute="_compute_account_accnumber",string="N° Cuenta Bancaria Autorizado",readonly=False,store=True)
    name_bank = fields.Many2one(related='acc_number_partner.bank_id', string="Banco", readonly=True)
    name_bank_autorizado = fields.Many2one(related='acc_number_partner_autorizado.bank_id', string="Banco del Autorizado", readonly=True)

    @api.depends('partner_id','autorizado','company_id')
    def _compute_account_accnumber(self):
        for rec in self:
            rec.acc_number_partner_autorizado = False
            rec.acc_number_partner = False
            if rec.partner_id:
                rec.acc_number_partner = self.env['res.partner.bank'].search([('partner_id', '=', rec.partner_id.id),('company_id', '=', rec.company_id.id)],limit=1)
            if rec.autorizado:
                rec.acc_number_partner_autorizado = self.env['res.partner.bank'].search([('partner_id', '=', rec.autorizado.autorizados.id),('company_id', '=', rec.company_id.id)],limit=1)
            if rec.partner_bank_id and not rec.autorizado:
                rec.acc_number_partner = rec.partner_bank_id.id

class AccountJournalTxt(models.Model):
    _inherit = 'account.journal'

    txt_payment =  fields.Selection([
        ("0102", 'Banco de Venezuela S.A.C.A. Banco Universal'),
        ("0104", 'Venezolano de Crédito, S.A. Banco Universal'),
        ("0105", 'Banco Mercantil, C.A S.A.C.A. Banco Universal'),
        ("0108", 'Banco Provincial, S.A. Banco Universal'),
        ("0114", 'Bancaribe C.A. Banco Universal'),
        ("0115", 'Banco Exterior C.A. Banco Universal'),
        ("0116", 'Banco Occidental de Descuento, Banco Universal C.A.'),
        ("0128", 'Banco Caroní C.A. Banco Universal'),
        ("0134", 'Banesco Banco Universal S.A.C.A.'),
        ("0137", 'Banco Sofitasa Banco Universal'),
        ("0138", 'Banco Plaza Banco Universal'),
        ("0146", 'Banco de la Gente Emprendedora C.A.'),
        ("0149", 'Banco del Pueblo Soberano, C.A. Banco de Desarrollo'),
        ("0151", 'BFC Banco Fondo Común C.A Banco Universal'),
        ("0156", '100% Banco, Banco Universal C.A.'),
        ("0157", 'DelSur Banco Universal, C.A.'),
        ("0163", 'Banco del Tesoro, C.A. Banco Universal'),
        ("0166", 'Banco Agrícola de Venezuela, C.A. Banco Universal'),
        ("0168", 'Bancrecer, S.A. Banco Microfinanciero'),
        ("0169", 'Mi Banco Banco Microfinanciero C.A.'),
        ("0171", 'Banco Activo, C.A. Banco Universal'),
        ("0172", 'Bancamiga Banco Microfinanciero C.A.'),
        ("0173", 'Banco Internacional de Desarrollo, C.A. Banco Universal'),
        ("0174", 'Banplus Banco Universal, C.A.'),
        ("0175", 'Banco Bicentenario Banco Universal C.A.'),
        ("0176", 'Banco Espirito Santo, S.A. Sucursal Venezuela B.U.'),
        ("0177", 'Banco de la Fuerza Armada Nacional Bolivariana, B.U.'),
        ("0190", 'Citibank N.A.'),
        ("0191", 'Banco Nacional de Crédito, C.A. Banco Universal'),
        ("0601", 'Instituto Municipal de Crédito Popular'),
        ], string="Banco para Generación de TXT",)

