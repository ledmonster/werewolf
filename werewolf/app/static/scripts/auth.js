namespace('werewolf.auth', function(ns) {

    'use strict';

    ns.disconnect = disconnect;
    window.onGoogleSignInCallback = onGoogleSignIn;

    function onGoogleSignIn(authResult) {

        var $result = $('#result'),
            $authResult = $('#auth-result'),
            $gConnect = $('#g-connect'),
            $disConnect = $('#disconnect');

        $result.show();
        $authResult.html('Auth Result:<br/>');
        for (var field in authResult) {
            $authResult.append(' ' + field + ': ' +
                               authResult[field] + '<br/>');
        }
        if (authResult['access_token']) {
            $gConnect.hide();
            authenticateWerewolf(authResult['id_token']);
            $disConnect.show();
        } else if (authResult['error']) {
            console.log('There was an error: ' + authResult['error']);
            $authResult.append('Logged out');
            $gConnect.show();
        }
        console.log('authResult', authResult);
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
