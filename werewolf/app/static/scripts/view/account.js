namespace('werewolf.view.account', function(ns) {

    'use strict';

    werewolf.$.on('ready', function(router) {

        new werewolf.View(router, {

            view: 'account_nickname',

            el: router.$bodyContainer,

            initialize: function() {

                var userRepo = new werewolf.repository.user.UserRepository();

                this.onLoad()
                    .doAction(function(params) {
                        router.loadView('header', {title: 'ニックネーム設定'});
                    })
                    .flatMap(userRepo, 'get')
                    .endOnError(function() {
                        alert('ユーザ情報の取得に失敗しました');
                    })
                    .map(function (user) {
                        return {'user': user};
                    })
                    .doAction(this, 'renderTemplate', 'account_nickname')
                    .onValue(function(user) {
                        var $nickname = $('#nickname'),
                            $updateButton = $('#update-button'),
                            $msg = $('#msg'),
                            nickname = Bacon.$.textFieldValue($nickname);

                        nickname.sampledBy($updateButton.clickE())
                            .flatMap(userRepo, "updateNickname")
                            .log()
                            .onValue(function() {
                                $msg.text('更新しました');
                            });
                    });
            }
        });
    });
});
