namespace('werewolf.repository.village', function(ns) {

    'use strict';

    ns.VillageRepository = VillageRepository;

    /**
     * Village情報を返すレポジトリ
     *
     * Note:
     *
     * - 非同期処理なので返り値は Bacon.Property
     * - エラー処理は受け手側で行う
     */
    function VillageRepository(settings) {

        settings = settings || {};

        this.urls = {
            'findAll': '/api/v1/village/list',
            'getByIdentity': '/api/v1/village/%s'
        };
    }

    /**
     * Village 一覧を返す
     *
     * @return {Bacon.Property(Array.<Village>)} Village の配列の Bacon.Property
     */
    VillageRepository.prototype.findAll = function() {
        return Bacon.$.lazyAjax({
            type: 'GET',
            url: this.urls['findAll'],
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', "Bearer " + localStorage.getItem("access_token"));
                xhr.setRequestHeader('Accept', "application/json");
            },
            data: {},
            dataType: 'json'
        })
            .map(".villages")
            .map(function (villages) {
                return villages.map(function (v) {
                    return new werewolf.model.village.Village(v.identity, v.name, v.status);
                });
            }).toProperty();
    };

    /**
     * Village 詳細を返す
     *
     * @param  {string} Village の識別子
     * @return {Bacon.Property(Village)} Village オブジェクトの Bacon.Property
     */
    VillageRepository.prototype.getByIdentity = function(identity) {
        return Bacon.$.lazyAjax({
            type: 'GET',
            url: _.str.sprintf(this.urls['getByIdentity'], identity),
            beforeSend: function (xhr) {
                xhr.setRequestHeader('Authorization', "Bearer " + localStorage.getItem("access_token"));
                xhr.setRequestHeader('Accept', "application/json");
            },
            data: {},
            dataType: 'json'
        })
            .map(function (v) {
                return new werewolf.model.village.Village(v.identity, v.name, v.status);
            }).toProperty();
    };

});
