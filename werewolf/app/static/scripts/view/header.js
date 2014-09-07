namespace('werewolf.view.header', function(ns) {

    'use strict';

    werewolf.$.on('ready', function(router) {

        new werewolf.View(router, {

            view: 'header',

            el: router.$headerContainer,

            initialize: function() {
                this.renderTemplate('header');
                this.onLoad()
                    .doAction(this, 'renderTemplate', 'header')
                    .onValue(function(params) {

                    });
                // ログアウト (TODO: logout view を実装)
                $('#disconnect')
                    .clickE()
                    .onValue(werewolf.auth, 'disconnect', undefined);
            }
        });
    });
});
