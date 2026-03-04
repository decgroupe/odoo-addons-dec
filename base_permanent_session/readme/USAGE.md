To create a permanent session, include the following HTTP header when
authenticating:

```
X-Odoo-Session-Permanent: True
```

Once authenticated, the session is periodically touched during garbage
collection cycles and will not expire as long as the server keeps running and
the session file persists in the session store.
