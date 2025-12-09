This module prevents accidental or unauthorized changes to the `web.base.url` system parameter in production databases.

- It introduces a server-level configuration option (`db_url_freeze_allowedlist`) that lists which databases are allowed to modify `web.base.url`.
- When `web.base.url.freeze` is enabled, any attempt to change the URL from a non-allowed database is silently ignored and the parameter is forced back to `False`.
- This protects multi-database installations (e.g. production, staging, test) from having their public URL accidentally overwritten by a developer or automated process running on the wrong database.

## Technical details

**Server configuration**

The module reads the comma-separated list of allowed database names from the `db_url_freeze_allowedlist` option in the Odoo server configuration file (or environment). The list is cached using `@ormcache` for performance.

**Parameter override**

It inherits from `ir.config_parameter` and overrides the `get_param` method. Whenever the key `web.base.url.freeze` is requested and its value is truthy, the method checks whether the current database name (`self.env.cr.dbname`) exists in the allowed list. If not, it logs an informational message and returns `False` instead of the stored value.

**Use case**

This is particularly useful in environments where multiple databases share the same Odoo installation and developers or migration scripts might inadvertently call `ir.config_parameter.set_param("web.base.url", ...)` on the production database.
