# -*- coding: utf-8 -*-

import base64
import json

from odoo import http
from odoo.http import request
from odoo import fields

from pytz import timezone


class ConCalender(http.Controller):

    @http.route('/api/meeting/get_alarm', type='json', auth='none')
    def get_alarm(self, **post):
        request.session.db = post.get('db')
        alarm = request.env['calendar.alarm'].sudo().search([])
        if alarm:
            data_rec = []
            for rec in alarm:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'alarm_type': rec.alarm_type
                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลการแจ้งเตือน', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_alarm_by_id', type='json', auth='none')
    def get_alarm_by_id(self, **post):
        request.session.db = post.get('db')
        alarm = request.env['calendar.alarm'].sudo().search([('type', '=', 'email'), ('id', '=', post.get('id'))])
        if alarm:
            data_rec = []
            for rec in alarm:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'alarm_type': rec.alarm_type
                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลการแจ้งเตือน', 'message': 'success'}
            return data
