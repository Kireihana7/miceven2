# -*- coding: utf-8 -*-

# Odoo:
from odoo import _, api, fields, models  # noqa


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Fiscal data
    license = fields.Char(string="Licencia")
    code_sada = fields.Char(string="Código SADA")

    # Contact additional info
    responsible_of = fields.Selection(
        selection=[
            ("Dueño // Socio", "Dueño // Socio"),
            (
                "Ventas (Gerente - Coordinador - Supervisor)",
                "Ventas (Gerente - Coordinador - Supervisor)",
            ),
            ("Cuentas por Pagar", "Cuentas por Pagar"),
            ("Almacén // Recepcion de despacho", " Almacén // Recepcion de despacho"),
        ],
        string="Responsible of",
    )

    # Delivery additional info
    ramp = fields.Boolean(string="Ramp")
    stairs = fields.Boolean(string="Stairs")
    elevator = fields.Boolean(string="Elevator")
    basement = fields.Boolean(string="Basement")
    mezzanine = fields.Boolean(string="Mezzanine")
    restrictions = fields.Text(
        string="Restricciones de horario",
        help="Restricciones de tiempo en la zona de carga y descarga por ordenanzas municipales",
    )
    physical_boxes = fields.Integer(
        string="Cajas físicas",
        help="Número de cajas físicas que puede recibir por día.",
    )
    transportation_units = fields.Integer(
        string="Unidades de transporte", help="¿En cuántas unidades de transporte?"
    )
    time_available_from = fields.Float(string="Horario disponible desde")
    time_available_to = fields.Float(string="Horario disponible hasta")
    regional_holidays = fields.Text(
        string="Feriados regionales",
        help="Indique feriados regionales y municipales (no laborables)",
    )
    vehicle_size = fields.Char(
        string="Tamaño máximo del vehículo",
        help="Tamaño máximo de la unidad que puede acceder al área local y al área de descarga",
    )
    helpers = fields.Boolean(
        string="Ayudantes adicionales?", help="Requiere ayudantes adicionales"
    )
    helpers_count = fields.Integer(
        string="Cuantos ayudantes?", help="¿Cuántos ayudantes adicionales?"
    )
    additional_equipment = fields.Text(
        string="Equipamiento adicional", help="¿Requiere algún equipo adicional?"
    )
    personal_equipment = fields.Boolean(
        string="¿Es esencial el uso de equipo de protección personal?",
        help="¿Es esencial el uso de equipo de protección personal?",
    )
    boots = fields.Boolean(string="Botas de seguridad")
    helmet = fields.Boolean(string="Casco de seguridad")
    gloves = fields.Boolean(string="Guantes de seguridad")
    mouths_cover = fields.Boolean(string="Tapa boca")
    ears_cover = fields.Boolean(string="Cubierta de orejas")
    capital_percent = fields.Float(
        string="Capital (%)", help="Capital que representa (%)"
    )
    availability_reception = fields.Selection(
        selection=[("Bulk", "Bulk"), ("Paletizado", "Paletizado"), ("Both", "Both")],
        string="Disponibilidad para la recepción del producto.",
    )
    preferred_reception = fields.Selection(
        selection=[
            ("Lun", "Lun"),
            ("Mar", "Mar"),
            ("Miér", "Miér"),
            ("Jue", "Jue"),
            ("Vie", "Vie"),
            ("Sab", "Sab"),
            ("Dom", "Dom"),
        ],
        string="Día preferido para la recepción.",
    )

    # Additional Info
    zone = fields.Many2one("partner.zone", string="Zona")
    code = fields.Char(string="Código de cliente")
    registry_or_place = fields.Char(
        string="Registro Mercantil",
        help="Registro mercantil o lugar de constitución y legalización del documento",
    )
    date_incorporation = fields.Date(string="Fecha de incorporación")
    volume = fields.Char(string="Volumen")
    folio = fields.Char(string="Folio")
    channel = fields.Char(string="Canal")
    segmentation = fields.Char(string="Segmentación")
    client_category = fields.Char(string="Categoría de cliente")
    cash_days = fields.Char(string="Días de pago")
    admin_contact = fields.Many2one(
        "res.partner", string="Persona contacto Adm. (Pagos)"
    )
    legal_representative = fields.Many2one("res.partner", string="Representante legal")
    place_of_correspondence = fields.Selection(
        selection=[("Oficina", "Oficina"), ("Email", "Email")],
        string="Lugar para la entrega de correspondencia",
    )
    correspondence_days = fields.Char(string="Días de correspondencia")
    correspondence_schedule_from = fields.Float(string="Horario de correspondencia desde")
    correspondence_schedule_to = fields.Float(string="Horario de correspondencia hasta")
    stop_dates = fields.Text(
        string="Fechas de parada",
        help="Fechas de detención programadas para control interno (inventarios // cierres fiscales)",
    )

    aniversario = fields.Date(string="Fecha de Aniversario")
    fecha_cumpleanos = fields.Date(string="Fecha de Cumpleaños")
    creencias = fields.Selection(selection=[
        ("Bahaismo",   "Bahaísmo"), ("Budismo", "Budismo"), ("Confucianismo", "Confucianismo"), ("Cristianismo", "Cristianismo"),
        ("Iglesia catolica", "Iglesia Católica"), ("Iglesia veterocatólica", "Iglesia Veterocatólica"),
        ("Iglesia copta", "Iglesia copta"), ("Iglesia ortodoxa", "Iglesia Ortodoxa"), ("Mormonismo", "Mormonismo"),
        ("Iglesia anglicana", "Iglesia Anglicana"), ("Iglesia Episcopal", "Iglesia Episcopal"),
        ("Protestantismo", "Protestantismo"), ("Baptista", "Baptista"), ("Metodismo", "Metodismo"),
        ("Pentecostalismo", "Pentecostalismo"),
        ("Iglesias adventistas o derivadas del adventismo", "Iglesias adventistas o derivadas del adventismo"),
        ("Iglesia Adventista del Séptimo Día", "Iglesia Adventista del Séptimo Día"),
        ("Espiritismo", "Espiritismo"), ("Helenismo", "Helenismo"), ("Hinduismo", "Hinduismo"), ("Indigenas", "Indígenas"),
        ("Judaismo", "Judaísmo"),], string="Creencias Religiosas",)

    deporte_fav = fields.Selection(selection=[
        ("Atletismo",    "Atletismo"), ("Baloncesto", "Baloncesto"), ("Beisbol", "Béisbol"),
        ("Boxeo", "Boxeo"), ("Ciclismo", "Ciclismo"), ("Esgrima", "Esgrima"), ("Futbol", "Fútbol"),
        ("Gimnasia", "Gimnasia"), ("Karate", "Kárate"), ("Lucha", "Lucha"), ("Motociclismo", "Motociclismo"),
        ("Natación", "Natación"), ("Taekwondo", "Taekwondo"), ("Tenis", "Tenis"), ("Tenis de mesa", "Tenis de mesa"),
        ("Voleibol", "Voleibol"),],
        string="Deporte Favorito",)

    tipo_cliente = fields.Selection(selection=[
        ("oro", "Oro"), 
        ("bronce", "Bronce"),
        ("silver", "Silver"),],
        string="Tipo de Cliente",)

    #tiempo_entrega_mercancia = 

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        


    def name_get(self):
        result = []
        for partner in self:
            name = partner.name
            result.append((partner.id, name))
        return result

























