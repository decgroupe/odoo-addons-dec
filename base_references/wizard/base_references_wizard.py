# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BaseReferencesWizard(models.TransientModel):
    """Wizard that scans all installed models for references to a record."""

    _name = "base.references.wizard"
    _description = "Find Record References"

    model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        required=True,
        readonly=True,
        help="The model of the record whose references are being searched.",
    )
    model_name = fields.Char(
        related="model_id.model",
        string="Model Name",
        readonly=True,
    )
    res_id = fields.Integer(
        string="Record ID",
        required=True,
        help="ID of the record to find references for.",
    )
    record_display_name = fields.Char(
        string="Record",
        compute="_compute_record_display_name",
        help="Display name of the selected record, shown as confirmation.",
    )
    result_count = fields.Integer(
        string="Results",
        readonly=True,
        default=0,
    )
    line_ids = fields.One2many(
        comodel_name="base.references.result",
        inverse_name="wizard_id",
        string="References",
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        """Pre-fill model_id from context when opened from the ir.model form."""
        res = super().default_get(fields_list)
        active_model = self.env.context.get("active_model")
        active_id = self.env.context.get("active_id")
        if active_model == "ir.model" and active_id:
            res["model_id"] = active_id
        return res

    @api.depends("model_id", "res_id")
    def _compute_record_display_name(self):
        """Compute the display name of the selected record for visual feedback."""
        for wizard in self:
            name = False
            if wizard.model_id and wizard.res_id:
                model_name = wizard.model_id.model
                if model_name in self.env:
                    try:
                        record = self.env[model_name].sudo().browse(wizard.res_id)
                        if record.exists():
                            name = record.display_name
                    except Exception:  # pylint: disable=except-pass
                        pass
            wizard.record_display_name = name

    def action_search_references(self):
        """Search all installed models for fields referencing the selected record.

        Iterates over many2one, many2many, reference, and many2one_reference
        fields stored in ir.model.fields whose relation points to the target
        model. For each matching field, searches the owning model with an
        appropriate domain using sudo() and active_test=False so that archived
        records are also considered.

        one2many fields are intentionally excluded: they are virtual inverse
        fields derived from many2one columns on the opposite side; including
        them would duplicate results already captured via many2one traversal.

        Returns an ir.actions.act_window opening the result list filtered to
        this wizard instance.
        """
        self.ensure_one()
        if not self.model_id:
            raise UserError(self.env._("Please select a model."))
        if not self.res_id:
            raise UserError(self.env._("Please enter a record ID."))
        target_model = self.model_id.model
        if target_model not in self.env:
            raise UserError(
                self.env._("Model '%s' is not available in the registry.")
                % target_model
            )
        # clear previous results belonging to this wizard
        self.line_ids.unlink()
        target_record = self.env[target_model].sudo().browse(self.res_id)
        if not target_record.exists():
            raise UserError(
                self.env._("Record with ID %d does not exist in model '%s'.")
                % (self.res_id, target_model)
            )
        results = []
        # find all stored many2one fields whose relation is the target model
        many2one_fields = (
            self.env["ir.model.fields"]
            .sudo()
            .search(
                [
                    ("ttype", "=", "many2one"),
                    ("relation", "=", target_model),
                    ("store", "=", True),
                ]
            )
        )
        # find all stored many2many fields whose relation is the target model
        many2many_fields = (
            self.env["ir.model.fields"]
            .sudo()
            .search(
                [
                    ("ttype", "=", "many2many"),
                    ("relation", "=", target_model),
                    ("store", "=", True),
                ]
            )
        )
        # reference fields have no static relation; we filter at search time by
        # building the "model,id" string and matching it against stored values
        reference_fields = (
            self.env["ir.model.fields"]
            .sudo()
            .search(
                [
                    ("ttype", "=", "reference"),
                    ("store", "=", True),
                ]
            )
        )
        # many2one_reference fields (e.g. mail.message.res_id) store an integer
        # ID; the companion model-name field is discovered at runtime via the
        # Python field's model_field attribute
        many2one_reference_fields = (
            self.env["ir.model.fields"]
            .sudo()
            .search(
                [
                    ("ttype", "=", "many2one_reference"),
                    ("store", "=", True),
                ]
            )
        )
        for field in many2one_fields:
            results += self._search_many2one(field, target_record)
        for field in many2many_fields:
            results += self._search_many2many(field, target_record)
        for field in reference_fields:
            results += self._search_reference(field, target_model, target_record)
        for field in many2one_reference_fields:
            results += self._search_many2one_reference(
                field, target_model, target_record
            )
        if results:
            self.env["base.references.result"].sudo().create(results)
        self.result_count = len(results)
        return {
            "type": "ir.actions.act_window",
            "name": self.env._("References to %s #%d") % (target_model, self.res_id),
            "res_model": "base.references.result",
            "view_mode": "list,form",
            "domain": [("wizard_id", "=", self.id)],
            "target": "current",
        }

    def _is_model_searchable(self, model_name):
        """Return True if the model is safe and meaningful to search.

        Models are skipped when they are transient, abstract, not registered in
        the current environment, or backed by a SQL view (_auto=False).
        """
        if model_name not in self.env:
            return False
        model = self.env[model_name]
        # transient models have volatile data; abstract models have no table
        if model._transient or model._abstract:
            return False
        # non-auto models are backed by SQL views or external tables
        if not model._auto:
            return False
        return True

    def _search_many2one(self, field, target_record):
        """Search records whose many2one column equals the target record.

        Domain: [(field_name, '=', target_record.id)]
        """
        model_name = field.model_id.model
        if not self._is_model_searchable(model_name):
            return []
        results = []
        try:
            domain = [(field.name, "=", target_record.id)]
            records = (
                self.env[model_name]
                .with_context(active_test=False)
                .sudo()
                .search(domain)
            )
            for rec in records:
                results.append(self._build_result(rec, field, "many2one"))
        except Exception as e:
            _logger.debug(
                "skipping many2one field '%s' on '%s': %s",
                field.name,
                model_name,
                e,
            )
        return results

    def _search_many2many(self, field, target_record):
        """Search records whose many2many set contains the target record.

        Domain: [(field_name, 'in', [target_record.id])]
        """
        model_name = field.model_id.model
        if not self._is_model_searchable(model_name):
            return []
        results = []
        try:
            domain = [(field.name, "in", [target_record.id])]
            records = (
                self.env[model_name]
                .with_context(active_test=False)
                .sudo()
                .search(domain)
            )
            for rec in records:
                results.append(self._build_result(rec, field, "many2many"))
        except Exception as e:
            _logger.debug(
                "skipping many2many field '%s' on '%s': %s",
                field.name,
                model_name,
                e,
            )
        return results

    def _search_reference(self, field, target_model, target_record):
        """Search records whose Reference field points to the target record.

        Reference fields store values as 'model_name,record_id' strings.
        Domain: [(field_name, '=', 'model.name,record_id')]
        """
        model_name = field.model_id.model
        if not self._is_model_searchable(model_name):
            return []
        results = []
        try:
            ref_value = "%s,%d" % (target_model, target_record.id)
            domain = [(field.name, "=", ref_value)]
            records = (
                self.env[model_name]
                .with_context(active_test=False)
                .sudo()
                .search(domain)
            )
            for rec in records:
                results.append(self._build_result(rec, field, "reference"))
        except Exception as e:
            _logger.debug(
                "skipping reference field '%s' on '%s': %s",
                field.name,
                model_name,
                e,
            )
        return results

    def _search_many2one_reference(self, field, target_model, target_record):
        """Search records whose Many2oneReference field points to the target.

        Many2oneReference fields (e.g. mail.message.res_id) store an integer ID
        while a companion char field stores the model name. The Python field
        definition exposes the companion field name via the 'model_field'
        attribute. We read this attribute from the live registry to build the
        correct two-clause domain.

        Domain: [(model_field, '=', target_model), (field_name, '=', target_id)]

        If the 'model_field' attribute is absent the field is silently skipped,
        because we cannot safely narrow the search to the target model without
        it - matching only on the integer ID could produce false positives.
        """
        model_name = field.model_id.model
        if not self._is_model_searchable(model_name):
            return []
        results = []
        try:
            py_field = self.env[model_name]._fields.get(field.name)
            if py_field is None:
                return []
            model_field = getattr(py_field, "model_field", None)
            if not model_field:
                _logger.debug(
                    "many2one_reference '%s' on '%s' exposes no model_field, skipping",
                    field.name,
                    model_name,
                )
                return []
            domain = [
                (model_field, "=", target_model),
                (field.name, "=", target_record.id),
            ]
            records = (
                self.env[model_name]
                .with_context(active_test=False)
                .sudo()
                .search(domain)
            )
            for rec in records:
                results.append(self._build_result(rec, field, "many2one_reference"))
        except Exception as e:
            _logger.debug(
                "skipping many2one_reference field '%s' on '%s': %s",
                field.name,
                model_name,
                e,
            )
        return results

    def _build_result(self, record, field, reference_type):
        """Build a result dict for a single referencing record."""
        try:
            display = record.display_name
        except Exception:
            display = False
        return {
            "wizard_id": self.id,
            "model": record._name,
            "res_id": record.id,
            "record_display_name": display,
            "field_id": field.id,
            "field_name": field.name,
            "field_label": field.field_description,
            "reference_type": reference_type,
        }
