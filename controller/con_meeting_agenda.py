from odoo import http
from odoo.http import request


class ControllerAgenda(http.Controller):

    @http.route('/api/meeting/create_personal_note', type='json', auth='none')
    def create_personal_note(self, **post):
        request.session.db = post.get('db')
        data_create = request.env['meeting.agenda.personal.note'].create({
            'agenda_id': post.get('agenda_id'),
            'partner_id': post.get('partner_id'),
            'note_detail': post.get('note_detail'),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/update_personal_note', type='json', auth='none')
    def update_personal_note(self, **post):
        request.session.db = post.get('db')
        data_model = request.env['meeting.agenda.personal.note'].sudo().search(
            [('id', '=', post.get('id'))])
        if data_model:
            data_model.write({
                'note_detail': post.get('note_detail'),
            })
            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล การประชุม', 'message': 'error'}
            return data

    @http.route('/api/meeting/get_personal_note', type='json', auth='none')
    def get_personal_note(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['meeting.agenda.personal.note'].search([])
        if data_info:
            data_rec = {
                'agenda_id': data_info.agenda_id.id,
                'id': data_info.id,
                'partner_id': data_info.partner_id.id,
                'note_detail': data_info.note_detail or None
            }
            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'error'}
            return data

    @http.route('/api/meeting/get_personal_note_by_partner_id', type='json', auth='none')
    def get_personal_note_by_partner_id(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['meeting.agenda.personal.note'].search([
            ('agenda_id', '=', post.get('agenda_id')),
            ('partner_id', '=', post.get('partner_id'))])
        if data_info:
            data_rec = {
                'agenda_id': data_info.agenda_id.id,
                'id': data_info.id,
                'partner_id': data_info.partner_id.id,
                'note_detail': data_info.note_detail or None
            }
            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล', 'message': 'error'}
            return data