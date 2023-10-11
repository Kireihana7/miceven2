# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.account.models.chart_template import update_taxes_from_templates


def migrate(cr, version):
<<<<<<< HEAD
    update_taxes_from_templates(cr, 'l10n_tr.chart_template_common')
=======
    update_taxes_from_templates(cr, 'l10n_tr.l10ntr_tek_duzen_hesap')
>>>>>>> 57f59f2088c46f4603ff83bbcf2db42d705331fe
