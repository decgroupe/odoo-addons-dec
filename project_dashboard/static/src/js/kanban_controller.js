odoo.define('project_dashboard.KanbanController', function (require) {
    "use strict";

    var KanbanController = require('web.KanbanController');

    var ProjectDashboardKanbanController = KanbanController.extend({
        buttons_template: 'ProjectDashboardKanbanView.buttons',

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
                    self._rpc({
                        model: state.model,
                        method: 'action_open_all_tasks',
                        args: [state.res_ids],
                        kwargs: {},
                        context: context,
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

    return ProjectDashboardKanbanController;

});
