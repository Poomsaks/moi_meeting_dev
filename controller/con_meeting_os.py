import calendar

import pytz
from dateutil import relativedelta
from odoo import http, fields
from odoo.http import Controller, route, request, Response
import json
import datetime
from datetime import timedelta, MAXYEAR

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from pytz import timezone
from werkzeug import exceptions


class ConMeetingOS(http.Controller):

    # TODO API Create Meeting
    @http.route('/api/meeting/ext/create_meeting_all', type='json', auth='user')
    def create_meeting_all(self, **post):
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
            'requester_code': post.get('requester_code'),
            'meeting_root_type': post.get('meeting_root_type')
        })
        attendee_list = []
        if post.get('attendee_ids'):
            attendee_data = json.loads(json.dumps(post.get('attendee_ids')))
            for rec in attendee_data:
                attendee_list.append((0, 0, {
                    'meeting_id': data_create.id,
                    'partner_id': rec.get('partner_id'),
                    'position_id': rec.get('attendee_meeting_position'),
                    'vote_type': rec.get('vote_type')
                }))
        agenda_list = []
        if post.get('agenda_ids'):
            attendee_data = json.loads(json.dumps(post.get('agenda_ids')))
            for agenda_item in attendee_data:
                agenda_create = request.env['meeting.agenda'].create({
                    'meeting_id': data_create.id,
                    'agenda_title_name': agenda_item.get('agenda_title_name'),
                    'agenda_no': agenda_item.get('agenda_no'),
                    'agenda_detail': agenda_item.get('agenda_detail'),
                    'partner_id': agenda_item.get('partner_id'),
                })
                sub_agenda_ids = agenda_item.get('sub_agenda_ids', [])
                for sub_agenda_item in sub_agenda_ids:
                    sub_agenda_create = request.env['meeting.sub.agenda'].create({
                        'agenda_id': agenda_create.id,
                        'sub_agenda_no': sub_agenda_item.get('sub_agenda_no'),
                        'sub_agenda_name': sub_agenda_item.get('sub_agenda_name'),
                        'sub_agenda_detail': sub_agenda_item.get('sub_agenda_detail'),
                        'partner_id': sub_agenda_item.get('partner_id'),
                    })
                    sub_agenda_attach_ids = sub_agenda_item.get('sub_agenda_attach_ids', [])
                    for sub_agenda_attach_item in sub_agenda_attach_ids:
                        request.env['meeting.sub.agenda.attach'].create({
                            'sub_agenda_id': sub_agenda_create.id,
                            'attach_user': sub_agenda_attach_item.get('attach_user'),
                            'attach_type': sub_agenda_attach_item.get('attach_type'),
                            'attach_flag': sub_agenda_attach_item.get('attach_flag'),
                            'attachment_file': sub_agenda_attach_item.get('attachment_file'),
                            'attachment_name': sub_agenda_attach_item.get('attachment_name'),
                        })
        data_create.write({
            'attendee_ids': attendee_list,
            'agenda_ids': agenda_list,
        })

        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/ext/create_meeting_everything', type='json', auth='user')
    def create_meeting_everything(self, **post):
        ICT = timezone('Asia/Bangkok')
        duration = float(post.get('duration'))
        start_datetime = datetime.datetime.strptime(post.get('start_datetime'), DEFAULT_SERVER_DATETIME_FORMAT)
        start = ICT.localize(start_datetime).astimezone(timezone('Asia/Bangkok')).replace(tzinfo=None)
        end_date_time = start_datetime + timedelta(hours=duration)
        stop = ICT.localize(end_date_time).astimezone(timezone('Asia/Bangkok')).replace(tzinfo=None)
        partner_id = request.env['res.partner'].sudo().search([('personal_code', '=', post.get('requester_code'))])
        data_model = request.env['calendar.event']
        apikey = request.httprequest.headers.get('x-api-key')
        print(apikey)
        # data_create = data_model.create({
        #     'name': post.get('name'),
        #     'start': start,
        #     'stop': stop,
        #     'start_date': start,
        #     'end_date': stop,
        #     'meeting_type_id': post.get('meeting_type_id'),
        #     'description': post.get('description'),
        #     'room_id': post.get('room_id'),
        #     'join_inside': post.get('join_inside'),
        #     'join_outside': post.get('join_outside'),
        #     'meet_name': post.get('meet_name'),
        #     'meet_url': post.get('meet_url'),
        #     'meet_number': post.get('meet_number'),
        #     'meet_passcode': post.get('meet_passcode'),
        #     'requester_code': partner_id.id,
        #     'meeting_root_type': post.get('meeting_root_type')
        # })
        # equipment_list = []
        # if post.get('equipment_ids'):
        #     attendee_data = json.loads(json.dumps(post.get('equipment_ids')))
        #     for rec in attendee_data:
        #         equipment_list.append((0, 0, {
        #             'meeting_id': data_create.id,
        #             'equipment_id': rec.get('equipment_id'),
        #             'equipment_qty': rec.get('equipment_qty')
        #         }))
        # attendee_list = []
        # if post.get('attendee_ids'):
        #     attendee_data = json.loads(json.dumps(post.get('attendee_ids')))
        #     for rec in attendee_data:
        #         attendee_list.append((0, 0, {
        #             'event_id': data_create.id,
        #             'partner_id': rec.get('partner_id'),
        #             'position_id': rec.get('attendee_meeting_position'),
        #             'vote_type': rec.get('vote_type')
        #         }))
        # agenda_list = []
        # if post.get('agenda_ids'):
        #     attendee_data = json.loads(json.dumps(post.get('agenda_ids')))
        #     for agenda_item in attendee_data:
        #         agenda_create = request.env['meeting.agenda'].create({
        #             'meeting_id': data_create.id,
        #             'agenda_title_name': agenda_item.get('agenda_title_name'),
        #             'agenda_no': agenda_item.get('agenda_no'),
        #             'agenda_detail': agenda_item.get('agenda_detail'),
        #             'partner_id': agenda_item.get('partner_id'),
        #         })
        #         sub_agenda_ids = agenda_item.get('sub_agenda_ids', [])
        #         for sub_agenda_item in sub_agenda_ids:
        #             sub_agenda_create = request.env['meeting.sub.agenda'].create({
        #                 'agenda_id': agenda_create.id,
        #                 'sub_agenda_no': sub_agenda_item.get('sub_agenda_no'),
        #                 'sub_agenda_name': sub_agenda_item.get('sub_agenda_name'),
        #                 'sub_agenda_detail': sub_agenda_item.get('sub_agenda_detail'),
        #                 'partner_id': sub_agenda_item.get('partner_id'),
        #             })
        #             sub_agenda_attach_ids = sub_agenda_item.get('sub_agenda_attach_ids', [])
        #             for sub_agenda_attach_item in sub_agenda_attach_ids:
        #                 request.env['meeting.sub.agenda.attach'].create({
        #                     'sub_agenda_id': sub_agenda_create.id,
        #                     'attach_user': sub_agenda_attach_item.get('attach_user'),
        #                     'attach_type': sub_agenda_attach_item.get('attach_type'),
        #                     'attach_flag': sub_agenda_attach_item.get('attach_flag'),
        #                     'attachment_file': sub_agenda_attach_item.get('attachment_file'),
        #                     'attachment_name': sub_agenda_attach_item.get('attachment_name'),
        #                 })
        # data_create.write({
        #     'attendee_ids': attendee_list,
        #     'agenda_ids': agenda_list,
        #     'equipment_ids': equipment_list
        # })
        #
        # data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        # return data

    @http.route('/api/meeting/ext/get_meeting_all_by_id', type='json', auth='none')
    def get_meeting_all_by_id(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')
        meeting = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
        if meeting:
            data_rec = []
            for rec in meeting:
                # TODO attendee
                public_space_rec = request.env['calendar.attendee'].sudo().search(
                    [('event_id', '=', meeting.id)])
                attendee_info = []
                for attendee in public_space_rec:
                    attendee_info.append({
                        'id': attendee.id,
                        'is_instead_attendee': attendee.is_instead_attendee,
                        'partner_id': attendee.partner_id.id,
                        'display_name': attendee.partner_id.display_name,
                        'email': attendee.email or None,
                        'position_id': attendee.position_id.id or None,
                        'position_name': attendee.position_id.name or None,
                        'declined_note': attendee.declined_note or None,
                        'state_text': dict(attendee._fields['state'].selection).get(attendee.state),
                        'state': attendee.state,
                        'vote_type': attendee.vote_type or None,
                    })
                # TODO meeting.agenda
                public_space_rec = request.env['meeting.agenda'].sudo().search(
                    [('meeting_id', '=', meeting.id)])
                agenda_info = []
                for agenda in public_space_rec:
                    agenda_info.append({
                        'attendee_id': agenda.id,
                        'partner_id': agenda.partner_id.id,
                        'agenda_title_name': agenda.agenda_title_name,
                        'agenda_name': agenda.agenda_name or None,
                        'agenda_no': agenda.agenda_no or None,
                        'agenda_detail': agenda.agenda_detail or None,
                        'vote_state_id': agenda.vote_state,
                        'vote_state_value': dict(agenda._fields['vote_state'].selection).get(agenda.vote_state),
                    })
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
                    'attendee_ids': attendee_info,
                    'agenda_ids': agenda_info

                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data

    @http.route('/api/meeting/ext/get_room_meeting_os', type='json', auth='none')
    def get_room_meeting_os(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.room'].sudo().search([])
        data_s = []
        if not data_info:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'error'}
            return data
        for room in data_info:
            # TODO equipment
            equipment_rec = request.env['mt.room.equipment'].sudo().search([('room_id', '=', room.id)])
            equipment_info = []
            for equipment in equipment_rec:
                equipment_info.append({
                    'id': equipment.id or None,
                    'room_id': equipment.room_id.id or None,
                    'equipment_id': equipment.equipment_id.id or None,
                    'equipment_unit': equipment.equipment_unit or None,
                    'equipment_qty': equipment.equipment_qty or None,
                })
            # TODO services
            services_rec = request.env['mt.room.services'].sudo().search([('room_id', '=', room.id)])
            services_info = []
            for services in services_rec:
                services_info.append({
                    'id': services.id or None,
                    'room_id': services.room_id.id or None,
                    'service_id': services.service_id.id or None,
                    'service_type': services.service_type or None,
                    'service_unit': services.service_unit or None,
                    'service_qty': services.service_qty or None,
                })

            for rec in room:
                vals = {
                    'id': rec.id,
                    'room_name': rec.room_name,
                    'floor': rec.floor,
                    'people_in_room': rec.people_in_room,
                    'image': rec.image or None,
                    'room_address': rec.room_address or None,
                    'access_type': rec.access_type,
                    'access_partner_ids': [{'id': record.id,
                                            'name': record.display_name, }
                                           for record in rec.access_partner_ids],

                    'room_type': dict(rec._fields['room_type'].selection).get(rec.room_type),

                    'room_type_ids': [{'id': record.id,
                                       'type_room': record.type_room, }
                                      for record in rec.room_type_ids],

                    'type_meeting_id': rec.type_meeting_id.id or None,
                    'room_admin_id': rec.room_admin_id.id or None,
                    'room_admin': rec.room_admin_id.name or None,
                    'organize_id': rec.organize_id or None,
                    'organize_type': rec.organize_type or None,
                    'service_status': rec.service_status,
                    'room_status': dict(rec._fields['room_status'].selection).get(rec.room_status),
                    'active': rec.active,
                    'meeting_color': rec.meeting_color,
                    'equipment_ids': equipment_info,
                    'services_ids': services_info
                }
                data_s.append(vals)
        data = {'status': 200, 'response': data_s, 'message': 'success'}
        return data

    @http.route('/api/meeting/ext/get_room_meeting_os_by_id', type='json', auth='none')
    def get_room_meeting_os_by_id(self, **post):
        request.session.db = post.get('db')
        rooms = request.env['mt.room'].sudo().search([('id', '=', post.get('room_id')), ('active', '=', True)])
        if rooms:
            data_rec = []
            for rec in rooms:
                data_equipment = []
                for equipment in rec.equipment_ids:
                    vals = {
                        'id': equipment.id,
                        'equipment_id': equipment.equipment_id.id,
                        'equipment_name': equipment.equipment_id.equip_name,
                        'equipment_unit': equipment.equipment_unit or None,
                        'equipment_qty': equipment.equipment_qty,
                    }
                    data_equipment.append(vals)

                data_service = []
                for services in rec.services_ids:
                    vals = {
                        'id': services.id,
                        'service_id': services.service_id.id,
                        'service_name': services.service_id.service_name,
                        'service_type': services.service_type or None,
                        'service_qty': services.service_qty,
                    }
                    data_service.append(vals)

                access_partner_list = []
                for partner in rec.access_partner_ids:
                    vals = {
                        'partner_id': partner.id,
                        'display_name': partner.display_name,
                    }
                    access_partner_list.append(vals)

                vals = {
                    'id': rec.id,
                    'room_name': rec.room_name,
                    'floor': rec.floor,
                    'people_in_room': rec.people_in_room,
                    'image': rec.image or None,
                    'room_address': rec.room_address or None,
                    'access_type': rec.access_type,
                    'access_partner_ids': [{'id': record.id,
                                            'name': record.display_name, }
                                           for record in rec.access_partner_ids],

                    'room_type': dict(rec._fields['room_type'].selection).get(rec.room_type),

                    'room_type_ids': [{'id': record.id,
                                       'type_room': record.type_room, }
                                      for record in rec.room_type_ids],

                    'type_meeting_id': rec.type_meeting_id.id or None,
                    'room_admin_id': rec.room_admin_id.id or None,
                    'room_admin': rec.room_admin_id.name or None,
                    'organize_id': rec.organize_id or None,
                    'organize_type': rec.organize_type or None,
                    'service_status': rec.service_status,
                    'room_status': dict(rec._fields['room_status'].selection).get(rec.room_status),
                    'active': rec.active,
                    'meeting_color': rec.meeting_color,
                    'equipment_ids': data_equipment,
                    'services_ids': data_service
                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อห้องประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/ext/add_user', type='json', auth='none')
    def add_user(self, **post):
        request.session.db = post.get('db')
        login_check = request.env['res.users'].sudo().search([('login', '=', post.get('email'))])

        if login_check and len(login_check) == 1:
            data = {'status': 301, 'message': 'อีเมลซ้ำ ไม่สามารถสมัครสมาชิกได้'}
            return data
        elif login_check and len(login_check) > 1:
            data = {'status': 302, 'message': 'มีผู้ใช้งานหลายคนที่ใช้อีเมลเดียวกัน'}
            return data

        profile_data = post.get('profile')
        values = {
            'login': profile_data.get('email'),
            'name': profile_data.get('name'),
            'password': "1234"
        }
        db, login, password = request.env['res.users'].sudo().signup(values, None)
        request.env.cr.commit()

        uid = request.session.authenticate(post.get('db'), login, password)
        if not uid:
            data = {'status': 400, 'message': 'เกิดข้อผิดพลาดจาก server ไม่สามารถทำรายการได้ กรุณาลองใหม่อีกครั้ง'}
            return data
        else:
            users_info = request.env['res.users'].sudo().search([('id', '=', uid)])
            print(users_info)

        data = {'status': 200, 'response': "ทดสอบ", 'message': 'success'}
        return data

    #     # request.session.db = "moi_meeting_dev"
    #     request.session.db = post.get('db')
    #     db_name = "moi_meeting_dev"
    #
    #     code = ""
    #     email = ""
    #     name = ""
    #     refId = ""
    #     profile_data = post.get('profile')
    #     if profile_data:
    #         code = profile_data.get('code')
    #         email = profile_data.get('email')
    #         name = profile_data.get('name')
    #         refId = profile_data.get('refId')
    #         positionName = profile_data.get('positionName')
    #         username = profile_data.get('username')
    #         usernameRef = profile_data.get('usernameRef')
    #
    #     login_check = request.env['res.users'].sudo().search([('login', '=', email)])
    #     print(login_check)
    #     if login_check:
    #         login_check.ensure_one()
    #
    #         data = {'status': 200, 'response': login_check.id, 'message': 'success'}
    #         return data
    #     else:
    #         values = {
    #             'login': email,
    #             'name': name,
    #             'password': "1234"
    #         }
    #         db, login, password = request.env['res.users'].sudo().signup(values,  context=None)
    #         request.env.cr.commit()
    #         uid = request.session.authenticate(post.get('db'), login, password)
    #
    #         # if not uid:
    #         #     data = {'status': 400, 'message': 'เกิดข้อผิดพลาดจาก server ไม่สามารถทำรายการได้ กรุณาลองใหม่อีกครั้ง'}
    #         #     return data
    #         # else:
    #         #     users_info = request.env['res.users'].sudo().search([('id', '=', uid)])
    #         #     users_info.ensure_one()
    #         #     response_return = []
    #         #     if users_info:
    #         #         partner_info = request.env['res.partner'].sudo().search([('id', '=', users_info.partner_id.id)])
    #         #         partner_info.write({
    #         #             'id': partner_info.id,
    #         #             'name': name,
    #         #             'attendee_code': code,
    #         #         })
    #         #
    #         #         response_return = {
    #         #             'id': partner_info.id,
    #         #             'name': name,
    #         #             'attendee_code': code,
    #         #         }
    #         #     data = {'status': 200, 'response': response_return, 'message': 'success'}
    #         #     return data
    #
    # # @route('/api/meeting/ext/add_user_test', type='json', auth='none', methods=['POST'])
    # # def add_user_test(self, **kwargs):
    # #     apikey = request.httprequest.headers.get('apikey')
    # #     print(apikey)
    # #     return {'status': 'success', 'message': 'User added successfully'}
