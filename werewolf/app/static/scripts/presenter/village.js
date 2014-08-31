namespace('werewolf.presenter.village', function(ns) {

    'use strict';

    werewolf.$.on('ready', function(router) {

        new werewolf.Presenter(router, {

            view: 'village_list',

            el: router.$bodyContainer,

            initialize: function() {

                /**
                 * 村一覧取得用パラメータ
                 */
                function getVillageListRequest() {
                    return {
                        type: 'GET',
                        url: '/api/v1/village/list',
                        data: {},
                        dataType: 'json'
                    };
                }

                this.onLoad()
                    .doAction(function(params) {
                        router.loadView('header', {title: '村一覧'});
                    })
                    .map(getVillageListRequest)
                    .ajax()
                    .endOnError(function() {
                        alert('サーバとの通信に失敗しました');
                    })
                    .doAction(this, 'renderTemplate', 'village_list')
                    .onValue(function(village_list) {
                        $('#disconnect')
                            .clickE()
                            .onValue(werewolf.auth, 'disconnect', undefined);
                    });
            }
        });
    });
});
