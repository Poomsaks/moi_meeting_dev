# -*- coding: utf-8 -*-
import base64
import json

import requests

import odoo
from odoo import http
from odoo.http import request


class ControllerMeetingLogSing(http.Controller):

    @http.route('/api/meeting/get_meeting_notify', type='json', auth='none')
    def get_meeting_notify(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['meeting.notify'].sudo().search([])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'notify_name': rec.notify_name,
                    'notify_time_send': rec.notify_time_send,
                    'notify_time_read': rec.notify_time_read,
                    'notify_url': rec.notify_url,
                    'notify_send_id': rec.notify_send_id,
                    'notify_send_name': rec.notify_send_name,
                    'notify_recipient_id': rec.notify_recipient_id,
                    'notify_recipient_name': rec.notify_recipient_name,
                    'notify_email': rec.notify_email,
                    'notify_project_id': rec.notify_project_id,
                    'notify_meeting_id': rec.notify_meeting_id,
                    'status_notify': rec.status_notify,
                    'other_lv1': rec.other_lv1,
                    'other_lv2': rec.other_lv2,
                    'other_lv3': rec.other_lv3
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่ข้อมูล', 'message': 'error'}
            return data

    @http.route('/api/meeting/get_meeting_notify_by_recipient_id', type='json', auth='none')
    def get_meeting_notify_by_recipient_id(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['meeting.notify'].sudo().search(
            [('notify_recipient_name', '=', post.get('notify_recipient_name'))])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'notify_name': rec.notify_name,
                    'notify_time_send': rec.notify_time_send,
                    'notify_time_read': rec.notify_time_read,
                    'notify_url': rec.notify_url,
                    'notify_send_id': rec.notify_send_id,
                    'notify_send_name': rec.notify_send_name,
                    'notify_recipient_id': rec.notify_recipient_id,
                    'notify_recipient_name': rec.notify_recipient_name,
                    'notify_email': rec.notify_email,
                    'notify_project_id': rec.notify_project_id,
                    'notify_meeting_id': rec.notify_meeting_id,
                    'status_notify': rec.status_notify,
                    'other_lv1': rec.other_lv1,
                    'other_lv2': rec.other_lv2,
                    'other_lv3': rec.other_lv3
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่ข้อมูล', 'message': 'error'}
            return data

    @http.route('/api/meeting/add_notify', type='json', auth='user')
    def add_notify(self, **post):
        data_model = request.env['meeting.notify'].sudo().search([])
        data_create = data_model.create({
            'notify_name': post.get('notify_name'),
            'notify_time_read': post.get('notify_time_read'),
            'notify_url': post.get('notify_url'),
            'notify_send_id': post.get('notify_send_id'),
            'notify_send_name': post.get('notify_send_name'),
            'notify_recipient_id': post.get('notify_recipient_id'),
            'notify_recipient_name': post.get('notify_recipient_name'),
            'notify_email': post.get('notify_email'),
            'notify_project_id': post.get('notify_project_id'),
            'notify_meeting_id': post.get('notify_meeting_id'),
            'status_notify': post.get('status_notify'),
            'other_lv1':  post.get('other_lv1'),
            'other_lv2':  post.get('other_lv2'),
            'other_lv3':  post.get('other_lv3')
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return json.dumps(data)

    @http.route('/api/meeting/update_notify', type='json', auth='user')
    def update_notify(self, **post):
        data_model = request.env['meeting.notify'].sudo().search([('id', '=', post.get('id'))])
        data_model.write({
            'notify_name': post.get('notify_name'),
            'notify_time_read': post.get('notify_time_read'),
            'notify_url': post.get('notify_url'),
            'notify_send_id': post.get('notify_send_id'),
            'notify_send_name': post.get('notify_send_name'),
            'notify_recipient_id': post.get('notify_recipient_id'),
            'notify_recipient_name': post.get('notify_recipient_name'),
            'notify_email': post.get('notify_email'),
            'notify_project_id': post.get('notify_project_id'),
            'notify_meeting_id': post.get('notify_meeting_id'),
            'status_notify': post.get('status_notify'),
            'other_lv1': post.get('other_lv1'),
            'other_lv2': post.get('other_lv2'),
            'other_lv3': post.get('other_lv3')
        })
        data = {'status': 200, 'response': data_model.id, 'message': 'success'}
        return json.dumps(data)

