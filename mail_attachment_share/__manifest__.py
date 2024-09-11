{
    "name": "Attachment Sharing (Public)",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_attachment.xml",
        "views/templates.xml",
        "wizard/attachment_sharing.xml",
    ],
    "qweb": [
        "static/src/xml/attachment_box_sharing.xml",
    ],
    "installable": True,
}
