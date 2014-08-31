var werewolf = (function (window, undefined){
  return {
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
