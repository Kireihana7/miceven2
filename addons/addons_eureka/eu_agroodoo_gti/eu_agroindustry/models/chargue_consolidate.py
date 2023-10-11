# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
    
class ChargueConsolidate(models.Model):
    _name = 'chargue.consolidate'
    _description ="Gestión de Agro Industria"
    _inherit= ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date desc'
    # Campos Base
    name = fields.Char(string="Nombre", readonly=True, default='/',tracking=True,) 
    company_id = fields.Many2one('res.company',string="Compañía", required=True, default=lambda self: self.env.company,tracking=True,invisible=True)
    state = fields.Selection([
        ('por_llegar', 'Por Llegar'),
        ('patio', 'Patio'),
        ('peso_bruto', 'Peso Bruto'),
        ('peso_tara', 'Peso Tara'),
        ('proceso', 'En Proceso'),
        ('aprobacion', 'Análisis Calidad'),
        ('por_salir', 'Por Salir'),
        ('finalizado', 'Finalizado'),
        ('rechazada', 'Rechazada'),
        ('multi', 'Multi Pesado'),
        ('cancelado', 'Cancelado'),
        ], string='Estatus', readonly=True, copy=False, index=True, tracking=True, default='por_llegar')
    origin = fields.Char(string="Origen")
    romana_cancel_reason_id = fields.Many2one("chargue.consolidate.cancel", string= "Motivo de cancelación",)
    descripcion = fields.Char(string="Observación de la Cancelación", readonly=True, store=True)
    # Tipo de Orden de Carga/Descarga/Transferencia
    operation_type = fields.Selection([
        ('venta', 'Venta'),
        ('compra', 'Compra'),
        ('transferencia', 'Transferencia'),
        ], string='Tipo de Operación', copy=False, index=True, tracking=True, default='')
    is_return = fields.Boolean("Es devolución", tracking=True)
    is_return_compra = fields.Boolean(
        "Devolución de compra",
        compute="_compute_is_return",
        tracking=True,
        store=True
    )
    is_return_venta = fields.Boolean(
        "Devolución de venta",
        compute="_compute_is_return",
        tracking=True,
        store=True
    )

    @api.depends("operation_type","is_return")
    def _compute_is_return(self):
        for rec in self:
            rec.is_return_compra = rec.is_return_venta = False

            if not rec.is_return:
                continue
                
            rec.is_return_compra = rec.operation_type == "compra"
            rec.is_return_venta = rec.operation_type == "venta"

    @api.model
    def _get_default_balanza(self):
        return self.env['romana.serial'].search([('company_id','=',self.env.company.id)],order="id ASC",limit=1)
    # Configuración Serial
    balanza = fields.Many2one('romana.serial',string="Balanza",tracking=True,default=_get_default_balanza)

    # Fechas
    date = fields.Datetime(string="Fecha de Creación",tracking=True,default=lambda self: fields.Datetime.now(),readonly=True)
    scheduled_date = fields.Datetime(string="Fecha Programada",tracking=True,default=lambda self: fields.Datetime.now(),)
    date_first_weight = fields.Datetime(string="Primera Pesada",tracking=True,readonly=True)
    date_second_weight = fields.Datetime(string="Segunda Pesada",tracking=True,readonly=True)
    date_first_weight_t = fields.Datetime(string="Primera Pesada Trailer",tracking=True,readonly=True)
    date_second_weight_t = fields.Datetime(string="Segunda Pesada Trailer",tracking=True,readonly=True)
    date_por_llegar = fields.Datetime(string="Fecha Entrada",tracking=True,readonly=True)
    date_patio = fields.Datetime(string="Fecha Aprobación",tracking=True,readonly=True)
    date_peso_bruto = fields.Datetime(string="Fecha en Proceso",tracking=True,readonly=True)
    date_aprobacion = fields.Datetime(string="Fecha Aprobación",tracking=True,readonly=True)
    date_peso_tara = fields.Datetime(string="Fecha Peso Tara",tracking=True,readonly=True)
    date_por_salir = fields.Datetime(string="Fecha por Salir",tracking=True,readonly=True)
    date_finalizado = fields.Datetime(string="Fecha de Salida",tracking=True,readonly=True)
    date_rechazada = fields.Datetime(string="Fecha de Rechazo",tracking=True,readonly=True)
    
    # Aprobaciones
    approval_first_weight = fields.Many2one('res.users',string="Aprobación Primera Pesada",tracking=True,readonly=True)
    approval_second_weight = fields.Many2one('res.users',string="Aprobación Segunda Pesada",tracking=True,readonly=True)
    approval_first_weight_t = fields.Many2one('res.users',string="Aprobación Primera Pesada Trailer",tracking=True,readonly=True)
    approval_second_weight_t = fields.Many2one('res.users',string="Aprobación Segunda Pesada Trailer",tracking=True,readonly=True)
    approval_por_llegar = fields.Many2one('res.users',string="Aprobación Fecha Entrada",tracking=True,readonly=True)
    approval_patio = fields.Many2one('res.users',string="Aprobación Fecha Aprobación",tracking=True,readonly=True)
    approval_peso_bruto = fields.Many2one('res.users',string="Aprobación Fecha en Proceso",tracking=True,readonly=True)
    approval_aprobacion = fields.Many2one('res.users',string="Aprobación Fecha Aprobación",tracking=True,readonly=True)
    approval_peso_tara = fields.Many2one('res.users',string="Aprobación Fecha Peso Tara",tracking=True,readonly=True)
    approval_por_salir = fields.Many2one('res.users',string="Aprobación Fecha por Salir",tracking=True,readonly=True)
    approval_finalizado = fields.Many2one('res.users',string="Aprobación Fecha de Salida",tracking=True,readonly=True)
    approval_rechazada = fields.Many2one('res.users',string="Aprobación Fecha de Rechazo",tracking=True,readonly=True)

    # Campo del Contacto
    partner_id      = fields.Many2one('res.partner', string="Contacto", tracking=True)

    # Vehículo, Tipo de Vehículo, Conductor, Placa, Si tiene remolque y Placa del Remolque
    vehicle_id      = fields.Many2one('fleet.vehicle', string="Vehículo", tracking=True)
    vehicle_type_property    = fields.Selection(related='vehicle_id.vehicle_type_property',store=True)
    driver_id       = fields.Many2one('res.partner', string="Conductor",store=True,readonly="0",domain="[('is_driver','=',True)]")
    license_plate   = fields.Char(string="Licencia", related="vehicle_id.license_plate",store=True)
    cedula          = fields.Char(string="Cédula", related="driver_id.cedula",store=True)
    with_trailer    = fields.Boolean(string="¿Tiene Remolque?",tracking=True)
    plate_trailer   = fields.Char(string="Placa del Remolque",tracking=True)
    
    #Relación con la PO
    purchase_id     = fields.Many2one('purchase.order',string="Orden de Compra",tracking=True,domain="[('state','=','purchase')]")

    #Relación con la SO
    sale_ids = fields.Many2many(
        "sale.order",
        "chargue_consolidate_sale_order_rel",
        "consolidate_id",
        "sale_order_id",
        string="Orden de Venta",
        readonly=True,
        tracking=True,
        domain="[('state','=','sale')]"
    )

    #Relación con la SU
    picking_id       = fields.Many2many('stock.picking',string="Movimiento de Inventario",tracking=True,)
    picking_id_weight = fields.Float(string="Total Peso",compute="_compute_total_weight")
    #picking_id_state = fields.Selection(related="picking_id.state",string="Estatus SU",tracking=True)

    # Relación con el multipeso
    multi_active        = fields.Boolean(string="¿Multi Pesado?",default=False)
    multi_weight        = fields.One2many(
        comodel_name='chargue.multi.weight',
        inverse_name='chargue_consolidate',
        string='Multi Peso',
    )
    # Pesos Romana (Bruto, Tara, Neto)
    peso_bruto = fields.Float(
        string="Peso Bruto",
        store=True,
        tracking=True,
        digits=(20,4),
    )
    peso_tara = fields.Float(
        string="Peso Tara",
        store=True,
        tracking=True
    )
    peso_bruto_trailer = fields.Float(
        string="Peso Bruto Trailer",
        store=True,
        tracking=True
    )
    peso_tara_trailer = fields.Float(
        string="Peso Tara Trailer",
        store=True,
        tracking=True
    )
    peso_neto = fields.Float(
        string="Peso Neto",
        store=False,
        compute="compute_peso_neto",
        tracking=False,
        digits=(20,4),
    )
    peso_neto_trailer = fields.Float(
        string="Peso Neto Trailer",
        store=False,
        compute="compute_peso_neto_trailer",
        tracking=False
    )
    peso_condicionado = fields.Float(
        string="Peso Acondicionado",
        store=False,
        compute="compute_peso_condicionado",
        tracking=False,
        digits=(20,4),
    )
    peso_tolerancia = fields.Float(
        string="Peso Tolerancia",
        store=False,
        compute="compute_peso_tolerancia",
        tracking=False,
    )
    peso_resta = fields.Float(
        string="Diferencia de Peso",
        store=False,
        compute="compute_peso_resta",
        tracking=False,
    )
    peso_neto_dashboard = fields.Float(
        string="Peso Neto Dashboard",
        store=True,
        compute="compute_peso_neto_dashboard",
        tracking=True,
    )
    peso_condicionado_dashboard = fields.Float(
        string="Peso Acondicionado Dashboard",
        store=True,
        compute="compute_peso_condicionado_dashboard",
        tracking=True,
    )
    peso_neto_total = fields.Float(compute="_compute_peso_neto_total", tracking=True, digits=(20,4),)
    peso_bruto_total = fields.Float(compute="_compute_peso_bruto_total", tracking=True, digits=(20,4),)
    peso_tara_total = fields.Float(compute="_compute_peso_tara_total", tracking=True, digits=(20,4),)
    peso_realizado_total = fields.Float(compute="_compute_peso_realizado_total", tracking=True, digits=(20,4),)
    diff_tolerancia = fields.Float(compute="_compute_diff_tolerancia", tracking=True, digits=(20,4),)
    descuento_realizado = fields.Float(string="Descuento Realizado",readonly=True)
    descuento_realizado_trailer = fields.Float(string="Descuento Realizado Trailer",readonly=True)
    aplicar_descuento = fields.Boolean(string="Aplicar Descuento",default=False)

    @api.onchange("picking_id")
    def _onchange_picking_id(self):
        return {
            "domain": {
                "product_id": [("id","in",self.picking_id.move_ids_without_package.product_id.ids)],
            }
        }
    
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """ This override is done in order for the grouped list view to display the total value of
        the quants inside a location. This doesn't work out of the box because `value` is a computed
        field.
        """
        #if 'peso_neto' not in fields or 'peso_neto_trailer' not in fields or 'peso_condicionado' not in fields or 'peso_tolerancia' not in fields or 'peso_resta' not in fields or 'peso_neto_total' not in fields or 'peso_bruto_total' not in fields or 'peso_tara_total':
        #    return super(ChargueConsolidate, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        res = super(ChargueConsolidate, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        for group in res:
            if group.get('__domain'):
                quants = self.search(group['__domain'])
                group['peso_neto'] = sum(quants.mapped('peso_neto'))
                group['peso_neto_trailer'] = sum(quants.mapped('peso_neto_trailer'))
                group['peso_condicionado'] = sum(quants.mapped('peso_condicionado'))
                group['peso_tolerancia'] = sum(quants.mapped('peso_tolerancia'))
                group['peso_resta'] = sum(quants.mapped('peso_resta'))
                group['peso_neto_total'] = sum(quants.mapped('peso_neto_total'))
                group['peso_bruto_total'] = sum(quants.mapped('peso_bruto_total'))
                group['peso_tara_total'] = sum(quants.mapped('peso_tara_total'))
                group['peso_liquidar'] = sum(quants.mapped('peso_liquidar'))
        return res

    # Datos para Aprobación
    is_approved = fields.Boolean(string="¿Aprobado?")
    approver    = fields.Many2one('hr.employee',string="Aprobador",domain="[('reponsable_quality', '=',True)]")
    with_obs    = fields.Boolean(string='¿Rechazado?')
    observation = fields.Text(string="Motivo de Rechazo")

    approver_pcp_in  = fields.Many2one('hr.employee',string='Inspector PCP Entrada',domain="[('reponsable_pcp', '=',True)]")
    approver_pcp_out = fields.Many2one('hr.employee',string='Inspector PCP Salida',domain="[('reponsable_pcp', '=',True)]")

    #Contador de Despachos para ese día
    chargue_count_per_day = fields.Integer("Cantidad de Ordenes", compute='_compute_chargue_count_per_day')
    
    customer_approval = fields.Boolean(string="Aprobado con Observación",default=False,onchange="on_change_customer_approval")

    currency_id = fields.Many2one(
        "res.currency", 
        default=lambda self: self.env.company.currency_id,
    )
    product_price = fields.Monetary("Precio del producto")
    usar_patio = fields.Boolean(compute="_compute_usar_patio")
    nota = fields.Text("Nota")

    @api.model
    def can_usar_patio(self):
        return bool(self.env["ir.config_parameter"].sudo().get_param("eu_agroindustry.usar_patio_romana"))

    @api.depends("peso_neto", "peso_neto_trailer")
    def _compute_peso_neto_total(self):
        for rec in self:
            rec.peso_neto_total = rec.peso_neto + rec.peso_neto_trailer

    @api.depends("peso_bruto", "peso_bruto_trailer")
    def _compute_peso_bruto_total(self):
        for rec in self:
            rec.peso_bruto_total = rec.peso_bruto + rec.peso_bruto_trailer

    @api.depends("peso_tara", "peso_tara_trailer")
    def _compute_peso_tara_total(self):
        for rec in self:
            rec.peso_tara_total = rec.peso_tara + rec.peso_tara_trailer

    @api.depends_context("company", "uid")
    def _compute_usar_patio(self):
        for rec in self:
            rec.usar_patio = self.can_usar_patio()

    @api.onchange('customer_approval')
    def on_change_customer_approval(self):
        self.is_approved = self.customer_approval
        
    @api.onchange("is_approved")
    def _onchange_is_approved(self):
        for rec in self:
            if rec.is_approved:
                rec.approver = self.env["hr.employee"].search([("reponsable_quality", "=", True)], limit=1)

    @api.onchange("sale_ids")
    def _onchange_sale_ids(self):
        for rec in self:
            so = rec.sale_ids

            if so:
                rec.update({
                    "partner_id": so[0].partner_id.id,
                    "vehicle_id": so[0].vehicle_id.id,
                    "origin": ", ".join(so.mapped("name")),
                })

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.product_price = self.product_id.lst_price

    #check_ids = fields.One2many(related='picking_id.check_ids', string='Checks')
    #quality_check_todo = fields.Boolean(related='picking_id.quality_check_todo' , string='Pending checks', )
    #quality_check_fail = fields.Boolean(related='picking_id.quality_check_fail' , string="Check Fails")
    #quality_alert_ids = fields.One2many(related='picking_id.quality_alert_ids' , string='Alerts')
    #quality_alert_count = fields.Integer(related='picking_id.quality_alert_count' )

    def _default_check_ids(self):
        self.env['quality.check'].search([('chargue_consolidate','=',self.id)])
    
    @api.onchange("check_ids")
    def _onchange_check_ids(self):
        if self.check_ids:
            self.update({"product_id": self.check_ids.product_id.id})
            self.check_ids.write({"vehicle_id": self.vehicle_id.id})

    check_ids = fields.Many2one(
        comodel_name='quality.check',
        string='Ordenes de calidad',
        default=_default_check_ids,
    )
    quality_state = fields.Selection(related="check_ids.quality_state", string="Estatus de QC")
    #Relación con el Producto
    # product_id       = fields.Many2one('product.product',string="Producto",readonly=True,tracking=True,store=True)
    product_id       = fields.Many2one('product.product',string="Producto",tracking=True,store=True)
    
    # Liquidación
    impureza = fields.Float("Impureza", compute="_compute_quality_values", digits=(20,4))
    humedad = fields.Float("Humedad", compute="_compute_quality_values", digits=(20,4))
    peso_liquidar_operation_ids = fields.One2many("peso.liquidar.operation", "chargue_consolidate_id")
    last_operation_id = fields.Many2one(
        "peso.liquidar.operation", 
        "Última operación de peso a liquidar", 
        tracking=True,
        compute="_compute_last_operation_id",
    )
    humedad_liquidar = fields.Float("Humedad Liquidar", related="last_operation_id.humedad_liquidar", digits=(20,4),)
    impureza_liquidar = fields.Float("Impureza Liquidar", related="last_operation_id.impurezas_liquidar", digits=(20,4),)
    peso_liquidar = fields.Float("Peso Liquidar", related="last_operation_id.peso_liquidar", digits=(20,4),)
    usuario_liquidar = fields.Many2one("res.users", related="last_operation_id.create_uid")

    location_dest_id = fields.Many2one(
        'stock.location', "Ubicación de Destino",
        domain="[('usage','=','internal')]",
        check_company=True,)

    # Campos Origen
    origen_peso_rubro = fields.Float(string="Origen Peso Bruto")
    origen_peso_tara = fields.Float(string="Origen Peso Tara")
    origen_peso_neto = fields.Float(string="Origen Peso Neto")
    origen_peso_acondicionado = fields.Float(string="Origen Peso Acondicionado ")
    origen_nro_origen = fields.Char(string="Guía Origen")
    origen_sitio = fields.Char(string="Ubicación de Origen")
    origen_guia_sada = fields.Char(tracking=True,)
    origen_guia_insai = fields.Char(tracking=True,)

    # Campos Check para Ventas
    conf_primera = fields.Boolean(string="Confirmado a la Primera")
    notif_desp = fields.Boolean(string="Notificado a Despacho")
    infestacion_percent = fields.Boolean(string="% Infestación")
    container_cava = fields.Boolean(string="Container o Cava")
    plataforma = fields.Boolean(string="Plataforma")
    lona_encerado = fields.Boolean(string="Lona o encerado")
    otros = fields.Text(string="Otros")

    descuento_humedad = fields.Float(string="Descuento Humedad", digits=(20,4))
    descuento_impureza = fields.Float(string="Descuento Impureza", digits=(20,4))
    total_descuento = fields.Float(string="Total Descuento", digits=(20,4))
    is_pesaje_externo = fields.Boolean()
    margen_tolerancia = fields.Float(compute="_compute_margen_tolerancia")

    @api.depends("peso_realizado_total", "peso_neto_total")
    def _compute_diff_tolerancia(self):
        for rec in self:
            if rec.peso_realizado_total:
                rec.diff_tolerancia = rec.peso_realizado_total - rec.peso_neto_total
            else:
                rec.diff_tolerancia = 0

    @api.depends("picking_id.move_ids_without_package.quantity_done","picking_id.state")
    def _compute_peso_realizado_total(self):
        for rec in self:
            if rec.picking_id and all([p.state == "done" for p in rec.picking_id]):
                rec.peso_realizado_total = sum(rec.picking_id.move_ids_without_package.mapped("quantity_done"))
            else:
                rec.peso_realizado_total = 0

    def _compute_margen_tolerancia(self):
        for rec in self:
            rec.margen_tolerancia = self.env["ir.config_parameter"] \
                .sudo() \
                .get_param("eu_agroindustry.margen_tolerancia_romana", 0)

    consolidate_product_line_ids = fields.One2many("consolidate.product.line", "consolidate_id", "Productos")

    @api.constrains("consolidate_product_line_ids")
    def _check_consolidate_product_line_ids(self):
        for rec in self:
            ids = rec.consolidate_product_line_ids.product_id.ids

            if len(set(ids)) != len([line.product_id.id for line in rec.consolidate_product_line_ids]):
                raise ValidationError("No puedes repetir los productos")

    @api.depends(
        "check_ids.line_ids.tolerancia_line_id.is_humedad",
        "check_ids.line_ids.tolerancia_line_id.is_impureza",
        "check_ids.line_ids.value",
    )
    def _compute_quality_values(self):
        for rec in self:
            impureza = rec.check_ids \
                .line_ids \
                .filtered("tolerancia_line_id.is_impureza") \
                .mapped(lambda l: float((l.value or "0").replace(",", ".")))

            humedad = rec.check_ids \
                .line_ids \
                .filtered("tolerancia_line_id.is_humedad") \
                .mapped(lambda l: float((l.value or "0").replace(",", ".")))

            rec.impureza = sum(impureza)
            rec.humedad = sum(humedad)

    @api.model    
    def create(self, vals):
        res = super().create(vals)

        for rec in res.filtered("is_pesaje_externo"):
            rec.name = self.env['ir.sequence'].next_by_code('external.orden.seq')

        for rec in res.filtered(lambda r: not r.is_pesaje_externo):
            if rec.operation_type == 'venta':
                rec.name = self.env['ir.sequence'].next_by_code('load.orden.seq')
            elif rec.operation_type == 'compra':
                rec.name = self.env['ir.sequence'].next_by_code('download.orden.seq')
            else:
                rec.name = self.env['ir.sequence'].next_by_code('transfer.orden.seq')

        return res

    def check_quality(self):
        self.ensure_one()
        checks = self.check_ids.filtered(lambda check: check.quality_state == 'none')
        if checks:
            action = self.env.ref('quality_control.quality_check_action_small').read()[0]
            action['context'] = self.env.context
            action['res_id'] = checks.ids[0]
            return action
        return False
        
    @api.depends("peso_liquidar_operation_ids")
    def _compute_last_operation_id(self):
        for rec in self:
            rec.last_operation_id = None

            if rec.peso_liquidar_operation_ids:
                rec.last_operation_id = rec.peso_liquidar_operation_ids.sorted("id", reverse=True)[0]
            
    @api.depends('scheduled_date')
    def _compute_chargue_count_per_day(self):
        for rec in self:
            contador = 0
            chargue_consolidate = self.env['chargue.consolidate'].sudo().search([('state', '=', 'por_llegar')])
            if len(chargue_consolidate)>0:
                fecha = rec.scheduled_date.strftime("%d-%m-%Y")
                for chargue in chargue_consolidate:
                    fecha_busqueda = chargue.scheduled_date.strftime("%d-%m-%Y")
                    if fecha == fecha_busqueda:
                        contador += 1
            rec.chargue_count_per_day = contador

    # Evitar eliminación
    def unlink(self):
        if any(rec.name != "/" for rec in self):
            raise UserError(_("No puedes borrar una Orden que esté confirmada."))

        return super().unlink()
    
    def action_open_peso_liquidar(self):
        return {
            "name": "Peso por liquidar",
            "type": "ir.actions.act_window",
            "res_model": "peso.liquidar.operation",
            "view_mode": "form",
            "context": {
                "default_chargue_consolidate_id": self.id,
            },
            "target": "new",
        }
    
    @api.onchange("chargue_consolidate")
    def _onchange_chargue_consolidate(self):
        vehicles = self.chargue_consolidate.vehicle_id.ids

        if vehicles:
            self.update({"vehicle_id": vehicles[0]})


    # Botón Confirmar Guía de Descarga, Carga o Transferencia y se le asigna su sequence
    def button_patio(self):
        for rec in self.sudo():
            if not rec.vehicle_id:
                raise UserError('Debe establecer el vehículo para ingresarlo')

            if rec.operation_type in ['compra','venta']:
                if not rec.approver_pcp_in:
                    rec.approver_pcp_in = self.env.user.employee_id.id

                rec.write({
                    "date_por_llegar": fields.Datetime.now(),
                    "approval_por_llegar": self.env.uid,
                    "state": 'patio',
                })
            else:
                return self.env['chargue.consolidate.picking']\
                    .sudo() \
                    .with_context(active_ids=self.ids, active_model='chargue.consolidate', active_id=self.id)\
                    .action_create_picking()

    # Botón Pasar a Romana
    def button_proceso(self):
        for rec in self.sudo():
            if all([
                not rec.is_pesaje_externo,
                bool(self.env["quality.point"].search([("product_ids","in",self.product_id.ids)], limit=1)),
                bool(rec.check_ids),
                rec.check_ids.quality_state != 'pass',
            ]):
                raise UserError('Debe confirmar la Orden de Calidad')

            if not rec.is_pesaje_externo:
                if not rec.picking_id:
                    raise UserError('Debe seleccionar un Movimiento de Inventario')
                    
            if rec.with_obs and not rec.customer_approval:
                raise UserError('Si la orden está Rechazada, debe aprobarla con observación para poder continuar')

            if rec.operation_type == 'compra' and len(rec.picking_id) > 1:
                raise UserError('Una compra solo debe tener un movimiento de inventario asociado')

            now = fields.Datetime.now()
            uid = self.env.uid

            vals = {
                "date_patio": now,
                "date_por_llegar": now,
                "approval_por_llegar": uid,
                "approval_patio": uid,
                "state": "peso_bruto" if (rec.operation_type != 'venta' or rec.is_return_venta) else "peso_tara"
            }

            if rec.is_pesaje_externo:
                if not rec.approver_pcp_in:
                    rec.approver_pcp_in = self.env.user.employee_id.id

            rec.write(vals)
            rec.picking_id.write({"vehicle_id": rec.vehicle_id.id,"driver_id":rec.driver_id.id,"chargue_consolidate_create":rec.id})

    # Botón Pasar a peso_bruto
    def button_peso_bruto(self):
        orders_1 = self.filtered(lambda r: r.operation_type != "venta" or r.is_return_venta)
        orders_2 = self.filtered(lambda r: (r.id not in orders_1.ids) and r.operation_type == "venta" or r.is_return_compra)

        orders_1.write({"state": "peso_tara"})
        orders_2.write({
            "date_peso_bruto": fields.Datetime.now(),
            "approval_peso_bruto": self.env.uid,
            "state": "peso_bruto",
        })

    # Botón Pasar a peso_bruto
    def button_por_proceso(self):
        for rec in self:
            quality = self.env["quality.check"].sudo().search_count([("picking_id","in",rec.picking_id.ids)])

            if not all([rec.purchase_id, rec.is_pesaje_externo, self.product_price]) and \
                all([(rec.operation_type == "compra" or rec.is_return_venta), rec.state == "por_salir"]):
                raise UserError("El precio del producto no puede ser cero")

            if quality and not rec.is_pesaje_externo and rec.check_ids.quality_state != 'pass' and rec.state in ["peso_bruto", "peso_tara"]:
                raise UserError('Debe confirmar la Orden de Calidad')

            if rec.state == "peso_tara":
                if rec.peso_tara <= 0:
                    raise UserError('Debe establecer el Peso Tara')
                if rec.with_trailer and rec.peso_tara_trailer <= 0:
                    raise UserError('Debe establecer el Peso Tara del Remolque')
            else:
                if rec.peso_bruto <= 0:
                    raise UserError('Debe establecer el Peso Bruto')
                if rec.with_trailer and rec.peso_bruto_trailer <= 0:
                    raise UserError('Debe establecer el Peso Bruto del Remolque')

            if (rec.operation_type == "compra" or rec.is_return_venta) and rec.state == "peso_bruto":
                rec.write({
                    "date_peso_bruto": fields.Datetime.now(),
                    "approval_peso_bruto": self.env.uid,
                    "state": 'proceso',
                }) 
            elif (rec.operation_type == 'compra' or rec.is_return_venta) and rec.state == 'peso_tara':
                if quality and not rec.is_pesaje_externo and not rec.is_approved:
                    raise UserError('Debe aprobar esta Orden para pasar a Romana')

                if rec.diff_tolerancia > rec.margen_tolerancia:
                    raise UserError("La diferencia supera el márgen establecido en la compañia")
                
                rec.write({
                    "date_peso_bruto": fields.Datetime.now(),
                    "approval_peso_bruto": self.env.uid,
                    "state": 'por_salir',
                })

                if rec.is_pesaje_externo:
                    continue

                if rec.product_id.auto_validate:
                    if not rec.location_dest_id:
                        raise UserError('Debe establecer la Ubicación de Destino')
                    for pic in rec.picking_id:
                        product_exist = False
                        for line1 in pic.move_ids_without_package.filtered(lambda line: line.product_id.id == rec.product_id.id):
                            line1.write({
                                'quantity_done': rec.peso_condicionado,
                                'location_dest_id': rec.location_dest_id.id,
                                'price_unit': rec.product_price,
                            })
                            product_exist = True
                            # line.quantity_done = rec.peso_neto_total
                            # line.location_dest_id = rec.location_dest_id.id
                        
                        for lines3 in pic.move_line_nosuggest_ids.filtered(lambda line: line.product_id.id == rec.product_id.id):
                            lines3.write({
                                'qty_done': rec.peso_condicionado,
                                'location_dest_id': rec.location_dest_id.id,
                            })
                            product_exist = True
                            # lines.qty_done = rec.peso_neto_total
                            # lines.location_dest_id = rec.location_dest_id.id
                        if pic.picking_type_id.show_operations:
                            for line2 in pic.move_line_ids_without_package.filtered(lambda line: line.product_id.id == rec.product_id.id):
                                line2.write({
                                    'qty_done': rec.peso_condicionado,
                                    'location_dest_id': rec.location_dest_id.id,
                                })
                                product_exist = True
                                # line.qty_done = rec.peso_neto_total
                                # line.location_dest_id = rec.location_dest_id.id
                            
                            for lines4 in pic.move_line_ids.filtered(lambda line: line.product_id.id == rec.product_id.id):
                                lines4.write({
                                    'qty_done': rec.peso_condicionado,
                                    'location_dest_id': rec.location_dest_id.id,
                                })
                                product_exist = True

                        if not product_exist:
                            raise UserError('La PO Asociada no posee el mismo Producto que la SU, contacte con el administrador del sistema')
                        pic.chargue_consolidate_create = rec.id
                        if pic.state not in ('cancel','done'):
                            pic.action_confirm()
                            pic.with_context(cancel_backorder=True)._action_done()
                if rec.product_id.with_excedente and rec.product_id.product_excedente and rec.product_id.need_romana:
                    pick = {}
                    excedente_exist = self.env['chargue.consolidate.excedente'].sudo().search([('product_id','=',rec.product_id.product_excedente.id),('company_id', '=',rec.company_id.id)])
                    if excedente_exist:
                        excedente_exist.qty_residual += rec.peso_resta 
                    else:
                        pick = {
                            'name': rec.product_id.name,
                            'product_id': rec.product_id.product_excedente.id,
                            'qty_residual': rec.peso_resta,
                            'company_id': rec.company_id.id,
                            'date_last_full': fields.Datetime.now(),
                        }
                        excedente = self.env['chargue.consolidate.excedente'].sudo().create(pick)
            elif ((rec.operation_type == 'venta' or rec.is_return_compra) and rec.state == 'peso_tara') \
                or (rec.operation_type == "transferencia" and rec.state == "peso_bruto"):
                if rec.multi_weight:
                    rec.write({
                        "peso_bruto": max(rec.multi_weight.mapped('peso_bruto')),
                        "peso_tara": min(rec.multi_weight.mapped('peso_tara')),
                        "peso_bruto_trailer": max(rec.multi_weight.mapped('peso_bruto_trailer')),
                        "peso_tara_trailer": min(rec.multi_weight.mapped('peso_tara_trailer')),
                    })
                
                rec.write({
                    "date_peso_tara": fields.Datetime.now(),
                    "approval_peso_tara": self.env.uid,
                    "state": 'proceso',
                })
            elif ((rec.operation_type == 'venta' or rec.is_return_compra) and rec.state == 'peso_bruto') \
                or (rec.operation_type == 'transferencia' and rec.state == 'peso_tara'):
                if rec.multi_weight:
                    rec.write({
                        "peso_bruto": max(rec.multi_weight.mapped('peso_bruto')),
                        "peso_tara": min(rec.multi_weight.mapped('peso_tara')),
                        "peso_bruto_trailer": max(rec.multi_weight.mapped('peso_bruto_trailer')),
                        "peso_tara_trailer": min(rec.multi_weight.mapped('peso_tara_trailer')),
                    })

                rec.write({
                    "date_peso_bruto": fields.Datetime.now(),
                    "approval_peso_bruto": self.env.uid
                })

                if not rec.is_pesaje_externo and rec.operation_type == 'transferencia' and rec.product_id.auto_validate:
                    if not rec.location_dest_id:
                        raise UserError('Debe establecer la Ubicación de Destino')
                    
                    peso = rec.peso_neto_total
                    uom = rec.product_id.uom_id

                    if uom.uom_type == "bigger":
                        peso /= uom.factor_inv
                    elif uom.uom_type == "smaller":
                        peso *= uom.factor

                    for pic in rec.picking_id:
                        rec.picking_id.location_dest_id = rec.location_dest_id.id
                        rec.picking_id.write({
                            'location_dest_id': rec.location_dest_id.id,
                        })
                        for line1 in pic.move_ids_without_package.filtered(lambda line: line.product_id.id == rec.product_id.id):
                            line1.write({
                                'quantity_done': peso,
                                'location_dest_id': rec.location_dest_id.id,
                            })
          
                        for lines3 in pic.move_line_nosuggest_ids.filtered(lambda line: line.product_id.id == rec.product_id.id):
                            lines3.write({
                                'qty_done': peso,
                                'location_dest_id': rec.location_dest_id.id,
                            })

                        if pic.picking_type_id.show_operations:
                            for lines4 in pic.move_line_ids.filtered(lambda line: line.product_id.id == rec.product_id.id):
                                lines4.write({
                                    'qty_done': peso,
                                    'location_dest_id': rec.location_dest_id.id,
                                })
                            for line2 in pic.move_line_ids_without_package.filtered(lambda line: line.product_id.id == rec.product_id.id):
                                line2.write({
                                    'qty_done': peso,
                                    'location_dest_id': rec.location_dest_id.id,
                                })

                        if pic.state not in ('cancel','done'):
                            pic.action_confirm()
                            pic.with_context(cancel_backorder=True)._action_done()
                if rec.operation_type == 'venta' or rec.is_return_compra:
                    if rec.diff_tolerancia > rec.margen_tolerancia:
                        raise UserError("La diferencia supera el márgen establecido en la compañia")
                
                    rec.write({
                        "state": "por_salir",
                        "date_por_salir": fields.Datetime.now(),
                    })
                if rec.operation_type == 'transferencia':
                    picking_ids = rec.picking_id - (rec.purchase_id.picking_ids + rec.sale_ids.picking_ids)

                    if picking_ids and not all([state == "done" for state in picking_ids.filtered(lambda x:x.state != 'cancel').mapped("state")]):
                        raise UserError("Todas las transferencias deben estar validadas para proceder")

                    rec.write({
                        "state": "finalizado",
                        "date_finalizado": fields.Datetime.now(),
                    })

            if not rec.is_return and \
                self.env["ir.config_parameter"].sudo().get_param("eu_agroindustry.create_po_consolidate", False) and \
                not all([rec.purchase_id, rec.is_pesaje_externo]) and \
                all([rec.operation_type == "compra", rec.state == "por_salir"]):
                return rec.action_create_po()
            if rec.purchase_id.aplicar_descuento and rec.descuento_realizado != 0:
                pick = {}
                descuento_exist = self.env['chargue.consolidate.descuento'].sudo().search([('product_id','=',rec.product_id.id),('company_id', '=',rec.company_id.id)])
                if descuento_exist:
                    descuento_exist.qty_residual += (rec.descuento_realizado + rec.descuento_realizado_trailer)
                else:
                    pick = {
                        'name': rec.product_id.name,
                        'product_id': rec.product_id.id,
                        'qty_residual': (rec.descuento_realizado + rec.descuento_realizado_trailer),
                        'company_id': rec.company_id.id,
                        'date_last_full': fields.Datetime.now(),
                    }
                    descuento = self.env['chargue.consolidate.descuento'].sudo().create(pick)

    # Botón Pasar a Por Salir en Ventas
    def button_por_proceso_venta(self):
        for rec in self:
            if rec.operation_type == 'venta' or rec.is_return_compra:
                if rec.peso_bruto <= 0:
                    raise UserError('Debe establecer el Peso Bruto')
                if rec.with_trailer and rec.peso_bruto_trailer <= 0:
                    raise UserError('Debe establecer el Peso Bruto del Remolque')
                if rec.picking_id_state != 'done':
                    raise UserError('La SU debe estar Validada')

            rec.write({
                "state": 'por_salir',
                "date_por_salir": fields.Datetime.now(),
                "approval_por_salir": self.env.uid,
            })

    # Botón Pasar a Finalizado
    def button_finalizado(self):
        for rec in self.sudo():
            picking_ids = rec.picking_id - (rec.purchase_id.picking_ids + rec.sale_ids.picking_ids)
            
            if picking_ids and not all([state == "done" for state in picking_ids.filtered(lambda x: x.state != 'cancel').mapped("state")]):
                raise UserError("Todas las transferencias deben estar validadas para proceder")

            if self.env["quality.check"].sudo().search_count([("picking_id","in",rec.picking_id.ids)]) and not rec.is_pesaje_externo:
                if not rec.check_ids and (rec.operation_type == 'compra' and not rec.is_return) and rec.picking_id.state != 'cancel':
                    raise UserError('Debe asignar una Orden de Calidad al pesado')
                if rec.check_ids and rec.check_ids.quality_state != 'pass':
                    raise UserError('Debe aprobar la Orden de Calidad')

            if not rec.approver_pcp_out:
                rec.approver_pcp_out = self.env.user.employee_id.id
            if rec.romana_cancel_reason_id or rec.observation=='Cancelado Manualmente':
                rec.write({                
                    "date_rechazada": fields.Datetime.now(),
                    "approval_rechazada": self.env.uid,
                    "state": 'cancelado',
                })
            else:
                rec.write({                
                    "date_finalizado": fields.Datetime.now(),
                    "approval_finalizado": self.env.uid,
                    "state": 'finalizado',
                })
            if rec.aplicar_descuento and rec.purchase_id.aplicar_descuento and len(rec.purchase_id.order_line.filtered(lambda x: x.product_id == rec.product_id)) == 1:
                rec.purchase_id.order_line.filtered(lambda x: x.product_id == rec.product_id).peso_liquidar += (rec.peso_neto - rec.descuento_realizado - rec.descuento_realizado_trailer)

    def get_po_vals(self):
        return {
            "date_order": fields.Datetime.now(),
            "partner_id": self.partner_id.id,
            "currency_id": self.env.company.currency_id.id,
            "picking_type_id": self.picking_id.picking_type_id.id,
            "vehicle_id": self.vehicle_id.id,
            "chargue_consolidate": [(6, 0, self.ids)],
        }
    
    def action_create_po(self):
        self.ensure_one()

        peso_compra = 0
        peso_liquidar = self.env["peso.liquidar.operation"].sudo().create({
            "chargue_consolidate_id": self.id,
            "humedad_liquidar": self.humedad,
            "impurezas_liquidar": self.impureza,
        })

        purchase_id = self.env["purchase.order"].create(self.get_po_vals())

        line_id = self.picking_id.move_ids_without_package[0]
        product_id = line_id.product_id
        if self.aplicar_descuento and not peso_liquidar:
            purchase_id.aplicar_descuento = True
            peso_compra = self.peso_neto - self.descuento_realizado - self.descuento_realizado_trailer
        if peso_liquidar:
            peso_compra = peso_liquidar.peso_liquidar
        self.env["purchase.order.line"].create({
            "product_id": product_id.id,
            "order_id": purchase_id.id,
            "product_qty": line_id.quantity_done,
            "product_uom": line_id.product_uom.id,
            "peso_liquidar": peso_compra,
            "price_unit": product_id.lst_price,
            "taxes_id": product_id.taxes_id.ids,
        })

        self.picking_id.move_ids_without_package[0].purchase_line_id = purchase_id.order_line[0].id
        self.purchase_id = purchase_id.id

        if self.env["ir.config_parameter"].sudo().get_param("eu_agroindustry.confirm_po_consolidate", False):
            self.purchase_id.button_confirm()

    # Botón para Cancelar
    def button_cancel(self):
        return self.env['chargue.consolidate.reason']\
            .with_context(active_ids=self.ids, active_model='chargue.consolidate', active_id=self.id)\
            .action_cancelar_manual()

    # Botón para Crear SU
    def button_picking(self):
        return self.env['chargue.consolidate.picking']\
            .with_context(active_ids=self.ids, active_model='chargue.consolidate', active_id=self.id)\
            .action_create_picking()
    # Botón para Crear SU
    def button_link_picking(self):
        return self.env['chargue.consolidate.link.picking']\
            .with_context(active_ids=self.ids, active_model='chargue.consolidate', active_id=self.id)\
            .action_create_link_picking()
    def action_peso_manual(self):
        return self.env['chargue.manual']\
            .with_context(active_ids=self.ids, active_model='chargue.consolidate', active_id=self.id)\
            .action_register_manual()
    # Botón para Cancelación Masiva
    def action_multi_cancel(self):
        vals = {
            "with_obs": True,
            "observation": 'Cancelado Manualmente',
        }

        for order in self.env['chargue.consolidate'].browse(self.env.context.get('active_ids')):
            if order.state == 'por_llegar':
                order.write({
                    **vals,
                    "state": "rechazada",
                })
            elif order.state in ('peso_bruto','peso_tara','proceso','patio') and order.operation_type in ('venta','compra'):
                order.write({
                    **vals,
                    "state": "por_salir",
                })
            elif order.state in ('peso_bruto','peso_tara','proceso','patio') and order.operation_type in ('transferencia'):
                order.write({
                    **vals,
                    "state": "cancelado",
                })
            elif order.operation_type in ('venta','compra','transferencia') and order.state == 'finalizado' and self.env.user.has_group('eu_agroindustry.permiso_cancelacion_romana_finalizada'):
                order.write({
                    **vals,
                    "state": "cancelado",
                })
            else:
                raise UserError('No puede cancelar un Proceso que esté en por salir o finalizada')
    # Botón Obtener Peso Bruto
    def obtener_peso_bruto(self):
        for rec in self:
            if not rec.balanza:
                raise UserError('Debe seleccionar la balanza a utilizar')
        
            rec.peso_bruto = 0.0

            balanza = rec.balanza.get_weight()
            if rec.purchase_id.aplicar_descuento:
                descuento = float(self.env["ir.config_parameter"].sudo().get_param("eu_agroindustry.descuento_permitido"))
                #balanza = balanza - descuento
                rec.descuento_realizado = descuento
            if balanza:
                rec.write({
                    "peso_bruto": balanza,
                    "date_first_weight": fields.Datetime.now(),
                    "approval_first_weight": self.env.uid,
                })
            
    # Botón Obtener Peso Tara
    def obtener_peso_tara(self):
        for rec in self:
            if not rec.balanza:
                raise UserError('Debe seleccionar la balanza a utilizar')
        
            rec.peso_tara = 0.0

            balanza = rec.balanza.get_weight()

            if balanza:
                rec.write({
                    "peso_tara": balanza,
                    "date_second_weight": fields.Datetime.now(),
                    "approval_second_weight": self.env.uid,
                })
                
    # Botón Obtener Peso Bruto Trailer
    def obtener_peso_bruto_trailer(self):
        for rec in self:
            if not rec.balanza:
                raise UserError('Debe seleccionar la balanza a utilizar')
        
            rec.peso_bruto_trailer = 0.0

            balanza = rec.balanza.get_weight()
            if rec.purchase_id.aplicar_descuento:
                descuento = float(self.env["ir.config_parameter"].sudo().get_param("eu_agroindustry.descuento_permitido"))
                #balanza = balanza - descuento
                rec.descuento_realizado_trailer = descuento
            if balanza:
                rec.write({
                    "peso_bruto_trailer": balanza,
                    "date_first_weight_t": fields.Datetime.now(),
                    "approval_first_weight_t": self.env.uid,
                })
            
    # Botón Obtener Peso Tara Trailer
    def obtener_peso_tara_trailer(self):
        for rec in self:
            if not rec.balanza:
                raise UserError('Debe seleccionar la balanza a utilizar')
        
            rec.peso_tara_trailer = 0.0

            balanza = rec.balanza.get_weight()

            if balanza:
                rec.write({
                    "peso_tara_trailer": balanza,
                    "date_second_weight_t": fields.Datetime.now(),
                    "approval_second_weight_t": self.env.uid,
                })
            
    # Calculo de Peso Neto
    @api.depends('peso_bruto','peso_tara')        
    def compute_peso_neto(self):
        for rec in self:
            rec.peso_neto = rec.peso_bruto - rec.peso_tara

    # Calculo de Peso Neto Trailer
    @api.depends('peso_bruto_trailer','peso_tara_trailer')
    def compute_peso_neto_trailer(self):
        for rec in self:
            rec.peso_neto_trailer = rec.peso_bruto_trailer - rec.peso_tara_trailer
    # Calculo de Peso Neto Trailer
    @api.depends('peso_neto','origen_peso_neto')
    def compute_peso_tolerancia(self):
        for rec in self:
            rec.peso_tolerancia = rec.peso_neto - rec.origen_peso_neto
    @api.depends('peso_neto','peso_condicionado')
    def compute_peso_resta(self):
        for rec in self:
            rec.peso_resta = (rec.peso_neto_total) - rec.peso_condicionado
    
    # Computar Peso Total
    @api.depends('picking_id',)
    def _compute_total_weight(self):
        for rec in self:
            rec.picking_id_weight = 0.0

            if rec.picking_id:
                picking_ids = self.env['stock.picking'].search([('chargue_consolidate_create', '=', rec.id),('state','!=','cancel')])
                rec.picking_id_weight = sum(picking_ids.filtered(lambda x: x.picking_type_id.code == 'outgoing').mapped("weight")) - sum(picking_ids.filtered(lambda y: y.picking_type_id.code == 'incoming').mapped('weight'))

    # Calculo de Peso Condicionado
    @api.depends(
        'peso_neto',
        'peso_neto_trailer',
        'check_ids.line_ids.diff',
        'check_ids.line_ids.tolerancia_line_id.is_humedad',
        'check_ids.line_ids.tolerancia_line_id.is_impureza',
    )
    def compute_peso_condicionado(self):
        for rec in self.sudo():
            # Peso Neto
            total = rec.peso_neto_trailer + rec.peso_neto

            # Humedades
            descuento_humedad = rec.check_ids \
                .line_ids \
                .filtered("tolerancia_line_id.is_humedad") \
                .mapped("diff")

            descuento_humedad = sum(map(float, descuento_humedad))

            rec.descuento_humedad = descuento_humedad = (descuento_humedad / 88) * total

            total -= descuento_humedad

            # Impurezas
            descuento_impureza = rec.check_ids \
                .line_ids \
                .filtered("tolerancia_line_id.is_impureza") \
                .mapped("diff")

            descuento_impureza = sum(map(float, descuento_impureza))
            
            rec.descuento_impureza = descuento_impureza = (descuento_impureza * total) / 100

            # Total
            rec.total_descuento = total_descuento = descuento_humedad + descuento_impureza
            total = (rec.peso_neto_trailer + rec.peso_neto) - total_descuento

            # Peso Condicionado
            rec.peso_condicionado = total

    # Obtener si tiene remolque el vehículo y su placa
    @api.onchange('vehicle_id')
    def onchange_vehicle_id(self):
        for rec in self:
            if rec.vehicle_id:
                rec.update({
                    "with_trailer": rec.vehicle_id.with_trailer,
                    "driver_id": rec.driver_id.id,
                    "plate_trailer": rec.vehicle_id.plate_trailer,
                })

    @api.onchange("operation_type")
    def _onchange_operation_type(self):
        for rec in self:
            if rec.is_pesaje_externo:
                rec.partner_id = None
            
    # Obtener Contacto desde la Compra
    @api.onchange('purchase_id')
    def onchange_purchase_id(self):
        for rec in self:
            po = rec.purchase_id
            
            if po:
                rec.update({
                    "partner_id": po.partner_id.id,
                    "vehicle_id": po.vehicle_id.id,
                    "origin": po.name,
                    "aplicar_descuento":po.aplicar_descuento,
                })

    @api.depends('peso_condicionado')
    def compute_peso_condicionado_dashboard(self):
        for rec in self:
            rec.peso_condicionado_dashboard = rec.peso_condicionado
            
    @api.depends('peso_neto','peso_neto_trailer')
    def compute_peso_neto_dashboard(self):
        for rec in self:
            rec.peso_neto_dashboard = rec.peso_neto_total
    # DASHBOARD #

    @api.model
    def retrieve_quotes(self):
        """ This function returns the values to populate the custom dashboard in
            the sale order views.
        """
        self.check_access_rights('read')

        result = {
            'por_llegar': 0,
            'patio': 0,
            'peso_bruto': 0,
            'peso_tara': 0,
            'proceso': 0,
            'por_salir': 0,
            'finalizado': 0,
        }

        # easy counts
        so = self.env['chargue.consolidate']

        result['por_llegar'] = so.search_count([('state', '=', 'por_llegar'),('company_id', '=', self.env.company.id)])
        result['patio'] = so.search_count([('state', '=', 'patio'),('company_id', '=', self.env.company.id)])
        result['peso_bruto'] = so.search_count([('state', '=', 'peso_bruto'),('company_id', '=', self.env.company.id)])
        result['peso_tara'] = so.search_count([('state', '=', 'peso_tara'),('company_id', '=', self.env.company.id)])
        result['proceso'] = so.search_count([('state', '=', 'proceso'),('company_id', '=', self.env.company.id)])
        result['por_salir'] = so.search_count([('state', '=', 'por_salir'),('company_id', '=', self.env.company.id)])
        result['finalizado'] = so.search_count([('state', '=', 'finalizado'),('company_id', '=', self.env.company.id)])

        return result

    @api.model
    def agros_por_llegar(self):
        return self.search([])._action_view_agros(state='por_llegar')
    @api.model
    def agros_patio(self):
        return self.search([])._action_view_agros(state='patio')
    @api.model
    def agros_peso_bruto(self):
        return self.search([])._action_view_agros(state='peso_bruto')
    @api.model
    def agros_peso_tara(self):
        return self.search([])._action_view_agros(state='peso_tara')
    @api.model
    def agros_proceso(self):
        return self.search([])._action_view_agros(state='proceso')
    @api.model
    def agros_aprobacion(self):
        return self.search([])._action_view_agros(state='aprobacion')
    @api.model
    def agros_por_salir(self):
        return self.search([])._action_view_agros(state='por_salir')
    @api.model
    def agros_finalizado(self):
        return self.search([])._action_view_agros(state='finalizado')
    @api.model
    def agros_rechazada(self):
        return self.search([])._action_view_agros(state='rechazada')
    @api.model
    def agros_multi(self):
        return self.search([])._action_view_agros(state='multi')
    
    def _action_view_agros(self,state=''):
        domain = [('company_id', '=', self.env.company.id),('state', '=', state)]
        
        action = self.env["ir.actions.actions"]._for_xml_id("eu_agroindustry.open_chargue_consolidate_without")
        action['domain'] = domain
        action['views'] = [
            (self.env.ref('eu_agroindustry.view_chargue_consolidate_tree_without').id, 'tree'),
            (self.env.ref('eu_agroindustry.view_guide_consolidate_form_without').id, 'form')
        ]

        return action

    picking_count = fields.Integer("Movimiento de Inventario", compute='_compute_picking_count')

    def _compute_picking_count(self):
        for rec in self:
            rec.picking_count = self.env['stock.picking'] \
                .sudo() \
                .search_count([('chargue_consolidate_create', '=', rec.id)])

    def open_pickings(self):
        self.ensure_one()

        res = self.env.ref('stock.action_picking_tree_all')
        res = res.read()[0]
        res['domain'] = str([('chargue_consolidate_create', '=', self.id)])

        return res

    # def get_demanda_venta(self):
    #     data = []
    #     if self.operation_type == 'venta':
    #         if len(self.sale_ids) > 0:
    #             if len(self.sale_ids.order_line) > 0:   
    #                 dict_repetidos = {}
    #                 for lines in self.sale_ids.order_line:
    #                     producto = lines.product_id.id
    #                     dict_repetidos[producto] = 0

    #                 for lines in self.sale_ids.order_line:
    #                     producto = lines.product_id.id
    #                     dict_repetidos[producto] += 1
    #                     if dict_repetidos[producto] <= 1:
    #                         data.append({
    #                             'producto': lines.product_id.name,
    #                             'demanda': sum(self.sale_ids.order_line.filtered(lambda line: line.product_id.id == lines.product_id.id).mapped('product_uom_qty'))
    #                         })
    #     return data

    def get_demanda_venta(self):
        data = []
        if self.operation_type == 'venta':
            if len(self.sale_ids) > 0:
                if len(self.sale_ids.order_line) > 0:   
                    for lines in self.sale_ids.order_line:
                        data.append({
                            'producto': lines.product_id.name,
                            'descripcion': lines.name,
                            'demanda': lines.product_uom_qty,
                        })
        return data