odoo.define('mail_activity_team_image/static/src/models/activity_team/activity_team.js', function (require) {
    'use strict';

    const { registerNewModel } = require('mail/static/src/model/model_core.js');
    const { attr } = require('mail/static/src/model/model_field.js');

    function factory(dependencies) {

        class ActivityTeam extends dependencies['mail.model'] {

            //----------------------------------------------------------------------
            // Public
            //----------------------------------------------------------------------

            /**
             * @static
             * @private
             * @param {Object} data
             * @return {Object}
             */
            static convertData(data) {
                const data2 = {};
                if ('active' in data) {
                    data2.active = data.active;
                }
                if ('display_name' in data) {
                    data2.displayName = data.display_name;
                }
                if ('name' in data) {
                    data2.name = data.name;
                }
                return data2;
            }

            //----------------------------------------------------------------------
            // Private
            //----------------------------------------------------------------------

            /**
             * @override
             */
            static _createRecordLocalId(data) {
                return `${this.modelName}_${data.id}`;
            }

        }

        ActivityTeam.fields = {
            active: attr({
                default: true,
            }),
            displayName: attr(),
            name: attr(),
            id: attr(),
        };

        ActivityTeam.modelName = 'mail.activity_team';

        return ActivityTeam;
    }

    registerNewModel('mail.activity_team', factory);

});
