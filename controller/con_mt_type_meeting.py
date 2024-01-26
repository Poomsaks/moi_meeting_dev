# -*- coding: utf-8 -*-

import base64
import json

from odoo import http
from odoo.http import request
from odoo import fields

from pytz import timezone


class ConMtTypeMeeting(http.Controller):

    @http.route('/api/meeting/get_type_meeting', type='json', auth='none')
    def get_type_meeting(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.type.meeting'].sudo().search([])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'type_code': rec.type_code,
                    'type_name': rec.type_name,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อประเภทการประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/create_type_meeting', type='json', auth='user')
    def create_type_meeting(self, **post):
        data_create = request.env['mt.type.meeting'].create({
            'type_code': post.get('type_code'),
            'type_name': post.get('type_name'),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/get_type_meeting_by_id', type='json', auth='none')
    def get_type_meeting_by_id(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.type.meeting'].sudo().search([('id', '=', post.get('id'))])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'type_code': rec.type_code,
                    'type_name': rec.type_name,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อประเภทการประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/update_type_meeting', type='json', auth='user')
    def update_type_meeting(self, **post):
        data_model = request.env['mt.type.meeting'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.write({
                'type_code': post.get('type_code'),
                'type_name': post.get('type_name'),
            })
            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อประเภทการประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_type_meeting', type='json', auth='user')
    def delete_type_meeting(self, **post):
        data_model = request.env['mt.type.meeting'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.unlink()
            data = {'status': 200, 'response': 'Delete success', 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อประเภทการประชุม', 'message': 'success'}
            return data