from datetime import date

from odoo.tests import common


class TestSequence(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.date = date(2023, 4, 24)

    def get_sequence(self, method):
        return self.env["ir.sequence"].create(
            {
                "name": "Test sequence",
                "implementation": "standard",
                "use_date_range": True,
                "range_reset": method,
                "padding": "5",
            }
        )

    def test_01_number_first(self):
        sequence = self.get_sequence(False)
        sequence.number_first = 100
        self.assertFalse(sequence.date_range_ids)
        self.assertEqual(
            "00100", sequence.with_context(ir_sequence_date=self.date).next_by_id()
        )
        xrange = sequence.date_range_ids
        self.assertTrue(xrange)
        xrange.invalidate_cache()
        self.assertEqual(xrange.number_next_actual, 101)
        self.assertEqual(
            "00101", sequence.with_context(ir_sequence_date=self.date).next_by_id()
        )
        xrange.invalidate_cache()
        self.assertEqual(xrange.number_next_actual, 102)

