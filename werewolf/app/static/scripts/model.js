namespace('werewolf', function(ns) {

    'use strict';

    ns.Model = Model;

    function Model(settings) {

        var model = Bacon.Model(settings.initialValue);

        model.load = function(params) {

            var stream = Bacon.$.lazyAjax({
                type: 'GET',
                url: settings.url,
                data: $.param(params || {})
            });

            if (settings.errorHandler) {
                stream.onError(settings.errorHandler);
            } else if (Model.defaultErrorHandler) {
                stream.onError(Model.defaultErrorHandler);
            }

            model.addSource(stream);

            return stream;
        }

        return model;
    }

});
