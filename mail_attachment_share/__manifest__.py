{
    "name": "Attachment Sharing (Public)",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_attachment.xml",
        "wizard/attachment_sharing.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "mail_attachment_share/static/src/js/share.esm.js",
            "mail_attachment_share/static/src/xml/share.xml",
        ],
    },
    "installable": True,
}
