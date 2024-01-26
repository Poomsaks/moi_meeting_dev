from odoo import api, fields, models, _


class PosWork(models.Model):
    _name = 'mt.pos.work'
    _rec_name = 'pos_name'
    _order = 'pos_no'

    pos_name = fields.Char(string="ชื่อตำแหน่งที่ประชุม", required=True)
    pos_no = fields.Integer(string="ลำดับ", required=True)
    active = fields.Boolean(string="สถานะการใช้งาน", default=True)

    _sql_constraints = [
        ('unique_pos_name', 'UNIQUE(pos_name)', _('ชื่อตำแหน่งที่ประชุมี้มีในระบบแล้ว !!'))
    ]


    def copy(self, default={}):
        copied_count = self.search_count(
            [('pos_name', '=like', _("สำเนา {}%").format(self.pos_name))])
        if not copied_count:
            new_name = _("สำเนา {}").format(self.pos_name)
        else:
            new_name = _("สำเนา {} ({})").format(self.pos_name, copied_count)
        default['pos_name'] = new_name

        return super(PosWork, self).copy(default)
