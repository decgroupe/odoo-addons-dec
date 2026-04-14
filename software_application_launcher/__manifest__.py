{
    "name": "Software Application (launcher)",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "base_default",
        "software_application",
        "software_license",
        "website_sale",  # for css styles
        "auth_api_key",  # OCA": API Key authentication for external systems
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/software_application.xml",
        "views/software_application_image.xml",
        "views/menu.xml",
        "data/software_tag.xml",
    ],
    "demo": [
        "demo/software_tag.xml",
        "demo/software_application.xml",
    ],
    "installable": True,
}
