{
    "name": "Software License (keygen)",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "DEC",
    "website": "https://decgroupe.com",
    "external_dependencies": {
        "python": [
            "key_generator",  # pip install key-generator
            "Crypto",  # pip install pycryptodome
        ],
    },
    "depends": [
        "software_license",
    ],
    "data": [
        "views/software_license.xml",
        "views/software_application.xml",
    ],
    "demo": [
        "demo/software_application.xml",
    ],
    "installable": True,
}
