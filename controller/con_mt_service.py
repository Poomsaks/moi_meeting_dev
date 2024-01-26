# -*- coding: utf-8 -*-

import base64
import json

from odoo import http
from odoo.http import request
from odoo import fields

from pytz import timezone


class ConMtService(http.Controller):

    @http.route('/api/meeting/get_service', type='json', auth='none')
    def get_service(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.service'].sudo().search([('active', '=', True)])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'service_name': rec.service_name,
                    'service_type': rec.service_type or "",
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อบริการ', 'message': 'success'}
            return data

    @http.route('/api/meeting/create_service', type='json', auth='user')
    def create_service(self, **post):
        data_create = request.env['mt.service'].create({
            'service_name': post.get('service_name'),
            'service_type': post.get('service_type'),
            'active': post.get('active', True),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/get_meeting_services', type='json', auth='none')
    def get_meeting_services(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['meeting.services'].sudo().search([('meeting_id', '=', post.get('meeting_id'))])
        if data_info:
            services_list = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'service_id': rec.service_id.id,
                    'service_name': rec.service_id.service_name,
                    'service_unit': rec.service_unit,
                    'qty_morning': rec.qty_morning,
                    'qty_afternoon': rec.qty_afternoon,
                    'service_qty': rec.service_qty,
                    'sum_qty': rec.sum_qty,
                }
                services_list.append(vals)

            data_rec = {
                'meeting_id': post.get('meeting_id'),
                'services_list': services_list
            }

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล บริการ', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_service_by_id', type='json', auth='none')
    def get_service_by_id(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.service'].sudo().search([('id', '=', post.get('id'))])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'service_name': rec.service_name,
                    'service_type': rec.service_type or "",
                    'active': rec.active,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อบริการ', 'message': 'success'}
            return data

    @http.route('/api/meeting/update_service', type='json', auth='user')
    def update_service(self, **post):
        data_model = request.env['mt.service'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.write({
                'service_name': post.get('service_name'),
                'service_type': post.get('service_type'),
                'active': post.get('active', True),
            })
            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อบริการ', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_service', type='json', auth='user')
    def delete_service(self, **post):
        data_model = request.env['mt.service'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.unlink()
            data = {'status': 200, 'response': 'Delete success', 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อบริการ', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_meeting_services', type='json', auth='user')
    def delete_meeting_services(self, **post):
        if post.get('id'):
            data_model = request.env['meeting.services'].search(
                [('meeting_id', '=', post.get('meeting_id')), ('id', '=', post.get('id'))])
            if data_model:
                data_model.unlink()

                data = {'status': 200, 'response': 'Delete Success', 'message': 'success'}
                return data

        elif post.get('ids'):
            data_model = request.env['meeting.services'].search(
                [('meeting_id', '=', post.get('meeting_id')), ('id', 'in', post.get('ids'))])
            if data_model:
                data_model.unlink()

                data = {'status': 200, 'response': 'Delete Success', 'message': 'success'}
                return data

        data = {'status': 500, 'response': 'ไม่พบข้อมูล บริการ', 'message': 'success'}
        return data