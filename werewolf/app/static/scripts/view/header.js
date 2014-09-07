namespace('werewolf.view.header', function(ns) {

    'use strict';

    werewolf.$.on('ready', function(router) {

        new werewolf.View(router, {

            view: 'header',

            el: router.$headerContainer,

            initialize: function() {
                this.renderTemplate('header');
                this.onLoad()
                    .onValue(this, 'renderTemplate', 'header');
            }
        });
    });
});
