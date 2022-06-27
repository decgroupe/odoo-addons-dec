odoo.define('project_dashboard.KanbanView', function (require) {
    "use strict";

    var ProjectDashboardKanbanController = require('project_dashboard.KanbanController');
    var KanbanView = require('web.KanbanView');
    var viewRegistry = require('web.view_registry');

    var ProjectDashboardKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: ProjectDashboardKanbanController,
        }),
    });

    viewRegistry.add('project_dashboard_kanban', ProjectDashboardKanbanView);

    return ProjectDashboardKanbanView;

});
