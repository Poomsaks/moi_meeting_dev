from odoo import http, fields
from odoo.http import request
from datetime import datetime
import requests
from json import loads, dumps
from pytz import timezone, utc


class ConProjectProject(http.Controller):

    # Project
    @http.route('/api/meeting/get_project', type='json', auth='none')
    def get_project(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['project.project'].sudo().search([])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'date_start': rec.date_start or None,
                    'date_end': rec.date_end or None,
                    'state': rec.state or None,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่ข้อมูล', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_project_by_id', type='json', auth='none')
    def get_project_by_id(self, **post):
        request.session.db = post.get('db')
        projects = request.env['project.project'].sudo().search([('id', '=', post.get('id')), ('active', '=', True)])
        if projects:
            data_rec = []
            for rec in projects:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'responsible_id': rec.user_id.id or None,
                    'responsible_name': rec.user_id.name or None,
                    'date_start': rec.date_start or None,
                    'date_end': rec.date_end or None,
                    'state': dict(rec._fields['state'].selection).get(rec.state) or None,
                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อโครงการ', 'message': 'success'}
            return data