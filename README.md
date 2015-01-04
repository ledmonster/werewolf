みんなの人狼
==========

Pyramid + socket.io ベースの人狼アプリです。
詳細は下記発表資料を参照してください。

* https://www.slideshare.net/secret/8CMopw2DnvjVVB

開発環境
=======

Backend
-------

* Python 2.7.x
* Pyramid
* gevent-socketio
* DynamoDB

Frontend
--------

* socket.io-client
* bacon.js
* handlebars

環境設定
=======

AWS上、または dynamodb-local 環境とともに動作します。

Google API Console の設定
------------------------

OAuth 2.0 認証のために credentials の発行が必要です。


依存パッケージのインストール
-----------------------

```bash
$ python setup.py develop
$ npm install
$ gulp
$ bower update
```

テーブル生成
----------

```bash
$ python scripts/create_tables.py
```
