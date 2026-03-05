# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from psycopg2 import IntegrityError

from odoo import Command
from odoo.tests.common import TransactionCase


class TestPartnerTraining(TransactionCase):
    """test partner training models."""

    def setUp(self):
        super().setUp()
        self.Training = self.env["res.partner.training"]
        self.Specialty = self.env["res.partner.training.specialty"]

    def test_01_create_training_and_specialties(self):
        """create one training and two specialties."""
        training = self.Training.create({"name": "PLM TEST"})
        specialty_a = self.Specialty.create(
            {
                "name": "Option A",
                "acronym": "OA",
                "training_id": training.id,
            }
        )
        specialty_b = self.Specialty.create(
            {
                "name": "Option B",
                "acronym": "OB",
                "training_id": training.id,
            }
        )
        self.assertEqual(training.name, "PLM TEST")
        self.assertEqual(training.specialty_ids, specialty_a | specialty_b)

    def test_02_training_name_must_be_unique(self):
        """prevent duplicate training names."""
        self.Training.create({"name": "DTP TEST"})
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.Training.create({"name": "DTP TEST"})

    def test_03_specialty_name_must_be_unique_per_training(self):
        """prevent duplicate specialty names inside the same training."""
        training_a = self.Training.create({"name": "TMA"})
        training_b = self.Training.create({"name": "TMB"})
        self.Specialty.create(
            {
                "name": "SP1",
                "acronym": "SP1",
                "training_id": training_a.id,
            }
        )
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.Specialty.create(
                {
                    "name": "SP1",
                    "acronym": "SP2",
                    "training_id": training_a.id,
                }
            )
        specialty_other_training = self.Specialty.create(
            {
                "name": "SP1",
                "acronym": "SP3",
                "training_id": training_b.id,
            }
        )
        self.assertEqual(specialty_other_training.training_id, training_b)

    def test_04_specialty_acronym_must_be_unique_per_training(self):
        """prevent duplicate specialty acronyms inside the same training."""
        training = self.Training.create({"name": "LICENCE TEST"})
        self.Specialty.create(
            {"name": "Informatique", "acronym": "INFO", "training_id": training.id}
        )
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.Specialty.create(
                {
                    "name": "Informatique avancee",
                    "acronym": "INFO",
                    "training_id": training.id,
                }
            )

    def test_05_complete_name_uses_acronym_when_available(self):
        """build complete_name from training and acronym."""
        training = self.Training.create({"name": "PLM"})
        specialty = self.Specialty.create(
            {"name": "Sciences", "acronym": "SCI", "training_id": training.id}
        )
        self.assertEqual(specialty.complete_name, "PLM SCI")

    def test_06_partner_can_link_training_specialties(self):
        """link specialties to partner through many2many field."""
        partner_model = self.env["res.partner"]
        training = self.Training.create({"name": "DTP"})
        specialty_a = self.Specialty.create(
            {"name": "Engineering", "acronym": "EGN", "training_id": training.id}
        )
        specialty_b = self.Specialty.create(
            {"name": "Computer", "acronym": "CMP", "training_id": training.id}
        )
        partner = partner_model.create({"name": "Partner Test"})
        partner.training_specialty_ids = [Command.set((specialty_a | specialty_b).ids)]
        self.assertEqual(partner.training_specialty_ids, specialty_a | specialty_b)
