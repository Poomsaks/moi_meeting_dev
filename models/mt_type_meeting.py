from odoo import api, fields, models, _


class MtTypeMeeting(models.Model):
    _name = 'mt.type.meeting'
    _rec_name = 'type_name'

    type_name = fields.Char(string="ชื่อประเภท", required=True)
    type_code = fields.Char(string="รหัส", required=True)

    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(type_name)', _('ชื่อประเภทนี้ มีในระบบแล้ว !!')),
        ('unique_type_code', 'UNIQUE(type_code)', _('รหัสนี้ มีในระบบแล้ว !!'))
    ]


    def copy(self, default={}):
        copied_count = self.search_count(
            [('type_name', '=like', _("สำเนา {}%").format(self.type_name))])
        if not copied_count:
            new_name = _("สำเนา {}").format(self.type_name)
        else:
            new_name = _("สำเนา {} ({})").format(self.type_name, copied_count)
        default['type_name'] = new_name

        copied_count = self.search_count(
            [('type_code', '=like', _("สำเนา {}%").format(self.type_code))])
        if not copied_count:
            new_name = _("สำเนา {}").format(self.type_code)
        else:
            new_name = _("สำเนา {} ({})").format(self.type_code, copied_count)
        default['type_code'] = new_name

        return super(MtTypeMeeting, self).copy(default)
