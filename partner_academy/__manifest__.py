{
    "name": "Partner Academy",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "base",
        "contacts",
        "l10n_fr_department",
        "l10n_fr_department_oversea",
        "partner_fax",
        "web_xml_export", # needed for initial loading of `res_partner_academy.xml` data
    ],
    "data": [
        "security/model_security.xml",
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/res_partner_academy.xml",
        "data/res_partner.xml",
        "data/res_partner_academy.xml",
    ],
    "installable": False,
}
