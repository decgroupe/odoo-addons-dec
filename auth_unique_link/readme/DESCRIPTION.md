This module adds passwordless authentication to Odoo by generating temporary
sign-in tokens that are sent to the user's email address.

- **Magic link**: a one-time URL containing a secure 32-character random token
  that signs the user in directly when clicked.
- **One-time code**: a 6-digit numeric code displayed to an internal user (e.g.
  a support agent) or sent by email, valid for a configurable duration
  (default: 10 minutes).
- **Impersonation wizard**: internal users with the `Impersonate` group can
  generate a code for any portal user from the partner form, allowing support
  staff to assist users without knowing their password.
- **REST API endpoint**: exposes a `/api/auth_unique_link/v1/SendLink` JSON
  route (authenticated by API key) to trigger the email from an external
  system.

## Technical details

**Token generation**

Two token helpers are defined in `models/res_users.py`:

- `random_token(n=32)` - generates a URL-safe alphanumeric token using
  `random.SystemRandom` (CSPRNG).
- `random_digit_token(n=6)` - generates a 6-digit numeric code using the same
  CSPRNG.

Both token fields (`signin_link_token`, `signin_link_expiration`) are protected
by the `auth_unique_link.group_impersonate` group at field level.

**Authentication**

`ResUsers._check_credentials` is overridden to try the stored token as a
fallback when the standard password check fails. If the token matches and is
still valid, the sign-in succeeds and the token is immediately invalidated via
`signin_link_cancel`.

**Controller**

`AuthUniqueLink` extends `Home` and adds two routes on `/web/login_link`:

- `GET` - validates the token from the query string and redirects.
- `POST` - receives the email, generates and sends the token, then redirects
  back to the login page.
