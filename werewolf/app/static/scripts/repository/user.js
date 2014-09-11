namespace('werewolf.repository.user', function(ns) {

    'use strict';

    ns.UserRepository = UserRepository;

    /**
     * User情報を返すレポジトリ
     *
     * Note:
     *
     * - 非同期処理なので返り値は Bacon.Property
     * - エラー処理は受け手側で行う
     */
    function UserRepository(settings) {

        settings = settings || {};

        this.urls = {
            'get': '/api/v1/user',
            'updateNickname': '/api/v1/user/nickname/update'
        };
    }

    /**
     * ログインユーザの情報を取得する
     *
     * @return {Bacon.Property(User)} User の Bacon.Property
     */
    UserRepository.prototype.get = function() {
        return Bacon.$.lazyAjax({
            type: 'GET',
            url: this.urls['get'],
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', "Bearer " + localStorage.getItem("access_token"));
                xhr.setRequestHeader('Accept', "application/json");
            },
            data: {},
            dataType: 'json'
        })
            .map(function (user) {
                return new werewolf.model.user.User(user.identity, user.name, user.email, user.status, user.hue);
            }).toProperty();
    };

    /**
     * ニックネームを変更する
     *
     * @return {Bacon.Property(User)} User の Bacon.Property
     */
    UserRepository.prototype.updateNickname = function(nickname) {
        return Bacon.$.lazyAjax({
            type: 'POST',
            url: this.urls['updateNickname'],
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', "Bearer " + localStorage.getItem("access_token"));
                xhr.setRequestHeader('Accept', "application/json");
            },
            data: {nickname: nickname},
            dataType: 'json'
        })
            .flatMap(function (response){
                if (response.result == "error") {
                    return new Bacon.Error(response.message);
                } else {
                    return response.user;
                }
            })
            .map(function (user) {
                return new werewolf.model.user.User(user.identity, user.name, user.email, user.status, user.hue);
            }).toProperty();
    };

});
