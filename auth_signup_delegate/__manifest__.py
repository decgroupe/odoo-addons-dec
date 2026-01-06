{
    "name": "Auth Signup Delegate",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "summary": "",
    "depends": [
        "base",
        "auth_signup",
        "portal",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "templates/delegate_signup.xml",
        "wizard/res_partner_signup_delegate.xml",
    ],
    "installable": True,
}
