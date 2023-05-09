# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2023


from odoo.addons.tagging.tests.common import TestTaggingCommon


class TestTagging(TestTaggingCommon):
    """ """

    def setUp(self):
        super().setUp()

    def _test_format_on_create_and_write(self, name, final_name):
        # try create
        tag_id = self.model.create({"name": name})
        self.assertEqual(tag_id.name, final_name)
        # set a none value
        tag_id.name = "-"
        self.assertEqual(tag_id.name, "-")
        # try write
        tag_id.name = name
        self.assertEqual(tag_id.name, final_name)
        return tag_id

    def test_01_name_format_unaccent(self):
        self._test_format_on_create_and_write(
            "François",
            "francois",
        )

    def test_02_name_format_unaccent(self):
        self._test_format_on_create_and_write(
            "kožušček",
            "kozuscek",
        )

    def test_03_name_format_simple_spaces(self):
        self._test_format_on_create_and_write(
            "Lorem Ipsum Dolor Sit Amet",
            "lorem-ipsum-dolor-sit-amet",
        )

    def test_04_name_format_double_spaces(self):
        self._test_format_on_create_and_write(
            "Lorem  Ipsum  Dolor  Sit  Amet",
            "lorem-ipsum-dolor-sit-amet",
        )

    def test_05_name_format_double_spaces_with_separator(self):
        self._test_format_on_create_and_write(
            "Lorem  Ipsum - Dolor  Sit  Amet",
            "lorem-ipsum-dolor-sit-amet",
        )

    def test_06_name_format_double_spaces_with_triple_separator(self):
        self._test_format_on_create_and_write(
            "Lorem  Ipsum --- Dolor  Sit  Amet",
            "lorem-ipsum-dolor-sit-amet",
        )

    def test_07_basic_hello_world(self):
        self._test_format_on_create_and_write(
            "Hello World",
            "hello-world",
        )
