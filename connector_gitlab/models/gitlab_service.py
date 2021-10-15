# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import json
import requests
import logging

from datetime import datetime

from odoo import _, api, models, fields

_logger = logging.getLogger(__name__)

TIMEOUT = 20
PARAMS_METHODS = ('GET', 'DELETE', 'HEAD')
DATA_METHODS = ('POST', 'PATCH', 'PUT')
PROVIDER = 'odoo'


class GitlabService(models.AbstractModel):
    _name = 'gitlab.service'

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

    def _get_user_id(self, odoo_id, search_email=False):
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

    def create_user(self, odoo_id, email, password):
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
            'name': email,
        }
        status, response, headers, ask_time = self._do_request(
            '/api/v4/users', params, self._get_common_headers(), 'POST'
        )
        if status == 201:
            return response.get('id')
        return 0

    def update_user(self, odoo_id, email, password):
        id = self._get_user_id(odoo_id, email)
        if id:
            username = self._get_username_from_email(email)
            params = {
                'extern_uid': str(odoo_id),
                'provider': PROVIDER,
                'email': email,
                'username': username,
                'password': password,
                'name': email,
            }
            status, response, headers, ask_time = self._do_request(
                '/api/v4/users/%d' % (id), params, self._get_common_headers(), 'PUT'
            )
        return status, response, headers, ask_time

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
        token, preuri = self._get_token_preuri()
        headers.update({'PRIVATE-TOKEN': token})
        ask_time = fields.Datetime.now()
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
            # print(status, res, res.content, res.headers,  dir(res))
            status = res.status_code
            headers = res.headers
            response = res.json() if res.content else {}

            try:
                ask_time = datetime.strptime(
                    res.headers.get('date'), "%a, %d %b %Y %H:%M:%S %Z"
                )
            except Exception as e:
                _logger.exception("GitLab date: %s" % str(e))
        except requests.HTTPError as error:
            _logger.exception(
                "Bad GitLab request with params %s : %s !", params,
                error.response.content
            )
            if error.response.status_code in (400, 401, 410):
                raise error
            raise self.env['res.config.settings'].get_config_warning(
                _("Something went wrong with your request to GitLab")
            )
        return (status, response, headers, ask_time)
