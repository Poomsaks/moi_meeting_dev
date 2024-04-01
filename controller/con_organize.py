# -*- coding: utf-8 -*-

import base64
import json

from odoo import http
from odoo.http import request


class ConOrganize(http.Controller):

    @http.route('/api/meeting/get_organize', type='json', auth='none')
    def get_organize(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mdm.organize'].sudo().search([])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'code': rec.code,
                    'ref_code': rec.ref_code,
                    'ref_level_code': rec.ref_level_code,
                    'name': rec.name,
                    'full_name': rec.full_name,
                    'name_en': rec.name_en,
                    'full_name_en': rec.full_name_en,
                    'level': rec.level,
                    'level_id': rec.level_id,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'error'}
            return data

    @http.route('/api/meeting/get_organize_by_code', type='json', auth='none')
    def get_organize_by_code(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mdm.organize'].sudo().search([('code', '=', post.get('code'))])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'code': rec.code,
                    'ref_code': rec.ref_code,
                    'ref_level_code': rec.ref_level_code,
                    'name': rec.name,
                    'full_name': rec.full_name,
                    'name_en': rec.name_en,
                    'full_name_en': rec.full_name_en,
                    'level': rec.level,
                    'level_id': rec.level_id,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'error'}
            return data
