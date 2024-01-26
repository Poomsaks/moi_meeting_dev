# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import date, datetime, timedelta, MAXYEAR
import requests
import json
from odoo.modules import get_module_resource
import csv
import os

_logger = logging.getLogger(__name__)


class MainFunctions(models.Model):
    _name = 'main.functions'
    _description = 'Functions'

    @api.model
    def connect_helios(self):
        # get url host helios
        host_url = self.get_urlconfig('helios')
        # url = "https://helios.demotoday.net/helios/api/token"
        url = host_url + "/helios/api/token"
        client = requests.session()
        # Retrieve the CSRF token first
        client.get(host_url)  # sets the cookie

        # Get user GOV Connect OAuth User ID
        oauth_id = self.env['res.users'].sudo().search([('id', '=', self.env.user.id)], limit=1).oauth_uid
        if not oauth_id:
            raise ValueError('user นี้ไม่ได้เชื่อมต่อ gov connect ไม่สามารถสร้าง helios vote ได้ !!')

        payload = json.dumps({
            "user_type": "connect",
            "user_id": oauth_id,
            # "user_id": "AAAAAAAAAAAAAAAAAAAAACY45seNLvp3Xi5LDEEeXrk",
        })
        session_id = client.cookies.get_dict()
        session = session_id['sessionid']
        # print(session)
        headers = {
            # 'Content-Type': 'application/json',
            'Cookie': 'sessionid=' + str(session)
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        if response.status_code == 200:
            # response.encoding = 'utf-8'
            if response.content:
                print('เชื่อมต่อ helios สำเร็จ')
                return str(response.text), str(session)
        else:
            raise ValueError('เชื่อมต่อ helios ไม่สำเร็จ')

    @api.model
    def get_urlconfig(self, app):
        host_url = self.env['config.url'].sudo().search([('app_name', '=', app)], limit=1).url
        if not host_url:
            raise Warning('ไม่พบ url เชื่อมต่อ' + app)
        else:
            return host_url

    @api.model
    def open_registration(self, election_id, openreg, token, session):

        # Connect helios
        host_url = self.get_urlconfig('helios')
        # url = "https://helios.demotoday.net/helios/api/set_reg?election_id=23451890-413d-11ec-9417-87d834c5eb02&openreg=0"
        url = host_url + "/helios/api/set_reg?election_id=" + election_id + "&openreg=" + str(openreg)
        payload = {}
        headers = {
            'Authorization': str(token),
            # 'Authorization': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc3JmIjoiNzI0MjUyNGQtMGNkZi00ZmNmLWExYzYtOTY4YjhkMTYwYTA2IiwidXNlcl90eXBlIjoibGl2ZSIsInVzZXJfaWQiOiJBQUFBQUFBQUFBQUFBQUFBQUFBQUFDWTQ1c2VOTHZwM1hpNUxERUVlWHJrIn0.SqVat--IiSGfvgscovHY929I56JB9rouygEaRp3cSf8',
            'Cookie': 'sessionid=' + session
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        # print(response.text)
        if response.text == "SUCCESS":
            print("registration " + str(openreg) + "สำเร็จ")