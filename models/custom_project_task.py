# -*- coding: utf-8 -*-

from email.utils import formataddr

from odoo import _, api, exceptions, fields, models, tools
from datetime import datetime
import mimetypes
from odoo.tools.mimetypes import guess_mimetype


class ProjectTask(models.Model):
    _inherit = "project.task"

    meeting_id = fields.Many2one(comodel_name="calendar.event", string="การประชุม", required=False, index=True, )
    task_state = fields.Selection(string="สถานะ",
                                  selection=[('draft', 'ยังไม่ดำเนินการ'),
                                             ('process', 'กำลังดำเนินการ'),
                                             ('waiting', 'รอดำเนินการ'),
                                             ('close', 'ปิดงาน')],
                                  required=False, default='draft')

    actual_start = fields.Date(string="Actual Start", required=False, )
    actual_finish = fields.Date(string="Actual Finish", required=False, )
    task_hour = fields.Float(string="จำนวน (ชั่วโมง)", default=1)

    task_attach_ids = fields.One2many(comodel_name="project.task.attach", inverse_name="project_id",
                                      string="แนบไฟล์")

    user_id = fields.Many2one('res.users', string='User')
    partner_id = fields.Many2one('res.partner',
                                 string='Assigned',
                                 compute='_compute_partner_id',
                                 inverse='_set_partner_id',
                                 store=True,
                                 readonly=False,
                                 states={'done': [('readonly', True)]}
                                 )

    tag = fields.Char(string='Tag')

    @api.depends('user_id')
    def _compute_partner_id(self):
        for rec in self:
            rec.partner_id = rec.user_id.partner_id

    def _set_partner_id(self):
        for rec in self:
            user = self.env['res.users'].sudo().search([('partner_id', '=', rec.partner_id.id)], limit=1)
            if user:
                rec.user_id = user.id

    # @Override 'mail.thread' core method _message_log
    def _message_log(self, body='', subject=False, message_type='notification', **kwargs):
        """ Shortcut allowing to post note on a document. It does not perform
        any notification and pre-computes some values to have a short code
        as optimized as possible. This method is private as it does not check
        access rights and perform the message creation as sudo to speedup
        the log process. This method should be called within methods where
        access rights are already granted to avoid privilege escalation. """
        if len(self.ids) > 1:
            raise exceptions.Warning(
                _('Invalid record set: should be called as model (without records) or on single-record recordset'))

        kw_author = kwargs.pop('author_id', False)
        if kw_author:
            author = self.env['res.partner'].sudo().browse(kw_author)
        else:
            author = self.env.user.partner_id
        if not author.email:
            return False
            # raise exceptions.UserError(_("Unable to log message, please configure the sender's email address."))

        email_from = formataddr((author.name, author.email))
        message_values = {
            'subject': subject,
            'body': body,
            'author_id': author.id,
            'email_from': email_from,
            'message_type': message_type,
            'model': kwargs.get('model', self._name),
            'res_id': self.ids[0] if self.ids else False,
            'subtype_id': self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
            'record_name': False,
            'reply_to': self.env['mail.thread']._notify_get_reply_to(default=email_from, records=None)[False],
            'message_id': tools.generate_tracking_message_id('message-notify'),
        }
        message_values.update(kwargs)
        message = self.env['mail.message'].sudo().create(message_values)
        return message

    # Link project
    @api.model
    def project_task(self):
        self.ensure_one()
        action = self.env.ref('project.open_view_project_all_config').read()[0]
        action['domain'] = [('id', '=', self.project_id.id)]
        return action

    # list of meeting in oe_button
    @api.model
    def schedule_meeting(self):
        # action = self.env.ref('odoo_thai_meeting.meeting_calendar_event_view_action').read()[0]
        # action['domain'] = [('id', '=', self.meeting_id.id)]
        # action['view_id'] = self.env.ref('odoo_thai_meeting.meeting_calendar_event_view_tree').id,
        # return action

        return {
            "type": "ir.actions.act_window",
            "name": "การประชุม",
            "res_id": self.id,
            "res_model": "calendar.event",
            "view_type": "form",
            "view_mode": "tree,form",
            'view_id': False,
            'views': [(self.env.ref('odoo_thai_meeting.meeting_calendar_event_view_tree').id, 'tree'),
                      (self.env.ref('odoo_thai_meeting.meeting_calendar_event_view_form').id, 'form')],
            "domain": [('id', '=', self.meeting_id.id)],
            "flags": {"form": {"action_buttons": True}},
        }

    # create meeting
    @api.model
    def create_meeting(self):
        return {
            "type": "ir.actions.act_window",
            "name": "การประชุม",
            "res_model": "calendar.event",
            "view_type": "form",
            "view_mode": "form",
            "view_id": False,
            'views': [(self.env.ref('odoo_thai_meeting.meeting_calendar_event_view_form').id, 'form')],
            'context': {'default_name': 'งาน ' + self.name,
                        'default_project_id': self.project_id.id},
            'target': 'new',
        }


class ProjectTaskAttach(models.Model):
    _name = 'project.task.attach'

    project_id = fields.Many2one(comodel_name="project.task",
                                 string="Task", ondelete='cascade', required=True,
                                 index=True)

    attachment_file = fields.Binary("ชื่อเอกสาร", attachment=True, required=False)
    attachment_name = fields.Char("ชื่อเอกสาร")
    attachment_import_date = fields.Datetime(string='วันที่นำเข้า',
                                             default=lambda self: fields.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
