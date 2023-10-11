from odoo import models


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

<<<<<<< HEAD
    def _get_rendering_context(self, report, docids, data):
        data = super()._get_rendering_context(report, docids, data)
        data['din_header_spacing'] = report.get_paperformat().header_spacing
=======
    def _get_rendering_context(self, docids, data):
        data = super()._get_rendering_context(docids, data)
        data['din_header_spacing'] = self.get_paperformat().header_spacing
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
        return data
