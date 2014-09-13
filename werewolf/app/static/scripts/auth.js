namespace('werewolf.auth', function(ns) {

    'use strict';

    ns.isLoggedIn = isLoggedIn;
    ns.on = on;
    ns.trigger = trigger;
    ns.disconnect = disconnect;
    ns.authenticateByIdToken = authenticateByIdToken;
    window.onLoadGoogleLibrary = onLoadGoogleLibrary;

    var _event = new Bacon.Bus();

    function isLoggedIn() {
        return !! localStorage.getItem("access_token");
    }

    function trigger(eventName, params) {
        _event.push({event: eventName, params: params});
    }

    function on(eventName, f) {
        _event.where().containerOf({event: eventName}).map(".params").onValue(f);
    }

    function onLoadGoogleLibrary() {
        var params = {
            'clientid': "793850702446.apps.googleusercontent.com",
            'cookiepolicy': "single_host_origin",
            'callback': onGoogleSignIn,
            'scope': "https://www.googleapis.com/auth/plus.login https://www.googleapis.com/auth/userinfo.profile openid email"
        };
        var $googleLoginButton = $('#google-login');
        $googleLoginButton.clickE()
            .onValue(function() {
                gapi.auth.signIn(params);
            });
    }

    function onGoogleSignIn(response) {
        if (response['access_token']) {
            trigger('googleAuthenticated', {response: response});
        } else if (response['error']) {
            trigger('googleAuthenticationFailed', {response: response});
        }
    };

    function authenticateByIdToken(idToken) {
        $.ajax({
            type: 'POST',
            url: '/api/v1/auth/token',
            data: {
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'client_id': '793850702446.apps.googleusercontent.com',
                'assertion': idToken
            },
            dataType: 'json',
            success: function(response) {
                localStorage.setItem("access_token", response["access_token"]);
                localStorage.setItem("refresh_token", response["refresh_token"]);
                trigger('authenticated', {response: response});
            },
            error: function(error) {
                trigger('authenticationFailed', {response: response});
            }
        });
    };

    /**
     * TODO: refactoring
     */
    function disconnect() {
        var $authResult = $('#auth-result'),
            $googleLogin = $('#google-login'),
            $disConnect = $('#disconnect');

        // remove token
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");

        // Revoke the access token.
        if (gapi.auth.getToken()) {
            $.ajax({
                type: 'GET',
                url: 'https://accounts.google.com/o/oauth2/revoke?token=' +
                    gapi.auth.getToken().access_token,
                async: false,
                contentType: 'application/json',
                dataType: 'jsonp',
                success: function(result) {
                    console.log('revoke response: ' + result);
                    $authResult.empty();
                    $googleLogin.show();
                    $disConnect.hide();
                },
                error: function(e) {
                    console.log(e);
                }
            });
        }
    };
});

werewolf.auth.on('googleAuthenticated', function(params) {
    console.log('google authenticated');
    console.log(params.response);

    // Google 認証に成功したら続けて werewolf サーバで認証
    werewolf.auth.authenticateByIdToken(params.response['id_token']);
});

werewolf.auth.on('googleAuthenticationFailed', function(params) {
    console.log('google authentication failed');
    console.log(params.response);
});

werewolf.auth.on('authenticated', function(params) {
    console.log('werewolf authenticated');
    console.log(params.response);
});

werewolf.auth.on('authenticationFailed', function(params) {
    console.log('werewolf authentication failed');
    console.log(params.response);
});
