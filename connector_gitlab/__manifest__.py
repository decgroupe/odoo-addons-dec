{
    "name": "GitLab Connector",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "base",
        "auth_signup",
    ],
    "data": [
        "security/model_security.xml",
        "security/ir.model.access.csv",
        "views/gitlab_resource.xml",
        "views/res_users.xml",
    ],
    "installable": True,
}
