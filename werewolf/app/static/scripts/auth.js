namespace('werewolf.auth', function(ns) {

    'use strict';

    ns.on = on;
    ns.disconnect = disconnect;
    window.onGoogleSignInCallback = onGoogleSignIn;

    var _event = new Bacon.Bus();

    function on(eventName, f) {
        _event.where().containerOf({event: eventName}).map(".params").onValue(f);
    }

    function onGoogleSignIn(response) {
        if (response['access_token']) {
            _event.push({event: 'googleAuthenticated',
                         params: {response: response}});
            // Google 認証に成功したら続けて werewolf サーバで認証
            authenticateWerewolf(response['id_token']);
        } else if (response['error']) {
            _event.push({event: 'googleAuthenticationFailed',
                         params: {response: response}});
        }
    };

    function authenticateWerewolf(idToken) {
       var  $werewolfAuthResult = $('#werewolf-auth-result'),
            $gConnect = $('#g-connect'),
            $disConnect = $('#disconnect');

        console.log('id_token: ', idToken);
        $.ajax({
            type: 'POST',
            url: 'http://' + location.host + '/api/v1/auth/token',
            data: {
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'client_id': '793850702446.apps.googleusercontent.com',
                'assertion': idToken
            },
            dataType: 'json',
            success: function(result) {
                $werewolfAuthResult.html('Werewolf Auth Result:<br/>');
                for (var field in result) {
                    $werewolfAuthResult.append(' ' + field + ': ' +
                                               result[field] + '<br/>');
                };
                localStorage.setItem("access_token", result["access_token"]);
                localStorage.setItem("refresh_token", result["refresh_token"]);
            },
            error: function(error) {
                $werewolfAuthResult.html('Werewolf Auth Result: Error');
                console.log(error);
                $gConnect.show();
                $disConnect.hide();
            }
        });
    };

    function disconnect() {
        var $authResult = $('#auth-result'),
            $gConnect = $('#g-connect'),
            $disConnect = $('#disconnect');

        // remove token
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");

        // Revoke the access token.
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
                $gConnect.show();
                $disConnect.hide();
            },
            error: function(e) {
                console.log(e);
            }
        });
    };
});

werewolf.auth.on('googleAuthenticated', function(params) {
    console.log('google authenticated');
    console.log(params.response);
});

werewolf.auth.on('googleAuthenticationFailed', function(params) {
    console.log('google authentication failed');
    console.log(params.response);
});

werewolf.auth.on('authenticated', function(user) {
});

werewolf.auth.on('authenticationFailed', function(error) {
});
