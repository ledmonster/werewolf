namespace('werewolf', function(ns) {

    'use strict';

    var _proxyEvents = {
        initialize: new Bacon.Bus(),
        ready: new Bacon.Bus()
    };

    ns.$ = (function(){

        var _router = null,
            _events = _.mapValues(_proxyEvents, function(v) {
                return v.toProperty(null).skipDuplicates()
                        .where().truthy();
            });

        function _initialize(config) {
            _router = new _Router(config);
        }

        function _getRouter() {
            return _router;
        }

        function _on(eventName, f) {
            _events[eventName].onValue(f);
        }

        return {
            initialize: _initialize,
            router: _getRouter,
            on: _on
        };
    })();

    function _Router(config) {

        this.currentPath = function () {

            var location = history.location || document.location;
            return location.hash.length > 0 ?
                   location.hash.slice(1) :
                   location.pathname + location.search;
        }

        this.observe = function(eventInfo, f) {
            return _onValue(_event.where().containerOf(eventInfo), f);
        }

        this.on = function(eventInfo, f) {
            return _onValue(this.observe(_makeEventInfo(eventInfo)).map('.params'), f);
        }

        this.route = function(path) {
            history.pushState(null, null, path);
            this.dispatch(path.replace(/^.*\/\/[^\/]+/, ''));
        }

        this.loadView = function(view, params) {
            _trigger({event: 'loadView', value: view, params: params});
        };

        this.dispatch = function(path) {
            path = path || this.currentPath();
            var r = _parse(path);
            _trigger({event: 'dispatch', value: r.view});
            this.loadView(r.view, r.params);
        }

        this.config = _.defaults(config, {
            body: 'body',
            link: 'a',
            defaultView: '',
            routes: {},
            initialPath: this.currentPath()
        });

        var _routes = _.map(this.config.routes, function(v, k) {
            var keys = [];
            var r = _pathtoRegexp(k, keys);
            return {
                regexp: r,
                keys: keys,
                view: v
            };
        }),
            _event = new Bacon.Bus(),
            self = this;

        _.each(['dispatch', 'loadView'], function(event) {
            self['on' + _capitalize(event)] = function(value, f) {
                return self.on({event: event, value: value}, f);
            }
        });

        _proxyEvents.initialize.push(this);
        _proxyEvents.initialize.end();

        _proxyEvents.ready.push(this);
        _proxyEvents.ready.end();

        this.dispatch(config.initialPath);

        function _onValue(stream, f) {
            return _.isUndefined(f) ? stream : stream.onValue(f);
        }

        function _makeEventInfo(info) {
            if (_.isObject(info)) {
                return info;
            } else if (_.isString(info)) {
                return _(['event', 'value']).zipObject(info.split(':')).omit(function(v) { return _.isUndefined(v); }).value();
            } else {
                throw new TypeError('invalid event info value "' + info + '".');
            }
        }

        function _capitalize(str) {
            return str.charAt(0).toUpperCase() + str.slice(1);
        }

        function _trigger(eventInfo) {
            _event.push(eventInfo);
        }

        function _parse(path) {

            if (path) {
                path = path.replace(/^#\//, '/');
            } else {
                path = '';
            }

            var paths = path.split('?'),
                params = {};
            if (paths.length === 2) {
                paths[1].replace(/([^&=]+)=([^&]*)/g, function() {
                    params[decodeURIComponent(arguments[1])] = decodeURIComponent(arguments[2]);
                });
            }

            var viewInfo = {
                view: config.defaultView,
                params: params
            };
            _.find(_routes, function(route) {

                var m = route.regexp.exec(paths[0]);
                if (!m) {
                    return false;
                }

                _.each(m.slice(1), function(value, i) {
                    params[route.keys[i].name] = decodeURIComponent(value);
                });

                viewInfo.view = route.view;
                viewInfo.params = params;

                return true;
            });

            return viewInfo;
        }

        function _pathtoRegexp(path, keys, sensitive, strict) {
            if (path instanceof RegExp) return path;
            if (path instanceof Array) path = '(' + path.join('|') + ')';
            path = path
                .concat(strict ? '' : '/?')
                .replace(/\/\(/g, '(?:/')
                .replace(/(\/)?(\.)?:(\w+)(?:(\(.*?\)))?(\?)?/g, function(_, slash, format, key, capture, optional){
                    keys.push({ name: key, optional: !! optional });
                    slash = slash || '';
                    return ''
                        + (optional ? '' : slash)
                        + '(?:'
                        + (optional ? slash : '')
                        + (format || '') + (capture || (format && '([^/.]+?)' || '([^/]+?)')) + ')'
                        + (optional || '');
                })
                .replace(/([\/.])/g, '\\$1')
                .replace(/\*/g, '(.*)');
            return new RegExp('^' + path + '$', sensitive ? '' : 'i');
        }
    }
});

werewolf.$.on('ready', function(router) {

    // router.on('before:loadView', function(viewName) { track.page('/' + viewName) });

    $(router.config.body).clickE(router.config.link)
        .doAction('.preventDefault')
        .map('.target.href')
        .assign(router, 'route');

    $(window).on('popstate', function(e) {
        router.dispatch();
    });
});
