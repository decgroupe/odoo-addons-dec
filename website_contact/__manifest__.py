{
    "name": "Website Contact",
    "version": "14.0.1.0.0",
    "author": "DEC, Yann Papouin",
    "website": "https://www.decgroupe.com",
    "summary": "Allow helpdesk data manipulation without user account",
    "depends": [
        "helpdesk_notify",
        "crm",
        "website",
        "website_form",
        "google_recaptcha",
    ],
    "data": [
        "data/utm_data.xml",
        "views/assets.xml",
        "views/helpdesk_ticket_category.xml",
        "templates/website_contact.xml",
        "templates/website_page_contactus.xml",
    ],
    "installable": True,
}
