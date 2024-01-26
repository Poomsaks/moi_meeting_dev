from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import date, datetime, timedelta, MAXYEAR


class MeetingGenCode(models.Model):
    _name = 'meeting.gen.code'

    meeting_id = fields.Many2one(comodel_name="calendar.event",
                                 string="Meeting",)
    partner_id = fields.Many2one(comodel_name="res.partner", string="รายชื่อ", required=True, )
    passcode = fields.Char(string="รหัส Passcode", required=True, size=7)
    time_minutes = fields.Integer(string="จำนวน (นาที)", required=False, default=30)
    start_datetime = fields.Datetime(string="เริ่ม", required=False, default=None)
    end_datetime = fields.Datetime(string="สิ้นสุด", required=False, default=None)

