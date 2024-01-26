# -*- coding: utf-8 -*-

import base64
import json

from odoo import http
from odoo.http import request
from odoo import fields

from pytz import timezone


class ConRoom(http.Controller):

    @http.route('/api/meeting/get_room_meeting', type='json', auth='none')
    def get_room_meeting(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.room'].sudo().search([])
        data_s = []
        if not data_info:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'error'}
            return data
        for room in data_info:
            # TODO equipment
            equipment_rec = request.env['mt.room.equipment'].sudo().search([('room_id', '=', room.id)])
            equipment_info = {
                "counter": len(equipment_rec),
                "equipment_ids": []
            }
            for equipment in equipment_rec:
                equipment_info['equipment_ids'].append({
                    'id': equipment.id or None,
                    'room_id': equipment.room_id.id or None,
                    'equipment_id': equipment.equipment_id.id or None,
                    'equipment_unit': equipment.equipment_unit or None,
                    'equipment_qty': equipment.equipment_qty or None,
                })
            # TODO services
            services_rec = request.env['mt.room.services'].sudo().search([('room_id', '=', room.id)])
            services_info = {
                "counter": len(services_rec),
                "services_ids": []
            }
            for services in services_rec:
                services_info['services_ids'].append({
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
                    'room_address': rec.room_address,
                    'access_type': rec.access_type,
                    'room_type': rec.room_type,
                    'organize_id': rec.organize_id,
                    'organize_type': rec.organize_type,
                    'meeting_color': rec.meeting_color,
                    # 'room_status': rec.room_status,
                    'active': rec.active,
                    'type_meeting_id': rec.type_meeting_id.id,
                    'equipment_ids': equipment_info,
                    'services_ids': services_info,
                }
                data_s.append(vals)
        data = {'status': 200, 'response': data_s, 'message': 'success'}
        return data

    @http.route('/api/meeting/create_room_meeting', type='json', auth='user')
    def create_room_meeting(self, **post):
        data_create = request.env['mt.room'].create({
            'room_name': post.get('room_name'),
            'floor': post.get('floor'),
            'people_in_room': post.get('people_in_room'),
            'image': post.get('image'),
            'room_address': post.get('room_address'),
            'access_type': post.get('access_type', 'public'),
            'access_partner_ids': [(6, 0, post.get('access_partner_ids'))] if post.get('access_partner_ids') else [],
            'room_type': post.get('room_type'),
            'type_meeting_id': post.get('type_meeting_id'),
            'room_admin_id': post.get('room_admin_id'),
            'organize_id': post.get('organize_id'),
            'organize_type': post.get('organize_type'),
            'service_status': post.get('service_status', True),
            'room_status': post.get('room_status'),
            'meeting_color': post.get('meeting_color'),
            'active': post.get('active', True),
            'partner_id': post.get('partner_id'),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/get_room_meeting_by_id', type='json', auth='none')
    def get_room_meeting_by_id(self, **post):
        request.session.db = post.get('db')
        rooms = request.env['mt.room'].sudo().search([('id', '=', post.get('id')), ('active', '=', True)])
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

                    # 'room_type_ids': rec.type_meeting_id.id or None,
                    'room_type_ids': [{'id': record.id,
                                       'type_room': record.type_room, }
                                      for record in rec.room_type_ids],

                    # 'type_meeting': rec.type_meeting_id.type_name or None,
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

    @http.route('/api/meeting/update_room_meeting', type='json', auth='user')
    def update_room_meeting(self, **post):
        data_model = request.env['mt.room'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.write({
                'room_name': post.get('room_name'),
                'floor': post.get('floor', data_model.floor),
                'people_in_room': post.get('people_in_room', data_model.people_in_room),
                'image': post.get('image', data_model.image),
                'room_address': post.get('room_address', data_model.room_address),
                'access_type': post.get('access_type', data_model.access_type),
                'access_partner_ids': [(6, 0, post.get('access_partner_ids', data_model.access_partner_ids.ids) or [])],
                'room_type': post.get('room_type', data_model.room_type),
                'type_meeting_id': post.get('type_meeting_id', data_model.type_meeting_id),
                'room_admin_id': post.get('room_admin_id', data_model.room_admin_id),
                'organize_id': post.get('organize_id', data_model.organize_id),
                'organize_type': post.get('organize_type', data_model.organize_type),
                'service_status': post.get('service_status', data_model.service_status),
                'room_status': post.get('room_status', data_model.room_status),
                'meeting_color': post.get('meeting_color', data_model.meeting_color),
                'active': post.get('active', True),
                'partner_id': post.get('partner_id'),
            })
            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อห้องประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_room_meeting', type='json', auth='user')
    def delete_room_meeting(self, **post):
        data_model = request.env['mt.room'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.unlink()
            data = {'status': 200, 'response': 'Delete success', 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่อห้องประชุม', 'message': 'success'}
            return data

    ### API Meeting Equipment --------------------------------

    @http.route('/api/meeting/create_update_room_equipment', type='json', auth='user')
    def create_update_room_equipment(self, **post):
        data_model = request.env['mt.room.equipment'].search([('room_id', '=', post.get('room_id'))])

        count_create = 0
        count_update = 0
        equipment_list = post.get('equipment_list')
        for rec in equipment_list:
            update_model = data_model.filtered(lambda r: r.id == rec.get('id')) if rec.get('id') else None
            if update_model:
                update_model.write({
                    'equipment_id': rec.get('equipment_id', update_model.equipment_id.id),
                    # 'equipment_unit': rec.get('equipment_unit', update_model.equipment_unit),
                    'equipment_qty': rec.get('equipment_qty', update_model.equipment_qty),
                })
                count_update += 1
            else:
                data_create = request.env['mt.room.equipment'].create({
                    'room_id': post.get('room_id'),
                    'equipment_id': rec.get('equipment_id'),
                    # 'equipment_unit': rec.get('equipment_unit'),
                    'equipment_qty': rec.get('equipment_qty') or 1,
                })
                count_create += 1

        records = count_create + count_update
        result = {
            'records': records,
            'create': count_create,
            'update': count_update,
        }

        data = {'status': 200, 'response': result, 'message': 'success'}
        return data

    @http.route('/api/meeting/get_room_equipment', type='json', auth='none')
    def get_room_equipment(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.room.equipment'].sudo().search([('room_id', '=', post.get('room_id'))])
        if data_info:
            equipment_list = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'equipment_id': rec.equipment_id.id,
                    'equipment_name': rec.equipment_id.equip_name,
                    'equipment_unit': rec.equipment_unit or None,
                    'equipment_qty': rec.equipment_qty or None,
                }
                equipment_list.append(vals)

            data_rec = {
                'room_id': post.get('room_id'),
                'equipment_list': equipment_list
            }

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล รายการอุปกรณ์', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_room_equipment', type='json', auth='user')
    def delete_room_equipment(self, **post):
        if post.get('id'):
            data_model = request.env['mt.room.equipment'].search(
                [('room_id', '=', post.get('room_id')), ('id', '=', post.get('id'))])
            if data_model:
                data_model.unlink()

                data = {'status': 200, 'response': 'Delete Success', 'message': 'success'}
                return data

        elif post.get('ids'):
            data_model = request.env['mt.room.equipment'].search(
                [('room_id', '=', post.get('room_id')), ('id', 'in', post.get('ids'))])
            if data_model:
                data_model.unlink()

                data = {'status': 200, 'response': 'Delete Success', 'message': 'success'}
                return data

        data = {'status': 500, 'response': 'ไม่พบข้อมูล รายการอุปกรณ์', 'message': 'success'}
        return data

    # ---------------------------------------------

    ### API Meeting Services --------------------------------

    @http.route('/api/meeting/create_update_room_services', type='json', auth='user')
    def create_update_room_services(self, **post):
        data_model = request.env['mt.room.services'].search([('room_id', '=', post.get('room_id'))])

        count_create = 0
        count_update = 0
        services_list = post.get('services_list')
        for rec in services_list:
            update_model = data_model.filtered(lambda r: r.id == rec.get('id')) if rec.get('id') else None
            if update_model:
                update_model.write({
                    'service_id': rec.get('service_id', update_model.service_id.id),
                    # 'service_type': rec.get('service_type', update_model.service_type),
                    'service_qty': rec.get('service_qty', update_model.service_qty),
                })
                count_update += 1
            else:
                data_create = request.env['mt.room.services'].create({
                    'room_id': post.get('room_id'),
                    'service_id': rec.get('service_id'),
                    # 'service_type': rec.get('service_type'),
                    'service_qty': rec.get('service_qty') or 1,
                })
                count_create += 1

        records = count_create + count_update
        result = {
            'records': records,
            'create': count_create,
            'update': count_update,
        }

        data = {'status': 200, 'response': result, 'message': 'success'}
        return data

    @http.route('/api/meeting/get_room_services', type='json', auth='none')
    def get_room_services(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.room.services'].sudo().search([('room_id', '=', post.get('room_id'))])
        if data_info:
            services_list = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'service_id': rec.service_id.id,
                    'service_name': rec.service_id.service_name,
                    'service_type': rec.service_type,
                    'service_qty': rec.service_qty,
                }
                services_list.append(vals)

            data_rec = {
                'room_id': post.get('room_id'),
                'services_list': services_list
            }

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล บริการ', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_room_services', type='json', auth='user')
    def delete_room_services(self, **post):
        if post.get('id'):
            data_model = request.env['mt.room.services'].search(
                [('room_id', '=', post.get('room_id')), ('id', '=', post.get('id'))])
            if data_model:
                data_model.unlink()

                data = {'status': 200, 'response': 'Delete Success', 'message': 'success'}
                return data

        elif post.get('ids'):
            data_model = request.env['mt.room.services'].search(
                [('room_id', '=', post.get('room_id')), ('id', 'in', post.get('ids'))])
            if data_model:
                data_model.unlink()

                data = {'status': 200, 'response': 'Delete Success', 'message': 'success'}
                return data

        data = {'status': 500, 'response': 'ไม่พบข้อมูล บริการ', 'message': 'success'}
        return data

        # ---------------------------------------------
