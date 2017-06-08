(function ($, Backbone, _, app) {

    var AppRouter = Backbone.Router.extend({
        routes: {
            '(/)': 'books',
            '?*query': 'books',
        },

        initialize: function (options) {    
            this.contentElement = '#content';
            this.current = null;
            Backbone.history.start({root: '/books/'});
        },

        parse: function (query, key, val) {
            var reg = new RegExp('(^|&)' + key + '=([^&]*)(&|$)');
            var res = decodeURI(query).match(reg);
            if (res != null) return decodeURI(res[2]); return val;
        },

        books: function (query) {
            var view = new app.views.BooksView({
                el: this.contentElement,
                page: this.parse(query, 'page', 1),
                sort: this.parse(query, 'sort', 'date'),
                q: this.parse(query, 'q', null) || null
            });
        },

        render: function (view) {
            if (this.current) {
                this.current.undelegateEvents();
                this.current.$el = $();
                this.current.remove();
            }
            this.current = view;
            this.current.render();
        }
    });
    
    app.router = AppRouter;

})(jQuery, Backbone, _, app);