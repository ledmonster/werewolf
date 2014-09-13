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

                        // よくわからないけど safari で自動ログインがうまく動かないので追加
                        // gapi.signin.go('g-connect');

                        var $result = $('#result'),
                            $authResult = $('#auth-result'),
                            $googleLogin = $('#google-login'),
                            $disConnect = $('#disconnect'),
                            $werewolfAuthResult = $('#werewolf-auth-result');

                        function toggleAuthButton() {
                            console.log('called');
                            if (werewolf.auth.isLoggedIn()) {
                                $googleLogin.hide();
                                $disConnect.show();
                            } else {
                                $googleLogin.show();
                                $disConnect.hide();
                            }
                        }

                        toggleAuthButton();

                        $disConnect.clickE()
                            .onValue(function() {
                                werewolf.auth.disconnect();
                            });

                        werewolf.auth.on('googleAuthenticated', function(params) {
                            $result.show();
                            $authResult.html('Auth Result:<br/>');
                            for (var field in params.response) {
                                $authResult.append(' ' + field + ': ' +
                                                   params.response[field] + '<br/>');
                            }
                            toggleAuthButton();
                        });

                        werewolf.auth.on('googleAuthenticationFailed', function(params) {
                            $result.show();
                            $authResult.html('Auth Result:<br/>');
                            for (var field in params.response) {
                                $authResult.append(' ' + field + ': ' +
                                                   params.response[field] + '<br/>');
                            }
                            $authResult.append('Logged out');
                            toggleAuthButton();
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
                            toggleAuthButton();
                        });

                    });
            }
        });
    });
});
