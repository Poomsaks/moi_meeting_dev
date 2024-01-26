# -*- coding: utf-8 -*-

import base64
import json

from odoo import http
from odoo.http import request

class ControllerMtTypeVote(http.Controller):

    @http.route('/api/meeting/create_type_vote', type='json', auth='user')
    def create_type_vote(self, **post):
        data_create = request.env['mt.type.vote'].create({
            'type_name': post.get('type_name'),
            'type_vote': post.get('type_vote'),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data


    @http.route('/api/meeting/get_type_vote', type='json', auth='none')
    def get_type_vote(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.type.vote'].sudo().search([])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'type_name': rec.type_name,
                    'type_vote': rec.type_vote,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อประเภทการ Vote', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_type_vote_by_id', type='json', auth='none')
    def get_type_vote_by_id(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.type.vote'].sudo().search([('id', '=', post.get('id'))])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'type_name': rec.type_name,
                    'type_vote': rec.type_vote,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อประเภทการ Vote', 'message': 'success'}
            return data


    @http.route('/api/meeting/update_type_vote', type='json', auth='user')
    def update_type_vote(self, **post):
        data_model = request.env['mt.type.vote'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.write({
                'type_name': post.get('type_name'),
                'type_vote': post.get('type_vote'),
            })
            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อประเภทการ Vote', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_type_vote', type='json', auth='user')
    def delete_type_vote(self, **post):
        data_model = request.env['mt.type.vote'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.unlink()
            data = {'status': 200, 'response': 'Delete success', 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อประเภทการ Vote', 'message': 'success'}
            return data

