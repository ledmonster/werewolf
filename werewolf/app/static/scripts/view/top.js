namespace('werewolf.view.top', function(ns) {

    'use strict';

    werewolf.$.on('ready', function(router) {

        new werewolf.View(router, {

            view: 'top',

            el: router.$bodyContainer,

            initialize: function() {

                this.onLoad()
                    .doAction(function(params) {
                        router.loadView('header', {title: 'みんなの人狼'});
                    })
                    .doAction(this, 'renderTemplate', 'top')
                    .onValue(function (params) {
                        $('#disconnect')
                            .clickE()
                            .onValue(werewolf.auth, 'disconnect', undefined);
                    });
            }
        });
    });
});
