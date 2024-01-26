from json import loads, dumps

from odoo import http
from odoo.http import request
from odoo.tools import json


class ControllerSvAgendaVote(http.Controller):

    @http.route('/api/meeting/create_agenda_vote', type='json', auth='user')
    def create_agenda_vote(self, **post):
        data_create = request.env['common.agenda.vote'].create({
            'agenda_meeting_id': post.get('agenda_meeting_id'),
            'vote_name': post.get('vote_name'),
            'vote_type_id': post.get('vote_type_id'),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/create_update_agenda_vote_choice', type='json', auth='user')
    def create_update_agenda_vote_choice(self, **post):
        data_model = request.env['common.agenda.vote'].sudo().search([('id', '=', post.get('agenda_vote_id'))])
        if data_model:

            for rec in data_model:
                vote_choice = []
                if post.get('vote_choice_ids'):
                    vote_choice_data = json.loads(json.dumps(post.get('vote_choice_ids')))
                    for rec_choice in vote_choice_data:
                        if rec_choice['vote_choice_id']:
                            vote_choice_line = []
                            if rec_choice['vote_choice_line_ids']:
                                vote_choice_data = json.loads(json.dumps(rec_choice['vote_choice_line_ids']))
                                for rec_choice_line in vote_choice_data:
                                    if rec_choice_line['vote_choice_line_id']:
                                        vote_choice_line.append((1, rec_choice_line['vote_choice_line_id'], {
                                            'agenda_vote_choice_id': rec_choice['vote_choice_id'],
                                            'answer_num': rec_choice_line['answer_num'],
                                            'answer_label': rec_choice_line['answer_label'],
                                            'answer': rec_choice_line['answer'],
                                        }))
                                    else:
                                        vote_choice_line.append((0, 0, {
                                            'agenda_vote_choice_id': rec_choice['vote_choice_id'],
                                            'answer_num': rec_choice_line['answer_num'],
                                            'answer_label': rec_choice_line['answer_label'],
                                            'answer': rec_choice_line['answer'],
                                        }))
                            vote_choice.append((1, rec_choice['vote_choice_id'], {
                                'agenda_vote_id': rec.id,
                                'number': rec_choice['number'],
                                'question': rec_choice['question'],
                                'active': rec_choice['active'],
                                'vote_choice_line_ids': vote_choice_line,
                            }))
                        else:
                            vote_choice.append((0, 0, {
                                'agenda_vote_id': rec.id,
                                'number': rec_choice['number'],
                                'question': rec_choice['question'],
                                'active': rec_choice['active'],
                            }))
                data_model.write({
                    'vote_choice_ids': vote_choice,
                })

        data = {'status': 200, 'response': data_model.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/get_agenda_vote', type='json', auth='none')
    def get_agenda_vote(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['common.agenda.vote'].sudo().search(
            [('agenda_meeting_id', '=', post.get('agenda_meeting_id'))])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'agenda_meeting_id': rec.agenda_meeting_id.id,
                    'agenda_title_name': rec.agenda_meeting_id.agenda_title_name,
                    'vote_name': rec.vote_name,
                    'vote_type_id': rec.vote_type_id.id or None,
                    'vote_type_name': rec.vote_type_id.type_name or None,
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล หัวข้อโหวต', 'message': 'success'}
            return data

    @http.route('/api/meeting/create_meeting_agenda', type='json', auth='user')
    def create_meeting_agenda(self, **post):
        data_create = request.env['meeting.agenda'].create({
            'meeting_id': post.get('meeting_id'),
            'agenda_title_name': post.get('agenda_title_name'),
            'agenda_no': post.get('agenda_no'),
            'agenda_detail': post.get('agenda_detail'),
            'vote_state': post.get('vote_state_id')
        })
        sub_agenda_append = []
        if post.get('sub_agenda_ids'):
            detail_data = loads(dumps(post.get('sub_agenda_ids')))
            for rec in detail_data:
                sub_agenda_append.append((0, 0, {
                    'agenda_id': data_create.id,
                    'sub_agenda_no': rec.get('sub_agenda_no'),
                    'sub_agenda_name': rec.get('sub_agenda_name'),
                    'sub_agenda_detail': rec.get('sub_agenda_detail'),
                    'vote_state': rec.get('vote_state')
                }))
            data_create.write({
                'sub_agenda_ids': sub_agenda_append,
            })
            sub_agenda_attach_append = []
            meeting_agenda = request.env['meeting.agenda'].sudo().search([('id', '=', data_create.id)])
            if meeting_agenda:
                sub_agenda_ids = meeting_agenda.sub_agenda_ids
                for sub_agenda in sub_agenda_ids:
                    if post.get('sub_agenda_attach_ids'):
                        detail_data = loads(dumps(post.get('sub_agenda_attach_ids')))
                        for rec2 in detail_data:
                            sub_agenda_attach_append.append((0, 0, {
                                'sub_agenda_id': sub_agenda.id,
                                'attach_user': rec2.get('attach_user'),
                                'attach_type': rec2.get('attach_type'),
                                'attach_flag': rec2.get('attach_flag'),
                                'attachment_file': rec2.get('attachment_file'),
                                'attachment_name': rec2.get('attachment_name'),
                            }))
                    sub_agenda.write({
                        'sub_agenda_attach_ids': sub_agenda_attach_append,
                    })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data

    @http.route('/api/meeting/get_meeting_agenda', type='json', auth='none')
    def get_meeting_agenda(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['meeting.agenda'].sudo().search([('meeting_id', '=', post.get('meeting_id'))])
        if data_info:
            agenda_list = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'agenda_title_name': rec.agenda_title_name or None,
                    'agenda_no': rec.agenda_no,
                    'agenda_detail': rec.agenda_detail or None,
                    'partner_id': rec.partner_id.id or None,
                    'partner_name': rec.partner_id.name or None,
                    'vote_state_id': rec.vote_state or None,
                    'vote_state': rec.vote_state or None,
                    'sub_agenda_ids': [{'id': record.id,
                                        'sub_agenda_no': record.sub_agenda_no or None,
                                        'sub_agenda_name': record.sub_agenda_name or None,
                                        'sub_agenda_detail': record.sub_agenda_detail or None,
                                        'partner_id': record.partner_id.id or None,
                                        'partner_name': record.partner_id.name or None,
                                        'vote_state': record.vote_state or None,
                                        'sub_agenda_attach_ids': [{'id': record_in.id,
                                                                   'attach_user': record_in.attach_user.id,
                                                                   'attach_user_name': record_in.attach_user_name,
                                                                   'attach_type': record_in.attach_type,
                                                                   'attach_flag': record_in.attach_flag,
                                                                   'attachment_file': record_in.attachment_file,
                                                                   'attachment_name': record_in.attachment_name,
                                                                   'attachment_import_date': record_in.attachment_import_date,
                                                                   }
                                                                  for record_in in record.sub_agenda_attach_ids],
                                        }
                                       for record in rec.sub_agenda_ids],
                }
                agenda_list.append(vals)

            data_rec = {
                'meeting_id': post.get('meeting_id'),
                'agenda_list': agenda_list
            }

            data = {'status': 200, 'response': data_rec, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล ชื่อหัวข้อการประชุม', 'message': 'success'}
            return data

    @http.route('/api/meeting/get_agenda_vote_choice', type='json', auth='none')
    def get_agenda_vote_choice(self, **post):
        request.session.db = post.get('db')
        data_info = request.env['common.agenda.vote.choice'].sudo().search([])
        if data_info:
            data_s = []
            for rec in data_info:
                vals = {
                    'id': rec.id,
                    'agenda_vote_id': rec.agenda_vote_id.id or None,
                    'agenda_meeting_id': rec.agenda_meeting_id.id or None,
                    'meeting_name': rec.agenda_meeting_id.meeting_id.name or None,
                    'number': rec.number,
                    'question': rec.question or None,
                    'voted_partner_ids': [{'id': record.id,
                                           'name': record.name, }
                                          for record in rec.voted_partner_ids],
                    'vote_choice_line_ids': [{'id': record.id,
                                              'answer_label': record.answer_label,
                                              'answer': record.answer,
                                              'answer_count': record.answer_count}
                                             for record in rec.vote_choice_line_ids]
                }
                data_s.append(vals)
            data = {'status': 200, 'response': data_s, 'message': 'success'}
            return data
        else:
            data = {'status': 500, 'response': 'ไม่พบข้อมูล หัวข้อโหวต', 'message': 'success'}
            return data

    @http.route('/api/meeting/create_agenda_vote_line', type='json', auth='user')
    def create_agenda_vote_line(self, **post):
        data_create = request.env['common.agenda.vote.line'].create({
            'vote_choice_line_id': post.get('vote_choice_line_id'),
            'vote_answer': post.get('vote_answer'),
            'vote_point': post.get('vote_point'),
            'signature': post.get('signature'),
            'vote_partner_id': post.get('vote_partner_id'),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data
