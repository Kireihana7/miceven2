# -*- coding: utf-8 -*-

from odoo import sql_db
from datetime import datetime, timedelta
from odoo import api, fields, models, _

class IrCron(models.Model):
    _inherit = 'ir.cron'

    @classmethod
    def _process_job(cls, job_cr, job, cron_cr):

        if job['cron_name'] == 'Envío de nóminas gradual a correos':

            if job['numbercall'] == 1:
                job['numbercall'] = 50
                date = datetime.today()
                month = date.month+1 if date.month<12 else 1
                year= date.year if month !=1 else date.year+1

                next_date = datetime.date(year=year, month=month, day=monthrange(year, month + 1)[1])
                    
                job['nextcall'] = next_date

        res = super(IrCron, cls)._process_job(job_cr, job, cron_cr)
        return res
