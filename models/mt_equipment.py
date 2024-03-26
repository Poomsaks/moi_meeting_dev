from odoo import api, fields, models, _


class MtEquipment(models.Model):
    _name = 'mt.equipment'
    _rec_name = 'equip_name'

    equip_name = fields.Char(string="ชื่ออุปกรณ์", required=True, size=100)
    equip_brand = fields.Char(string="ยี่ห้อ/แบรนด์", required=False, size=100)
    ref_equip_id = fields.Char(
        string='Ref_equip_id', 
        required=False)
    equip_quantity = fields.Integer(
        string='จำนวน',
        default=1,
        required=True,
    )
    equip_unit = fields.Char(
        string="หน่วย", 
        required=False, 
        size=50,
        copy=False,
    )
    active = fields.Boolean(string="สถานะการใช้งาน", default=True)

    # @TODO remove
    # equip_pic = fields.Binary(
    #     string="รูป", 
    #     attachment=True,
    #     copy=False,
    # )
    # -----

    _sql_constraints = [
        ('unique_equip_name', 'UNIQUE(equip_name)', _('ชื่ออุปกรณ์นี้มีในระบบแล้ว !!'))
    ]


    # def copy(self, default={}):
    #     copied_count = self.search_count(
    #         [('equip_name', '=like', _("สำเนา {}%").format(self.equip_name))])
    #     if not copied_count:
    #         new_name = _("สำเนา {}").format(self.equip_name)
    #     else:
    #         new_name = _("สำเนา {} ({})").format(self.equip_name, copied_count)
    #     default['equip_name'] = new_name
    #
    #     return super(MtEquipment, self).copy(default)
