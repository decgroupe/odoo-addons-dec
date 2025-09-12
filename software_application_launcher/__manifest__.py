{
    "name": "Software Application (launcher)",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "software_application",
        "software_license",
        "website_sale",  # for css styles
        "auth_api_key",  # for API key authentication
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
