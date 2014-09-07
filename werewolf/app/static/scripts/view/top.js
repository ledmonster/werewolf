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

                        var $result = $('#result'),
                            $authResult = $('#auth-result'),
                            $gConnect = $('#g-connect'),
                            $disConnect = $('#disconnect'),
                            $werewolfAuthResult = $('#werewolf-auth-result');

                        werewolf.auth.on('googleAuthenticated', function(params) {
                            $result.show();
                            $authResult.html('Auth Result:<br/>');
                            for (var field in params.response) {
                                $authResult.append(' ' + field + ': ' +
                                                   params.response[field] + '<br/>');
                            }
                            $gConnect.hide();
                            $disConnect.show();
                        });

                        werewolf.auth.on('googleAuthenticationFailed', function(params) {
                            $result.show();
                            $authResult.html('Auth Result:<br/>');
                            for (var field in params.response) {
                                $authResult.append(' ' + field + ': ' +
                                                   params.response[field] + '<br/>');
                            }
                            $authResult.append('Logged out');
                            $gConnect.show();
                        });

                        werewolf.auth.on('authenticated', function(params) {
                            $werewolfAuthResult.html('Werewolf Auth Result:<br/>');
                            for (var field in params.response) {
                                $werewolfAuthResult.append(' ' + field + ': ' +
                                                           params.response[field] + '<br/>');
                            };
                        });

                        werewolf.auth.on('authenticationFailed', function(params) {
                            $werewolfAuthResult.html('Werewolf Auth Result: Error');
                            $gConnect.show();
                            $disConnect.hide();
                        });

                    });
            }
        });
    });
});
