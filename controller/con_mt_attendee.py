# -*- coding: utf-8 -*-

import base64
import json

from odoo import http
from odoo.http import request
from odoo import fields

from pytz import timezone


class ConMtAttendee(http.Controller):

    @http.route('/api/meeting/get_attendee', type='json', auth='none')
    def get_attendee(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['calendar.event'].sudo().search([])
        data_s = []
        if not data_info:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'error'}
            return data
        for meeting in data_info:
            # TODO attendee
            meeting_rec = request.env['calendar.attendee'].sudo().search([('event_id', '=', meeting.id)])
            partner_info = {
                "counter": len(meeting_rec),
                "partner_ids": []
            }
            for partner in meeting_rec:
                partner_info['partner_ids'].append({
                    'id': partner.id or None,
                    'name': partner.partner_id.name or None,
                    'email': partner.partner_id.email or None,
                    'phone': partner.partner_id.phone or None,
                    'declined_note': partner.declined_note or None,
                })

            for rec in meeting:
                vals = {
                    'id': rec.id,
                    'partner_ids': partner_info,
                }
                data_s.append(vals)
        data = {'status': 200, 'response': data_s, 'message': 'success'}
        return data

    @http.route('/api/meeting/get_meeting_attendee_confirm', type='json', auth='none')
    def get_meeting_attendee_confirm(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['calendar.attendee'].sudo().search([('event_id', '=', post.get('meeting_id'))])
        if data_info:
            attendee_confirm_list = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'is_instead_attendee': rec.is_instead_attendee,
                    'partner_id': rec.partner_id.id,
                    'display_name': rec.partner_id.display_name,
                    'email': rec.email or None,
                    'position_id': rec.position_id.id or None,
                    'position_name': rec.position_id.name or None,
                    'declined_note': rec.declined_note or None,
                    'state_text': dict(rec._fields['state'].selection).get(rec.state),
                    'state': rec.state,
                    'vote_type': rec.vote_type or None,
                    'agenda_list': [{'agenda_id': record.id,
                                     'agenda_title_name': record.agenda_title_name,
                                     'note': record.note,
                                     'vote_choice_id': record.vote_choice_id.id or None,
                                     }
                                    for record in rec.attendee_agenda_ids],
                }
                attendee_confirm_list.append(vals)

            data_rec = {
                'meeting_id': post.get('meeting_id'),
                'attendee_confirm_list': attendee_confirm_list
            }

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล ผู้เข้าร่วมการประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/update_meeting_attendee_confirm', type='json', auth='user')
    def update_meeting_attendee_confirm(self, **post):
        data_model = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
        if data_model:
            attendee_list = []
            if post.get('attendee_confirm_list'):
                attendee_data = json.loads(json.dumps(post.get('attendee_confirm_list')))
                for rec in attendee_data:
                    if rec['id']:
                        if rec.get('agenda_list'):
                            agenda_data = json.loads(json.dumps(rec.get('agenda_list')))
                            attendee_agenda_update = request.env['attendee.agenda'].search(
                                [('attendee_id', '=', rec.get('id'))])
                            for rec_2 in agenda_data:
                                if rec_2.get('id'):
                                    attendee_agenda_update.write({
                                        'attendee_id': rec.get('id'),
                                        'agenda_title_name': rec_2.get('agenda_title_name'),
                                        'note': rec_2.get('note'),
                                        'vote_choice_id': rec_2.get('vote_choice_id'),
                                    })
                                else:
                                    request.env['attendee.agenda'].create({
                                        'attendee_id': rec.get('id'),
                                        'agenda_title_name': rec_2.get('agenda_title_name'),
                                        'note': rec_2.get('note'),
                                        'vote_choice_id': rec_2.get('vote_choice_id'),
                                    })
                        attendee_list.append((1, rec['id'], {
                            'event_id': post.get('meeting_id'),
                            'email': rec.get('email'),
                            'declined_note': rec.get('declined_note'),
                            'instead_partner_id': rec.get('instead_partner_id'),
                            'state': rec.get('state')
                        }))
                    else:
                        attendee_list.append((0, 0, {
                            'event_id': post.get('meeting_id'),
                            'email': rec.get('email'),
                            'declined_note': rec.get('declined_note'),
                            'instead_partner_id': rec.get('instead_partner_id'),
                            'state': rec.get('state')
                        }))

            data_model.write({
                'attendee_ids': attendee_list,
            })

        data = {'status': 200, 'response': data_model.id, 'message': 'success'}
        return data

        # data_model = request.env['calendar.attendee'].search([('event_id', '=', post.get('meeting_id'))])
        #
        # count_update = 0
        # attendee_confirm_list = post.get('attendee_confirm_list')
        # for rec in attendee_confirm_list:
        #     update_model = data_model.filtered(lambda r: r.id == rec.get('id')) if rec.get('id') else None
        #     if update_model:
        #         update_model.write({
        #             'email': rec.get('email', update_model.email),
        #             'declined_note': rec.get('declined_note', update_model.declined_note),
        #             'instead_partner_id': rec.get('instead_partner_id', update_model.instead_partner_id.id),
        #             'state': rec.get('state', update_model.state),
        #         })
        #         count_update += 1
        #
        # records = count_update
        # result = {
        #     'records': records,
        #     'update': count_update,
        # }
        #
        # data = {'status': 200, 'response': result, 'message': 'success'}
        # return data
