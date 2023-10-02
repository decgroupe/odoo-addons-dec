{
    "name": "Merge Locations",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "base_location",
        "deltatech_merge",
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
