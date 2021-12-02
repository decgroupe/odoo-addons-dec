# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import json
import requests
import logging

from lxml import html
from datetime import datetime

from odoo import _, api, models, fields
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

TIMEOUT = 20
PARAMS_METHODS = ('GET', 'DELETE', 'HEAD')
DATA_METHODS = ('POST', 'PATCH', 'PUT')
PROVIDER = 'odoo'


class GitlabService(models.AbstractModel):
    _name = 'gitlab.service'
    _description = 'GitLab Service'

    def _get_token_preuri(self):
        ICP = self.env['ir.config_parameter'].sudo()
        token = ICP.get_param('gitlab.private_token')
        preuri = ICP.get_param("gitlab.pre_uri")
        return token, preuri

    def _get_common_headers(self):
        return {
            'Cache-control': 'no-cache',
            'Content-encoding': 'utf-8',
        }

    def _get_user_uid(self, odoo_id, search_email=False):
        params = {
            'extern_uid': str(odoo_id),
            'provider': PROVIDER,
        }
        status, response, headers, ask_time = self._do_request(
            '/api/v4/users', params, self._get_common_headers(), 'GET'
        )
        # If no result, use the GitLab built-in search method
        # to retrieve a possible existing account
        if status == 200 and len(response) == 0 and search_email:
            params = {
                'search': search_email,
            }
            status, response, headers, ask_time = self._do_request(
                '/api/v4/users', params, self._get_common_headers(), 'GET'
            )
        if status == 200 and len(response) == 1:
            return response[0].get('id')
        return 0

    def _get_username_from_email(self, email):
        return email.replace('@', '-').replace('+', '-')

    def create_user(self, odoo_id, email, name, password):
        username = self._get_username_from_email(email)
        params = {
            'extern_uid': str(odoo_id),
            'provider': PROVIDER,
            'email': email,
            'username': username,
            'password': password,
            'reset_password': False,
            'skip_confirmation': True,
            'external': True,
            'projects_limit': 0,
            'name': name,
        }
        status, response, headers, ask_time = self._do_request(
            '/api/v4/users', params, self._get_common_headers(), 'POST'
        )
        if status == 201:
            return response.get('id')
        return 0

    def create_or_update_user(self, odoo_id, email, name, password=False):
        search_email = self.env.context.get('search_email', email)
        user_uid = self._get_user_uid(odoo_id, search_email)
        if user_uid:
            username = self._get_username_from_email(email)
            # We also update the extern_uid for users previoulsy created
            # (manually) in GitLab
            params = {
                'extern_uid': str(odoo_id),
                'provider': PROVIDER,
                'email': email,
                'username': username,
                'name': name,
                'skip_confirmation': True,
                'skip_reconfirmation': True,
            }
            if password:
                params.update({
                    'password': password,
                })
            status, response, headers, ask_time = self._do_request(
                '/api/v4/users/%d' % (user_uid), params,
                self._get_common_headers(), 'PUT'
            )
            if status == 200:
                return response.get('id')
        elif password:
            return self.create_user(odoo_id, email, name, password)
        else:
            raise UserError(
                _(
                    "This User exists in the Odoo portal but not in GitLab.\n"
                    "To fix this error, please create an external User in "
                    "GitLab with this email and retry:\n"
                    "%s"
                ) % (search_email)
            )

    def add_project_member(self, project_uid, user_uid, access_level=10):
        """ Adds a member to a group or project. 

        Args:
            project_uid ([int]): GitLab project database identifier
            user_uid ([int]): GitLab user database identifier
            access_level ([int]): GitLab access level
                Possible values:
                    0:  No access
                    5:  Minimal access (Introduced in GitLab 13.5.)
                    10: Guest
                    20: Reporter
                    30: Developer
                    40: Maintainer
                    50: Owner - Only valid to set for groups 

        Returns:
            [type]: [description]
        """

        params = {
            'user_id': user_uid,
            'access_level': access_level,
        }
        status, response, headers, ask_time = self._do_request(
            '/api/v4/projects/%d/members' % (project_uid), params,
            self._get_common_headers(), 'POST'
        )
        return status == 201

    def remove_project_member(self, project_uid, user_uid):
        params = {}
        status, response, headers, ask_time = self._do_request(
            '/api/v4/projects/%d/members/%d' % (project_uid, user_uid), params,
            self._get_common_headers(), 'DELETE'
        )
        return status == 204

    def get_project_members(self, project_uid):
        params = {}
        status, response, headers, ask_time = self._do_request(
            '/api/v4/projects/%d/members' % (project_uid), params,
            self._get_common_headers(), 'GET'
        )
        return response

    def get_user_memberships(self, user_uid):
        params = {}
        status, response, headers, ask_time = self._do_request(
            '/api/v4/users/%d/memberships' % (user_uid), params,
            self._get_common_headers(), 'GET'
        )
        return response

    def _do_request(
        self,
        uri,
        params=None,
        headers=None,
        method='POST',
    ):
        """ Execute the request to GitLab API (https://docs.gitlab.com/ee/api).

        Args:
            :param uri : the url to contact
            :param params : dict or already encoded parameters for the request
                to make
            :param headers : headers of request
            :param method : the method to use to make the request
            :param params_as_json : if True, the params dict will be converted
                to json string

        Returns: a tuple ('HTTP_CODE', 'HTTP_RESPONSE', ask_time)

            List of possible 'HTTP_CODE':
            200 OK: The GET, PUT or DELETE request was successful, and the
                resource(s) itself is returned as JSON.
            204 No Content: The server has successfully fulfilled the request,
                and there is no additional content to send in the response
                payload body.
            201 Created: The POST request was successful, and the resource is
                returned as JSON.
            304 Not Modified: The resource hasn’t been modified since the last
                request.
            400 Bad Request: A required attribute of the API request is
                missing. For example, the title of an issue is not given.
            401 Unauthorized: The user isn’t authenticated. A valid user token
                is necessary.
            403 Forbidden: The request isn’t allowed. For example, the user
                isn’t allowed to delete a project.
            404 Not Found: A resource couldn’t be accessed. For example, an ID
                for a resource couldn’t be found.
            405 Method Not Allowed: The request isn’t supported.
            409 Conflict: A conflicting resource already exists. For example,
                creating a project with a name that already exists.
            412 ---: The request was denied. This can happen if the
                If-Unmodified-Since header is provided when trying to delete a
                resource, which was modified in between.
            422 Unprocessable: The entity couldn’t be processed.
            429 Too Many Requests: The user exceeded the application rate
                limits.
            500 Server Error: While handling the request, something went wrong
                on the server. 
        """
        if params is None:
            params = {}
        if headers is None:
            headers = {}
        _logger.debug(
            "Uri: %s - method : %s - Headers: %s - Params : %s !", uri, method,
            headers, params
        )
        ask_time = fields.Datetime.now()

        def res_to_tuple(response, ask_time):
            status = response.status_code
            headers = response.headers
            response = response.json() if response.content else {}
            try:
                ask_time = datetime.strptime(
                    headers.get('Date'), "%a, %d %b %Y %H:%M:%S %Z"
                )
            except Exception as e:
                _logger.exception("GitLab date: %s" % str(e))

            res = (status, response, headers, ask_time)
            _logger.debug(res)
            return res

        token, preuri = self._get_token_preuri()
        headers.update({'PRIVATE-TOKEN': token})
        try:
            uri = preuri + uri
            if method.upper() in PARAMS_METHODS:
                res = requests.request(
                    method.lower(),
                    uri,
                    params=params,
                    headers=headers,
                    timeout=TIMEOUT
                )
            elif method.upper() in DATA_METHODS:
                headers.update({'Content-type': 'application/json'})
                res = requests.request(
                    method.lower(),
                    uri,
                    data=json.dumps(params),
                    headers=headers,
                    timeout=TIMEOUT
                )
            else:
                raise Exception(
                    _('Method not supported [%s] not in %s!') %
                    (method, PARAMS_METHODS + DATA_METHODS)
                )
            res.raise_for_status()
            result = res_to_tuple(res, ask_time)

        except requests.HTTPError as error:
            _logger.exception(
                "Bad GitLab request with params %s : %s !", params,
                error.response.content
            )
            result = res_to_tuple(error.response, ask_time)
            if result[1] and result[1].get('message'):
                message = str(result[1].get('message'))
            else:
                message = str(result[0])
            raise UserError(
                _("Something went wrong with a request to GitLab: %s") %
                (message)
            )
        return result

    def _get_session(self, login, password):
        """ The `session` api endpoint has been removed since GitLab 10.2, so
            we use this hack to get a session token
        """
        res = False
        crsf_token = False
        token, preuri = self._get_token_preuri()
        session = requests.Session()
        sign_in_page = session.get(preuri + '/users/sign_in').content
        sign_in_page_tree = html.fromstring(sign_in_page)

        crsf_input = sign_in_page_tree.xpath(
            "//div[@id='login-pane']//form/input[@name='authenticity_token']"
        )
        if crsf_input:
            crsf_token = crsf_input[0].value
        if not crsf_token:
            raise UserError(_("Unable to find the authenticity token"))
        data = {
            'user[login]': login,
            'user[password]': password,
            'authenticity_token': crsf_token,
        }
        r = session.post(preuri + '/users/sign_in', data=data)
        if r.status_code == 200:
            # We need to check if the `known_sign_in` cookie is there, as it
            # is the only way to know if the sign in was successfull.
            if 'known_sign_in' in session.cookies:
                res = session.cookies.get('_gitlab_session', res)
        else:
            raise UserError(_("Failed to sign in, error %d") % (r.status_code))
        return res
