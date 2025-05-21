{
    "name": "Permanent Session",
    "version": "14.0.1.0.0",
    "author": "DEC",
    "website": "https://www.decgroupe.com",
    "depends": [
        "base",
        "web",
        "base_deterministic_session_gc_extended", # to ensure proper GC
    ],
    "data": [
        "data/ir_cron.xml",
    ],
    "demo": [],
    "installable": False,
}
