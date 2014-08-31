namespace('werewolf.presenter.header', function(ns) {

    'use strict';

    werewolf.$.on('ready', function(router) {

        new werewolf.Presenter(router, {

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
