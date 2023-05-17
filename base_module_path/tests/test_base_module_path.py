from odoo.tests.common import TransactionCase


class TestBaseModulePath(TransactionCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.IrModuleModule = self.env["ir.module.module"]
        self.MODULE_NAME = "base_module_path"

    def test_01_valid_paths(self):
        """Tests of computed paths matches the `__file__` one"""
        self.IrModuleModule.action_recompute_path()
        module_id = self.IrModuleModule.search([("name", "=", self.MODULE_NAME)])
        self.assertTrue(len(module_id), 1)
        self.assertTrue(__file__.startswith(module_id.addons_path))
        self.assertTrue(__file__.startswith(module_id.path))
