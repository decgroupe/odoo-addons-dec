/* License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define('mail_activity_my', function (require) {
    'use strict';

    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var mailActivity = require('mail.Activity');
    var _lt = core._lt;
    var KanbanActivity = field_registry.get('kanban_activity');


    // -----------------------------------------------------------------------------
    // Activities Widget for Kanban views ('kanban_activity' widget)
    // -----------------------------------------------------------------------------
    var KanbanActivityMy = KanbanActivity.extend({
        className: 'o_mail_activity_kanban',
        template: 'mail.KanbanActivityMy',

        /**
         * @override
         */
        init: function (parent, name, record) {
            this._super.apply(this, arguments);
            var selection = {};
            _.each(record.fields.activity_my_state.selection, function (value) {
                selection[value[0]] = value[1];
            });
            this.selection = selection;
            this._setState(record);
        },

        /**
         * @private
         * @param {Object} record
         */
        _setState: function (record) {
            this.record_id = record.id;
            this.activityState = this.recordData.activity_my_state;
        },

    });

    // -----------------------------------------------------------------------------
    // Activities Widget for List views ('list_activity_my' widget)
    // -----------------------------------------------------------------------------
    const ListActivityMy = KanbanActivity.extend({
        template: 'mail.ListActivityMy',
        events: Object.assign({}, KanbanActivity.prototype.events, {
            'click .dropdown-menu.o_activity': '_onDropdownClicked',
        }),
        fieldDependencies: _.extend({}, KanbanActivity.prototype.fieldDependencies, {
            activity_my_state: {type: 'char'},
            activity_my_summary: {type: 'char'},
            activity_my_type_id: {type: 'many2one', relation: 'mail.activity.type'},
            activity_my_type_icon: {type: 'char'},
        }),
        label: _lt('My Next Activity'),

        /**
         * @override
         */
        init: function (parent, name, record) {
            this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         */
        _render: async function () {
            await this._super(...arguments);
            // set the 'special_click' prop on the activity icon to prevent from
            // opening the record when the user clicks on it (as it opens the
            // activity dropdown instead)
            this.$('.o_activity_btn > span').prop('special_click', true);
            if (this.value.count) {
                let text = this.recordData.activity_my_summary || this.recordData.activity_my_type_id.data.display_name;
                this.$('.o_activity_my_summary').text(text);
                // Colorize the label
                this.$('.o_activity_my_summary').addClass('o_activity_color_' + (this.activityState || 'default'));
            }
            if (this.recordData.activity_my_type_icon) {
                this.el.querySelector('.o_activity_btn > span').classList.replace('fa-clock', this.recordData.activity_my_type_icon);
            }
        },

        /**
         * @private
         * @param {Object} record
         */
        _setState: function (record) {
            this._super.apply(this, arguments);
            this.activityState = this.recordData.activity_my_state;
        },


        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * As we are in a list view, we don't want clicks inside the activity
         * dropdown to open the record in a form view.
         *
         * @private
         * @param {MouseEvent} ev
         */
        _onDropdownClicked: function (ev) {
            ev.stopPropagation();
        },
    });

    field_registry.add('kanban_activity_my', KanbanActivityMy);
    field_registry.add('list_activity_my', ListActivityMy);

    return {
        KanbanActivityMy: KanbanActivityMy,
        ListActivityMy: ListActivityMy,
    };
});
