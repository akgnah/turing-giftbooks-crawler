(function ($, Backbone, _, app) {
    var BaseModel = Backbone.Model.extend({
        defaults: {
            date: 'unknown',
            id: 'unknown',
            title: 'unknown',
            gift: 'unknown',
            price: 'unknown',
            img: 'unknown'
        }
    });

    app.models.BooksModel = BaseModel.extend({
    });

    app.models.SearchModel = BaseModel.extend({
    });


    var BaseCollection = Backbone.Collection.extend({
        parse: function (response) {
            this._total = response.total;
            this._end = response.end;
            return response.results;
        },
    });

    app.collections.Books = BaseCollection.extend({
        model: app.models.BooksModel,
        url: '/api/books'
    });
    app.books = new app.collections.Books();

    app.collections.Search = BaseCollection.extend({
        model: app.models.SearchModel,
        url: '/api/search'
    });
    app.search = new app.collections.Search();

})(jQuery, Backbone, _, app);