from odoo import api, fields, models, modules, _

class ResUsers(models.Model):    
    _inherit = 'res.users'
    
    attendance_geolocation = fields.Boolean(string="Attendances Geolocation", default=False)

    def __init__(self, pool, cr):
        init_res = super(ResUsers, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        type(self).SELF_WRITEABLE_FIELDS.extend(["attendance_geolocation"])
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = list(self.SELF_READABLE_FIELDS)
        type(self).SELF_READABLE_FIELDS.extend(["attendance_geolocation"])
        return init_res

    
    def attendance_geolocation_reload(self):
        return {
            "type": "ir.actions.client",
            "tag": "reload_context"
        }