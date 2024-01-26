from odoo import http, fields
from odoo.http import request
from datetime import datetime
import requests
from json import loads, dumps
from pytz import timezone, utc


class ConPartner(http.Controller):

    @http.route('/api/meeting/create_res_partner', type='json', auth='user')
    def create_res_partner(self, **post):
        data_create = request.env['res.partner'].create({
            'name': post.get('name'),
            'email': post.get('email'),
            'phone': post.get('phone'),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    # Project
    @http.route('/api/meeting/get_partner', type='json', auth='none')
    def get_partner(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['res.partner'].sudo().search([])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'email': rec.email,
                    'phone': rec.phone
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่ข้อมูล', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_partner_by_id', type='json', auth='none')
    def get_partner_by_id(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['res.partner'].sudo().search([("id", '=', post.get("id"))])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'email': rec.email,
                    'phone': rec.phone
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่ข้อมูล', 'message': 'success'}
            return data
