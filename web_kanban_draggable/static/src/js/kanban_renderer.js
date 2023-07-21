odoo.define('kanban_draggable.kanban_renderer', function (require) {
    "use strict";

    var KanbanRenderer = require('web.KanbanRenderer');

    KanbanRenderer.include({
        _setState: function (state) {
            this._super.apply(this, arguments);
            var arch = this.arch;
            this.columnOptions.sortable = true;
            if (arch.attrs.columns_draggable) {
                if (arch.attrs.columns_draggable == 'false') {
                    this.columnOptions.sortable = false;
                }
            }
        },
        _renderGrouped: function (fragment) {
            this._super.apply(this, arguments);
            if (this.columnOptions.sortable == false) {
                if (this.$el.sortable('instance') !== undefined) {
                    this.$el.sortable("disable");
                }
            }
        },
    });

});