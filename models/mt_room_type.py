from odoo import api, fields, models, _


class MtRoomType(models.Model):
    _name = 'mt.room.type'
    _rec_name = 'type_room'
    _order = 'type_room'

    type_room = fields.Char(string="ชื่อประเภท", required=True)