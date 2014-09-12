namespace('werewolf.helper', function(ns) {

    'use strict';

    ns.Handlebars = {
        /**
         * Handlebars に formatMessage を追加
         */
        registerFormatMessage: function() {
            Handlebars.registerHelper('formatMessage', function(value) {

                function escapeHtml(str) {
                    return $('<div>').text(str).html();
                }

                function nl2br(str) {
                    return str.replace(/(\r\n|\r|\n)/g, '<br>');
                }

                return nl2br(escapeHtml(value));
            });
        },
    };
});
