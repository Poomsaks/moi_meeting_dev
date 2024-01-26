from odoo import http
from odoo.http import request


class ConWorkGroup(http.Controller):

    @http.route('/api/meeting/get_work_group', type='json', auth='none')
    def get_work_group(self, **post):
        request.session.db = post.get('db')
        groups = request.env['mt.work.group'].sudo().search([('active', '=', True)])
        if groups:
            data_rec = []
            for rec in groups:
                data_agenda = []
                for agenda in rec.agenda_ids:
                    vals = {
                        'agenda_id': agenda.agenda_id.id,
                        'agenda_no': agenda.agenda_no,
                        'agenda_name': agenda.agenda_id.agenda_name,
                    }
                    data_agenda.append(vals)

                data_personal = []
                for personal in rec.personal_ids:
                    vals = {
                        'personal_id': personal.personal_id.id,
                        'pos_work_no': personal.pos_work_no,
                        'personal_name': personal.personal_id.name,
                        'personal_pos': personal.personal_pos,
                        'pos_in_meeting': personal.pos_work_id.pos_name,
                    }
                    data_personal.append(vals)

                vals = {
                    'id': rec.id,
                    'work_group_name': rec.work_group_name or "",
                    'work_group_last_mame': rec.work_group_last_mame or "",
                    'work_group_doc': rec.work_group_doc or "",
                    'work_group_type_id': rec.work_group_type,
                    'work_group_type': dict(rec._fields['work_group_type'].selection).get(rec.work_group_type),
                    'position_id': rec.position_id.id or "",
                    'position_name': rec.position_id.name or "",
                    'agenda_ids': data_agenda or "",
                    'personal_ids': data_personal or "",
                    'create_date': rec.create_date or "",
                    'write_date': rec.write_date or "",
                }
                data_rec.append(vals)

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data

    @http.route('/api/meeting/create_work_group', type='json', auth='user')
    def create_work_group(self, **post):
        data_create = request.env['mt.work.group'].create({
            'work_group_name': post.get('work_group_name'),
            'work_group_last_mame': post.get('work_group_last_mame'),
            'work_group_doc': post.get('work_group_doc'),
            'position_id': post.get('position_id'),
            'work_group_type': post.get('work_group_type_id'),
            'active': post.get('active', True),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/update_work_group', type='json', auth='user')
    def update_work_group(self, **post):
        data_model = request.env['mt.work.group'].sudo().search(
            [('id', '=', post.get('id'))])
        if data_model:
            data_model.write({
                'work_group_name': post.get('work_group_name'),
                'work_group_last_mame': post.get('work_group_last_mame'),
                'work_group_doc': post.get('work_group_doc'),
                'position_id': post.get('position_id'),
                'work_group_type': post.get('work_group_type_id'),
                'active': post.get('active'),
            })
            data = {'status': 200, 'response': data_model.id, 'message': 'success'}
            return data

    @http.route('/api/meeting/delete_work_group', type='json', auth='user')
    def delete_work_group(self, **post):
        data_model = request.env['mt.work.group'].sudo().search(
            [('id', '=', post.get('id'))])
        if data_model:
            data_model.unlink()
            data = {'status': 200, 'response': 'Delete success', 'message': 'success'}
            return data
