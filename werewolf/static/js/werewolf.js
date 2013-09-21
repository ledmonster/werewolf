var werewolf = (function (){
  return {
    onSignInCallback: function(authResult) {
      $('#result').show();
      $('#authResult').html('Auth Result:<br/>');
      for (var field in authResult) {
        $('#authResult').append(' ' + field + ': ' +
            authResult[field] + '<br/>');
      }
      if (authResult['access_token']) {
        $('#gConnect').hide();
        werewolf.authenticateWerewolf(authResult['id_token']);
        $('#disconnect').show();
      } else if (authResult['error']) {
        console.log('There was an error: ' + authResult['error']);
        $('#authResult').append('Logged out');
        $('#gConnect').show();
      }
      console.log('authResult', authResult);
    },

    disconnect: function() {
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
          $('#authOps').hide();
          $('#profile').empty();
          $('#visiblePeople').empty();
          $('#authResult').empty();
          $('#gConnect').show();
          $('#disconnect').hide();
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
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
        url: 'http://werewolf.example.com:8000/api/v1/auth/token',
        data: {
          'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
          'client_id': '793850702446.apps.googleusercontent.com',
          'assertion': idToken
        },
        dataType: 'json',
        success: function(result) {
          $('#werewolfAuthResult').html('Werewolf Auth Result:<br/>');
          for (var field in result) {
            $('#werewolfAuthResult').append(' ' + field + ': ' +
                result[field] + '<br/>');
          };
          localStorage.setItem("access_token", result["access_token"]);
          localStorage.setItem("refresh_token", result["refresh_token"]);
        },
        error: function(error) {
          $('#werewolfAuthResult').html('Werewolf Auth Result: Error');
          console.log(error);
        }
      });
    },

    loadVillageList: function() {
      $.ajax({
        type: 'GET',
        url: 'http://werewolf.example.com:8000/api/v1/village/list',
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
               .append($("<td></td>").text(item.start_at))
               .append($("<td></td>").text(item.end_at))
               .append($("<td></td>")
                 .append($("<button type='button' class='btn btn-default'>参加する</button>"))
               )
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
        url: 'http://werewolf.example.com:8000/api/v1/village/join',
        beforeSend: function (xhr) {
          xhr.setRequestHeader('Authorization', "OAuth " + localStorage.getItem("access_token"));
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
})();
