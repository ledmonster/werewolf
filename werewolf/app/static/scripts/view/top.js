namespace('werewolf.view.top', function(ns) {

    'use strict';

    werewolf.$.on('ready', function(router) {

        new werewolf.View(router, {

            view: 'top',

            el: router.$bodyContainer,

            initialize: function() {

                /**
                 * initialize google plus
                 */
                function initializeGooglePlus() {
                    var po = document.createElement('script');
                    po.type = 'text/javascript';
                    po.async = true;
                    po.src = 'https://plus.google.com/js/client:plusone.js';
                    var s = document.getElementsByTagName('script')[0];
                    s.parentNode.insertBefore(po, s);
                }

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
