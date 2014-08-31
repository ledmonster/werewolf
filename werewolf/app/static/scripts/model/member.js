namespace('werewolf.model.member', function(ns) {

    'use strict';

    ns.Member = Member;

    function Member(name, customers) {
        this.name = name;
        this.customers = customers;
    }
});
