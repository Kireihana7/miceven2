# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import common, new_test_user
from odoo import fields


<<<<<<< HEAD
class TestFleet(common.TransactionCase):
=======
class TestFleet(common.SavepointCase):
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    def test_search_renewal(self):
        """
            Should find the car with overdue contract or renewal due soon
        """
        user = new_test_user(self.env, "test base user", groups="base.group_user")
        brand = self.env["fleet.vehicle.model.brand"].create({
            "name": "Audi",
        })
        model = self.env["fleet.vehicle.model"].create({
            "brand_id": brand.id,
            "name": "A3",
        })
        car_1 = self.env["fleet.vehicle"].create({
            "model_id": model.id,
            "driver_id": user.partner_id.id,
            "plan_to_change_car": False
        })

        car_2 = self.env["fleet.vehicle"].create({
            "model_id": model.id,
            "driver_id": user.partner_id.id,
            "plan_to_change_car": False
        })
        Log = self.env['fleet.vehicle.log.contract']
<<<<<<< HEAD
        Log.create({
=======
        log = Log.create({
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            'vehicle_id': car_2.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=10)
        })
        res = self.env["fleet.vehicle"].search([('contract_renewal_due_soon', '=', True), ('id', '=', car_2.id)])
        self.assertEqual(res, car_2)

<<<<<<< HEAD
        Log.create({
=======
        log = Log.create({
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
            'vehicle_id': car_1.id,
            'expiration_date': fields.Date.add(fields.Date.today(), days=-10)
        })
        res = self.env["fleet.vehicle"].search([('contract_renewal_overdue', '=', True), ('id', '=', car_1.id)])
        self.assertEqual(res, car_1)
