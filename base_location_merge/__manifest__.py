{
    "name": "Merge Locations",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "depends": [
        "base_location",
        "base_merge",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "wizard/merge_res_city.xml",
        "wizard/merge_res_city_zip.xml",
    ],
    "demo": [
        "demo/res_city.xml",
        "demo/res_city_zip.xml",
    ],
    "installable": True,
}
