import calendar

import pytz
from dateutil import relativedelta
from odoo import http, fields
from odoo.http import Controller, route, request
import json
import datetime
from datetime import timedelta, MAXYEAR

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from pytz import timezone


class ConMeeting(http.Controller):

    # TODO API Create Meeting
    @http.route('/api/meeting/create_meeting', type='json', auth='user')
    def create_meeting(self, **post):
        ICT = timezone('Asia/Bangkok')
        duration = float(post.get('duration'))
        start_datetime = datetime.datetime.strptime(post.get('start_datetime'), DEFAULT_SERVER_DATETIME_FORMAT)
        start = ICT.localize(start_datetime).astimezone(timezone('Asia/Bangkok')).replace(tzinfo=None)
        end_date_time = start_datetime + timedelta(hours=duration)
        stop = ICT.localize(end_date_time).astimezone(timezone('Asia/Bangkok')).replace(tzinfo=None)
        data_model = request.env['calendar.event']
        data_create = data_model.create({
            'name': post.get('name'),
            'start': start,
            'stop': stop,
            'start_date': start,
            'end_date': stop,
            'meeting_type_id': post.get('meeting_type_id'),
            'description': post.get('description'),
            'room_id': post.get('room_id'),
            'join_inside': post.get('join_inside'),
            'join_outside': post.get('join_outside'),
            'meet_name': post.get('meet_name'),
            'meet_url': post.get('meet_url'),
            'meet_number': post.get('meet_number'),
            'meet_passcode': post.get('meet_passcode'),
            'requester_id': post.get('requester_id'),
            'meeting_root_type': post.get('meeting_root_type')
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/create_update_meeting_agenda', type='json', auth='user')
    def create_update_meeting_agenda(self, **post):
        if post.get('agenda_ids'):
            agenda_data = json.loads(json.dumps(post.get('agenda_ids')))
            for agenda_item in agenda_data:
                if agenda_item.get('agenda_id'):
                    agenda_update = request.env['meeting.agenda'].search([('id', '=', agenda_item.get('agenda_id'))])
                    if agenda_update:
                        agenda_update.write({
                            'meeting_id': post.get('meeting_id'),
                            'agenda_title_name': agenda_item.get('agenda_title_name'),
                            'agenda_no': agenda_item.get('agenda_no'),
                            'agenda_detail': agenda_item.get('agenda_detail'),
                            'partner_id': agenda_item.get('partner_id'),
                            'vote_state': agenda_item.get('vote_state_id')
                        })
                        sub_agenda_ids = agenda_item.get('sub_agenda_ids', [])
                        for sub_agenda_item in sub_agenda_ids:
                            if sub_agenda_item.get('sub_agenda_id'):
                                sub_agenda_update = request.env['meeting.sub.agenda'].search(
                                    [('id', '=', sub_agenda_item.get('sub_agenda_id'))])
                                if sub_agenda_update:
                                    sub_agenda_update.write({
                                        'agenda_id': agenda_item.get('agenda_id'),
                                        'sub_agenda_no': sub_agenda_item.get('sub_agenda_no'),
                                        'sub_agenda_name': sub_agenda_item.get('sub_agenda_name'),
                                        'sub_agenda_detail': sub_agenda_item.get('sub_agenda_detail'),
                                        'partner_id': sub_agenda_item.get('partner_id'),
                                        'vote_state': sub_agenda_item.get('vote_state')
                                    })
                                    sub_agenda_attach_ids = sub_agenda_item.get('sub_agenda_attach_ids', [])
                                    for sub_agenda_attach_item in sub_agenda_attach_ids:
                                        if sub_agenda_attach_item.get('attach_id'):
                                            sub_agenda_attach_update = request.env['meeting.sub.agenda.attach'].search(
                                                [('id', '=', sub_agenda_attach_item.get('attach_id'))])
                                            if sub_agenda_attach_update:
                                                sub_agenda_attach_update.write({
                                                    'sub_agenda_id': sub_agenda_item.get('sub_agenda_id'),
                                                    'attach_user': sub_agenda_item.get('attach_user'),
                                                    'attach_type': sub_agenda_item.get('attach_type'),
                                                    'attach_flag': sub_agenda_item.get('attach_flag'),

                                                    'attachment_file': sub_agenda_attach_item.get('attachment_file'),
                                                    'attachment_name': sub_agenda_attach_item.get('attachment_name'),
                                                })
                                        else:
                                            request.env['meeting.sub.agenda.attach'].create({
                                                'sub_agenda_id': sub_agenda_update.id,
                                                'attach_user': sub_agenda_attach_item.get('attach_user'),
                                                'attach_type': sub_agenda_attach_item.get('attach_type'),
                                                'attach_flag': sub_agenda_attach_item.get('attach_flag'),
                                                'attachment_file': sub_agenda_attach_item.get('attachment_file'),
                                                'attachment_name': sub_agenda_attach_item.get('attachment_name'),
                                            })
                            else:
                                sub_agenda_create = request.env['meeting.sub.agenda'].create({
                                    'agenda_id': agenda_update.id,
                                    'sub_agenda_no': sub_agenda_item.get('sub_agenda_no'),
                                    'sub_agenda_name': sub_agenda_item.get('sub_agenda_name'),
                                    'sub_agenda_detail': sub_agenda_item.get('sub_agenda_detail'),
                                    'partner_id': sub_agenda_item.get('partner_id'),
                                    'vote_state': sub_agenda_item.get('vote_state')
                                })
                                sub_agenda_attach_ids = sub_agenda_item.get('sub_agenda_attach_ids', [])
                                for sub_agenda_attach_item in sub_agenda_attach_ids:
                                    if sub_agenda_attach_item.get('attach_id'):
                                        sub_agenda_attach_update = request.env['meeting.sub.agenda.attach'].search(
                                            [('id', '=', sub_agenda_attach_item.get('attach_id'))])
                                        if sub_agenda_attach_update:
                                            sub_agenda_attach_update.write({
                                                'sub_agenda_id': sub_agenda_item.get('sub_agenda_id'),
                                                'attach_user': sub_agenda_attach_item.get('attach_user'),
                                                'attach_type': sub_agenda_attach_item.get('attach_type'),
                                                'attach_flag': sub_agenda_attach_item.get('attach_flag'),
                                                'attachment_file': sub_agenda_attach_item.get('attachment_file'),
                                                'attachment_name': sub_agenda_attach_item.get('attachment_name'),
                                            })
                                    else:
                                        request.env['meeting.sub.agenda.attach'].create({
                                            'sub_agenda_id': sub_agenda_create.id,
                                            'attach_user': sub_agenda_attach_item.get('attach_user'),
                                            'attach_type': sub_agenda_attach_item.get('attach_type'),
                                            'attach_flag': sub_agenda_attach_item.get('attach_flag'),
                                            'attachment_file': sub_agenda_attach_item.get('attachment_file'),
                                            'attachment_name': sub_agenda_attach_item.get('attachment_name'),
                                        })
                else:
                    agenda_create = request.env['meeting.agenda'].create({
                        'meeting_id': post.get('meeting_id'),
                        'agenda_title_name': agenda_item.get('agenda_title_name'),
                        'agenda_no': agenda_item.get('agenda_no'),
                        'agenda_detail': agenda_item.get('agenda_detail'),
                        'partner_id': agenda_item.get('partner_id'),
                    })
                    sub_agenda_ids = agenda_item.get('sub_agenda_ids', [])
                    for sub_agenda_item in sub_agenda_ids:
                        if sub_agenda_item.get('sub_agenda_id'):
                            sub_agenda_update = request.env['meeting.sub.agenda'].search(
                                [('id', '=', sub_agenda_item.get('sub_agenda_id'))])
                            if sub_agenda_update:
                                sub_agenda_update.write({
                                    'agenda_id': agenda_item.get('agenda_id'),
                                    'sub_agenda_no': sub_agenda_item.get('sub_agenda_no'),
                                    'sub_agenda_name': sub_agenda_item.get('sub_agenda_name'),
                                    'sub_agenda_detail': sub_agenda_item.get('sub_agenda_detail'),
                                    'partner_id': sub_agenda_item.get('partner_id'),
                                    'vote_state': sub_agenda_item.get('vote_state')
                                })
                        else:
                            sub_agenda_create = request.env['meeting.sub.agenda'].create({
                                'agenda_id': agenda_create.id,
                                'sub_agenda_no': sub_agenda_item.get('sub_agenda_no'),
                                'sub_agenda_name': sub_agenda_item.get('sub_agenda_name'),
                                'sub_agenda_detail': sub_agenda_item.get('sub_agenda_detail'),
                                'partner_id': sub_agenda_item.get('partner_id'),
                            })
                            sub_agenda_attach_ids = sub_agenda_item.get('sub_agenda_attach_ids', [])
                            for sub_agenda_attach_item in sub_agenda_attach_ids:
                                if sub_agenda_attach_item.get('attach_id'):
                                    sub_agenda_attach_update = request.env['meeting.sub.agenda.attach'].search(
                                        [('id', '=', sub_agenda_attach_item.get('attach_id'))])
                                    if sub_agenda_attach_update:
                                        sub_agenda_attach_update.write({
                                            'sub_agenda_id': sub_agenda_item.get('sub_agenda_id'),
                                            'attach_user': sub_agenda_attach_item.get('attach_user'),
                                            'attach_type': sub_agenda_attach_item.get('attach_type'),
                                            'attach_flag': sub_agenda_attach_item.get('attach_flag'),
                                            'attachment_file': sub_agenda_attach_item.get('attachment_file'),
                                            'attachment_name': sub_agenda_attach_item.get('attachment_name'),
                                        })
                                else:
                                    request.env['meeting.sub.agenda.attach'].create({
                                        'sub_agenda_id': sub_agenda_create.id,
                                        'attach_user': sub_agenda_attach_item.get('attach_user'),
                                        'attach_type': sub_agenda_attach_item.get('attach_type'),
                                        'attach_flag': sub_agenda_attach_item.get('attach_flag'),
                                        'attachment_file': sub_agenda_attach_item.get('attachment_file'),
                                        'attachment_name': sub_agenda_attach_item.get('attachment_name'),
                                    })
        data = {'status': 200, 'response': "เพิ่มข้อมูลสำเร็จ", 'message': 'success'}
        return data

    # @http.route('/api/meeting/create_update_meeting_agenda', type='json', auth='user')
    # def create_update_meeting_agenda(self, **post):
    #     data_model = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
    #     set_sub_agenda_old = set()
    #     set_sub_agenda_attach_old = set()
    #     for rec_0 in data_model:
    #         for agenda_id in rec_0.agenda_ids.ids:
    #             set_sub_agenda_old.add(agenda_id)
    #             sub_agenda = request.env['meeting.agenda'].sudo().browse(agenda_id)
    #             for sub_agenda_id in sub_agenda.sub_agenda_ids.ids:
    #                 set_sub_agenda_attach_old.add(sub_agenda_id)
    #         agenda_append = []
    #         if post.get('agenda_ids'):  # เช็ค agenda ว่ามีข้อมูลหรือไม่
    #             agenda_data = json.loads(
    #                 json.dumps(post.get('agenda_ids')))  # ถ้ามีอข้อมูล ให้ทำการ โหลด ข้อทูลมาใส่
    #             for rec_1 in agenda_data:
    #                 if rec_1.get('agenda_id'):  # เช็ค agenda_id ว่าเป็น null หรือไม่
    #                     # เพิ่มส่วน อื่นๆ
    #                     sub_agenda_append = []
    #                     if rec_1.get('sub_agenda_ids'):  # เช็คว่า มี sub agenda หรือไม่
    #                         sub_agenda_data = json.loads(
    #                             json.dumps(rec_1.get('sub_agenda_ids')))  # ถ้ามีอข้อมูล ให้ทำการ โหลด ข้อทูลมาใส่
    #                         for rec_2 in sub_agenda_data:
    #                             if rec_2.get('sub_agenda_id'):  # เช็ค sub_agenda_id ว่าเป็น null หรือไม่
    #                                 sub_agenda_attach = []
    #                                 if rec_2.get('sub_agenda_attach_ids'):  # เช็คว่า มี sub attach หรือไม่
    #                                     agenda_attach_data = json.loads(json.dumps(rec_2.get(
    #                                         'sub_agenda_attach_ids')))  # ถ้ามีอข้อมูล ให้ทำการ โหลด ข้อทูลมาใส่
    #                                     for rec_3 in agenda_attach_data:
    #                                         if rec_3.get('attach_id'):  # เช็ค attach_id ว่าเป็น null หรือไม่
    #                                             sub_agenda_attach.append((1, rec_3.get('attach_id'), {
    #                                                 'sub_agenda_id': rec_2.get('sub_agenda_id'),
    #                                                 'attachment_file': rec_3.get('attachment_file'),
    #                                                 'attachment_name': rec_3.get('attachment_name'),
    #                                             }))
    #                                             request.env['meeting.sub.agenda'].sudo().search(
    #                                                 [('id', '=', rec_2.get('sub_agenda_id'))]).write(
    #                                                 {'sub_agenda_attach_ids': sub_agenda_attach, })
    #
    #                                 sub_agenda_append.append((1, rec_2.get('sub_agenda_id'), {
    #                                     'agenda_id': rec_1.get('agenda_id'),
    #                                     'sub_agenda_no': rec_2.get('sub_agenda_no'),
    #                                     'sub_agenda_name': rec_2.get('sub_agenda_name'),
    #                                     'sub_agenda_detail': rec_2.get('sub_agenda_detail'),
    #                                     'partner_id': rec_2.get('partner_id'),
    #                                 }))
    #                                 request.env['meeting.agenda'].sudo().search(
    #                                     [('id', '=', rec_1.get('agenda_id'))]).write({
    #                                     'agenda_title_name': rec_1.get('agenda_title_name'),
    #                                     'agenda_no': rec_1.get('agenda_no'),
    #                                     'agenda_detail': rec_1.get('agenda_detail'),
    #                                     'sub_agenda_ids': sub_agenda_append,
    #                                 })
    #                                 # จบ ส่วน อื่นๆ
    #                     agenda_append.append((1, rec_1.get('agenda_id'), {
    #                         'meeting_id': rec_0.id,
    #                         'agenda_title_name': rec_1.get('agenda_title_name'),
    #                         'agenda_no': rec_1.get('agenda_no'),
    #                         'agenda_detail': rec_1.get('agenda_detail'),
    #                         'partner_id': rec_1.get('partner_id'),
    #                     }))
    #                 else:
    #                     agenda_append.append((0, 0, {
    #                         'meeting_id': rec_0.id,
    #                         'agenda_title_name': rec_1.get('agenda_title_name'),
    #                         'agenda_no': rec_1.get('agenda_no'),
    #                         'agenda_detail': rec_1.get('agenda_detail'),
    #                         'partner_id': rec_1.get('partner_id'),
    #                     }))
    #             request.env['calendar.event'].sudo().search([('id', '=', rec_0.id)]).write({
    #                 'agenda_ids': agenda_append,
    #             })
    #     data_model_2 = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
    #     for rec_4 in data_model_2:
    #         for agenda_id in rec_4.agenda_ids.ids:
    #             if agenda_id not in set_sub_agenda_old:
    #                 sub_agenda_append = []
    #                 if post.get('agenda_ids'):  # เช็ค agenda ว่ามีข้อมูลหรือไม่
    #                     agenda_data = json.loads(
    #                         json.dumps(post.get('agenda_ids')))  # ถ้ามีอข้อมูล ให้ทำการ โหลด ข้อทูลมาใส่
    #                     for rec_1 in agenda_data:
    #                         if rec_1.get('sub_agenda_ids'):  # เช็คว่า มี sub agenda หรือไม่
    #                             sub_agenda_data = json.loads(json.dumps(
    #                                 rec_1.get('sub_agenda_ids')))  # ถ้ามีอข้อมูล ให้ทำการ โหลด ข้อทูลมาใส่
    #                             for rec_2 in sub_agenda_data:
    #                                 sub_agenda_append.append((0, 0, {
    #                                     'agenda_id': agenda_id,
    #                                     'sub_agenda_no': rec_2.get('sub_agenda_no'),
    #                                     'sub_agenda_name': rec_2.get('sub_agenda_name'),
    #                                     'sub_agenda_detail': rec_2.get('sub_agenda_detail'),
    #                                     'partner_id': rec_2.get('partner_id'),
    #                                 }))
    #                 request.env['meeting.agenda'].sudo().search(
    #                     [('id', '=', agenda_id)]).write({'sub_agenda_ids': sub_agenda_append})
    #     data_model_3 = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
    #     for rec_5 in data_model_3:
    #         for agenda_id in rec_5.agenda_ids.ids:
    #             if agenda_id not in set_sub_agenda_old:
    #                 sub_agenda = request.env['meeting.agenda'].sudo().browse(agenda_id)
    #                 for sub_agenda_id in sub_agenda.sub_agenda_ids.ids:
    #                     if sub_agenda_id not in set_sub_agenda_attach_old:
    #                         sub_agenda_attach = []
    #                         if post.get('agenda_ids'):  # เช็ค agenda ว่ามีข้อมูลหรือไม่
    #                             agenda_data = json.loads(
    #                                 json.dumps(post.get('agenda_ids')))  # ถ้ามีอข้อมูล ให้ทำการ โหลด ข้อทูลมาใส่
    #                             for rec_1 in agenda_data:
    #                                 if rec_1.get('sub_agenda_ids'):  # เช็คว่า มี sub agenda หรือไม่
    #                                     sub_agenda_data = json.loads(json.dumps(
    #                                         rec_1.get('sub_agenda_ids')))  # ถ้ามีอข้อมูล ให้ทำการ โหลด ข้อทูลมาใส่
    #                                     for rec_2 in sub_agenda_data:
    #                                         if rec_2.get('sub_agenda_attach_ids'):  # เช็คว่า มี sub attach หรือไม่
    #                                             agenda_attach_data = json.loads(json.dumps(rec_2.get(
    #                                                 'sub_agenda_attach_ids')))  # ถ้ามีอข้อมูล ให้ทำการ โหลด ข้อทูลมาใส่
    #                                             for rec_3 in agenda_attach_data:
    #                                                 sub_agenda_attach.append((0, 0, {
    #                                                     'sub_agenda_id': sub_agenda_id,
    #                                                     'attachment_file': rec_3.get('attachment_file'),
    #                                                     'attachment_name': rec_3.get('attachment_name'),
    #                                                 }))
    #                                             request.env['meeting.sub.agenda'].sudo().search(
    #                                                 [('id', '=', sub_agenda_id)]).write(
    #                                                 {'sub_agenda_attach_ids': sub_agenda_attach, })
    #
    #     data = {'status': 200, 'response': data_model.id, 'message': 'success'}
    #     return data

    # @http.route('/api/meeting/create_update_meeting_agenda', type='json', auth='user')
    # def create_update_meeting_agenda(self, **post):
    #     data_model = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
    #     for rec_0 in data_model:
    #         agenda_append = []
    #         if post.get('agenda_ids'):  # เช็ค agenda ว่ามีข้อมูลหรือไม่
    #             agenda_data = json.loads(json.dumps(post.get('agenda_ids')))  # ถ้ามีอข้อมูล ให้ทำการ โหลด ข้อทูลมาใส่
    #             for rec_1 in agenda_data:
    #                 if rec_1.get('agenda_id'):  # เช็ค agenda_id ว่าเป็น null หรือไม่
    #                     sub_agenda_append = []
    #                     if rec_1.get('sub_agenda_ids'):  # เช็คว่า มี sub agenda หรือไม่
    #                         sub_agenda_data = json.loads(
    #                             json.dumps(rec_1.get('sub_agenda_ids')))  # ถ้ามีอข้อมูล ให้ทำการ โหลด ข้อทูลมาใส่
    #                         for rec_2 in sub_agenda_data:
    #                             if rec_2.get('sub_agenda_id'):  # เช็ค sub_agenda_id ว่าเป็น null หรือไม่
    #                                 sub_agenda_attach = []
    #                                 if rec_2.get('sub_agenda_attach_ids'):  # เช็คว่า มี sub attach หรือไม่
    #                                     agenda_attach_data = json.loads(json.dumps(rec_2.get(
    #                                         'sub_agenda_attach_ids')))  # ถ้ามีอข้อมูล ให้ทำการ โหลด ข้อทูลมาใส่
    #                                     for rec_3 in agenda_attach_data:
    #                                         if rec_3.get('attach_id'):  # เช็ค attach_id ว่าเป็น null หรือไม่
    #                                             sub_agenda_attach.append((1, rec_3.get('attach_id'), {
    #                                                 'sub_agenda_id': rec_2.get('sub_agenda_id'),
    #                                                 'attachment_file': rec_3.get('attachment_file'),
    #                                                 'attachment_name': rec_3.get('attachment_name'),
    #                                             }))
    #                                         else:
    #                                             sub_agenda_attach.append((0, 0, {
    #                                                 'sub_agenda_id': rec_2.get('sub_agenda_id'),
    #                                                 'attachment_file': rec_3.get('attachment_file'),
    #                                                 'attachment_name': rec_3.get('attachment_name'),
    #                                             }))
    #                                     request.env['meeting.sub.agenda'].sudo().search(
    #                                         [('id', '=', rec_2.get('sub_agenda_id'))]).write(
    #                                         {'sub_agenda_attach_ids': sub_agenda_attach, })
    #
    #                                 sub_agenda_append.append((1, rec_2.get('sub_agenda_id'), {
    #                                     'agenda_id': rec_1.get('agenda_id'),
    #                                     'sub_agenda_no': rec_2.get('sub_agenda_no'),
    #                                     'sub_agenda_name': rec_2.get('sub_agenda_name'),
    #                                     'sub_agenda_detail': rec_2.get('sub_agenda_detail'),
    #                                     'partner_id': rec_2.get('partner_id'),
    #                                 }))
    #                             else:
    #                                 sub_agenda_append.append((0, 0, {
    #                                     'agenda_id': rec_1.get('agenda_id'),
    #                                     'sub_agenda_no': rec_2.get('sub_agenda_no'),
    #                                     'sub_agenda_name': rec_2.get('sub_agenda_name'),
    #                                     'sub_agenda_detail': rec_2.get('sub_agenda_detail'),
    #                                     'partner_id': rec_2.get('partner_id'),
    #                                 }))
    #                         request.env['meeting.agenda'].sudo().search([('id', '=', rec_1.get('agenda_id'))]).write({
    #                             'agenda_title_name': rec_1.get('agenda_title_name'),
    #                             'agenda_no': rec_1.get('agenda_no'),
    #                             'agenda_detail': rec_1.get('agenda_detail'),
    #                             'sub_agenda_ids': sub_agenda_append,
    #                         })
    #
    #                     agenda_append.append((1, rec_1.get('agenda_id'), {
    #                         'meeting_id': rec_0.id,
    #                         'agenda_title_name': rec_1.get('agenda_title_name'),
    #                         'agenda_no': rec_1.get('agenda_no'),
    #                         'agenda_detail': rec_1.get('agenda_detail'),
    #                         'partner_id': rec_1.get('partner_id'),
    #                     }))
    #                 else:
    #                     agenda_append.append((0, 0, {
    #                         'meeting_id': rec_0.id,
    #                         'agenda_title_name': rec_1.get('agenda_title_name'),
    #                         'agenda_no': rec_1.get('agenda_no'),
    #                         'agenda_detail': rec_1.get('agenda_detail'),
    #                         'partner_id': rec_1.get('partner_id'),
    #                     }))
    #             request.env['calendar.event'].sudo().search([('id', '=', rec_0.id)]).write({
    #                 'agenda_ids': agenda_append,
    #             })
    #     data = {'status': 200, 'response': data_model.id, 'message': 'success'}
    #     return data

    @http.route('/api/meeting/delete_meeting_agenda', type='json', auth='user')
    def delete_meeting_agenda(self, **post):
        data_model = request.env['calendar.event'].search([('id', '=', post.get('meeting_id'))])
        if data_model and post.get('agenda_id'):
            agenda_id_to_unlink = post.get('agenda_id')
            for rec in data_model:
                agenda_record = rec.agenda_ids.filtered(lambda r: r.id == agenda_id_to_unlink)
                if agenda_record:
                    agenda_record.unlink()
                    data = {'status': 200, 'response': 'Delete success', 'message': 'success'}
                    return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_meeting_sub_agenda', type='json', auth='user')
    def delete_meeting_sub_agenda(self, **post):
        data_model = request.env['calendar.event'].search([('id', '=', post.get('meeting_id'))])
        if data_model and post.get('agenda_id'):
            agenda_id = post.get('agenda_id')
            sub_agenda_id = post.get('sub_agenda_id')
            for rec_0 in data_model:
                agenda_record = rec_0.agenda_ids.filtered(lambda r: r.id == agenda_id)
                for rec_1 in agenda_record:
                    sub_agenda_record = rec_1.sub_agenda_ids.filtered(lambda r: r.id == sub_agenda_id)
                    if sub_agenda_record:
                        sub_agenda_record.unlink()
                        data = {'status': 200, 'response': 'Delete success', 'message': 'success'}
                        return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'success'}
            return data

        # data_model = request.env['calendar.event'].search([('id', '=', post.get('meeting_id'))])
        # if data_model:
        #     if post.get('agenda_id'):
        #         agenda_id = post.get('agenda_id')
        #     if data_model:
        #         if not agenda_id:
        #             return
        #         for rec in data_model:
        #             for agenda in agenda_id:
        #                 rec.agenda_ids.filtered(lambda r: r.id == agenda).unlink()
        #     data = {'status': 200, 'response': 'Delete success', 'message': 'success'}
        #     return data
        # else:
        #     data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'success'}
        #     return data

    @http.route('/api/meeting/create_update_meeting_services', type='json', auth='user')
    def create_update_meeting_services(self, **post):
        data_model = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
        if data_model:
            for rec in data_model:
                service_ids_to_remove = rec.service_ids.ids
                if service_ids_to_remove:
                    rec.service_ids.unlink()
        if data_model:
            service_list = []
            if post.get('service_ids'):
                service_data = json.loads(json.dumps(post.get('service_ids')))
                for rec in service_data:
                    if rec['mt_service_id']:
                        service_list.append((1, rec['mt_service_id'], {
                            'meeting_id': post.get('meeting_id'),
                            'service_id': rec['service_id'],
                            'qty_morning': rec['qty_morning'],
                            'qty_afternoon': rec['qty_afternoon'],
                            'service_qty': rec['service_qty'],
                        }))
                    else:
                        service_list.append((0, 0, {
                            'meeting_id': post.get('meeting_id'),
                            'service_id': rec['service_id'],
                            'qty_morning': rec['qty_morning'],
                            'qty_afternoon': rec['qty_afternoon'],
                            'service_qty': rec['service_qty'],
                        }))

            data_model.write({
                'service_ids': service_list,
            })

        data = {'status': 200, 'response': data_model.id, 'message': 'success'}
        return data

    # API - อัพเดทสถานะ การประชุม
    @http.route('/api/meeting/update_meeting_status', type='json', auth='user')
    def update_meeting_status(self, **post):
        data_model = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
        if data_model:
            data_model.write({
                'meeting_state': post.get('status'),
                'meeting_summary': post.get('meeting_summary'),
                'cancel_reason': post.get('cancel_reason'),
                'cancel_description': post.get('cancel_description'),
            })
            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'success'}
            return data

    # API - อัพเดทรายการ จองห้องประชุม
    @http.route('/api/meeting/update_meeting', type='json', auth='user')
    def update_meeting(self, **post):
        data_model = request.env['calendar.event'].search([('id', '=', post.get('meeting_id'))])
        if data_model:
            ICT = timezone('Asia/Bangkok')
            duration = float(post.get('duration'))
            start_datetime = datetime.datetime.strptime(post.get('start_datetime'), DEFAULT_SERVER_DATETIME_FORMAT)
            start = ICT.localize(start_datetime).astimezone(timezone('UTC')).replace(tzinfo=None)
            end_date_time = start_datetime + timedelta(hours=duration)
            stop = ICT.localize(end_date_time).astimezone(timezone('UTC')).replace(tzinfo=None)
            data_model.write({
                'name': post.get('name'),
                ### Add fields ###
                'description': post.get('description', data_model.description),
                'join_inside': post.get('join_inside', data_model.join_inside),
                'join_outside': post.get('join_outside', data_model.join_outside),
                'president_id': post.get('president_id', data_model.president_id),
                'contact_person': post.get('contact_person', data_model.contact_person),
                'contact_number': post.get('contact_number', data_model.contact_number),
                'room_id': post.get('room_id', data_model.room_id.id),
                'meeting_type_id': post.get('meeting_type_id', data_model.meeting_type_id.id),
                'start': start,
                'stop': stop,
                'start_date': start,
                'end_date': stop,
                'meet_name': post.get('meet_name'),
                'meet_url': post.get('meet_url'),
                'meet_number': post.get('meet_number'),
                'meet_passcode': post.get('meet_passcode'),
                'requester_id': post.get('requester_id'),
                'meeting_root_type': post.get('meeting_root_type'),

            })

            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/create_update_meeting_attach', type='json', auth='user')
    def create_update_meeting_attach(self, **post):
        data_model = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
        if data_model:
            attach_list = []
            if post.get('attach_ids'):
                attach_data = json.loads(json.dumps(post.get('attach_ids')))
                for rec in attach_data:
                    if rec['attach_id']:
                        attach_list.append((1, rec['attach_id'], {
                            'meeting_id': post.get('meeting_id'),
                            'attach_user': rec.get('attach_user'),
                            'attach_type': rec.get('attach_type'),
                            'attach_flag': rec.get('attach_flag'),
                            'attachment_note': rec['attachment_note'],
                            'attachment_file': rec['attachment_file'],
                            'attachment_name': rec['attachment_name'],
                            'attachment_import_date': rec['attachment_import_date'],
                        }))
                    else:
                        attach_list.append((0, 0, {
                            'meeting_id': post.get('meeting_id'),
                            'attachment_note': rec['attachment_note'],
                            'attach_user': rec.get('attach_user'),
                            'attach_type': rec.get('attach_type'),
                            'attach_flag': rec.get('attach_flag'),
                            'attachment_file': rec['attachment_file'],
                            'attachment_name': rec['attachment_name'],
                            'attachment_import_date': rec['attachment_import_date'],
                        }))

            data_model.write({
                'attach_ids': attach_list,
            })

        data = {'status': 200, 'response': data_model.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/update_meeting_attendee', type='json', auth='user')
    def update_meeting_attendee(self, **post):
        data_model = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
        if data_model:
            for rec in data_model:
                attendee_ids_to_remove = rec.attendee_ids.ids
                if attendee_ids_to_remove:
                    rec.attendee_ids.unlink()
        if data_model:
            attendee_list = []
            if post.get('attendee_ids'):
                attendee_data = json.loads(json.dumps(post.get('attendee_ids')))
                for rec in attendee_data:
                    if rec['attendee_id']:
                        attendee_list.append((1, rec['attendee_id'], {
                            'event_id': post.get('meeting_id'),
                            'partner_id': rec.get('partner_id'),
                            'position_id': rec.get('position_id'),
                            'vote_type': rec.get('vote_type')
                        }))
                    else:
                        attendee_list.append((0, 0, {
                            'event_id': post.get('meeting_id'),
                            'partner_id': rec.get('partner_id'),
                            'position_id': rec.get('position_id'),
                            'vote_type': rec.get('vote_type')
                        }))

            data_model.write({
                'attendee_ids': attendee_list,
            })
        data = {'status': 200, 'response': data_model.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/check_meeting_list_available', type='json', auth='none')
    def check_meeting_list_available(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')

        local_start_datetime = datetime.datetime.strptime(post.get('first_start_datetime'),
                                                          DEFAULT_SERVER_DATETIME_FORMAT)
        utc_dt = ICT.localize(local_start_datetime, is_dst=None).astimezone(timezone('UTC'))
        start_datetime = utc_dt.replace(tzinfo=None)

        local_end_date_time = datetime.datetime.strptime(post.get('first_end_datetime'), DEFAULT_SERVER_DATETIME_FORMAT)
        utc_dt = ICT.localize(local_end_date_time, is_dst=None).astimezone(timezone('UTC'))
        end_date_time = utc_dt.replace(tzinfo=None)

        final_date = datetime.datetime.strptime(post.get('final_date'), DEFAULT_SERVER_DATE_FORMAT).date()

        chk_state = "AND meeting_state != 'draft' AND meeting_state != 'cancel'"
        if post.get('all_state') == True:
            chk_state = ""

        chk_not_meeting_id = ""
        if post.get('not_meeting_id'):
            chk_not_meeting_id = "AND id != {}".format(post.get('not_meeting_id'))

        pass_all = True
        data_rec = []
        while local_start_datetime.date() <= final_date:
            # Query Check
            # -- SELECT id, room_id, meeting_state, start_datetime, end_date_time FROM public.calendar_event
            query_chk = """
                    SELECT id FROM public.calendar_event
                    WHERE active=true AND room_id = %(room_id)s {chk_state} {chk_not_meeting_id}
                    AND ((start_datetime <= %(start_datetime)s AND end_date_time >= %(end_date_time)s)
                    OR (start_datetime >= %(start_datetime)s AND start_datetime < %(end_date_time)s
                    OR end_date_time > %(start_datetime)s AND end_date_time <= %(end_date_time)s))
                    ORDER BY id DESC;
                """.format(chk_state=chk_state, chk_not_meeting_id=chk_not_meeting_id)
            request.cr.execute(query_chk, {
                'room_id': post.get('room_id'),
                'start_datetime': start_datetime,
                'end_date_time': end_date_time,
            })

            ids = [column for column, in request.cr.fetchall()]
            if len(ids):
                available = False
                pass_all = False
                vals = {
                    'start_datetime': local_start_datetime,
                    'end_datetime': local_end_date_time,
                    'available_status': available,
                    'available_name': "ว่าง" if available else "ไม่ว่าง",
                }
                data_rec.append(vals)
            else:
                available = True
                vals = {
                    'start_datetime': local_start_datetime,
                    'end_datetime': local_end_date_time,
                    'available_status': available,
                    'available_name': "ว่าง" if available else "ไม่ว่าง",
                }
                data_rec.append(vals)

            local_start_datetime = local_start_datetime + timedelta(days=1)
            start_datetime = start_datetime + timedelta(days=1)
            local_end_date_time = local_end_date_time + timedelta(days=1)
            end_date_time = end_date_time + timedelta(days=1)

        data_response = {
            "start_date": datetime.datetime.strptime(post.get('first_start_datetime'),
                                                     DEFAULT_SERVER_DATETIME_FORMAT).date(),
            "final_date": final_date,
            "day_count": len(data_rec),
            "pass_all": pass_all,
            "list_data": data_rec
        }

        data = {'status': 200, 'response': data_response, 'message': 'success'}
        return data

    @http.route('/api/meeting/get_meeting', type='json', auth='none')
    def get_meeting(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')
        domain = []
        if post.get('meeting_state'):
            domain.append(('meeting_state', '=', post.get('meeting_state')))
        if post.get('room_id'):
            domain.append(('room_id', '=', post.get('room_id')))
        if post.get('requester_id'):
            domain.append(('requester_id', '=', post.get('requester_id')))
        if post.get('month'):
            current_date = fields.Datetime.now().astimezone(timezone('Asia/Bangkok'))
            year = str(current_date.year)
            month = str(current_date.month).zfill(2)
            day = "01"

            if post.get('year'):
                year = post.get('year')
            if post.get('month'):
                month = post.get('month')

            start_date_str = "{}/{}/{}".format(day, month, year)
            start_date = datetime.datetime.strptime(start_date_str, "%d/%m/%Y").date()
            start_datetime = datetime.datetime.combine(start_date, datetime.time(0, 0, 0))
            start_datetime = timezone('Asia/Bangkok').localize(start_datetime, is_dst=None).astimezone(timezone('UTC'))

            end_date = datetime.datetime(start_date.year, start_date.month,
                                         calendar.monthrange(start_date.year, start_date.month)[1]).date()
            end_datetime = datetime.datetime.combine(end_date, datetime.time(23, 59, 59))
            end_datetime = timezone('Asia/Bangkok').localize(end_datetime, is_dst=None).astimezone(timezone('UTC'))

            domain.append(('start_date', '>=', start_datetime))
            domain.append(('start_date', '<=', end_datetime))

        if domain:
            meeting = request.env['calendar.event'].sudo().search(domain)
        else:
            meeting = request.env['calendar.event'].sudo().search([])
        if meeting:
            data_rec = []
            for rec in meeting:
                vals = {
                    'meeting_id': rec.id,
                    'meeting_state_code': rec.meeting_state,
                    'meeting_state': dict(rec._fields['meeting_state'].selection).get(rec.meeting_state),
                    'meeting_name': rec.name,
                    ### Add fields ###
                    'alarm': rec.alarm_ids.ids or None,
                    'join_inside': rec.join_inside or None,
                    'join_outside': rec.join_outside or None,
                    'join_count': rec.join_count or None,
                    'president_id': rec.president_id.id or None,
                    'president_name': rec.president_id.display_name or None,
                    'contact_person': rec.contact_person or None,
                    'contact_number': rec.contact_number or None,

                    'meet_name': rec.meet_name or None,
                    'meet_url': rec.meet_url or None,
                    'meet_passcode': rec.meet_passcode or None,
                    'meet_number': rec.meet_number or None,
                    'meeting_root_type': rec.meeting_root_type or None,

                    'room_id': rec.room_id.id or None,
                    'room_name': rec.room_id.room_name or None,
                    'room_type_code': rec.room_id.room_type or None,
                    'room_type': dict(rec.room_id._fields['room_type'].selection).get(rec.room_id.room_type) or None,
                    'room_address': "%s ชั้น %s %s" % (
                        rec.room_id.room_name, str(rec.room_id.floor), (rec.room_id.room_address or "")),
                    'start': rec.start.astimezone(ICT) if rec.start else None,
                    'stop': rec.stop.astimezone(ICT) if rec.stop else None,
                    'start_datetime': rec.start.astimezone(ICT) if rec.start else None,
                    'end_datetime': rec.stop.astimezone(ICT) if rec.stop else None,
                    'start_date': rec.start.astimezone(ICT) if rec.start else None,
                    'end_date': rec.stop.astimezone(ICT) if rec.stop else None,
                    'description': rec.description or None,
                    'duration': rec.duration,
                    'requester_id': rec.partner_id.id,
                    'requester_name': rec.partner_id.display_name,
                    'create_date': rec.create_date.astimezone(ICT) if rec.create_date else None,
                    'meeting_type_id': rec.meeting_type_id.id or None,
                    'meeting_type_name': rec.meeting_type_id.type_name or None,
                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_meeting_by_id', type='json', auth='none')
    def get_meeting_by_id(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')
        meeting = request.env['calendar.event'].sudo().search([('id', '=', post.get('id'))])
        if meeting:
            data_rec = []
            for rec in meeting:
                vals = {
                    'meeting_id': rec.id,
                    'meeting_state_code': rec.meeting_state,
                    'meeting_state': dict(rec._fields['meeting_state'].selection).get(rec.meeting_state),
                    'meeting_name': rec.name,
                    ### Add fields ###
                    'alarm': rec.alarm_ids.ids or None,
                    'join_inside': rec.join_inside or None,
                    'join_outside': rec.join_outside or None,
                    'join_count': rec.join_count or None,
                    'president_id': rec.president_id.id or None,
                    'president_name': rec.president_id.display_name or None,
                    'contact_person': rec.contact_person or None,
                    'contact_number': rec.contact_number or None,

                    'meet_name': rec.meet_name or None,
                    'meet_url': rec.meet_url or None,
                    'meet_passcode': rec.meet_passcode or None,
                    'meet_number': rec.meet_number or None,
                    'meeting_root_type': rec.meeting_root_type or None,

                    'room_id': rec.room_id.id or None,
                    'room_name': rec.room_id.room_name or None,
                    'room_type_code': rec.room_id.room_type or None,
                    'room_type': dict(rec.room_id._fields['room_type'].selection).get(rec.room_id.room_type) or None,
                    'room_address': "%s ชั้น %s %s" % (
                        rec.room_id.room_name, str(rec.room_id.floor), (rec.room_id.room_address or "")),
                    'start': rec.start.astimezone(ICT) if rec.start else None,
                    'stop': rec.stop.astimezone(ICT) if rec.stop else None,
                    'start_datetime': rec.start.astimezone(ICT) if rec.start else None,
                    'end_datetime': rec.stop.astimezone(ICT) if rec.stop else None,
                    'start_date': rec.start.astimezone(ICT) if rec.start else None,
                    'end_date': rec.stop.astimezone(ICT) if rec.stop else None,
                    'description': rec.description or None,
                    'duration': rec.duration,
                    'requester_id': rec.partner_id.id or None,
                    'requester_name': rec.partner_id.display_name or None,

                    'cancel_reason': rec.cancel_reason or None,
                    'cancel_description': rec.cancel_description or None,

                    'create_date': rec.create_date.astimezone(ICT) if rec.create_date else None,
                    'meeting_type_id': rec.meeting_type_id.id or None,
                    'meeting_type_name': rec.meeting_type_id.type_name or None,
                    'meeting_summary': rec.meeting_summary or None,

                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_meeting_attach_list', type='json', auth='none')
    def get_meeting_attach_list(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['meeting.attach'].sudo().search([('meeting_id', '=', post.get('meeting_id'))])
        if data_info:
            la_tz = timezone('Asia/Bangkok')
            attach_list = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'attachment_note': rec.attachment_note or None,
                    'attachment_name': rec.attachment_name or None,
                    'attach_user': rec.attach_user or None,
                    'attach_type': rec.attach_type or None,
                    'attach_flag': rec.attach_flag or None,
                    'attachment_file': rec.attachment_file or None,
                    'attachment_import_date': rec.attachment_import_date.astimezone(
                        la_tz) if rec.attachment_import_date else None,
                }
                attach_list.append(vals)

            data_rec = {
                'meeting_id': post.get('meeting_id'),
                'attach_list': attach_list
            }

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล รายการเอกสาร', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_meeting_attach_file', type='json', auth='user')
    def get_meeting_attach_file(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['meeting.attach'].search([
            ('meeting_id', '=', post.get('meeting_id')),
            ('id', '=', post.get('id'))], limit=1)
        if data_info:
            la_tz = timezone('Asia/Bangkok')
            data_rec = {
                'meeting_id': data_info.meeting_id.id,
                'id': data_info.id,
                'attachment_note': data_info.attachment_note or None,
                'attach_user': data_info.attach_user or None,
                'attach_type': data_info.attach_type or None,
                'attach_flag': data_info.attach_flag or None,
                'attachment_file': data_info.attachment_file,
                'attachment_name': data_info.attachment_name or None,
                'attachment_import_date': data_info.attachment_import_date.astimezone(
                    la_tz) if data_info.attachment_import_date else None,
            }

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลเอกสาร', 'message': 'success'}
            return data

    @http.route('/api/meeting/final_call_meeting_api', type='json', auth='user')
    def final_call_meeting_api(self, **post):
        meeting = request.env['calendar.event'].search([('id', '=', post.get('meeting_id'))])
        if meeting:
            if post.get('final_date'):
                final_date = datetime.datetime.strptime(post.get('final_date'), DEFAULT_SERVER_DATE_FORMAT).date()
                all_recurrent = meeting.create_meeting_by_recurrent(final_date)
            else:
                all_recurrent = meeting

            if all_recurrent:
                ICT = timezone('Asia/Bangkok')
                data_rec = []
                for rec in all_recurrent:
                    vals = {
                        'meeting_id': rec.id,
                        'meeting_state_code': rec.meeting_state,
                        'meeting_state': dict(rec._fields['meeting_state'].selection).get(rec.meeting_state),
                        'meeting_name': rec.name,
                        ### Add fields ###
                        'alarm': rec.alarm_ids.ids or None,
                        'join_inside': rec.join_inside or None,
                        'join_outside': rec.join_outside or None,
                        'join_count': rec.join_count or None,
                        'president_id': rec.president_id.id or None,
                        'president_name': rec.president_id.display_name or None,
                        'contact_person': rec.contact_person or None,
                        'contact_number': rec.contact_number or None,

                        'room_id': rec.room_id.id or None,
                        'room_name': rec.room_id.room_name or None,
                        'room_type_code': rec.room_id.room_type or None,
                        'room_type': dict(rec.room_id._fields['room_type'].selection).get(
                            rec.room_id.room_type) or None,
                        'room_address': "%s ชั้น %s %s" % (
                            rec.room_id.room_name, str(rec.room_id.floor), (rec.room_id.room_address or "")),
                        'description': rec.description or None,
                        'start': rec.start.astimezone(ICT) if rec.start else None,
                        'stop': rec.stop.astimezone(ICT) if rec.stop else None,
                        'duration': rec.duration,
                        'requester_id': rec.partner_id.id,
                        'requester_name': rec.partner_id.display_name,
                        'meeting_summary': rec.meeting_summary or None,
                        'cancel_reason': rec.cancel_reason or None,
                        'cancel_description': rec.cancel_description or None,
                        'create_date': rec.create_date.astimezone(ICT) if rec.create_date else None,
                    }
                    data_rec.append(vals)
                data = {'status': 200, 'response': data_rec, 'message': 'success'}
                return data
            else:
                data = {'status': 500, 'response': 'ไม่สามารถจองห้องประชุม/จองแบบหลายวันได้ (ห้องประชุมไม่ว่าง)',
                        'message': 'success'}
                return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'success'}
            return data

    # API - ตรวจสอบสถานะ จองห้องประชุม แบบหลายวัน
    @http.route('/api/meeting/check_meeting_list_available', type='json', auth='none')
    def check_meeting_list_available(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')
        room_id = post.get('room_id')
        start_datetime = post.get('start_datetime')
        end_datetime = post.get('end_date_time')
        # สร้าง domain สำหรับการค้นหา
        domain = [
            ("room_id", "=", room_id),
            ("start", ">=", start_datetime),
            ("stop", "<=", end_datetime),
        ]
        # ทำการค้นหา meeting จาก domain ที่กำหนด
        meeting = request.env['calendar.event'].sudo().search(domain)
        if meeting:
            data_rec = []
            for rec in meeting:
                vals = {
                    'meeting_id': rec.id,
                    'meeting_state_code': rec.meeting_state,
                    'meeting_state': dict(rec._fields['meeting_state'].selection).get(rec.meeting_state),
                    'meeting_name': rec.name,

                    'alarm': rec.alarm_ids.ids or None,
                    'join_inside': rec.join_inside or None,
                    'join_outside': rec.join_outside or None,
                    'join_count': rec.join_count or None,
                    'president_id': rec.president_id.id or None,
                    'president_name': rec.president_id.display_name or None,
                    'contact_person': rec.contact_person or None,
                    'contact_number': rec.contact_number or None,

                    'room_id': rec.room_id.id or None,
                    'room_name': rec.room_id.room_name or None,
                    'room_type_code': rec.room_id.room_type or None,
                    'room_type': dict(rec.room_id._fields['room_type'].selection).get(rec.room_id.room_type) or None,
                    'room_address': "%s ชั้น %s %s" % (
                        rec.room_id.room_name, str(rec.room_id.floor), (rec.room_id.room_address or "")),
                    'start': rec.start.astimezone(ICT) if rec.start else None,
                    'stop': rec.stop.astimezone(ICT) if rec.stop else None,
                    'description': rec.description or None,
                    'duration': rec.duration,
                    'requester_id': rec.partner_id.id,
                    'requester_name': rec.partner_id.display_name,
                    'create_date': rec.create_date.astimezone(ICT) if rec.create_date else None,
                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'success'}
            return data

    # API - ตรวจสอบการใช้งานห้องประชุม ตามช่วงเวลา
    @http.route('/api/meeting/get_meeting_check_true', type='json', auth='none')
    def get_meeting_check_true(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')
        room_id = post.get('room_id')
        start_datetime = post.get('first_start_datetime')
        end_datetime = post.get('first_end_datetime')

        not_meeting_id = post.get('not_meeting_id')
        # สร้าง domain สำหรับการค้นหา
        domain = [
            ("room_id", "=", room_id),
            "|",
            "&",
            ("start", ">=", start_datetime),
            ("start", "<=", end_datetime),
            "&",
            ("stop", ">=", start_datetime),
            ("stop", "<=", end_datetime),
        ]
        # ทำการค้นหา meeting จาก domain ที่กำหนด
        meeting = request.env['calendar.event'].sudo().search(domain)

        if meeting:
            data_rec = []
            for rec in meeting:
                if not_meeting_id != rec.id:
                    vals = {
                        'meeting_id': rec.id,
                        'meeting_state_code': rec.meeting_state,
                        'meeting_state': dict(rec._fields['meeting_state'].selection).get(rec.meeting_state),
                        'meeting_name': rec.name,

                        'alarm': rec.alarm_ids.ids or None,
                        'join_inside': rec.join_inside or None,
                        'join_outside': rec.join_outside or None,
                        'join_count': rec.join_count or None,
                        'president_id': rec.president_id.id or None,
                        'president_name': rec.president_id.display_name or None,
                        'contact_person': rec.contact_person or None,
                        'contact_number': rec.contact_number or None,

                        'room_id': rec.room_id.id or None,
                        'room_name': rec.room_id.room_name or None,
                        'room_type_code': rec.room_id.room_type or None,
                        'room_type': dict(rec.room_id._fields['room_type'].selection).get(
                            rec.room_id.room_type) or None,
                        'room_address': "%s ชั้น %s %s" % (
                            rec.room_id.room_name, str(rec.room_id.floor), (rec.room_id.room_address or "")),
                        'start': rec.start.astimezone(ICT) if rec.start else None,
                        'stop': rec.stop.astimezone(ICT) if rec.stop else None,
                        'description': rec.description or None,
                        'duration': rec.duration,
                        'requester_id': rec.partner_id.id,
                        'requester_name': rec.partner_id.display_name,
                        'create_date': rec.create_date.astimezone(ICT) if rec.create_date else None,
                    }
                    data_rec.append(vals)
                else:
                    data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'success'}
                    return data
            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'success'}
            return data

    # API - ดึงรายการ ผู้เข้าร่วมประชุม
    @http.route('/api/meeting/get_meeting_attendee', type='json', auth='none')
    def get_meeting_attendee(self, **post):
        request.session.db = post.get('db')
        meeting = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
        if meeting:
            attendee_list = []
            for attendee in meeting.attendee_ids:
                vals = {
                    'attendee_id': attendee.id,
                    'partner_id': attendee.partner_id.id,
                    'name': attendee.name,
                    'email': attendee.email or None,
                    'phone': attendee.phone or None,
                    'position_id': attendee.position_id.id or None,
                    'position_name': attendee.position_id.name or None,
                    'vote_type': attendee.vote_type or None,
                }
                attendee_list.append(vals)

            data_rec = {
                'meeting_id': meeting.id,
                'partner_list': attendee_list
            }

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_user_confirm_meeting_list', type='json', auth='user')
    def get_user_confirm_meeting_list(self, **post):
        attendees = request.env['calendar.attendee'].sudo().search([
            ('partner_id', '=', post.get('partner_id')),
        ])
        if attendees:
            data_rec = []
            for record1 in attendees:
                # print(record1.event_id.id)
                meetings = request.env['calendar.event'].sudo().search([('id', '=', record1.event_id.id)])
                for record in meetings:
                    vals = {
                        'attendee_id': record1.id,
                        'meeting_id': record.id,
                        'meeting_name': record.name,
                        'room': record.room_id.room_name,
                        'room_address': "%s ชั้น %s %s" % (
                            record.room_id.room_name, str(record.room_id.floor), (record.room_id.room_address or "")),
                        'description': record.description,
                        'create_date': record.create_date,
                        'start': record.start,
                        'stop': record.stop,
                        'state_text': dict(record1._fields['state'].selection).get(record1.state),
                        'state': record1.state,
                        'vote_type': record1.vote_type or None
                    }
                    data_rec.append(vals)
            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data

        # meetings = request.env['calendar.event'].sudo().search([])
        # if meetings:
        #     data_rec = []
        #     for record in meetings:
        #         attendees = request.env['calendar.attendee'].sudo().search([
        #             ('partner_id', '=', post.get('partner_id')),
        #         ], limit=1)
        #         if attendees:
        #             vals = {
        #                 'attendee_id': attendees.id,
        #                 'meeting_id': record.id,
        #                 'meeting_name': record.name,
        #                 'room': record.room_id.room_name,
        #                 'room_address': "%s ชั้น %s %s" % (
        #                     record.room_id.room_name, str(record.room_id.floor), (record.room_id.room_address or "")),
        #                 'description': record.description,
        #                 'start_datetime': record.start_datetime,
        #                 'stop_datetime': record.end_datetime,
        #                 'state_text': dict(attendees._fields['state'].selection).get(attendees.state),
        #                 'state': attendees.state,
        #                 'vote_type': attendees.vote_type or None
        #             }
        #             data_rec.append(vals)
        #         data = {'status': 200, 'response': data_rec, 'message': 'success'}
        #         return data

    # API - Summary สถานะ: การจองวันนี้, ห้องประชุมทั้งหมด, จำนวนอนุมัติ, จำนวนไม่อนุมัติ
    @http.route('/api/meeting/get_meeting_summary_status', type='json', auth='none')
    def get_meeting_summary_status(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')

        search_date = datetime.datetime.strptime(post.get('start_datetime'), "%Y-%m-%d").date() if post.get(
            'start_datetime') else fields.Datetime.now().astimezone(ICT).date()
        start_datetime = datetime.datetime.combine(search_date, datetime.time(0, 0, 0))
        start_datetime = ICT.localize(start_datetime, is_dst=None).astimezone(timezone('UTC'))

        # start_date_str = post.get('start_datetime')
        # if start_date_str:
        #     start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        # else:
        #     start_date = datetime.now().date()
        # start_datetime = datetime.datetime.combine(start_date, datetime.datetime.min.time())
        # start_datetime = ICT.localize(start_datetime, is_dst=None).astimezone(timezone('UTC'))

        # การประชุมตามวันที่ระบุ/วันนี้ (all)
        all_domain = [
            ('meeting_state', '!=', 'draft'),
            ('meeting_state', '!=', 'cancel'),
            ('start_datetime', '>=', start_datetime)
        ]

        # การประชุมตามวันที่ระบุ/วันนี้ (cancel)
        cancel_domain = [
            ('meeting_state', '=', 'cancel'),
            ('start_datetime', '>=', start_datetime)
        ]

        # ห้องประชุม
        room_domain = [
            ('active', '=', True),
            ('room_status', '=', 'active')
        ]

        if post.get('end_date_time') != False:
            end_search_date = datetime.datetime.strptime(post.get('end_datetime'), "%Y-%m-%d").date() if post.get(
                'end_datetime') else search_date
            end_date_time = datetime.datetime.combine(end_search_date, datetime.time(23, 59, 59))
            end_date_time = ICT.localize(end_date_time, is_dst=None).astimezone(timezone('UTC'))
            all_domain.append(('end_datetime', '<=', end_date_time))
            cancel_domain.append(('end_datetime', '<=', end_date_time))
        if post.get('partner_id'):
            all_domain.append(('partner_id', '=', post.get('partner_id')))
            cancel_domain.append(('partner_id', '=', post.get('partner_id')))

        if post.get('organize_id') or post.get('organize_id') == 0:
            all_domain.append(('organize_id', '=', post.get('organize_id')))
            cancel_domain.append(('organize_id', '=', post.get('organize_id')))
            room_domain.append(('organize_id', '=', post.get('organize_id')))
        if post.get('organize_type') or post.get('organize_type') == False:
            all_domain.append(('organize_type', '=', post.get('organize_type')))
            cancel_domain.append(('organize_type', '=', post.get('organize_type')))
            room_domain.append(('organize_type', '=', post.get('organize_type')))

        # การประชุมตามวันที่ระบุ/วันนี้ (all)
        meetings_all = request.env['calendar.event'].sudo().search(all_domain)

        # การประชุมตามวันที่ระบุ/วันนี้ (cancel)
        meetings_cancel = request.env['calendar.event'].sudo().search_count(cancel_domain)

        # ห้องประชุม
        rooms = request.env['mt.room'].sudo().search_count(room_domain)

        # การประชุมตามวันที่ระบุ/วันนี้ (approve)
        meetings_approve = len(meetings_all.filtered(lambda r: r.meeting_state != 'wp'))

        summary_data = {
            'meeting_request': len(meetings_all),
            'summary_rooms': rooms,
            'meeting_approve': meetings_approve,
            'meeting_not_approve': meetings_cancel
        }

        data = {'status': 200, 'response': summary_data, 'message': 'success'}
        return data

    @http.route('/api/meeting/create_recurrent_meeting', type='json', auth='user')
    def create_recurrent_meeting(self, **post):
        meeting = request.env['calendar.event'].search([('id', '=', post.get('meeting_id'))])
        if meeting:
            final_date = datetime.datetime.strptime(post.get('final_date'), DEFAULT_SERVER_DATE_FORMAT).date()
            all_recurrent = meeting.create_meeting_by_recurrent(final_date)

            if all_recurrent:
                ICT = timezone('Asia/Bangkok')
                data_rec = []
                for rec in all_recurrent:
                    vals = {
                        'meeting_id': rec.id,
                        'meeting_state_code': rec.meeting_state,
                        'meeting_state': dict(rec._fields['meeting_state'].selection).get(rec.meeting_state),
                        'meeting_name': rec.name,
                        'team_flag': rec.team_flag or None,
                        'team_url': rec.team_url or None,
                        'team_id': rec.team_id or None,
                        # 'project_id': rec.project_id.id or None,
                        # 'project_name': rec.project_id.name or None,
                        ### Add fields ###
                        'alarm': rec.alarm_ids.ids or None,
                        'join_inside': rec.join_inside or None,
                        'join_outside': rec.join_outside or None,
                        'join_count': rec.join_count or None,
                        'president_id': rec.president_id.id or None,
                        'president_name': rec.president_id.display_name or None,
                        'contact_person': rec.contact_person or None,
                        'contact_number': rec.contact_number or None,

                        'room_id': rec.room_id.id or None,
                        'room_name': rec.room_id.room_name or None,
                        'room_type_code': rec.room_id.room_type or None,
                        'room_type': dict(rec.room_id._fields['room_type'].selection).get(
                            rec.room_id.room_type) or None,
                        'room_address': "%s ชั้น %s %s" % (
                            rec.room_id.room_name, str(rec.room_id.floor), (rec.room_id.room_address or "")),
                        'type_meeting_id': rec.type_id.id or None,
                        'type_meeting': rec.type_id.type_name or None,
                        'description': rec.description or None,
                        'start_datetime': rec.start_datetime.astimezone(ICT) if rec.start_datetime else None,
                        'end_datetime': rec.end_date_time.astimezone(ICT) if rec.end_date_time else None,
                        'duration': rec.duration,
                        'requester_id': rec.partner_id.id,
                        'requester_name': rec.partner_id.display_name,
                        'meeting_summary': rec.meeting_summary or None,
                        'cancel_reason': rec.cancel_reason or None,
                        'cancel_description': rec.cancel_description or None,
                        'create_date': rec.create_date.astimezone(ICT) if rec.create_date else None,
                    }
                    data_rec.append(vals)

                data = {'status': 200, 'response': data_rec, 'message': 'success'}
                return data
            else:
                data = {'status': 500, 'response': 'ไม่สามารถจองห้องประชุม/จองแบบหลายวันได้ (ห้องประชุมไม่ว่าง)',
                        'message': 'success'}
                return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'success'}
            return data

    # API - ตรวจสอบสถานะ จองห้องประชุม แบบหลายวัน
    @http.route('/api/meeting/check_meeting_list_available', type='json', auth='none')
    def check_meeting_list_available(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')

        local_start_datetime = datetime.datetime.strptime(post.get('first_start_datetime'),
                                                          DEFAULT_SERVER_DATETIME_FORMAT)
        utc_dt = ICT.localize(local_start_datetime, is_dst=None).astimezone(timezone('UTC'))
        start_datetime = utc_dt.replace(tzinfo=None)

        local_end_date_time = datetime.datetime.strptime(post.get('first_end_datetime'),
                                                         DEFAULT_SERVER_DATETIME_FORMAT)
        utc_dt = ICT.localize(local_end_date_time, is_dst=None).astimezone(timezone('UTC'))
        end_date_time = utc_dt.replace(tzinfo=None)

        final_date = datetime.datetime.strptime(post.get('final_date'), DEFAULT_SERVER_DATE_FORMAT).date()

        chk_state = "AND meeting_state != 'draft' AND meeting_state != 'cancel'"
        if post.get('all_state') == True:
            chk_state = ""

        chk_not_meeting_id = ""
        if post.get('not_meeting_id'):
            chk_not_meeting_id = "AND id != {}".format(post.get('not_meeting_id'))

        pass_all = True
        data_rec = []
        while local_start_datetime.date() <= final_date:
            # Query Check
            # -- SELECT id, room_id, meeting_state, start_datetime, end_date_time FROM public.calendar_event
            query_chk = """
                    SELECT id FROM public.calendar_event
                    WHERE active=true AND room_id = %(room_id)s {chk_state} {chk_not_meeting_id}
                    AND ((start_datetime <= %(start_datetime)s AND end_date_time >= %(end_date_time)s)
                    OR (start_datetime >= %(start_datetime)s AND start_datetime < %(end_date_time)s
                    OR end_date_time > %(start_datetime)s AND end_date_time <= %(end_date_time)s))
                    ORDER BY id DESC;
                """.format(chk_state=chk_state, chk_not_meeting_id=chk_not_meeting_id)
            request.cr.execute(query_chk, {
                'room_id': post.get('room_id'),
                'start_datetime': start_datetime,
                'end_date_time': end_date_time,
            })

            ids = [column for column, in request.cr.fetchall()]
            if len(ids):
                available = False
                pass_all = False
                vals = {
                    'start_datetime': local_start_datetime,
                    'end_datetime': local_end_date_time,
                    'available_status': available,
                    'available_name': "ว่าง" if available else "ไม่ว่าง",
                }
                data_rec.append(vals)
            else:
                available = True
                vals = {
                    'start_datetime': local_start_datetime,
                    'end_datetime': local_end_date_time,
                    'available_status': available,
                    'available_name': "ว่าง" if available else "ไม่ว่าง",
                }
                data_rec.append(vals)

            local_start_datetime = local_start_datetime + timedelta(days=1)
            start_datetime = start_datetime + timedelta(days=1)
            local_end_date_time = local_end_date_time + timedelta(days=1)
            end_date_time = end_date_time + timedelta(days=1)

        data_response = {
            "start_date": datetime.datetime.strptime(post.get('first_start_datetime'),
                                                     DEFAULT_SERVER_DATETIME_FORMAT).date(),
            "final_date": final_date,
            "day_count": len(data_rec),
            "pass_all": pass_all,
            "list_data": data_rec
        }

        data = {'status': 200, 'response': data_response, 'message': 'success'}
        return data

    # API - ดึงรายการ จองห้องประชุม แบบหลายวัน
    @http.route('/api/meeting/get_recurrent_meeting', type='json', auth='none')
    def get_recurrent_meeting(self, **post):
        request.session.db = post.get('db')

        meeting = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
        if meeting:
            ICT = timezone('Asia/Bangkok')
            all_recurrent = request.env['calendar.event'].sudo().search(
                [('root_meeting_id', '=', meeting.root_meeting_id.id)],
                order="start_datetime asc")

            data_rec = []
            for rec in all_recurrent:
                vals = {
                    'start_datetime': rec.start_datetime.astimezone(ICT) if rec.start_datetime else None,
                    'end_datetime': rec.end_date_time.astimezone(ICT) if rec.end_date_time else None,
                    'meeting_id': rec.id,
                    'meeting_name': rec.name,
                    'room_id': rec.room_id.id or None,
                    'room_name': rec.room_id.room_name or None,
                    'requester_id': rec.partner_id.id,
                    'requester_name': rec.partner_id.display_name,
                }
                data_rec.append(vals)

            day_count = len(data_rec)
            data_response = {
                "start_date": data_rec[0]["start_datetime"].date() if data_rec[0]["start_datetime"] else None,
                "final_date": data_rec[day_count - 1]["start_datetime"].date() if data_rec[day_count - 1][
                    "start_datetime"] else None,
                "day_count": day_count,
                "list_data": data_rec
            }

            data = {'status': 200, 'response': data_response, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'success'}
            return data

    # API - ตรวจสอบห้องประชุม ว่าง/ไม่ว่าง
    @http.route('/api/meeting/get_room_check_available', type='json', auth='none')
    def get_room_check_available(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')

        if post.get('start_datetime') and post.get('end_date_time'):
            search_date = datetime.datetime.strptime(post.get('start_datetime'), DEFAULT_SERVER_DATETIME_FORMAT)
            utc_dt = ICT.localize(search_date, is_dst=None).astimezone(timezone('UTC'))
            start_datetime = utc_dt.replace(tzinfo=None)

            end_search_date = datetime.datetime.strptime(post.get('end_date_time'), DEFAULT_SERVER_DATETIME_FORMAT)
            utc_dt = ICT.localize(end_search_date, is_dst=None).astimezone(timezone('UTC'))
            end_date_time = utc_dt.replace(tzinfo=None)

            chk_state = "AND meeting_state != 'draft' AND meeting_state != 'cancel'"
            if post.get('all_state') == True:
                chk_state = ""

            chk_not_meeting_id = ""
            if post.get('not_meeting_id'):
                chk_not_meeting_id = "AND id != {}".format(post.get('not_meeting_id'))

            # Query Check
            # -- SELECT id, room_id, meeting_state, start_datetime, end_date_time FROM public.calendar_event
            query_chk = """
                    SELECT DISTINCT room_id FROM public.calendar_event
                    WHERE active=true {chk_state} {chk_not_meeting_id}
                    AND ((start_datetime <= %(start_datetime)s AND end_date_time >= %(end_date_time)s)
                    OR (start_datetime >= %(start_datetime)s AND start_datetime < %(end_date_time)s
                    OR end_date_time > %(start_datetime)s AND end_date_time <= %(end_date_time)s))
                    ORDER BY room_id ASC;
                """.format(chk_state=chk_state, chk_not_meeting_id=chk_not_meeting_id)
            request.cr.execute(query_chk, {
                'start_datetime': start_datetime,
                'end_date_time': end_date_time,
            })
            not_available_ids = [column for column, in request.cr.fetchall()]

            domain = []
            if post.get('access_partner_id') and post.get('access_type'):
                if post.get('access_type') == 'public':
                    domain.append(('access_type', '=', 'public'))
                elif post.get('access_type') == 'private':
                    domain.append(('access_partner_ids', 'in', post.get('access_partner_id')))
            elif post.get('access_partner_id'):
                domain.append('|')
                domain.append(('access_type', '=', 'public'))
                domain.append(('access_partner_ids', 'in', post.get('access_partner_id')))
            elif post.get('access_type'):
                domain.append(('access_type', '=', post.get('access_type')))

            domain.append(('room_status', '=', 'active'))
            if post.get('organize_id') or post.get('organize_id') == 0:
                domain.append(('organize_id', '=', post.get('organize_id')))
            if post.get('organize_type') or post.get('organize_type') == False:
                domain.append(('organize_type', '=', post.get('organize_type')))
            rooms = request.env['mt.room'].sudo().search(domain)

            if rooms:
                data_rec = []
                for rec in rooms:
                    available = True
                    if rec.id in not_available_ids:
                        available = False

                    vals = {
                        'id': rec.id,
                        'room_name': rec.room_name,
                        'floor': rec.floor,
                        'people_in_room': rec.people_in_room,
                        'room_address': rec.room_address or None,
                        'access_type': rec.access_type,
                        'access_partner_ids': rec.access_partner_ids.ids or None,
                        'room_type': dict(rec._fields['room_type'].selection).get(rec.room_type),
                        'type_meeting': rec.type_meeting_id.type_name or None,
                        'room_admin': rec.room_admin_id.name or None,
                        'organize_id': rec.organize_id or None,
                        'organize_type': rec.organize_type or None,
                        'service_status': rec.service_status,
                        'room_status': dict(rec._fields['room_status'].selection).get(rec.room_status),
                        'available_status': available,
                        'available_name': "ว่าง" if available else "ไม่ว่าง",
                    }
                    data_rec.append(vals)

                data = {'status': 200, 'response': data_rec, 'message': 'success'}
                return data
            else:
                data = {'status': 500, 'response': 'ไม่พบข้อมูลห้องประชุม', 'message': 'success'}
                return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลห้องประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_meeting_attach', type='json', auth='user')
    def delete_meeting_attach(self, **post):
        if post.get('id'):
            data_model = request.env['meeting.attach'].search(
                [('meeting_id', '=', post.get('meeting_id')), ('id', '=', post.get('id'))])
            if data_model:
                data_model.unlink()

                data = {'status': 200, 'response': 'Delete Success', 'message': 'success'}
                return data

        elif post.get('ids'):
            data_model = request.env['meeting.attach'].search(
                [('meeting_id', '=', post.get('meeting_id')), ('id', 'in', post.get('ids'))])
            if data_model:
                data_model.unlink()

                data = {'status': 200, 'response': 'Delete Success', 'message': 'success'}
                return data

        data = {'status': 500, 'response': 'ไม่พบข้อมูลเอกสาร', 'message': 'success'}
        return data

    @http.route('/api/meeting/get_meeting_select_date', type='json', auth='none')
    def get_meeting_select_date(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')

        # @Search check with timezone
        search_date = datetime.datetime.strptime(post.get('select_date'), '%d%m%Y').date() if post.get(
            'select_date') else fields.Datetime.now().astimezone(ICT).date()

        start_datetime = datetime.datetime.combine(search_date, datetime.time(0, 0, 0))
        start_datetime = ICT.localize(start_datetime, is_dst=None).astimezone(timezone('UTC'))
        # start_datetime = ICT.normalize(ICT.localize(start_datetime)).astimezone(timezone('UTC'))

        end_datetime = datetime.datetime.combine(search_date, datetime.time(23, 59, 59))
        end_datetime = ICT.localize(end_datetime, is_dst=None).astimezone(timezone('UTC'))
        # end_datetime = ICT.normalize(ICT.localize(end_datetime)).astimezone(timezone('UTC'))

        meetings = request.env['calendar.event'].sudo().search([
            "&", "&",
            ('start_datetime', '>=', start_datetime),
            ('start_datetime', '<=', end_datetime),
            "|",
            ('partner_ids', 'in', [post.get('partner_id')]),
            ('partner_id', '=', post.get('partner_id'))
        ])

        if meetings:
            data_rec = []
            for rec in meetings:
                vals = {
                    'meeting_id': rec.id,
                    'meeting_state': dict(rec._fields['meeting_state'].selection).get(rec.meeting_state),
                    'meeting_name': rec.name,
                    'team_flag': rec.team_flag or None,
                    'team_url': rec.team_url or None,
                    'team_id': rec.team_id or None,
                    'project_id': rec.project_id.id or None,
                    'project_name': rec.project_id.name or None,
                    'room_id': rec.room_id.id or None,
                    'room_name': rec.room_id.room_name or None,
                    'room_address': "%s ชั้น %s %s" % (
                        rec.room_id.room_name, str(rec.room_id.floor), (rec.room_id.room_address or "")),
                    'description': rec.description or None,
                    'start_datetime': rec.start_datetime.astimezone(ICT) if rec.start_datetime else None,
                    'end_datetime': rec.end_date_time.astimezone(ICT) if rec.end_date_time else None,
                    'duration': rec.duration,
                    'requester_id': rec.partner_id.id,
                    'requester_name': rec.partner_id.display_name,
                    'create_date': rec.create_date.astimezone(ICT) if rec.create_date else None,
                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'success'}
            return data
