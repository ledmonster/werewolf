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

        new werewolf.Presenter(router, {

            view: 'village_detail',

            el: router.$bodyContainer,

            initialize: function() {

                var self = this;

                /**
                 * 村取得用パラメータ
                 */
                function getVillageRequest(params) {
                    return {
                        type: 'GET',
                        url: '/api/v1/village/' + params.identity,
                        data: {},
                        dataType: 'json'
                    };
                }

                /**
                 * 村参加用パラメータ
                 */
                function getJoinToVillageRequest(village) {
                    return {
                        type: 'POST',
                        url: '/api/v1/village/join',
                        beforeSend: function (xhr) {
                            xhr.setRequestHeader('Authorization', "Bearer " + localStorage.getItem("access_token"));
                            xhr.setRequestHeader('Accept', "application/json");
                        },
                        data: {
                            'identity': village.identity
                        },
                        dataType: 'json'
                    };
                }

                /**
                 * 一番下へスクロール
                 */
                function scrollToBottom() {
                    window.scrollTo(0, document.body.scrollHeight);
                }

                /**
                 * 入力フォームへフォーカス
                 */
                function focusToInput() {
                    $("#input-text").focus();
                }

                /**
                 * 改行BR変換
                 */
                function nl2br(str) {
                    return str.replace(/(\r\n|\r|\n)/g, '<br />');
                }

                /**
                 * HTMLエスケープ
                 */
                function escapeHtml(str) {
                    return $('<div>').text(str).html();
                }

                this.onLoad()
                    .map(getVillageRequest)
                    .ajax()
                    .endOnError(function() {
                        alert('村の取得に失敗しました');
                    })
                    .doAction(function(params) {
                        router.loadView('header', {title: params.village.name});
                    })
                    .doAction(function() {
                        self.renderTemplate('village_detail');
                        scrollToBottom();
                        focusToInput();
                    })
                    .onValue(function(village) {
                        // ログアウト
                        $('#disconnect')
                            .clickE()
                            .onValue(werewolf.auth, 'disconnect', undefined);

                        // 村への参加
                        $('#joinToVillage')
                            .clickE()
                            .map(village)
                            .map(getJoinToVillageRequest)
                            .ajax()
                            .endOnError(function() {
                                alert('村への参加に失敗しました');
                            })
                            .onValue(function() {
                                $('#join').hide();
                                $('#joined').show();
                            });

                        // 送信ボタンで送信
                        var $inputText = $('#input-text'),
                            sendButtonEvent = $("#send").clickE(),
                            pressReturnEvent = $inputText.keyupE().filter(function(event){return event.keyCode == 13;});

                        sendButtonEvent
                            .merge(pressReturnEvent)
                            .onValue(function() {
                                var msg = $inputText.val();
                                msg = jQuery.trim(msg);
                                if (msg.length > 0) {
                                    ws.send(msg);
                                }
                                $inputText.val("");
                            });

                        var access_token = localStorage.getItem("access_token"),
                            ws = new WebSocket("ws://" + location.host + "/websocket?access_token=" + access_token + "&village_id=" + village.identity);

                        ws.onopen = function() {};

                        ws.onclose = function() {
                            alert("Sorry, websocket closed. Please reload the page.");
                        };

                        ws.onerror = function() {
                            alert("Sorry, error occured on websocket. Please reload the page.");
                        };

                        ws.onmessage = function (evt) {
                            var data = JSON.parse(evt.data);
                            var message = $("<div>").addClass("row").append(
                                $("<div>")
                                    .addClass("col-xs-2")
                                    .append(
                                        $("<img>")
                                            .attr("src", data.sender_avatar)
                                    )
                            ).append(
                                $("<div>")
                                    .addClass("col-xs-10")
                                    .append(
                                        $("<div>")
                                            .addClass("row sender")
                                            .css({"color": "hsl(" + data.sender_hue + ", 70%, 70%)"})
                                            .text(data.sender_name)
                                    ).append(
                                        $("<div>")
                                            .addClass("row")
                                            .append(
                                                $("<div>")
                                                    .addClass("message")
                                                    .css({"border-color": "hsl(" + data.sender_hue + ", 70%, 70%)"})
                                                    .html(
                                                        nl2br(escapeHtml(data.content))
                                                    )
                                            )
                                    )
                            );
                            $('#message_area').append(message);
                            scrollToBottom();
                        };
                    });
            }
        });
    });
});
