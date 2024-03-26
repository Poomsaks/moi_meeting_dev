import calendar
import uuid
import requests
from odoo import http
from odoo.http import Controller, route, request
import json
import datetime
from datetime import timedelta, MAXYEAR

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from pytz import timezone
from .config_database import ConfigDatabase

class ConMeetingOS(http.Controller):
    url_host = 'http://172.21.200.39:8082'

    def send_status_meeting(self, data_text):
        url = self.url_host + '/supply/services/meeting/updateStatus'
        headers = {'Content-Type': 'application/json'}
        create_date_str = data_text['create_date'].strftime('%Y-%m-%d %H:%M:%S')
        response_list = {
            'meeting_id': data_text['meeting_id'],
            'create_date': create_date_str
        }
        data = {'status': 200, 'response': response_list, 'message': 'success'}
        requests.post(url, json=data, headers=headers)

    @http.route('/api/meeting/ext/borrow_cancel', type='json', auth='none')
    def borrow_cancel(self, **post):
        ref_id = post.get('meeting_id')
        url = self.url_host + '/meeting-room/cancel-meeting/?ref-id=' + ref_id
        response = requests.put(url)
        return json.loads(response.text)

    @http.route('/api/meeting/ext/borrow_register', type='json', auth='none')
    def borrow_register(self, **post):
        url = self.url_host + '/meeting-room/register-meeting/'
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "referenceMeeting": post.get('referenceMeeting'),  # id ของ meeting_id ของเรา
            "meetingTitle": post.get('meetingTitle'),
            "meetingDescription": post.get('meetingDescription'),
            "requestDatetime": post.get('requestDatetime'),  # เวลาเริ่มประชุม
            "returnDatetime": post.get('returnDatetime'),  # เวลาจบการประชุม
            "borrower": post.get('borrower'),  # code ของ id_user ของ os
        }
        response = requests.post(url, headers=headers, json=data)
        data_event = request.env['calendar.event'].sudo().search([('id', '=', post.get('referenceMeeting'))])
        if data_event:
            data_event.write({
                'ref_borrow_flag': 'Y',
            })
        return json.loads(response.text)

    @http.route('/api/meeting/ext/borrow_status', type='json', auth='none')
    def borrow_status(self, **post):
        ref_id = post.get('meeting_id')
        url = self.url_host + '/meeting-room/status/?ref-id=' + ref_id
        response = requests.get(url)
        return json.loads(response.text)

    def con_authenticate(self):
        url = 'http://172.21.200.21/web/session/authenticate'
        headers = {'Content-Type': 'application/json'}
        data = {
            "params": {
                "login": "admin",
                "password": "1234",
                "db": "moi_meeting_dev"
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        return response.json()

    # @http.route('/api/meeting/ext/create_meeting', type='json', auth='none')
    # def create_meeting(self, **post):
    #     if self.con_authenticate():
    #         partner_id = request.env['res.partner'].sudo().search([('personal_code', '=', post.get('requester_code'))])
    #         return partner_id.id
    #     else:
    #         return "asdw"

    # TODO API Create Meeting

    def os_auth_integrate_service_valid_token(self, apikey_otp):
        url = "http://cloud-api.win-victor.com/api/integrate/auth/valid"
        apikey = apikey_otp
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'apikey': apikey
        }
        data = {}  # ไม่จำเป็นต้องส่งข้อมูล JSON ในกรณีนี้

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            access_token = response.json().get('token')
            return access_token
        else:
            print("Failed to get access token")
            return None

    def os_auth_profile(self, apikey_otp):
        url = "http://cloud-api.win-victor.com/api/integrate/auth/profile"
        headers = {
            'Accept': 'application/json',
            'apikey': apikey_otp
        }
        data = {}
        response = requests.get(url, headers=headers, json=data)
        if response.status_code == 200:
            access_token = response.json().get('profile')
            return access_token
        else:
            print("Failed to get access token")
            return None

    def add_os_user_none_profile(self, profile):
        username = profile['username']
        email = profile['email']
        name = profile['name']
        code = profile['code']
        ref_id = profile['refId']
        position_name = profile['positionName']
        db_authen = ConfigDatabase.database
        login_check = request.env['res.users'].sudo().search([('login', '=', username)])
        if login_check:
            request.session.authenticate(db_authen, email, "1234")
            return request.env['ir.http'].session_info()
        # existing_user = request.env['res.users'].sudo().search([('login', '=', username)])
        if login_check:
            login_check.ensure_one()
            data = {'status': 200, 'response': login_check.id, 'message': 'User already exists'}
            return data
        else:
            role_user = [request.env.ref('base.group_user').id]
            new_user = request.env['res.users'].sudo().create({
                'name': name,
                'login': username,
                'password': email,
                'groups_id': [(6, 0, role_user)],
            })
            if not new_user:
                data = {'status': 400, 'message': 'เกิดข้อผิดพลาดจาก server ไม่สามารถทำรายการได้ กรุณาลองใหม่อีกครั้ง'}
                return data

            else:
                users_info = request.env['res.users'].sudo().search([('id', '=', new_user.id)])
                users_info.ensure_one()
                response_return = []
                if users_info:
                    partner_info = request.env['res.partner'].sudo().search([('id', '=', users_info.partner_id.id)])
                    partner_info.write({
                        'id': partner_info.id,
                        'name': name,
                        'email': email,
                        'phone': ref_id,
                        'attendee_code': code,
                        'position_name': position_name
                    })

                    response_return = {
                        'id': partner_info.id,
                        'name': name,
                        'email': email,
                        'phone': ref_id,
                        'attendee_code': code,
                        'position_name': position_name
                    }
                data = {'status': 200, 'response': response_return, 'message': 'success'}
                return data

    @http.route('/api/meeting/ext/create_meeting', type='json', auth='none', csrf=False)
    def create_meeting(self, **post):
        request.session.db = 'moi_meeting_dev'
        if self.os_auth_integrate_service_valid_token(post.get('requester_code')):
            profile_os = self.os_auth_profile(self.os_auth_integrate_service_valid_token(post.get('requester_code')))
            username = profile_os['username']
            email = profile_os['email']
            name = profile_os['name']
            code = profile_os['code']
            ref_id = profile_os['refId']
            db_authen = ConfigDatabase.database
            login_check = request.env['res.users'].sudo().search([('login', '=', username)])
            print(login_check)
            # if self.add_os_user_none_profile(profile_os).get('status') == 200:
            #     data_model = request.env['calendar.event']
            #     data_create = data_model.create({
            #         'requester_code': profile_os['code'],
            #         'name': post.get('name'),
            #         'description': post.get('description'),
            #         'ref_id': post.get('ref_id'),
            #     })
            #     if post.get('attendee_ids'):
            #         attendee_list = []
            #         for rec in post.get('attendee_ids'):
            #             data_partner = request.env['res.partner'].search(
            #                 [('attendee_code', '=', rec.get('attendee_code'))], limit=1)
            #             if data_partner:
            #                 attendee_list.append((0, 0, {
            #                     'event_id': data_create.id,
            #                     'position_id': rec.get('position_id'),
            #                     'partner_id': data_partner.id,
            #                     'attendee_code': rec.get('attendee_code')
            #                 }))
            #         data_create.write({
            #             'attendee_ids': attendee_list,
            #         })
            #     response_list = {
            #         'meeting_id': data_create.id,
            #         'create_date': data_create.create_date
            #     }
            #     data = {'status': 200, 'response': response_list, 'message': 'success'}
            #     self.send_status_meeting(response_list)
            #     return data
            # else:
            #     data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'error'}
            #     return data

    @http.route('/api/meeting/ext/update_status_attendee', type='json', auth='none')
    def update_status_attendee(self, **post):
        request.session.db = post.get('db')
        data_event = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
        data_model = request.env['calendar.attendee'].sudo().search([
            ('event_id', '=', data_event.id),
            ('attendee_code', '=', post.get('attendee_code')),
            ('confirm_status', '=', post.get('confirm_status')),
            ('attendee_confirm', '=', post.get('attendee_confirm')),
            ('attendee_status', '=', post.get('attendee_status'))
        ])
        data_model.write({
            'state': post.get('state'),
        })
        data = {'status': 200, 'response': data_model.id, 'message': 'success'}
        return json.dumps(data)

    @http.route('/api/meeting/ext/external_users_attendee', type='json', auth='user')
    def external_users_attendee(self, **post):
        data_model = request.env['calendar.event'].search([('id', '=', post.get('meeting_id'))])

        if post.get('attendee_ids'):
            attendee_list = []
            for rec in post.get('attendee_ids'):
                data_partner = request.env['res.partner'].search([('attendee_code', '=', rec.get('attendee_code'))])
                if data_partner:
                    attendee_list.append((0, 0, {
                        'event_id': data_model.id,
                        'position_id': rec.get('position_id'),
                        'partner_id': data_partner.id,
                        'attendee_code': rec.get('attendee_code')
                    }))
            data_model.write({
                'attendee_ids': attendee_list,
            })
        response_list = {
            'meeting_id': data_model.id,
            'create_date': data_model.create_date
        }
        data = {'status': 200, 'response': response_list, 'message': 'success'}
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
                    'start': rec.start if rec.start else None,
                    'stop': rec.stop if rec.stop else None,
                    'start_datetime': rec.start if rec.start else None,
                    'end_datetime': rec.stop if rec.stop else None,
                    'start_date': rec.start if rec.start else None,
                    'end_date': rec.stop if rec.stop else None,
                    'description': rec.description or None,
                    'duration': rec.duration,
                    'requester_id': rec.partner_id.id,
                    'requester_name': rec.partner_id.display_name,
                    'create_date': rec.create_date if rec.create_date else None,
                    'meeting_type_id': rec.meeting_type_id.id or None,
                    'meeting_type_name': rec.meeting_type_id.type_name or None,
                    'attendee_ids': attendee_info,
                    'agenda_ids': agenda_info

                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่มีข้อมูล', 'message': 'error'}
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

    @http.route('/api/meeting/ext/add_user_ext', type='json', auth='none')
    def add_user_ext(self, **post):
        request.session.db = post.get('db')
        code = ""
        email = ""
        name = ""
        refId = ""
        positionName = ""
        profile_data = post.get('profile')
        if profile_data:
            code = profile_data.get('code')
            email = profile_data.get('email')
            name = profile_data.get('name')
            refId = profile_data.get('refId')
            positionName = profile_data.get('positionName')
            username = profile_data.get('username')
            usernameRef = profile_data.get('usernameRef')

        login_check = request.env['res.users'].sudo().search([('login', '=', email)])
        if login_check:
            login_check.ensure_one()
            data = {'status': 200, 'response': login_check.id, 'message': 'success'}
            return data
        else:
            web_company = request.env['res.company'].sudo().search([('id', '=', 1)])
            new_user = request.env['res.users'].with_company(web_company).sudo().create({
                'name': name,
                'login': email,
                'company_id': web_company.id
            })
            if not new_user:
                data = {'status': 400, 'message': 'เกิดข้อผิดพลาดจาก server ไม่สามารถทำรายการได้ กรุณาลองใหม่อีกครั้ง'}
                return data

            else:
                users_info = request.env['res.users'].sudo().search([('id', '=', new_user.id)])
                users_info.ensure_one()
                response_return = []
                if users_info:
                    partner_info = request.env['res.partner'].sudo().search([('id', '=', users_info.partner_id.id)])
                    partner_info.write({
                        'id': partner_info.id,
                        'name': name,
                        'email': email,
                        'attendee_code': code,
                        'personal_code': refId,
                        'position_name': positionName
                    })

                    response_return = {
                        'id': partner_info.id,
                        'name': name,
                        'email': email,
                        'attendee_code': code,
                        'personal_code': refId,
                        'position_name': positionName
                    }
                data = {'status': 200, 'response': response_return, 'message': 'success'}
                return data

    @http.route('/api/meeting/ext/auth_integrate_service_valid_token', type='json', auth='none')
    def auth_integrate_service_valid_token(self, **post):
        request.session.db = post.get('db')
        url = "http://cloud-api.win-victor.com/api/integrate/auth/valid"
        apikey = post.get("apikey")  # ดึงค่า apikey จาก post data
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'apikey': apikey
        }
        data = {}  # ไม่จำเป็นต้องส่งข้อมูล JSON ในกรณีนี้

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            access_token = response.json().get('token')
            return access_token
        else:
            print("Failed to get access token")
            return None

    @http.route('/api/meeting/ext/auth_profile', type='json', auth='none')
    def auth_profile(self, **post):
        request.session.db = post.get('db')
        url = "http://cloud-api.win-victor.com/api/integrate/auth/profile"
        headers = {
            'Accept': 'application/json',
            'apikey': post.get("apikey")
        }
        data = {}
        response = requests.get(url, headers=headers, json=data)
        if response.status_code == 200:
            access_token = response.json().get('profile')
            return access_token
        else:
            print("Failed to get access token")
            return None

    @http.route('/api/meeting/send_mail', type='json', auth='none')
    def send_mail(self, **post):
        request.session.db = post.get('db')
        email = post.get('email')
        if email:
            existing_user = http.request.env['res.users'].sudo().search([('login', '=', email)])
            data = ""
            if existing_user:
                attendee_info = request.env['calendar.attendee'].sudo().search(
                    [('partner_id', '=', existing_user.partner_id.id)])
                if attendee_info:
                    if existing_user.partner_id.attendee_code:
                        template = request.env.ref('moi_meeting_dev.calendar_template_meeting_custom')
                        template_values = {
                            'email_to': existing_user.email,
                            'email_cc': False,
                            'auto_delete': True,
                            'partner_to': False,
                            'scheduled_date': False,
                        }
                        template.sudo().write(template_values)
                        template.sudo().with_context(lang=existing_user.lang).send_mail(attendee_info.id,
                                                                                        force_send=True)
                    else:
                        template = request.env.ref('moi_meeting_dev.os_calendar_template_meeting_custom')
                        template_values = {
                            'email_to': existing_user.email,
                            'email_cc': False,
                            'auto_delete': True,
                            'partner_to': False,
                            'scheduled_date': False,
                        }
                        template.sudo().write(template_values)
                        template.sudo().with_context(lang=existing_user.lang).send_mail(attendee_info.id,
                                                                                        force_send=True)
                    data = {'status': 200, 'response': existing_user.email, 'message': 'success'}
            else:
                data = {'status': 500, 'response': "ไม่พบข้อมูล", 'message': 'error'}
        else:
            data = {'status': 500, 'response': "ไม่พบอีเมล", 'message': 'error'}
        return data

    @http.route('/api/meeting/send_mail_outsider', type='json', auth='none')
    def send_mail_outsider(self, **post):
        request.session.db = post.get('db')
        email = post.get('email')
        meeting_id = post.get('meeting_id')
        outsider_name = post.get('outsider_name')
        if email:
            user_info = request.env['res.users'].sudo().search([('login', '=', post.get('email'))], limit=1)
            meeting_info = request.env['calendar.event'].sudo().search([('id', '=', meeting_id)])
            mail_values = {
                'email_from': 'poomsak1994@gmail.com',
                'email_to': email,
                'subject': 'เอกสารเชิญ to ' + outsider_name,
                'body_html': f""" <div style="width: auto;height: 100%;">
                        <div style="width: 900px;margin: auto;height: 100%;border:1px solid #d5d5d5;">
                            <div style="width: 800px;margin: auto; height: 100%;">

                                <div
                                        style="width: 800px;font-size: 25px;font-weight: bold;text-align:left;font-family: 'Cordia New', 'Leelawadee UI', Silom, sans-serif;">
                                    เชิญประชุม
                                </div>


                                <table
                                        style="width: 600px; display: flex; border-collapse: collapse;font-family: 'Cordia New', 'Leelawadee UI', Silom, sans-serif;">

                                    <tr style="border: 0px solid #d5d5d5;text-align: left;">
                                        <td style="border: 0px solid #d5d5d5;">


                                            <div style="font-size: 20px;">
                                                <span style="color: windowtext;font-weight: bold;">ถึง</span>
                                                <span style="font-weight:bold;font-size: 20px;">
                                                    {outsider_name or ''}
                                                </span>
                                            </div>

                                            <div style="font-size: 20px;">
                                                <span style="color: windowtext;font-weight: bold;">สำเนาถึง</span>
                                                <span style="font-weight:bold;font-size: 20px;">
                                                    {meeting_info.name}
                                                </span>
                                            </div>

                                            <div style="font-size: 20px;">
                                                <span style="color: windowtext;font-weight: bold;">เรื่อง.</span>
                                                <span style="font-weight:bold;font-size: 20px;">
                                                    {meeting_info.name}
                                                </span>

                                            </div>
                                            <div style="font-size: 20px;">
                                                <span style="color: windowtext;font-weight: bold;">
                                                    เรียนให้ทราบเกี่ยวกับขอ"
                                                </span>
                                                <span
                                                        style="font-weight:bold;font-size: 20px;text-decoration:underline;color:rgb(255,0,0);">
                                                    เชิญประชุม
                                                </span>
                                                <span style="color: windowtext;font-weight: bold;">
                                                    "โดยมีรายละเอียดดังนี้
                                                </span>

                                            </div>
                                        </td>
                                    </tr>
                                </table>

                                <table
                                        style="width: 600px; display: flex; border-collapse: collapse;font-family: 'Cordia New', 'Leelawadee UI', Silom, sans-serif;font-size: 20px;">

                                    <tr style="border: 0px solid #d5d5d5;text-align: left;">
                                        <td style="border: 0px solid #d5d5d5;background-color:#D6EEEE;font-weight:bold;">
                                            ชื่อการประชุม:
                                        </td>
                                        <td style="border: 0px solid #d5d5d5;font-size: 20px;">
                                            {meeting_info.room_id.room_name or ''}
                                        </td>
                                    </tr>


                                    <tr style="border: 0px solid #d5d5d5;text-align: left;">
                                        <td style="border: 0px solid #d5d5d5;background-color:#D6EEEE;font-weight:bold;">
                                            ผู้การประชุม:
                                        </td>
                                        <td style="border: 0px solid #d5d5d5;font-size: 20px;">
                                            {meeting_info.president_id.name or ''}
                                        </td>
                                    </tr>

                                    <tr style="border: 0px solid #d5d5d5;text-align: left;">
                                        <td style="border: 0px solid #d5d5d5;background-color:#D6EEEE;font-weight:bold;">
                                            เริ่ม:
                                        </td>
                                        <td style="border: 0px solid #d5d5d5;font-size: 20px;">
                                            {meeting_info.start_datetime or ''}
                                        </td>
                                    </tr>

                                    <tr style="border: 0px solid #d5d5d5;text-align: left;"/>
                                    <td style="border: 0px solid #d5d5d5;background-color:#D6EEEE;font-weight:bold;">
                                        ถึง:
                                    </td>
                                    <td style="border: 0px solid #d5d5d5;font-size: 20px;">
                                        {meeting_info.end_datetime or ''}
                                    </td>

                                    <tr style="border: 0px solid #d5d5d5;text-align: left;">
                                        <td style="border: 0px solid #d5d5d5;background-color:#D6EEEE;font-weight:bold;">
                                            สถานที่:
                                        </td>
                                        <td style="border: 0px solid #d5d5d5;font-size: 20px;">
                                            {meeting_info.meeting_root_type or ''}
                                        </td>
                                    </tr>

                                </table>
                                <table
                                        style="width: 600px; display: flex; border-collapse: collapse;font-family: 'Cordia New', 'Leelawadee UI', Silom, sans-serif;">

                                    <tr style="border: 0px solid #d5d5d5;text-align: left;">
                                        <td style="border: 0px solid #d5d5d5;">
                                            <div style="font-size: 20px;">
                                                <span style="color: windowtext;font-weight: bold;">เพื่อดำเนินการ:
                                                </span>
                                                <a href="http://meeting-support.win-victor.com/reserve/meeting-summary?meeting_id={meeting_info.id}&partner_id={user_info.partner_id.attendee_code}&type=ext&start=2024-02-20"
                                                   style="font-weight: bold;font-size: 20px;">
                                                    กดตอบรับการเข้าร่วมประชุม/ไม่เข้าร่วมประชุม
                                                </a>
                                            </div>
                                        </td>
                                    </tr>

                                </table>
                            </div>
                        </div>
                </div> """,
                'auto_delete': True,
            }
            mail = request.env['mail.mail'].sudo().create(mail_values)
            mail.send()
            data = {'status': 200, 'response': email, 'message': 'success'}
        else:
            data = {'status': 500, 'response': "ไม่พบอีเมล", 'message': 'error'}
        return data

    @http.route('/api/meeting/send_link_mail', type='json', auth='none')
    def send_link_mail(self, **post):
        request.session.db = post.get('db')
        email = post.get('email')
        meeting_id = post.get('meeting_id')
        outsider_name = post.get('outsider_name')
        if email:
            user_info = request.env['res.users'].sudo().search([('login', '=', post.get('email'))], limit=1)
            meeting_info = request.env['calendar.event'].sudo().search([('id', '=', meeting_id)])
            mail_values = {
                'email_from': 'poomsak1994@gmail.com',
                'email_to': email,
                'subject': 'เอกสารเชิญ to ' + outsider_name,
                'body_html': f""" <div style="width: auto;height: 100%;">
                            <div style="width: 900px;margin: auto;height: 100%;border:1px solid #d5d5d5;">
                                <div style="width: 800px;margin: auto; height: 100%;">

                                    <div
                                            style="width: 800px;font-size: 25px;font-weight: bold;text-align:left;font-family: 'Cordia New', 'Leelawadee UI', Silom, sans-serif;">
                                        เชิญประชุม
                                    </div>
                                    <table
                                            style="width: 600px; display: flex; border-collapse: collapse;font-family: 'Cordia New', 'Leelawadee UI', Silom, sans-serif;">

                                        <tr style="border: 0px solid #d5d5d5;text-align: left;">
                                            <td style="border: 0px solid #d5d5d5;">
                                                <div style="font-size: 20px;">
                                                    <span style="color: windowtext;font-weight: bold;">เพื่อดำเนินการ:
                                                    </span>
                                                    <a href="http://meeting-support.win-victor.com/support/main/between-During-meeting?meeting_id={meeting_info.id}"
                                                       style="font-weight: bold;font-size: 20px;">
                                                        กดตอบรับการเข้าร่วมประชุม
                                                    </a>
                                                </div>
                                            </td>
                                        </tr>

                                    </table>
                                </div>
                            </div>
                    </div> """,
                'auto_delete': True,
            }
            mail = request.env['mail.mail'].sudo().create(mail_values)
            mail.send()
            data = {'status': 200, 'response': email, 'message': 'success'}
        else:
            data = {'status': 500, 'response': "ไม่พบอีเมล", 'message': 'error'}
        return data

    @http.route('/api/meeting/send_mail_meeting', type='json', auth='none')
    def send_mail_meeting(self, **post):
        request.session.db = post.get('db')
        email = post.get('email')
        meeting_id = post.get('meeting_id')
        outsider_name = post.get('outsider_name')
        if email:
            meeting_info = request.env['calendar.event'].sudo().search([('id', '=', meeting_id)])
            mail_values = {
                'email_from': 'your_sender_email@example.com',
                'email_to': email,
                'subject': 'เอกสารเชิญ to ' + outsider_name,
                'body_html': f""" <div
        style="width: 800px;font-size: 22px;font-weight: bold;text-align:left;font-family: 'Cordia New', 'Leelawadee UI', Silom, sans-serif;">
        ระบบบริหารจัดการห้องประชุม
    </div>

    <table
        style="width: 600px; display: flex;  font-size: 22px;border: 1px solid #d5d5d5;border-collapse: collapse;font-family: 'Cordia New', 'Leelawadee UI', Silom, sans-serif;">

        <tr style="border: 0px solid #d5d5d5;text-align: left;">
            <td style="border: 0px solid #d5d5d5;">

                <div style="font-size: 22px;">
                    <span style="font-weight: bold;font-size: 22px;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;เรียน: </span>
                    คุณ {outsider_name}
                </div>
                <div style="font-size: 22px;">
                    <span style="font-weight: bold;font-size: 22px;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;วันที่เริ่ม:</span>
                    {meeting_info.start}
                </div>
                <div style="font-size: 22px;">
                    <span style="font-weight: bold;font-size: 22px;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;วันที่สิ้นสุด:</span>
                    {meeting_info.stop}
                </div>

                <div style="font-size: 22px;">
                    <span style="font-weight: bold;font-size: 22px;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;รายละเอียด:</span>
                    {meeting_info.description}
                </div>
                <div style="font-size: 22px;">
                    <span style="font-weight: bold;font-size: 22px;">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Meeting URL:</span>
                    <a href="{outsider_name}" style="font-size: 22px;color:rgb(0, 0, 170)">{outsider_name}</a>
                    &nbsp;&nbsp;<span>
                    </span>
                </div>
            </td>
        </tr>
    </table> """,
                'auto_delete': True,
            }
            mail = request.env['mail.mail'].sudo().create(mail_values)
            mail.send()
            data = {'status': 200, 'response': email, 'message': 'success'}
        else:
            data = {'status': 500, 'response': "ไม่พบอีเมล", 'message': 'error'}
        return data

    @http.route('/api/meeting/summarize_send_mail', type='json', auth='none')
    def summarize_send_mail(self, **post):
        request.session.db = post.get('db')
        user_info = request.env['res.users'].sudo().search([('login', '=', post.get('email'))], limit=1)
        if user_info:
            attendee_info = request.env['calendar.attendee'].sudo().search(
                [('partner_id', '=', user_info.partner_id.id)])
            if attendee_info:
                template = request.env.ref('moi_meeting_dev.calendar_template_meeting_custom_end_meeting')
                template_values = {
                    'email_to': user_info.email,
                    'email_cc': False,
                    'auto_delete': True,
                    'partner_to': False,
                    'scheduled_date': False,
                }
                template.sudo().write(template_values)
                template.sudo().with_context(lang=user_info.lang).send_mail(attendee_info.id, force_send=True)

            data = {'status': 200, 'response': user_info.email, 'message': 'success'}
        else:
            data = {'status': 500, 'response': "ไม่พบข้อมูล", 'message': 'error'}
        return data

    @http.route('/api/meeting/ext/add_os_user', type='json', auth='none')
    def add_os_user(self, **post):
        request.session.db = post.get('db')
        email = post.get('email')
        name = post.get('name')
        phone = post.get('phone')
        positionName = post.get('positionName')
        existing_user = http.request.env['res.users'].sudo().search([('login', '=', email)])
        if existing_user:
            existing_user.ensure_one()
            data = {'status': 200, 'response': existing_user.id, 'message': 'User already exists'}
            return data
        else:
            web_company = request.env['res.company'].sudo().search([('id', '=', 1)])
            new_user = request.env['res.users'].with_company(web_company).sudo().create({
                'name': name,
                'login': email,
                'company_id': web_company.id
            })
            if not new_user:
                data = {'status': 400, 'message': 'เกิดข้อผิดพลาดจาก server ไม่สามารถทำรายการได้ กรุณาลองใหม่อีกครั้ง'}
                return data

            else:
                code = str(uuid.uuid4())
                users_info = request.env['res.users'].sudo().search([('id', '=', new_user.id)])
                users_info.ensure_one()
                response_return = []
                if users_info:
                    partner_info = request.env['res.partner'].sudo().search([('id', '=', users_info.partner_id.id)])
                    partner_info.write({
                        'id': partner_info.id,
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'attendee_code': code,
                        'position_name': positionName
                    })

                    response_return = {
                        'id': partner_info.id,
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'attendee_code': code,
                        'position_name': positionName
                    }
                data = {'status': 200, 'response': response_return, 'message': 'success'}
                return data

    @http.route('/api/meeting/get_meeting_new_by_partner', type='json', auth='none')
    def get_meeting_new_by_partner(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')
        meeting = request.env['calendar.event'].sudo().search([('meeting_state', '=', 'ap')])
        if meeting:
            data_rec = []
            for rec in meeting:
                # TODO attendee
                public_space_rec = request.env['calendar.attendee'].sudo().search(
                    [
                        ('event_id', '=', rec.id),
                        ('position_id', '=', 4),
                        ('partner_id', '=', post.get('partner_id'))
                    ])
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
                    [('meeting_id', '=', rec.id)])
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
                        'agenda_attach_ids': dict(agenda._fields['vote_state'].selection).get(agenda.vote_state),
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
                    'start': rec.start if rec.start else None,
                    'stop': rec.stop if rec.stop else None,
                    'start_datetime': rec.start if rec.start else None,
                    'end_datetime': rec.stop if rec.stop else None,
                    'start_date': rec.start if rec.start else None,
                    'end_date': rec.stop if rec.stop else None,
                    'description': rec.description or None,
                    'duration': rec.duration,
                    'requester_id': rec.partner_id.id,
                    'requester_name': rec.partner_id.display_name,
                    'create_date': rec.create_date if rec.create_date else None,
                    'meeting_type_id': rec.meeting_type_id.id or None,
                    'meeting_type_name': rec.meeting_type_id.type_name or None,
                    'attendee_ids': attendee_info,
                    'agenda_ids': agenda_info

                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'error'}
            return data

    @http.route('/api/meeting/get_meeting_by_room_admin_id', type='json', auth='none')
    def get_meeting_by_room_admin_id(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')
        meeting = request.env['calendar.event'].sudo().search(
            [
                ('meeting_state', '=', 'wp'),
                ('room_id.room_admin_id', '=', post.get('room_admin_id'))
            ])
        if meeting:
            data_rec = []
            for rec in meeting:
                # TODO attendee
                public_space_rec = request.env['calendar.attendee'].sudo().search(
                    [
                        ('event_id', '=', rec.id)
                    ])
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
                    [('meeting_id', '=', rec.id)])
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
                    'start': rec.start if rec.start else None,
                    'stop': rec.stop if rec.stop else None,
                    'start_datetime': rec.start if rec.start else None,
                    'end_datetime': rec.stop if rec.stop else None,
                    'start_date': rec.start if rec.start else None,
                    'end_date': rec.stop if rec.stop else None,
                    'description': rec.description or None,
                    'duration': rec.duration,
                    'requester_id': rec.partner_id.id,
                    'requester_name': rec.partner_id.display_name,
                    'create_date': rec.create_date if rec.create_date else None,
                    'meeting_type_id': rec.meeting_type_id.id or None,
                    'meeting_type_name': rec.meeting_type_id.type_name or None,
                    'attendee_ids': attendee_info,
                    'agenda_ids': agenda_info

                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'error'}
            return data

    @http.route('/api/meeting/get_meeting_by_user', type='json', auth='none')
    def get_meeting_by_user(self, **post):
        request.session.db = post.get('db')
        ICT = timezone('Asia/Bangkok')
        meeting = request.env['calendar.event'].sudo().search(
            [
                ('meeting_state', '=', 'ap')
            ])
        if meeting:
            data_rec = []
            for rec in meeting:
                # TODO attendee
                public_space_rec = request.env['calendar.attendee'].sudo().search(
                    [
                        ('event_id', '=', rec.id),
                        ('state', '=', 'accepted'),
                        ('partner_id', '=', post.get('partner_id'))
                    ])
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
                    [('meeting_id', '=', rec.id)])
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
                    'start': rec.start if rec.start else None,
                    'stop': rec.stop if rec.stop else None,
                    'start_datetime': rec.start if rec.start else None,
                    'end_datetime': rec.stop if rec.stop else None,
                    'start_date': rec.start if rec.start else None,
                    'end_date': rec.stop if rec.stop else None,
                    'description': rec.description or None,
                    'duration': rec.duration,
                    'requester_id': rec.partner_id.id,
                    'requester_name': rec.partner_id.display_name,
                    'create_date': rec.create_date if rec.create_date else None,
                    'meeting_type_id': rec.meeting_type_id.id or None,
                    'meeting_type_name': rec.meeting_type_id.type_name or None,
                    'attendee_ids': attendee_info,
                    'agenda_ids': agenda_info

                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'error'}
            return data
