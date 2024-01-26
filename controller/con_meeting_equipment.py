# -*- coding: utf-8 -*-

import base64
import json

from odoo import http
from odoo.http import request
from odoo import fields

from pytz import timezone


class ConMeetingEquipment(http.Controller):

    @http.route('/api/meeting/get_equipment', type='json', auth='none')
    def get_equipment(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.equipment'].sudo().search([('active', '=', True)])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'equip_name': rec.equip_name,
                    'equip_brand': rec.equip_brand or None,
                    'equip_quantity': rec.equip_quantity,
                    'uom_name': rec.equip_unit or None,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่ออุปกรณ์', 'message': 'success'}
            return data
        
    @http.route('/api/meeting/create_update_meeting_equipment', type='json', auth='user')
    def create_update_meeting_equipment(self, **post):
        data_model = request.env['calendar.event'].sudo().search([('id', '=', post.get('meeting_id'))])
        if data_model:
            for rec in data_model:
                equipment_ids_to_remove = rec.equipment_ids.ids
                if equipment_ids_to_remove:
                    rec.equipment_ids.unlink()
        if data_model:
            equipment_list = []
            if post.get('equipment_ids'):
                equipment_data = json.loads(json.dumps(post.get('equipment_ids')))
                for rec in equipment_data:
                    if rec['equip_id']:
                        equipment_list.append((1, rec['equip_id'], {
                            'meeting_id': post.get('meeting_id'),
                            'equipment_id': rec['equipment_id'],
                            'equipment_unit': rec['equipment_unit'],
                            'equipment_qty': rec['equipment_qty'],
                        }))
                    else:
                        equipment_list.append((0, 0, {
                            'meeting_id': post.get('meeting_id'),
                            'equipment_id': rec['equipment_id'],
                            'equipment_unit': rec['equipment_unit'],
                            'equipment_qty': rec['equipment_qty'],
                        }))

            data_model.write({
                'equipment_ids': equipment_list,
            })

        data = {'status': 200, 'response': data_model.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/get_meeting_equipment', type='json', auth='none')
    def get_meeting_equipment(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['meeting.equipment'].sudo().search([('meeting_id', '=', post.get('meeting_id'))])
        if data_info:
            equipment_list = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'equipment_id': rec.equipment_id.id or None,
                    'equipment_name': rec.equipment_id.equip_name or None,
                    'equipment_unit': rec.equipment_unit or None,
                    'equipment_qty': rec.equipment_qty or None,
                }
                equipment_list.append(vals)

            data_rec = {
                'meeting_id': post.get('meeting_id'),
                'equipment_list': equipment_list
            }

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล รายการอุปกรณ์', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_equipment_by_id', type='json', auth='none')
    def get_equipment_by_id(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['mt.equipment'].sudo().search([('id', '=', post.get('id'))])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'equip_name': rec.equip_name,
                    'equip_brand': rec.equip_brand or None,
                    'equip_quantity': rec.equip_quantity,
                    'uom_name': rec.equip_unit or None,
                    'active': rec.active,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่ออุปกรณ์', 'message': 'success'}
            return data

    @http.route('/api/meeting/create_equipment', type='json', auth='user')
    def create_equipment(self, **post):
        data_create = request.env['mt.equipment'].create({
            'equip_name': post.get('equip_name'),
            'equip_brand': post.get('equip_brand'),
            'equip_quantity': post.get('equip_quantity'),
            'equip_unit': post.get('uom_name'),
            'active': post.get('active', True),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/update_equipment', type='json', auth='user')
    def update_equipment(self, **post):
        data_model = request.env['mt.equipment'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.write({
                'equip_name': post.get('equip_name'),
                'equip_brand': post.get('equip_brand'),
                'equip_quantity': post.get('equip_quantity'),
                'equip_unit': post.get('uom_name'),
                'active': post.get('active', True),
            })
            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่ออุปกรณ์', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_equipment', type='json', auth='user')
    def delete_equipment(self, **post):
        data_model = request.env['mt.equipment'].search([('id', '=', post.get('id'))])
        if data_model:
            data_model.unlink()
            data = {'status': 200, 'response': 'Delete success', 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูลชื่ออุปกรณ์', 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_meeting_equipment', type='json', auth='user')
    def delete_meeting_equipment(self, **post):
        if post.get('id'):
            data_model = request.env['meeting.equipment'].search(
                [('meeting_id', '=', post.get('meeting_id')), ('id', '=', post.get('id'))])
            if data_model:
                data_model.unlink()

                data = {'status': 200, 'response': 'Delete Success', 'message': 'success'}
                return data

        elif post.get('ids'):
            data_model = request.env['meeting.equipment'].search(
                [('meeting_id', '=', post.get('meeting_id')), ('id', 'in', post.get('ids'))])
            if data_model:
                data_model.unlink()

                data = {'status': 200, 'response': 'Delete Success', 'message': 'success'}
                return data

        data = {'status': 500, 'response': 'ไม่พบข้อมูล รายการอุปกรณ์', 'message': 'success'}
        return data