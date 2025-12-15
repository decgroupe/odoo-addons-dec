This module adds a secondary local password (PIN) for users who connect from a private network.

- Users in the dedicated security group can set a local PIN on their user profile.
- The local PIN can be used only from private IP addresses (for example office LAN or VPN ranges).
- Local PIN authentication is refused when the connection comes from a public Internet IP.

## Technical details

**User model extension**

The module extends `res.users` with a `local_password` field and stores it as a hashed value through an inverse method. It also allows users to edit this field themselves by extending `SELF_WRITEABLE_FIELDS`. A minimum length check is enforced before hashing.

**Authentication flow**

The `_check_credentials` method is overridden on `res.users`. It first determines the client IP from `HTTP_X_FORWARDED_FOR` (first hop) or `REMOTE_ADDR`, then detects whether the address is private. If standard authentication fails, the module validates the provided password against the hashed `local_password` for users in `auth_local_password.group_local_password`.

If the local password matches and the request is local, authentication succeeds with `auth_method="local_password"`. If the same local password is used from a public IP, access is denied.

**Views and security**

The module adds the `local_password` field in inherited `res.users` forms (preferences and user form) and restricts the local authentication feature through the `auth_local_password.group_local_password` group.
