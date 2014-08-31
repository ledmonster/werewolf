var werewolf = (function (window, undefined){
  return {
    onSignInCallback: function(authResult) {
      $('#result').show();
      $('#auth-result').html('Auth Result:<br/>');
      for (var field in authResult) {
        $('#auth-result').append(' ' + field + ': ' +
            authResult[field] + '<br/>');
      }
      if (authResult['access_token']) {
        $('#g-connect').hide();
        werewolf.authenticateWerewolf(authResult['id_token']);
        $('#disconnect').show();
      } else if (authResult['error']) {
        console.log('There was an error: ' + authResult['error']);
        $('#auth-result').append('Logged out');
        $('#g-connect').show();
      }
      console.log('authResult', authResult);
    },

    disconnect: function() {
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
          $('#auth-result').empty();
          $('#g-connect').show();
          $('#disconnect').hide();
        },
        error: function(e) {
          console.log(e);
        }
      });
    },

    authenticateWerewolf: function(idToken) {
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
          $('#werewolf-auth-result').html('Werewolf Auth Result:<br/>');
          for (var field in result) {
            $('#werewolf-auth-result').append(' ' + field + ': ' +
                result[field] + '<br/>');
          };
          localStorage.setItem("access_token", result["access_token"]);
          localStorage.setItem("refresh_token", result["refresh_token"]);
        },
        error: function(error) {
          $('#werewolf-auth-result').html('Werewolf Auth Result: Error');
          console.log(error);
          $('#g-connect').show();
          $('#disconnect').hide();
        }
      });
    },

    loadVillageList: function() {
      $.ajax({
        type: 'GET',
        url: 'http://' + location.host + '/api/v1/village/list',
        data: {},
        dataType: 'json',
        success: function(result) {
          console.log(result);
          for (var identity in result) {
            var item = result[identity];
            $("#village_table").append(
             $("<tr></tr>")
               .append($("<td></td>")
                 .append($("<a href='/village/" + item.identity + "'></a>").text(item.name))
               )
               .append($("<td></td>").text(item.status))
            );
          }
        },
        error: function(error) {
          $('#error').show();
          $('#error').html(error);
        }
      });
    },

    joinToVillage: function(identity) {
      $.ajax({
        type: 'POST',
        url: 'http://' + location.host + '/api/v1/village/join',
        beforeSend: function (xhr) {
          xhr.setRequestHeader('Authorization', "Bearer " + localStorage.getItem("access_token"));
          xhr.setRequestHeader('Accept', "application/json");
        },
        data: {
          'identity': identity
        },
        dataType: 'json',
        success: function(result) {
          $('#join').hide();
          $('#joined').show();
          console.log(result);
        },
        error: function(error) {
          $('#error').show();
          $('#error').html(error);
        }
      });
    }

  };
})(window);
