from odoo import api, fields, models, _


class MtService(models.Model):
    _name = 'mt.service'
    _rec_name = 'service_name'

    service_name = fields.Char(string="ชื่อบริการ", required=True, size=500)

    # @TODO remove
    service_unit = fields.Char(
        string="หน่วย",
        required=False,
        size=50,
        copy=False,
    )
    # service_pic = fields.Binary(
    #     string="รูป",
    #     attachment=True,
    #     copy=False,
    # )
    # -----

    service_type = fields.Char(string="ประเภท", required=False, size=100)
    active = fields.Boolean(string="สถานะการใช้งาน", default=True)

    _sql_constraints = [
        ('unique_service_name', 'UNIQUE(service_name)', _('ชื่อบริการนี้มีในระบบแล้ว !!'))
    ]


    # def copy(self, default={}):
    #     copied_count = self.search_count(
    #         [('service_name', '=like', _("สำเนา {}%").format(self.service_name))])
    #     if not copied_count:
    #         new_name = _("สำเนา {}").format(self.service_name)
    #     else:
    #         new_name = _("สำเนา {} ({})").format(self.service_name, copied_count)
    #     default['service_name'] = new_name
    #
    #     return super(MtService, self).copy(default)
