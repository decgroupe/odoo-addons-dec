# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2024

import contextlib
from unittest import mock

import odoo.service.common
from odoo.release import RELEASE_LEVELS_DISPLAY
from odoo.tests import Form
from odoo.tests.common import TransactionCase
from odoo.tools.misc import DotDict


@contextlib.contextmanager
def MockDebugRequest(env):
    request = mock.Mock(
        db=None,
        env=env,
        session=DotDict(
            debug=True,
        ),
    )
    with contextlib.ExitStack() as s:
        odoo.http._request_stack.push(request)
        s.callback(odoo.http._request_stack.pop)
        yield request


class TestBaseModuleMigrationTracking(TransactionCase):
    """Test the 'base_module_migration_tracking' module."""

    def setUp(self):
        super().setUp()

        def exp_version():
            version_info = (50, 0, 0, "final", 0, "")
            version = (
                ".".join(str(s) for s in version_info[:2])
                + RELEASE_LEVELS_DISPLAY[version_info[3]]
                + str(version_info[4] or "")
                + version_info[5]
            )
            return {
                "server_version": version,
                "server_version_info": version_info,  # odoo.release.version_info
                "server_serie": ".".join(str(s) for s in version_info[:2]),
                "protocol_version": 1,
            }

        self.mock_patch_version = mock.patch.object(
            odoo.service.common, "exp_version", exp_version
        )
        self.mock_patch_version.start()
        self.version = odoo.release.version_info[0]
        self.module_base = self.env.ref("base.module_base")
        self.module_point_of_sale = self.env.ref("base.module_point_of_sale")
        self.module_web_studio = self.env.ref("base.module_web_studio")

    def tearDown(self):
        self.mock_patch_version.stop()
        super().tearDown()

    def test_01_initialize(self):
        # try with installed module
        self.assertFalse(self.module_base.migration_ids)
        self.assertEqual(self.module_base.state, "installed")
        self.module_base.action_init_migration_status()
        self.assertEqual(len(self.module_base.migration_ids), 1)
        migration_id = self.module_base.migration_ids[0]
        self.assertEqual(migration_id.version, 50)
        # retry
        self.module_base.action_init_migration_status()
        self.assertEqual(len(self.module_base.migration_ids), 1)
        # try with uninstalled module
        self.assertFalse(self.module_point_of_sale.migration_ids)
        self.assertEqual(self.module_point_of_sale.state, "uninstalled")
        self.module_point_of_sale.action_init_migration_status()
        self.assertEqual(len(self.module_point_of_sale.migration_ids), 1)
        migration_id = self.module_point_of_sale.migration_ids[0]
        self.assertEqual(migration_id.version, 50)
        # retry
        self.module_point_of_sale.action_init_migration_status()
        self.assertEqual(len(self.module_point_of_sale.migration_ids), 1)
        # try with uninstallable module
        self.assertFalse(self.module_web_studio.migration_ids)
        self.assertEqual(self.module_web_studio.state, "uninstallable")
        self.module_web_studio.action_init_migration_status()
        self.assertEqual(len(self.module_web_studio.migration_ids), 0)

    def test_02_form(self):
        # Get view with debug mode enabled in mocked http request
        def open_module_base_form():
            with MockDebugRequest(self.env):
                self.assertTrue(self.env.user.has_group("base.group_no_one"))
                return Form(
                    self.module_base,
                    view="base_module_migration_tracking.ir_module_module_form_view",
                )

        module_base_form = open_module_base_form()
        self.assertEqual(len(module_base_form.migration_ids), 0)
        # set value
        with module_base_form.migration_ids.new() as mig_line_form:
            mig_line_form.version = 10
            mig_line_form.state = "installed"
        with module_base_form.migration_ids.new() as mig_line_form:
            self.assertEqual(mig_line_form.version, 50)
            mig_line_form.version = 11
            mig_line_form.state = "installed"
        # re-add same version
        with module_base_form.migration_ids.new() as mig_line_form:
            self.assertEqual(mig_line_form.version, 50)
            mig_line_form.version = 11
            mig_line_form.state = "todo"
        module_base_form.save()
        self.assertEqual(len(self.module_base.migration_ids), 3)
        # reopen form
        module_base_form = open_module_base_form()
        # add "big" version
        with module_base_form.migration_ids.new() as mig_line_form:
            self.assertEqual(mig_line_form.version, 12)
            mig_line_form.version = 25
        module_base_form.save()
        # edit first line
        module_base_form = open_module_base_form()
        with module_base_form.migration_ids.edit(0) as mig_line_form:
            mig_line_form.version = 14
        module_base_form.save()
        # remove last line
        module_base_form = open_module_base_form()
        module_base_form.migration_ids.remove(3)
        # add new migration
        with module_base_form.migration_ids.new() as mig_line_form:
            self.assertEqual(mig_line_form.version, 15)
        module_base_form.save()
        self.assertEqual(len(self.module_base.migration_ids), 4)

    def test_03_view(self):
        self.test_02_form()
        # check views
        domain = []
        modules = self.env["ir.module.module"].search(domain)
        # use `load_all_views` to force loading all views from `_get_inheriting_views`
        view_infos = modules.with_context(load_all_views=True).get_view(
            view_type="list"
        )
        arch = view_infos["arch"]
        self.assertIn('<field name="x_mig_11_status"', arch)
        self.assertIn('<field name="x_mig_11_color"', arch)
        self.assertIn('<field name="x_mig_14_status"', arch)
        self.assertIn('<field name="x_mig_14_color"', arch)
        self.assertIn('<field name="x_mig_15_status"', arch)
        self.assertIn('<field name="x_mig_15_color"', arch)
        self.assertNotIn('<field name="x_mig_12_status"', arch)
        self.assertNotIn('<field name="x_mig_12_color"', arch)
        self.assertNotIn('<field name="x_mig_25_status"', arch)
        self.assertNotIn('<field name="x_mig_25_color"', arch)
        self.assertNotIn('<field name="x_mig_50_status"', arch)
        self.assertNotIn('<field name="x_mig_50_color"', arch)

    def test_04_computed_values(self):
        def create_mig(version, state):
            return self.env["ir.module.migration"].create(
                {
                    "module_id": self.module_base.id,
                    "version": version,
                    "state": state,
                }
            )

        self.assertFalse(self.module_base.migration_ids)
        self.assertEqual(self.module_base.state, "installed")
        self.module_base.action_init_migration_status()
        # check computation
        self.assertEqual(self.module_base.x_mig_50_status, "Installed")
        self.assertEqual(self.module_base.x_mig_50_color, "#8BC34A")
        # create other migration status
        create_mig(12, False)
        create_mig(13, "todo")
        create_mig(14, "adopted")
        create_mig(15, "migrated")
        create_mig(16, "ready")
        create_mig(17, "obsolete")
        create_mig(18, "removed")
        create_mig(19, "uninstalled")
        # check computation
        self.assertEqual(self.module_base.x_mig_12_status, "?")
        self.assertEqual(self.module_base.x_mig_12_color, "#C5CAE9")
        self.assertEqual(self.module_base.x_mig_13_status, "To-do")
        self.assertEqual(self.module_base.x_mig_13_color, "#FFEA00")
        self.assertEqual(self.module_base.x_mig_14_status, "Adopted")
        self.assertEqual(self.module_base.x_mig_14_color, "#1DE9B6")
        self.assertEqual(self.module_base.x_mig_15_status, "Migrated")
        self.assertEqual(self.module_base.x_mig_15_color, "#8BC34A")
        self.assertEqual(self.module_base.x_mig_16_status, "---")
        self.assertEqual(self.module_base.x_mig_16_color, "#8BC34A")
        self.assertEqual(self.module_base.x_mig_17_status, "Obsolete")
        self.assertEqual(self.module_base.x_mig_17_color, "#8BC34A")
        self.assertEqual(self.module_base.x_mig_18_status, "🗑️")
        self.assertEqual(self.module_base.x_mig_18_color, "#8BC34A")
        self.assertEqual(self.module_base.x_mig_19_status, "Not Installed")
        self.assertEqual(self.module_base.x_mig_19_color, "#FFCDD2")
        # PR case
        migration_id = create_mig(20, "migrated")
        migration_id.pr_address = "https://git.com/myproject/PR/123456"
        self.assertEqual(
            self.module_base.x_mig_20_status, "https://git.com/myproject/PR/123456"
        )
        self.assertEqual(self.module_base.x_mig_20_color, "#FF9800")
