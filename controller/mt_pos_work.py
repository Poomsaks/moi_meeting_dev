# -*- coding: utf-8 -*-

import base64
import json

from odoo import http
from odoo.http import request

class ControllerPosWork(http.Controller):

    @http.route('/api/meeting/create_pos_work', type='json', auth='user')
    def create_pos_work(self, **post):
        data_create = request.env['mt.pos.work'].create({
            'pos_name': post.get('pos_name'),
            'pos_no': post.get('pos_no'),
            'active': post.get('active', True),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data


    @http.route('/api/meeting/get_pos_work', type='json', auth='none')
    def get_pos_work(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.pos.work'].sudo().search([('active', '=', True)])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'pos_no': rec.pos_no,
                    'pos_name': rec.pos_name,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อตำแหน่งที่ประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_pos_work_by_id', type='json', auth='none')
    def get_pos_work_by_id(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.pos.work'].sudo().search([('id', '=', post.get('id'))])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'pos_no': rec.pos_no,
                    'pos_name': rec.pos_name,
                    'active': rec.active,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อตำแหน่งที่ประชุม', 'message': 'success'}
            return data


    @http.route('/api/meeting/update_pos_work', type='json', auth='user')
    def update_pos_work(self, **post):
        data_model = request.env['mt.pos.work'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.write({
                'pos_name': post.get('pos_name'),
                'pos_no': post.get('pos_no'),
                'active': post.get('active', True),
            })
            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อตำแหน่งที่ประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_pos_work', type='json', auth='user')
    def delete_pos_work(self, **post):
        data_model = request.env['mt.pos.work'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.unlink()
            data = {'status': 200, 'response': 'Delete success', 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อตำแหน่งที่ประชุม', 'message': 'success'}
            return data

