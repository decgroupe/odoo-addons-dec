{
    "name": "Website Contact",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "helpdesk_notify",
        "crm",
        "website",
        "google_recaptcha",
    ],
    "data": [
        "data/utm_data.xml",
        "views/helpdesk_ticket_category.xml",
        "templates/website_contact.xml",
        "templates/website_page_contactus.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_contact/static/src/css/style.scss",
        ],
    },
    "installable": True,
}
