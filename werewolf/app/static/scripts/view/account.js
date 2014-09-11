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

                        nickname
                            .onValue(function(value) {
                                if (value.match(/^\w+$/)) {
                                    $msg.text('');
                                    $updateButton.prop("disabled", false);
                                } else {
                                    $msg.text('ニックネームには半角英数字しか利用できません');
                                    $updateButton.prop("disabled", true);
                                }
                            });

                        var response = nickname
                                .sampledBy($updateButton.clickE())
                                .flatMap(userRepo, "updateNickname");

                        response.onError(function(error) {
                            $msg.text(error);
                        });
                        response.onValue(function() {
                            $msg.text('更新しました');
                        });
                    });
            }
        });
    });
});
