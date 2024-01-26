from odoo import api, fields, models, _


class MtRoom(models.Model):
    _name = 'mt.room'
    _rec_name = 'room_name'
    _order = 'room_name'

    room_name = fields.Char(string="ชื่อห้องประชุม", required=True)
    floor = fields.Integer(string="ชั้น", required=True, size=2)
    people_in_room = fields.Integer(string="ความจุ", required=True, size=3)

    image = fields.Binary(string="รูป", attachment=True, )
    room_address = fields.Text(string="ที่อยู่ห้องประชุม", required=False)
    meeting_color = fields.Char(string="สีห้องประชุม", required=False)
    access_type = fields.Selection(
        string="รูปแบบห้องประชุม (Public/Private)",
        selection=[('public', 'ห้องประชุม Public'), ('private', 'ห้องประชุม Private')],
        required=True,
        default='public'
    )
    access_partner_ids = fields.Many2many('res.partner', 'mt_room_access_partner_rel',
                                          string="รายชื่อผู้มีสิทธิ",
                                          help="กำหนดรายชื่อผู้มีสิทธิจัดการ (กรณี Private)"
                                          )
    partner_id = fields.Many2one(comodel_name="res.partner",
                                 string="ผู้ดูแลห้องประชุม",
                                 required=False,
                                 )
    room_type = fields.Selection(
        string="ประเภทห้องประชุม",
        selection=[('1', 'ห้องประชุม'), ('2', 'MS Teams'), ('3', 'Zoom')],
        required=False,
        default='1'
    )
    type_meeting_id = fields.Many2one(
        comodel_name="mt.type.meeting",
        string="ประเภทการประชุม",
        required=False,
    )
    room_type_ids = fields.Many2many(
        comodel_name='mt.room.type',
        string='ประเภทห้องประชุม')

    meeting_link = fields.Char(
        string='URL การประชุมออนไลน์',
        required=False)
    meeting_id = fields.Char(
        string='รหัสการประชุม (Meeting ID)',
        required=False)
    meeting_pass_code = fields.Char(
        string='รหัสผ่าน (Pass Code)',
        required=False)
    # @Link to DS organize_id
    organize_id = fields.Integer(
        string="หน่วยงาน/ฝ่าย",
        default=0,
    )
    organize_type = fields.Selection(
        string="ประเภทหน่วยงาน",
        selection=[('C', 'ส่วนกลาง'), ('R', 'ส่วนภูมิภาค')],
        required=False,
    )

    room_status = fields.Selection(
        string="สถานะห้องประชุม",
        selection=[('active', 'พร้อมใช้งาน'), ('maintenance', 'อยู่ระหว่างปรับปรุง')],
        required=True,
        default='active'
    )
    active = fields.Boolean(string="สถานะการใช้งาน", default=True)

    equipment_ids = fields.One2many(comodel_name="mt.room.equipment",
                                    inverse_name="room_id",
                                    string="อุปกรณ์"
                                    )

    service_status = fields.Boolean(string="สถานะ การใช้บริการ", default=True)
    services_ids = fields.One2many(comodel_name="mt.room.services",
                                   inverse_name="room_id",
                                   string="บริการ",
                                   required=False
                                   )
    room_admin_id = fields.Many2one(comodel_name="res.partner",
                                    string="ผู้ดูแลห้องประชุม",
                                    required=False,
                                    )
    _sql_constraints = [
        ('unique_room_name', 'UNIQUE(room_name)', _('ชื่อห้องประชุมนี้มีในระบบแล้ว !!'))
    ]


class MtRoomEquipment(models.Model):
    _name = 'mt.room.equipment'
    _rec_name = 'equipment_id'

    room_id = fields.Many2one(comodel_name="mt.room",
                              string="Room", ondelete='cascade', required=True,
                              index=True)
    equipment_id = fields.Many2one(comodel_name="mt.equipment", string="ชื่ออุปกรณ์", required=True, )

    equipment_unit = fields.Char(string="หน่วย", related="equipment_id.equip_unit", required=False, )

    equipment_qty = fields.Integer(
        string="จำนวน",
        default=1,
        required=False
    )

    _sql_constraints = [
        ('unique_room_equipment', 'UNIQUE(room_id, equipment_id)', _('มีรายการอุปกรณ์ซ้ำ ในห้องประชุม !!'))
    ]


class MtRoomServices(models.Model):
    _name = 'mt.room.services'
    _rec_name = 'service_id'

    room_id = fields.Many2one(comodel_name="mt.room", string="Room", required=False, ondelete='cascade')
    service_id = fields.Many2one(comodel_name="mt.service", string="บริการ", required=True, )
    service_type = fields.Char(
        string="ประเภท",
        related="service_id.service_type",
        required=False
    )

    # @TODO remove
    service_unit = fields.Char(string="หน่วย", related="service_id.service_unit", required=False, )
    # -----

    service_qty = fields.Integer(
        string="จำนวน",
        default=1,
        required=False
    )

    _sql_constraints = [
        ('unique_room_service', 'UNIQUE(room_id, service_id)', _('มีรายการบริการซ้ำ ในห้องประชุม !!'))
    ]
