
from odoo import http
from odoo import api, fields, models, _


class AlarmManager(models.AbstractModel):
    _inherit = 'calendar.alarm_manager'


    # @Override
    def do_mail_reminder(self, alert):
        result = False

        meeting = self.env['calendar.event'].browse(alert['event_id'])
        if meeting.meeting_state == 'cancel':
            return result

        alarm = self.env['calendar.alarm'].browse(alert['alarm_id'])
        if alarm.type == 'email':
            client_details = self.env.ref('base.main_company')
            if client_details.use_api_sendmail:
                result = meeting.attendee_ids.filtered(lambda r: r.state != 'declined' and r.state != 'instead')._send_mail_notification(client_details, meeting)
            else:
                # @Test mail reminder alarm.
                result = meeting.attendee_ids.filtered(lambda r: r.state != 'declined' and r.state != 'instead')._send_mail_notification(client_details, meeting, 'oic.mail01@gmail.com')

                # result = meeting.attendee_ids.filtered(lambda r: r.state != 'declined' and r.state != 'instead')._send_mail_to_attendees('odoo_thai_meeting.calendar_template_meeting_reminder', force_send=True)

        return result
