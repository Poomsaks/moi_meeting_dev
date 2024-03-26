from datetime import datetime

from odoo import http, fields
from odoo.http import request
import requests
from json import loads, dumps
from pytz import timezone, utc


class ConResUser(http.Controller):

    @http.route('/api/meeting/get_res_user', type='json', auth='user')
    def get_res_user(self, **post):
        data_info = request.env['res.users'].sudo().search([])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'login': rec.login,
                    'phone': rec.phone,
                    'email': rec.partner_id.email,
                    'user_role': rec.user_role,  # user_role
                    'user_type': rec.user_type,  # user_type
                    'state': rec.state,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่ข้อมูล', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_res_user_by_id', type='json', auth='user')
    def get_res_user_by_id(self, **post):
        data_info = request.env['res.users'].sudo().search([('id', '=', post.get('id'))])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'name': rec.name,
                    'login': rec.login,
                    'email': rec.partner_id.email,
                    'phone': rec.phone,
                    'user_role': rec.user_role,  # user_role
                    'user_type': rec.user_type,  # user_type
                    'state': rec.state,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่ข้อมูล', 'message': 'success'}
            return data

    @http.route('/api/meeting/update_res_user', type='json', auth='user')
    def update_res_user(self, **post):
        data_model = request.env['res.users'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.write({
                'user_role': post.get('user_role'),  # user_role
                'user_type': post.get('user_type'),  # user_type
            })
            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลวาระการประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_user_confirm_meeting', type='json', auth='user')
    def get_user_confirm_meeting(self, **post):
        ICT = timezone('Asia/Bangkok')

        search_date = datetime.strptime(post.get('start_datetime'), "%Y-%m-%d").date() if post.get(
            'select_date') else datetime.now(ICT).date()
        start_datetime = datetime.combine(search_date, datetime.min.time())
        ICT = timezone('Asia/Bangkok')
        start_datetime = ICT.localize(start_datetime, is_dst=None).astimezone()

        chk_state = "AND ca.state = 'needsAction'"
        if post.get('state'):
            chk_state = "AND ca.state = '{}'".format(post['state'])
        elif post.get('state') == False:
            chk_state = ""

        # Logical Table Query
        query = """
                SELECT count(ca.id) as meeting_count
                FROM public.calendar_attendee ca
                INNER JOIN public.calendar_event ce ON ce.id = ca.event_id
                WHERE ca.partner_id = %(partner_id)s {}
                AND ce.start_datetime >= %(start_datetime)s
            """.format(chk_state)
        request.cr.execute(query, {
            'partner_id': post['partner_id'],
            'start_datetime': start_datetime,
        })
        meeting_count = sum([column for column, in request.cr.fetchall()])

        vals = {
            'count': meeting_count,
        }
        data = {'status': 200, 'response': vals, 'message': 'success'}
        return data

    @http.route('/api/meeting/user_confirm_meeting', type='json', auth='user')
    def user_confirm_meeting(self, **post):
        attendee = request.env['calendar.attendee'].sudo().search([
            ('event_id', '=', post.get('meeting_id')),
            ('id', '=', post.get('attendee_id'))], limit=1)
        if attendee:
            if post.get('state'):
                vals = {
                    'state': post['state'],
                    'declined_note': post['declined_note'] or None,
                    'instead_partner_id': post['instead_partner_id'] or None,
                }
                attendee.write(vals)
            data_rec = {
                'status': 200,
                'response': dict(attendee._fields['state'].selection).get(attendee.state),
                'message': 'success'
            }
            return data_rec
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล ผู้เข้าร่วมการประชุม', 'message': 'success'}
            return data
