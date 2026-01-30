{
    "name": "Partner Academy",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "base",
        "contacts",
        "l10n_fr_department",
        "l10n_fr_department_oversea",
        "partner_fax",
    ],
    "data": [
        "security/model_security.xml",
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/res_partner_academy.xml",
        "data/res_partner.xml",
        "data/res_partner_academy.xml",
    ],
    "installable": True,
}
