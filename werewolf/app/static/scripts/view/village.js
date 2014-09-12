namespace('werewolf.view.village', function(ns) {

    'use strict';

    werewolf.$.on('ready', function(router) {

        new werewolf.View(router, {

            view: 'village_list',

            el: router.$bodyContainer,

            initialize: function() {

                var villageRepo = new werewolf.repository.village.VillageRepository();

                this.onLoad()
                    .doAction(function(params) {
                        router.loadView('header', {title: '村一覧'});
                    })
                    .flatMap(villageRepo, 'findAll')
                    .endOnError(function() {
                        alert('村一覧の取得に失敗しました');
                    })
                    .map(function (villages) {
                        return {'villages': villages};
                    })
                    .doAction(this, 'renderTemplate', 'village_list')
                    .onValue(function(village_list) {
                    });
            }
        });

        new werewolf.View(router, {

            view: 'village_detail',

            el: router.$bodyContainer,

            initialize: function() {

                var self = this,
                    villageRepo = new werewolf.repository.village.VillageRepository();

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
                    .map(".identity")
                    .flatMap(villageRepo, 'getByIdentity')
                    .endOnError(function() {
                        alert('村の取得に失敗しました');
                    })
                    .doAction(function(village) {
                        router.loadView('header', {title: village.name});
                    })
                    .doAction(function(village) {
                        self.renderTemplate('village_detail');
                        scrollToBottom();
                        focusToInput();
                    })
                    .onValue(function(village) {

                        var access_token = localStorage.getItem("access_token"),
                            socket = io.connect("/chat?" + $.param({access_token: access_token})),
                            $inputText = $('#input-text'),
                            sendButtonEvent = $("#send").clickE(),
                            pressReturnEvent = $inputText.keyupE().filter(function(event){return event.keyCode == 13;});

                        if (socket.connected) {
                            socket.emit('join', village.identity);
                        } else {
                            socket.on('connect', function() {
                                console.log('socket: connected');
                                socket.emit('join', village.identity);
                            });
                        }

                        socket.on('error', function(error) {
                            console.log('socket: got error from server: ' + error);
                            socket.disconnect();
                            alert("Sorry, error occured on websocket. Please reload the page.");
                        });

                        socket.on('disconnect', function() {
                            console.log('socket: disconnected');
                            alert("Sorry, socket.io closed. Please reload the page.");
                        });

                        socket.on('message', function(data) {
                            console.log(data);
                            $('#message_area').append(werewolf.template['message'](data));
                            scrollToBottom();
                        });

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
                        sendButtonEvent
                            .merge(pressReturnEvent)
                            .onValue(function() {
                                var msg = $inputText.val();
                                msg = jQuery.trim(msg);
                                if (msg.length > 0) {
                                    socket.emit('message', msg);
                                }
                                $inputText.val("");
                            });
                    });
            }
        });
    });
});
