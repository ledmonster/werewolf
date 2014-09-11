namespace('werewolf.model.user', function(ns) {

    'use strict';

    ns.User = User;

    function User(identity, name, email, status, hue) {
        this.identity = identity;
        this.name = name;
        this.email = email;
        this.status = status;
        this.hue = hue;
    }
});
