# -*- coding: utf-8 -*-

import base64
import json

from odoo import http
from odoo.http import request


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
