# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _
import pytz
import datetime


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    is_dotmatrix = fields.Boolean("Seleccionable para DotMatrix")
class ResCompanys(models.Model):
    _inherit = 'res.company'

    dotmatrika_templ = fields.Many2one('mail.template',"Seleccionar modelo para DotMatrix",domain="[('is_dotmatrix','=',True)]")

class AccountDotmatrixReceipt(models.TransientModel):
    _name = 'account.dotmatrix.receipt'

    name = fields.Char("Test")


class AccountMove(models.Model):
    _inherit = "account.move"
 

    vendor_id=fields.Many2one("hr.employee",string="Vendedor")
    def print_new_receipt(self):
        if not self.company_id.dotmatrika_templ:
            templ = self.env.ref("invoice_dotmatrix_printer_.template_dotmatrix_ai")
        else:
            templ=self.company_id.dotmatrika_templ
        if templ:
            data = self.env['mail.render.mixin']._render_template(templ.body_html, 'account.move', [self.id])
            view_id = self.env.ref('invoice_dotmatrix_printer_.account_dotmatrix_receipt_form').id
            res = {
            	"name":data[self.id],
            }
            wizard_id = self.env['account.dotmatrix.receipt'].create(res)
            context = self._context.copy()
            return {
                'name':'Print Receipt',
                'view_type':'form',
                'view_mode':'tree',
                'views' : [(view_id,'form')],
                'res_model':'account.dotmatrix.receipt',
                'view_id':view_id,
                'type':'ir.actions.act_window',
                'res_id':wizard_id.id,
                'target':'new',
                'context':context,

            }


    undiscounted_amount=fields.Float(compute="get_undiscounted")
    discount_total_amount=fields.Float(compute="get_discounted")
    amount_untaxed_excent=fields.Float(compute="get_exent")
    amount_untaxed_notexcent=fields.Float(compute="get_exent")
    @api.depends('invoice_line_ids')
    def get_undiscounted(self):
        for rec in self:
            undiscounted=0
            for line in rec.invoice_line_ids:
                undiscounted+=line.quantity*line.price_unit
            rec.undiscounted_amount=undiscounted

    @api.depends('invoice_line_ids','undiscounted_amount')
    def get_discounted(self):
        for rec in self:
            subtotal=0
            for line in rec.invoice_line_ids:
                subtotal+=line.price_subtotal
            rec.discount_total_amount=rec.undiscounted_amount-subtotal

    @api.depends('invoice_line_ids',)
    def get_exent(self):
        for rec in self:
            base_not_exent=0
            for line in rec.invoice_line_ids.filtered("tax_ids"):
                if any([tax.amount>0 for tax in line.tax_ids]):
                    base_not_exent+=line.price_subtotal
            rec.amount_untaxed_notexcent=base_not_exent
            rec.amount_untaxed_excent=rec.amount_untaxed-base_not_exent
    
    
    
    
    direccion_completa = fields.Char(
        compute = '_compute_direccion_completa',
        string='Filed Label',
    )
    direccion_entrega_completa = fields.Char(
        compute = '_compute_direccion_completa',
        string='Filed Label',
    )
    nombre_corto_factura = fields.Char(
        string='Nombre Corto',
        compute = '_compute_nombre_factura',
    )

    total_bolivares_letras=fields.Char(string='Nombre Corto',
        compute = '_compute_valor_bolivares')
    @api.depends("amount_total","tasa_del_dia")
    def _compute_valor_bolivares(self):
        for rec in self:
            rec.total_bolivares_letras=rec.numero_to_letras(round(rec.amount_total*rec.tasa_del_dia,2))
    def _compute_nombre_factura(self):
        
        for rec in self:
            nombre = rec.name.split('/')
            rec.nombre_corto_factura = nombre[-1]


    def _compute_direccion_completa(self):
        for rec in self:
            rec.direccion_completa = " ".join([
                *[x or "" for x in [rec.partner_id.street, rec.partner_id.street2]],
                *[x.name if x else "" for x in [
                    rec.partner_id.city_id, 
                    rec.partner_id.state_id, 
                    rec.partner_id.country_id
                ]]
            ])
            rec.direccion_entrega_completa= " ".join([
                *[x or "" for x in [rec.partner_shipping_id.street, rec.partner_shipping_id.street2]],
                *[x.name if x else "" for x in [
                    rec.partner_shipping_id.city_id, 
                    rec.partner_shipping_id.state_id, 
                    rec.partner_shipping_id.country_id
                ]]
            ])

    @api.onchange("journal_id")
    def _onchange_journal_id(self):
        for rec in self:
            if rec.journal_id.id == 39:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                    'params': {
                        "menu_id": self.env.ref("account.view_move_form").id
                    }
                }

    def numero_to_letras(self, numero):

        indicador = [("",""),("MIL","MIL"),("MILLON","MILLONES"),("MIL","MIL"),("BILLON","BILLONES")]
        entero = int(numero)
        decimal = int(round((numero - entero)*100))
        #print 'decimal : ',decimal 
        contador = 0
        numero_letras = ""
        while entero >0:
            a = entero % 1000
            if contador == 0:
                en_letras = convierte_cifra(a,1).strip()
            else :
                en_letras = convierte_cifra(a,0).strip()
            if a==0:
                numero_letras = en_letras+" "+numero_letras
            elif a==1:
                if contador in (1,3):
                    numero_letras = indicador[contador][0]+" "+numero_letras
                else:
                    numero_letras = en_letras+" "+indicador[contador][0]+" "+numero_letras
            else:
                numero_letras = en_letras+" "+indicador[contador][1]+" "+numero_letras
            numero_letras = numero_letras.strip()
            contador = contador + 1
            entero = int(entero / 1000)
        numero_letras = numero_letras+" con " + str(decimal) +"/100"
        # print 'numero: ',numero
        return numero_letras
 

def convierte_cifra(numero,sw):

    lista_centana = ["",("CIEN","CIENTO"),"DOSCIENTOS","TRESCIENTOS","CUATROCIENTOS","QUINIENTOS","SEISCIENTOS","SETECIENTOS","OCHOCIENTOS","NOVECIENTOS"]
    lista_decena = ["",("DIEZ","ONCE","DOCE","TRECE","CATORCE","QUINCE","DIECISEIS","DIECISIETE","DIECIOCHO","DIECINUEVE"),
                    ("VEINTE","VEINTI"),("TREINTA","TREINTA Y "),("CUARENTA" , "CUARENTA Y "),
                    ("CINCUENTA" , "CINCUENTA Y "),("SESENTA" , "SESENTA Y "),
                    ("SETENTA" , "SETENTA Y "),("OCHENTA" , "OCHENTA Y "),
                    ("NOVENTA" , "NOVENTA Y ")]

    lista_unidad = ["",("UN" , "UNO"),"DOS","TRES","CUATRO","CINCO","SEIS","SIETE","OCHO","NUEVE"]
    centena = int (numero / 100)
    decena = int((numero -(centena * 100))/10)
    unidad = int(numero - (centena * 100 + decena * 10))
    #print "centena: ",centena, "decena: ",decena,'unidad: ',unidad

    texto_centena = ""
    texto_decena = ""
    texto_unidad = "" 

    #Validad las centenas
    texto_centena = lista_centana[centena]
    if centena == 1:
        if (decena + unidad)!=0:
            texto_centena = texto_centena[1]
        else :
            texto_centena = texto_centena[0] 

    #Valida las decenas

    texto_decena = lista_decena[decena]
    if decena == 1 :
         texto_decena = texto_decena[unidad]
    elif decena > 1 :
        if unidad != 0 :
            texto_decena = texto_decena[1]
        else:
            texto_decena = texto_decena[0]

    #Validar las unidades
    #print "texto_unidad: ",texto_unidad

    if decena != 1:
        texto_unidad = lista_unidad[unidad]
        if unidad == 1:
            texto_unidad = texto_unidad[sw] 

    return "%s %s %s" %(texto_centena,texto_decena,texto_unidad)





