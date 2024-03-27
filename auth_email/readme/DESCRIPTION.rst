Since login can be different from email, check for both.

Also note that `auth_ldap` is badly implemented and does not safely allow a multiple arguments LDAP filter in case we wants to write something like:
``(&(|(uid=%s)(mail=%s))(!(userPassword=\*)))``

The ``_get_entry`` from ``odoo/addons/auth_ldap/models/res_company_ldap.py`` could be replaced with:

.. code-block::

    def _get_entry(self, conf, login):
        filter, dn, entry = False, False, False
        if "%s" in conf['ldap_filter']:
            # soft migration
            conf['ldap_filter'] = conf['ldap_filter'].replace("%s", "{0}")
        esc_login = escape_filter_chars(login)
        filter = conf['ldap_filter'].format(esc_login)
        if filter == conf['ldap_filter']:
            _logger.warning('Could not format LDAP filter. Your filter should contain at least one \'{0}\'.')
        if filter:
            results = self._query(conf, tools.ustr(filter))

            # Get rid of (None, attrs) for searchResultReference replies
            results = [i for i in results if i[0]]
            if len(results) == 1:
                entry = results[0]
                dn = results[0][0]
        return dn, entry

