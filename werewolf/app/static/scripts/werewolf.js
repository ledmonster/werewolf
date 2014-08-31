$(document).ready(function() {

    werewolf.$.initialize({

        link: '.app-link',

        routes: {
            '/': 'top',
            '/village/list': 'village_list'
        },

        defaultView: 'top'
    });
});

werewolf.$.on('initialize', function(router) {

    werewolf.Model.defaultErrorHandler = function(e) {
        if (e.status === 404) {
            alert('view not found.');
        } else {
            alert('server error.');
        }
    };

    router.$bodyContainer = $('#body-container');
    router.$headerContainer = $('#header-container');
});
