namespace('werewolf', function(ns) {

    'use strict';

    ns.Presenter = Presenter;

    function Presenter(router, settings) {

        settings = settings || {};
        this.router = router;

        if (settings.view) {
            this.onLoad = _.bind(router.onLoadView, router, settings.view);
        }

        if (settings.el) {
            this.$el = $(settings.el);
        }

        if (settings.model) {
            this.model = settings.model;
        }

        if (settings.initialize) {
            settings.initialize.call(this);
        }
    }

    Presenter.prototype.renderHTML = function(html) {
        this.$el.html(html);
    };

    Presenter.prototype.renderTemplate = function(viewName, data) {
        this.renderHTML(ns.template[viewName](data));
    };
});
