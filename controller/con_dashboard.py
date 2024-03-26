# -*- coding: utf-8 -*-
import base64
import json

import requests
from pytz import timezone

import odoo
from odoo import http
from odoo.http import request


class ControllerDashboard(http.Controller):

    @http.route('/api/meeting/get_dashboard_by_user', type='json', auth='none')
    def get_dashboard_by_user(self, **post):
        request.session.db = post.get('db')
        meeting = request.env['calendar.event'].sudo().search([('meeting_state', '=', 'sp')])
        if meeting:
            data_rec = []
            number_meeting = 0
            number_attach = 0
            attachment_name = post.get('attachment_name')
            for rec in meeting:
                if attachment_name:
                    # TODO attendee
                    public_space_rec = request.env['calendar.attendee'].sudo().search(
                        [
                            ('event_id', '=', rec.id),
                            ('partner_id', '=', post.get('partner_id'))
                        ])
                    if public_space_rec:
                        number_meeting += 1
                        attendee_info = []
                        for attendee in public_space_rec:
                            attendee_info.append({
                                'id': attendee.id,
                            })
                        # TODO meeting.agenda
                        public_space_rec = request.env['meeting.agenda'].sudo().search(
                            [('meeting_id', '=', rec.id)])
                        agenda_info = []

                        for agenda in public_space_rec:
                            agenda_info.append({
                                'attendee_id': agenda.id,
                                'partner_id': agenda.partner_id.id,
                            })
                            if agenda:
                                sub_agenda_info = request.env['meeting.sub.agenda'].search(
                                    [('agenda_id', '=', agenda.id)])
                                if sub_agenda_info:
                                    attach_data_rec = []
                                    for sub_agenda in sub_agenda_info:
                                        attach_data_info = request.env['meeting.sub.agenda.attach'].search(
                                            [('sub_agenda_id', '=', sub_agenda.id),
                                             ('attachment_name', '=', attachment_name)])
                                        if attach_data_info:
                                            la_tz = timezone('Asia/Bangkok')
                                            for attach in attach_data_info:
                                                number_attach += 1
                                                attach_data_rec.append({
                                                    'agenda_id': attach.sub_agenda_id.id,
                                                    'id': attach.id,
                                                    'attach_user': attach.attach_user.id or None,
                                                    'attach_type': attach.attach_type or None,
                                                    'attach_flag': attach.attach_flag or None,
                                                    'attachment_file': attach.attachment_file,
                                                    'attachment_name': attach.attachment_name or None,
                                                    'attachment_import_date': attach.attachment_import_date.astimezone(
                                                        la_tz) if attach.attachment_import_date else None,
                                                })

                                                num_attendees = len(attendee_info)
                                                num_agendas = len(agenda_info)
                                                num_attachments = len(attach_data_rec)

                                                vals = {
                                                    'meeting_id': rec.id,
                                                    'attendee_ids': attendee_info,
                                                    'num_attendees': num_attendees,
                                                    'agenda_ids': agenda_info,
                                                    'num_agendas': num_agendas,
                                                    'attach': attach_data_rec,
                                                    'num_attachments': num_attachments
                                                }
                                                data_rec.append(vals)
                else:
                    # TODO attendee
                    public_space_rec = request.env['calendar.attendee'].sudo().search(
                        [
                            ('event_id', '=', rec.id),
                            ('partner_id', '=', post.get('partner_id'))
                        ])
                    if public_space_rec:
                        number_meeting += 1
                        attendee_info = []
                        for attendee in public_space_rec:
                            attendee_info.append({
                                'id': attendee.id,
                            })
                        # TODO meeting.agenda
                        public_space_rec = request.env['meeting.agenda'].sudo().search(
                            [('meeting_id', '=', rec.id)])
                        agenda_info = []

                        for agenda in public_space_rec:
                            agenda_info.append({
                                'attendee_id': agenda.id,
                                'partner_id': agenda.partner_id.id,
                            })
                            if agenda:
                                sub_agenda_info = request.env['meeting.sub.agenda'].search(
                                    [('agenda_id', '=', agenda.id)])
                                if sub_agenda_info:
                                    attach_data_rec = []
                                    for sub_agenda in sub_agenda_info:
                                        number_attach += 1
                                        attach_data_info = request.env['meeting.sub.agenda.attach'].search(
                                            [('sub_agenda_id', '=', sub_agenda.id)])
                                        if attach_data_info:
                                            la_tz = timezone('Asia/Bangkok')
                                            for attach in attach_data_info:
                                                attach_data_rec.append({
                                                    'agenda_id': attach.sub_agenda_id.id,
                                                    'id': attach.id,
                                                    'attach_user': attach.attach_user.id or None,
                                                    'attach_type': attach.attach_type or None,
                                                    'attach_flag': attach.attach_flag or None,
                                                    'attachment_file': attach.attachment_file,
                                                    'attachment_name': attach.attachment_name or None,
                                                    'attachment_import_date': attach.attachment_import_date.astimezone(
                                                        la_tz) if attach.attachment_import_date else None,
                                                })

                                    num_attendees = len(attendee_info)
                                    num_agendas = len(agenda_info)
                                    num_attachments = len(attach_data_rec)

                                    vals = {
                                        'meeting_id': rec.id,
                                        'attendee_ids': attendee_info,
                                        'num_attendees': num_attendees,
                                        'agenda_ids': agenda_info,
                                        'num_agendas': num_agendas,
                                        'attach': attach_data_rec,
                                        'num_attachments': num_attachments
                                    }
                                    data_rec.append(vals)
            data = {'status': 200, 'response': data_rec, 'meeting_total': number_meeting,
                    'number_attach': number_attach, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'error'}
            return data
