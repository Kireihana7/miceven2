# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
<<<<<<< HEAD

import serial.tools.list_ports

=======

from glob import glob

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
from odoo.addons.hw_drivers.interface import Interface


class SerialInterface(Interface):
    connection_type = 'serial'

    def get_devices(self):
        serial_devices = {}
        for port in serial.tools.list_ports.comports():
            serial_devices[port.device] = {
                'identifier': port.device
            }
        return serial_devices
