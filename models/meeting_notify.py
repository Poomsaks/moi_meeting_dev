from odoo import models, fields, _


class MeetingNOTIFY(models.Model):
    _name = 'meeting.notify'
    _rec_name = 'notify_name'

    notify_name = fields.Char(string="ชื่อเรื่อง", required=True)
    notify_time_send = fields.Datetime(string="วันเวลาที่แจ้ง", required=False)
    notify_time_read = fields.Datetime(string="วันเวลาที่อ่าน", required=False, )
    notify_url = fields.Char(string="URL", required=False)
    notify_send_id = fields.Char(string="id ผู้ส่ง", required=False)
    notify_send_name = fields.Char(string="ชื่อผู้ส่ง", required=False)
    notify_recipient_id = fields.Char(string="id ผู้รับ", required=False)
    notify_recipient_name = fields.Char(string="ชื่อผู้รับ", required=False)
    notify_email = fields.Char(string="email", required=False)
    notify_project_id = fields.Char(string="project_id", required=False)
    notify_meeting_id = fields.Char(string="meeting_id", required=False)
    other_lv1 = fields.Char(string="other_lv1", required=False)
    other_lv2 = fields.Char(string="other_lv2", required=False)
    other_lv3 = fields.Char(string="other_lv3", required=False)
    status_notify = fields.Selection(string="สถานะ",
                                     selection=[('1', 'อ่านแล้ว'),
                                                ('2', 'ยังไม่อ่าน'),
                                                ],
                                     required=False, )
