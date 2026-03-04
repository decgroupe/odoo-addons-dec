This module allows user sessions to be marked as "permanent" so they are
regularly touched and kept alive, preventing automatic session expiration.

Use cases:

- Long-running background tasks that require an active session.
- Integrations or API clients that need a persistent authenticated session
  across multiple requests without re-authentication.

## Technical details

When a client sends the HTTP header `X-Odoo-Session-Permanent: True` during
authentication (via `/web/session/authenticate`), the `Session.authenticate`
controller sets `session.permanent = True` on the werkzeug session object.

During the regular session garbage collection cycle (`ir.http._gc_sessions`),
the method `_maintain_permanent_sessions` iterates over all stored sessions,
identifies those belonging to the current database with `session.permanent`
set, and calls `store.save(session)` to update their modification timestamp.
This prevents the session store from expiring them.
