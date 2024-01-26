from odoo import http
from odoo.http import request
from odoo.tools import json


class ConMtType(http.Controller):
    @http.route('/api/meeting/create_mt_type_vote', type='json', auth='user')
    def create_mt_type_vote(self, **post):
        data_create = request.env['mt.type.vote'].create({
            'type_name': post.get('type_name'),
            'type_vote': post.get('type_vote'),
        })
        data = {'status': 200, 'response': data_create.id, 'message': 'success'}
        return data
