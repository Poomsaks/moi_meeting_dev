from odoo import models, fields, _, api, exceptions, tools
from odoo.tools import formataddr


class CustomResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner Details'

    # @Link to DS Personal Data
    personal_id = fields.Integer()
    personal_code = fields.Char(string="personal_code")
    position_name = fields.Char(string="position_name")
    attendee_code = fields.Char(string="attendee_code")
    # @Link to DS position_id
    position_id = fields.Integer(
        string="ตำแหน่ง",
        default=0,
    )
    personal_pos = fields.Char(string="ตำแหน่ง", required=False)
    function = fields.Char(
        string='ตำแหน่ง',
        related="personal_pos",
        store=True,
    )

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
    affiliation = fields.Char(string="สังกัดฝ่าย", required=False)

    meeting_count = fields.Integer("การประชุม", compute='_compute_meeting_count')

    comment = fields.Text(
        string='หมายเหตุ',
        placeholder='หมายเหตุ...'
    )

    # count of meeting for that project
    @api.model
    def _compute_meeting_count(self):
        count = 0
        for record in self:
            meeting_ids = self.env['calendar.event'].search([])
            if meeting_ids:
                for meeting in meeting_ids:
                    for personal in meeting.partner_ids:
                        if record.id == personal.id:
                            count += 1
                            break
            record.meeting_count = count

    @api.model
    def schedule_meeting(self):
        return {
            "type": "ir.actions.act_window",
            "name": "การประชุม",
            "res_id": self.id,
            "res_model": "calendar.event",
            "view_type": "form",
            "view_mode": "tree,form",
            "view_id": False,
            'views': [(self.env.ref('odoo_thai_meeting.meeting_calendar_event_view_tree').id, 'tree'),
                      (self.env.ref('odoo_thai_meeting.meeting_calendar_event_view_form').id, 'form')],
            "domain": [('partner_ids', 'in', self.id)],
            "flags": {"form": {"action_buttons": True}},
        }

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
