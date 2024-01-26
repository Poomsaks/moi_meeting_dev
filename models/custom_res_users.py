# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    tmp_oauth_uid = fields.Char(
        string="Temp OAuth User ID",
        help="Technical field to save old oauth_uid"
    )

    user_role = fields.Char(string="Role", required=False)
    user_type = fields.Char(string="User Type", required=False)

    # # @Override
    # @api.model
    # def action_reset_password(self):
    #     """ create signup token for each user, and send their signup url by email """
    #     # prepare reset password signup
    #     create_mode = bool(self.env.context.get('create_user'))
    #
    #     # no time limit for initial invitation, only for reset password
    #     expiration = False if create_mode else now(days=+1)
    #
    #     self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)
    #
    #     # send email to users with their signup url
    #     template = False
    #     if create_mode:
    #         try:
    #             template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
    #         except ValueError:
    #             pass
    #     if not template:
    #         template = self.env.ref('auth_signup.reset_password_email')
    #     assert template._name == 'mail.template'
    #
    #     template_values = {
    #         'email_to': '${object.email|safe}',
    #         'email_cc': False,
    #         'auto_delete': True,
    #         'partner_to': False,
    #         'scheduled_date': False,
    #     }
    #     template.write(template_values)
    #
    #     for user in self:
    #         if not user.email:
    #             raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
    #
    #         # @Remark for not send reset password email.
    #         # with self.env.cr.savepoint():
    #         #     template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
    #         # _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)
    #
    # def chk_deactivate_user_data(self, record_status, personal_code, active=None, uid=None):
    #     deactivate = 0
    #     if record_status != 'A':
    #         deactivate += 1
    #     if personal_code:
    #         list_personal_code = []
    #         config = self.env['ir.config_parameter'].sudo().search([('key', '=', 'fix_active_personal_code')])
    #         if config and type(eval(config.value)) is list:
    #             list_personal_code = eval(config.value)
    #
    #         if (personal_code in list_personal_code):
    #             pass
    #         elif ('-9-' in personal_code):
    #             deactivate += 1
    #
    #     # @Set fix active by param.
    #     if active == False:
    #         deactivate += 1
    #     elif active == True:
    #         deactivate = 0
    #
    #     if deactivate > 0 and self.login != 'admin':
    #         active = False
    #         uid = None
    #
    #         # Query SET Active False
    #         query = """
    #             WITH update_res_users AS (
    #                 UPDATE res_users
    #                 SET active = %(active)s, oauth_uid = %(uid)s
    #                 WHERE id = %(id)s
    #                 RETURNING partner_id
    #             )
    #             UPDATE res_partner SET active = %(active)s
    #             FROM update_res_users
    #             WHERE res_partner.id = update_res_users.partner_id
    #         """
    #
    #     else:
    #         active = True
    #         uid = uid or self.oauth_uid or self.tmp_oauth_uid
    #
    #         # Query SET Active True
    #         query = """
    #             WITH update_res_users AS (
    #                 UPDATE res_users
    #                 SET active = %(active)s, oauth_uid = %(uid)s, tmp_oauth_uid = %(uid)s
    #                 WHERE id = %(id)s
    #                 RETURNING partner_id
    #             )
    #             UPDATE res_partner SET active = %(active)s
    #             FROM update_res_users
    #             WHERE res_partner.id = update_res_users.partner_id
    #         """
    #
    #     # Excute by Odoo Cursor Environment
    #     self.env.cr.execute(query, {
    #         'active': active,
    #         'uid': uid if uid else None,
    #         'id': self.id,
    #     })
    #     self.env.cr.commit()
    #
    #     return active
    #
    # def sync_users(self, view_name, db, create_view=True):
    #     if self.env.cr.dbname != db:
    #         result = 'ข้อมูล database ไม่ถูกต้อง'
    #         return result
    #
    #     if create_view:
    #         # Logical Table Query
    #         query = """
    #             CREATE or REPLACE VIEW {} AS (
    #                 select au.user_name, au.personal_id, cp.record_status, cp.personal_code, cp.personal_fname_tha, cp.personal_lname_tha,
    #                 cp.personal_email, cp.personal_tel_no, cps.position_id, cps.position_name,
    #                 co.organize_id, co.organize_type, co.organize_name_tha
    #                 from ds.adm_user au
    #                 inner join ds.cms_personal cp on au.personal_id = cp.personal_id
    #                 inner join ds.cms_position cps on cp.position_id = cps.position_id
    #                 inner join ds.cms_organize co on cp.org_id = co.organize_id
    #                 where au.user_name != ''
    #                 order by cp.record_status desc, cp.personal_code desc, au.user_name asc
    #             )
    #         """
    #
    #         # Excute by Odoo Cursor Environment
    #         self.env.cr.execute(query.format(view_name))
    #         self.env.cr.commit()
    #
    #     records = 0
    #     success = 0
    #     fail = 0
    #
    #     # @Set for more secure on backend.
    #     # provider = self.env['auth.oauth.provider'].sudo().search([('name', '=', 'OpenID'), ('enabled', '=', True)], limit=1)
    #     provider = self.env['auth.oauth.provider'].sudo().search([('name', '=', 'OpenID')], limit=1)
    #
    #     self.env.cr.execute(
    #         "SELECT * FROM {}".format(view_name)
    #     )
    #     for user_name, personal_id, record_status, personal_code, personal_fname_tha, personal_lname_tha, personal_email, personal_tel_no, \
    #         position_id, position_name, organize_id, organize_type, organize_name_tha in self.env.cr.fetchall():
    #         try:
    #             user_vals = {
    #                 'login': user_name,
    #                 'name': user_name,
    #                 'email': personal_email,
    #                 'phone': personal_tel_no,
    #                 'oauth_provider_id': provider.id,
    #                 'oauth_uid': personal_id,
    #                 # 'notification_type': 'inbox',
    #             }
    #             partner_vals = {
    #                 'firstname': personal_fname_tha,
    #                 'lastname': personal_lname_tha,
    #                 'email': personal_email,
    #                 'phone': personal_tel_no,
    #                 'position_id': position_id,
    #                 'personal_pos': position_name,
    #                 'organize_id': organize_id,
    #                 'organize_type': organize_type,
    #                 'affiliation': organize_name_tha,
    #                 ### Personal Data ###
    #                 'personal_id': personal_id,
    #                 'personal_code': personal_code,
    #             }
    #
    #             user = self.env['res.users'].sudo().search([('oauth_uid', '=', personal_id)], limit=1)
    #             if user:
    #                 user.update(user_vals)
    #                 if user.partner_id:
    #                     user.partner_id.update(partner_vals)
    #                 self.env.cr.commit()
    #
    #                 user.chk_deactivate_user_data(record_status, personal_code)
    #
    #             else:
    #                 user = self.env['res.users'].sudo().search([('login', '=', user_name)], limit=1)
    #                 if user:
    #                     user.update(user_vals)
    #                     if user.partner_id:
    #                         user.partner_id.update(partner_vals)
    #                     self.env.cr.commit()
    #
    #                     user.chk_deactivate_user_data(record_status, personal_code)
    #
    #                 else:
    #                     user = self.env['res.users'].sudo().search([('active', '=', False), ('login', '=', user_name)],
    #                                                                limit=1)
    #                     if user:
    #                         user.update(user_vals)
    #                         if user.partner_id:
    #                             user.partner_id.update(partner_vals)
    #                         self.env.cr.commit()
    #
    #                         user.chk_deactivate_user_data(record_status, personal_code)
    #
    #                     else:
    #                         # @Check if record_status not Active
    #                         # then not insert new user data.
    #                         if record_status != 'A':
    #                             continue
    #
    #                         user_vals.update(active=True)
    #                         new_user = self.env['res.users'].sudo().create(user_vals)
    #                         if new_user.partner_id:
    #                             new_user.partner_id.update(partner_vals)
    #                         self.env.cr.commit()
    #
    #                         new_user.chk_deactivate_user_data(record_status, personal_code)
    #
    #         except Exception:
    #             self.env.cr.commit()
    #             fail += 1
    #             continue
    #         success += 1
    #
    #     records = success + fail
    #     result = {
    #         'records': records,
    #         'success': success,
    #         'fail': fail,
    #     }
    #     return result
    #
    # def sync_personal_data_uid(self, uid=None):
    #     uid = uid or self.oauth_uid
    #     result = False
    #     try:
    #         # Logical Table Query
    #         query = """
    #             SELECT * FROM view_user_data
    #             WHERE personal_id = {}
    #             AND record_status = 'A'
    #             AND personal_code NOT LIKE '%-9-%'
    #             LIMIT 1
    #         """
    #
    #         # Excute by Odoo Cursor Environment
    #         self.env.cr.execute(query.format(uid))
    #         query_res = self.env.cr.dictfetchall()
    #
    #         record_status = None
    #         personal_code = None
    #         vals = {}
    #         for res in query_res:
    #             record_status = res['record_status']
    #             personal_code = res['personal_code']
    #             vals.update({
    #                 'firstname': res['personal_fname_tha'],
    #                 'lastname': res['personal_lname_tha'],
    #                 'email': res['personal_email'],
    #                 'phone': res['personal_tel_no'],
    #                 'position_id': res['position_id'],
    #                 'personal_pos': res['position_name'],
    #                 'organize_id': res['organize_id'],
    #                 'organize_type': res['organize_type'],
    #                 'affiliation': res['organize_name_tha'],
    #                 ### Personal Data ###
    #                 'personal_id': res['personal_id'],
    #                 'personal_code': res['personal_code'],
    #             })
    #
    #         if self.partner_id:
    #             self.partner_id.update(vals)
    #         self.env.cr.commit()
    #
    #         self.chk_deactivate_user_data(record_status, personal_code)
    #         result = True
    #
    #     except Exception:
    #         self.env.cr.commit()
    #         result = False
    #
    #     return result
    #
    # def sync_personal_data_login(self, login=None, active=None, uid=None):
    #     login = login or self.login
    #     result = False
    #     try:
    #         # Logical Table Query
    #         query = """
    #             SELECT * FROM view_user_data
    #             WHERE user_name = %(login)s
    #             AND record_status = %(record_status)s
    #             AND personal_code NOT LIKE %(personal_code)s
    #             LIMIT 1
    #         """
    #
    #         # Excute by Odoo Cursor Environment
    #         self.env.cr.execute(query, {
    #             'login': login,
    #             'record_status': 'A',
    #             'personal_code': '%-9-%',
    #         })
    #         query_res = self.env.cr.dictfetchall()
    #
    #         record_status = None
    #         personal_code = None
    #         personal_id = uid
    #         vals = {}
    #         for res in query_res:
    #             record_status = res['record_status']
    #             personal_code = res['personal_code']
    #             personal_id = uid or res['personal_id']
    #             vals.update({
    #                 'firstname': res['personal_fname_tha'],
    #                 'lastname': res['personal_lname_tha'],
    #                 'email': res['personal_email'],
    #                 'phone': res['personal_tel_no'],
    #                 'position_id': res['position_id'],
    #                 'personal_pos': res['position_name'],
    #                 'organize_id': res['organize_id'],
    #                 'organize_type': res['organize_type'],
    #                 'affiliation': res['organize_name_tha'],
    #                 ### Personal Data ###
    #                 'personal_id': res['personal_id'],
    #                 'personal_code': res['personal_code'],
    #             })
    #
    #         if vals:
    #             if self.partner_id:
    #                 self.partner_id.update(vals)
    #             self.env.cr.commit()
    #             self.chk_deactivate_user_data(record_status, personal_code, active=active, uid=personal_id)
    #             result = True
    #         else:
    #             self.env.cr.commit()
    #             result = False
    #
    #     except Exception:
    #         self.env.cr.commit()
    #         result = False
    #
    #     if not result and active != None:
    #         result = self.chk_deactivate_user_data(record_status=None, personal_code=None, active=active, uid=uid)
    #
    #     return result
