odoo.define('project_dashboard.ListView', function (require) {
    "use strict";

    var ProjectDashboardListController = require('project_dashboard.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');

    var ProjectDashboardListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: ProjectDashboardListController,
        }),
    });

    viewRegistry.add('project_dashboard_list', ProjectDashboardListView);

    return ProjectDashboardListView;

});
