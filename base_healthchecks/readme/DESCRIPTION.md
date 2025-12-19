This module integrates Odoo server actions with a Healthchecks-compatible
endpoint so scheduled jobs can be monitored from an external healthcheck
service.

- Adds a Ping URL on server actions.
- Sends a start ping when an action begins.
- Sends a success ping when an action ends normally.
- Sends a fail ping when an exception is raised.
- Exposes a ping_log helper in server-action Python code for intermediate
  progress messages.

## Technical details

**Healthchecks client model**

The model healthchecks.ping centralizes HTTP POST calls through requests and
builds a payload containing the hostname and current database name. It provides
helpers for base, start, log, and fail endpoints.

**Server action integration**

The module extends ir.actions.server by adding the ping_url field and
overriding run(). For each action with a configured URL, it sends start and
completion notifications and traps exceptions to emit a fail notification
before re-raising the original error.

**Execution context helper**

The module extends _get_eval_context() to inject a ping_log helper into the
server-action evaluation context, allowing custom Python code in actions to
send structured log payloads to the configured endpoint.

**Cron execution flag**

The module extends ir.cron._callback() to propagate cron_running=True in
context, so ping payloads can distinguish cron-triggered executions.
