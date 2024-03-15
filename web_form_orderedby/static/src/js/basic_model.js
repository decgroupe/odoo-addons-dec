odoo.define('web_form_orderedby.BasicModel', function (require) {
    'use strict';

    var BasicModel = require('web.BasicModel');
    BasicModel.include({

        /**
         * For list resources, this override the orderedBy key.
         *
         * @param {string} list resource
         * @param {string} order to restore
         * @returns {Promise}
         */
        restoreSort: function (list_id, orderedBy) {
            var list = this.localData[list_id];
            if (list.orderedBy != orderedBy) {
                list.orderedBy = orderedBy;

                // Following is an exact copy of the end of the `setSort` function
                list.orderedResIDs = null;
                if (list.static) {
                    // sorting might require to fetch the field for records where the
                    // sort field is still unknown (i.e. on other pages for example)
                    return this._fetchUngroupedList(list);
                }
            }
            return Promise.resolve();
        },

    });

});
