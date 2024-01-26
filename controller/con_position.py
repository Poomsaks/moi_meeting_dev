# -*- coding: utf-8 -*-

import base64
import json

from odoo import http
from odoo.http import request


class ConPosition(http.Controller):

    @http.route('/api/meeting/create_position', type='json', auth='user')
    def create_position(self, **post):
        data_create = request.env['mdm.position'].create({
            'name': post.get('pos_name'),
            'code': post.get('pos_no'),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/get_position', type='json', auth='none')
    def get_position(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mdm.position'].sudo().search([])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'code': rec.code,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อตำแหน่ง', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_position_by_id', type='json', auth='none')
    def get_position_by_id(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mdm.position'].sudo().search([('id', '=', post.get('id'))])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'code': rec.code,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อตำแหน่ง', 'message': 'success'}
            return data

    @http.route('/api/meeting/update_position', type='json', auth='user')
    def update_position(self, **post):
        data_model = request.env['mdm.position'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.write({
                'name': post.get('pos_name'),
                'code': post.get('pos_no'),
            })
            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อตำแหน่ง', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_position', type='json', auth='user')
    def delete_position(self, **post):
        data_model = request.env['mdm.position'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.unlink()
            data = {'status': 200, 'response': 'Delete success', 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อตำแหน่ง', 'message': 'success'}
            return data
