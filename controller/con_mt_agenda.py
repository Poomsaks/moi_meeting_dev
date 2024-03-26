# -*- coding: utf-8 -*-

import base64
import datetime
import json

from odoo import http
from odoo.http import request
from pytz import timezone


class ControllerAgenda(http.Controller):

    @http.route('/api/meeting/create_agenda', type='json', auth='user')
    def create_agenda(self, **post):
        data_create = request.env['mt.agenda'].create({
            'agenda_name': post.get('agenda_name'),
            'active': post.get('active', True),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/get_agenda', type='json', auth='none')
    def get_agenda(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.agenda'].sudo().search([('active', '=', True)])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'agenda_name': rec.agenda_name,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลวาระการประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_agenda_by_id', type='json', auth='none')
    def get_agenda_by_id(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.agenda'].sudo().search([('id', '=', post.get('id'))])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'agenda_name': rec.agenda_name,
                    'active': rec.active,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลวาระการประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_meeting_attach_file', type='json', auth='none')
    def get_meeting_attach_file(self, **post):
        request.session.db = post.get('db')
        meeting_id = post.get('meeting_id')
        if meeting_id:
            calendar_event_info = request.env['calendar.event'].search([
                ('id', '=', meeting_id),
                ('start_date', '>=', datetime.datetime.now().strftime('%Y-%m-%d 00:00:00')),
                ('end_date', '<=', datetime.datetime.now().strftime('%Y-%m-%d 23:59:59'))
            ])
            if calendar_event_info:
                meeting_agenda_info = request.env['meeting.agenda'].search(
                    [('meeting_id', '=', calendar_event_info.id)])
                if meeting_agenda_info:
                    attach_data_info = request.env['meeting.agenda.attach'].search(
                        [('agenda_id', '=', meeting_agenda_info.id)])
                    if attach_data_info:
                        la_tz = timezone('Asia/Bangkok')
                        data_rec = {
                            'agenda_id': attach_data_info.agenda_id.id,
                            'id': attach_data_info.id,
                            'attach_user': attach_data_info.attach_user or None,
                            'attach_type': attach_data_info.attach_type or None,
                            'attach_flag': attach_data_info.attach_flag or None,
                            'attachment_file': attach_data_info.attachment_file,
                            'attachment_name': attach_data_info.attachment_name or None,
                            'attachment_import_date': attach_data_info.attachment_import_date.astimezone(
                                la_tz) if attach_data_info.attachment_import_date else None,
                        }

                        data = {'status': 200, 'response': data_rec, 'message': 'success'}
                        return data
                    else:
                        data = {'status': 500, 'response': 'No attachment data found for the given agenda.',
                                'message': 'error'}
                        return data
                else:
                    data = {'status': 500, 'response': 'No meeting agenda found for the given calendar event.',
                            'message': 'error'}
                    return data
            else:
                data = {'status': 500, 'response': 'No calendar event found with the given ID.', 'message': 'error'}
                return data
        else:
            data = {'status': 500, 'response': 'No meeting ID provided.', 'message': 'error'}
            return data

    @http.route('/api/meeting/get_meeting_attach_file_by_id', type='json', auth='none')
    def get_meeting_attach_file_by_id(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['meeting.agenda.attach'].search([
            ('agenda_id', '=', post.get('agenda_id')),
            ('id', '=', post.get('id'))])
        if data_info:
            la_tz = timezone('Asia/Bangkok')
            data_rec = {
                'agenda_id': data_info.agenda_id.id,
                'id': data_info.id,
                'attach_user': data_info.attach_user or None,
                'attach_type': data_info.attach_type or None,
                'attach_flag': data_info.attach_flag or None,
                'attachment_file': data_info.attachment_file,
                'attachment_name': data_info.attachment_name or None,
                'attachment_import_date': data_info.attachment_import_date.astimezone(
                    la_tz) if data_info.attachment_import_date else None,
            }

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลเอกสาร', 'message': 'success'}
            return data

    @http.route('/api/meeting/update_agenda', type='json', auth='user')
    def update_agenda(self, **post):
        data_model = request.env['mt.agenda'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.write({
                'agenda_name': post.get('agenda_name'),
                'active': post.get('active', True),
            })
            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลวาระการประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_agenda', type='json', auth='user')
    def delete_agenda(self, **post):
        data_model = request.env['mt.agenda'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.unlink()
            data = {'status': 200, 'response': 'Delete success', 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลวาระการประชุม', 'message': 'success'}
            return data
