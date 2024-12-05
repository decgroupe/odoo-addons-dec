# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024

from odoo import http
from odoo.http import request


class HttpControllerUser(http.Controller):
    """Http Controller for Localisation"""

    #######################################################################

    def _override_request_with_user(self, user_id=False):
        """Replace request's user with another one and update context to use this new
        users's language. This context update is needed to ensure translation are
        effective because GettextAlias._get_lang is implemented like this:

            with current frame
            use: context.get('lang')
            else: kwargs['context'].get('lang'),
            else: self.env.lang
            else: self.localcontext.get('lang')
            else: request.env.lang  <== hook this last step

        Note that default language, if not set, will be extracted from browser settings
        in `setup_lang` using `httprequest.accept_languages.best`
        """
        # fallback to default request user (Public?)
        if not user_id:
            user_id = request.env.user
        if user_id:
            context = request.env.context.copy()
            context.update({"lang": user_id.lang})
            request.env.context = context
            request.env.user = user_id

    def _update_user_with_context(self, user_id, override_request_user=False):
        """Merge current user settings (lang, timezone) in current context since no
        session exists to set them when using an API key.
            - Default context {'lang': 'en_US'} miss the timezone and is set to English.
            - We use this assertion to force replace current context values with the ones
            from user's default context.
        """
        if "tz" not in user_id.env.context:
            default_context = user_id.context_get()
            if default_context:
                user_id = user_id.with_context(**default_context)
        if override_request_user:
            self._override_request_with_user(user_id)
        return user_id
