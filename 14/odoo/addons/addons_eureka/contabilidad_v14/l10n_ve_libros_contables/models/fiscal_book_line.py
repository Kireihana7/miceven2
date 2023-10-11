import time
from odoo import fields, models, api, _

class FiscalBookLines(models.Model):
    _description = "Venta y compra de líneas de libros fiscales en Venezuela"
    _name = 'fiscal.book.line'

    base = fields.Float('Base Imponible')
    amount =fields.Float('Monto Factura')
    name = fields.Char("Líneas de libros fiscales")
    fiscal_id = fields.Many2one('fiscal.book', 'Fiscal Book',
    help='Libro fiscal que posee esta línea de libro', ondelete='cascade', index=True)
    invoice_id = fields.Many2one('account.move', 'Factura',
    help="Factura relacionada con esta línea de libro")
    iwdl_id = fields.Many2one('account.wh.iva.line', 'Retencion de IVA',
    help="Retención de la línea iva relacionada con esta línea del libro")
    #  Invoice and/or Document Data
    emission_date = fields.Date(string='Fecha de emisión', help='Fecha del documento de factura / Fecha del comprobante de línea de IVA')
    accounting_date = fields.Date(string='Fecha Contable',
    help="El día del registro contable [(factura, fecha de factura), "
    "(línea de retencion de IVA, Fecha de retencion)]")
    doc_type = fields.Char('Tipo de Documento', size=20, help='Tipo de Documento')
    partner_name = fields.Char(size=128, string='Nombre de la Empresa', help='')
    people_type = fields.Char(string='Tipo de Persona', help='')
    partner_vat = fields.Char(size=128, string='Nro. RIF', help='')
    affected_invoice = fields.Char(string='Factura Afectada', size=64,
    help="Para un tipo de línea de factura significa factura principal para un Débito "
    "o Nota de crédito. Para un tipo de línea de retención se entiende la factura"
    "número relacionado con la retención")
    # Apply for wh iva lines
    get_wh_vat = fields.Many2one('account.wh.iva',string="Retención de IVA", help="Retención de IVA")
    wh_number = fields.Char(string='Nro de  Comprobante de Retención', size=64, help="")
    affected_invoice_date = fields.Date(string="Fecha de factura Afectada", help="")
    wh_rate = fields.Float(string="Porcentaje de retención", help="")
    wh_amount = fields.Float(string="Monto de la Retención", help="")

    get_wh_debit_credit = fields.Float(store=True,string="Base Debito Fiscal",
    help="Suma de toda la cantidad de impuestos para los impuestos relacionados con la línea de retencion de IVA")
    ctrl_number = fields.Char(string='Nro de Control de Factura', size=64, help='')
    invoice_number = fields.Char(string='Nro de Factura', size=64, help='')
    debit_affected = fields.Char(string='Notas de débito afectadas', size=256, help='Notas de débito afectadas')
    credit_affected = fields.Char(string='Notas de crédito afectadas', size=256, help='Notas de crédito afectadas')
    type = fields.Selection(([('01-reg','Registro'),
                                          ('02-complemento', 'Complemento'),
                                          ('03-anulacion', 'Anulación'),
                                          ('04-ajuste', 'Ajuste')]), string='Tipo de Transacción', readonly=True)
    total_with_iva = fields.Float('Total con IVA', help="Sub Total of the invoice (untaxed amount) plus"
    " all tax amount of the related taxes")
    vat_exempt = fields.Float("Exento", help="Exempt is a Tax with 0 tax percentage")
    vat_reduced_base = fields.Float("Base Reducido", help="Vat Reduced Base Amount")
    vat_reduced_tax = fields.Float("IVA Reducido", help="Vat Reduced Tax Amount")
    vat_general_base = fields.Float("Base Imponible", help="Vat General Base Amount")
    vat_general_tax = fields.Float("IVA", help="Vat General Tax Amount")
    vat_additional_base = fields.Float("Base Adicional", help="Vat Generald plus Additional Base Amount")
    vat_additional_tax = fields.Float("IVA Adicional", help="Vat General plus Additional Tax Amount")
