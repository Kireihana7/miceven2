# Part of Odoo. See LICENSE file for full copyright and licensing details.
import odoo
from odoo.tests import Form, HttpCase, tagged


@tagged('-at_install', 'post_install')
class TestStockReportTour(HttpCase):
<<<<<<< HEAD
=======
    def setUp(self):
        super().setUp()
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe

    def _get_report_url(self):
        return '/web#&model=product.template&action=stock.product_template_action_product'

<<<<<<< HEAD
=======

>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
    def test_stock_route_diagram_report(self):
        """ Open the route diagram report."""
        url = self._get_report_url()

        self.start_tour(url, 'test_stock_route_diagram_report', login='admin', timeout=180)
