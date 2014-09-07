namespace('werewolf.model.village', function(ns) {

    'use strict';

    ns.Village = Village;

    function Village(identity, name, status) {
        this.identity = identity;
        this.name = name;
        this.status = status;
    }
});
