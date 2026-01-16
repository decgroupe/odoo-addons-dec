This module extends software licenses with token-based activation controls
and encrypted license file generation.

- **Expiration date**: set a deadline on a license after which no new
  activation or renewal is allowed.
- **Activation limit**: restrict the number of hardware identifiers that can be
  registered against a single license.
- **Time-limited activations**: each hardware activation carries a validation
  date and a validity period (in days); the generated license file embeds a
  computed expiration timestamp.
- **Encrypted license files**: license data is serialised to JSON and
  optionally encrypted with a per-application RSA/AES key pair before being
  delivered to the end-user.
- **RSA key pair management**: generate a 2048-bit RSA key pair directly from
  the application form; the public key is used to encrypt outgoing license
  files and the private key stays server-side.

## Technical details

**`software.license` extension**

Adds `expiration_date` (Datetime) and `max_allowed_hardware` (Integer) fields.
Two `@api.constrains` methods enforce the limits: `_check_max_allowed_hardware`
raises a `ValidationError` when the registered hardware count exceeds the
allowed maximum, and `_check_expiration_date` rejects any hardware whose
validation date is past the license expiration. Both constraints are skipped
during XML data loading (`install_mode` context key).

`check_expired()` and `get_remaining_activation()` are helpers consumed by the
activation workflow. `check_max_activation_reached()` is overridden to bypass
the slot check when the hardware identifier is already known.

**`software.license.hardware` extension**

Adds `validation_date` (Datetime, default: now) and `validity_days` (Integer,
default: 365). The `create` and `write` ORM methods re-run the license
constraints after each mutation so limits are always enforced at the ORM level.
`_get_validation_expiration_date()` returns the earlier of
`validation_date + validity_days` and the parent license `expiration_date`.
`_get_license_data()` assembles the exportable payload, pads it to a 16-byte
boundary, then encrypts it with AES-CBC (session key) wrapped with PKCS1-OAEP
(RSA public key) when the application has a public key configured.

**`software.application` extension**

Adds `private_key` and `public_key` (Text) fields and an
`action_generate_rsa_keypair()` button that generates a 2048-bit RSA key pair
using `pycryptodome`. The `write` override clears both keys when the
application type is changed away from `inhouse`.
