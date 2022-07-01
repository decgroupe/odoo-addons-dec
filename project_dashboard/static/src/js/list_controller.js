odoo.define('project_dashboard.ListController', function (require) {
    "use strict";

    var ListController = require('web.ListController');

    var ProjectDashboardListController = ListController.extend({
        buttons_template: 'ProjectDashboardListView.buttons',

        /**
         * Extends the renderButtons function by adding an event
         * listener on our new button.
         *
         * @override
         */
        renderButtons: function () {
            this._super.apply(this, arguments); // Possibly sets this.$buttons
            if (this.$buttons) {
                var self = this;
                self.$buttons.on('click', '.o_header_button_view_all_tasks', function () {
                    var state = self.model.get(self.handle, { raw: true });
                    var context = state.getContext();
                    var domain = state.getDomain();
                    self._rpc({
                        model: state.model,
                        method: 'action_open_all_tasks',
                        args: [state.res_ids],
                        kwargs: {
                            view_domain: state.getDomain(),
                            view_type: 'list',
                        },
                    }).then(
                        function (act) {
                            if (act) {
                                self.do_action(act);
                            }
                        }
                    );

                });
            }
        }
    });

    return ProjectDashboardListController;

});
