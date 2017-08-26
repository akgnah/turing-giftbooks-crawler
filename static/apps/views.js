(function ($, Backbone, _, app) {

    var TemplateView = Backbone.View.extend({
        templateName: '',
        initialize: function () {
            this.templateFile = '/static/apps/views/' + this.templateName + '?v=' + app.version;
        },
        render: function () {
            var that = this;
            $.get(this.templateFile, function (data) {
                this.template = _.template(data);
                var context = that.getContext(),
                html = this.template(context);
                that.changeTitle();
                that.$el.html(html);  
                $('img.lazy').lazyload();
                $('body').animate({scrollTop: 0}, 500);
            }, 'html');
        },
        getContext: function () {
            return {}
        }
    });

    var FormView = TemplateView.extend({
        events: {
            'submit form': 'submit'
        },
        serializeForm: function (form) {
            return _.object(_.map(form.serializeArray(), function (item) {
                // Convert object to tuple of (name, value)
                return [item.name, item.value];
            }));
        },
        submit: function (event) {
            event.preventDefault();
            this.form = $(event.currentTarget);
        }
    });

    var BooksView = FormView.extend({
        templateName: 'books.html',
        initialize: function (options) {
            var self = this;
            this.query = {
                page:  Number(options.page),
                sort:  options.sort,
                q:  options.q
            }
            TemplateView.prototype.initialize.apply(this, arguments);
            app.books.fetch({
                data: this.query,
                success: $.proxy(self.render, self)
            });
        },
        getContext: function () {
            context = {
                books: app.books || null,
                args: {
                    date: this.query.sort === 'date'? 'active': '',
                    price: this.query.sort === 'price'? 'active': '',
                    search: this.query.q !== null? '&q=' + this.query.q: ''
                }
            };
            $.extend(context, this.query);
            return context;
        },
        submit: function (event) {
            var self = this;
            FormView.prototype.submit.apply(this, arguments);
            $.extend(this.query, {page: 1});
            $.extend(this.query, this.serializeForm(this.form));
            var tmp = [];
            for(key in this.query) {
                tmp.push([key, this.query[key]].join('='));
            }
            window.location.hash = '#?' + tmp.join('&');
        },
        changeTitle: function () {
            var title = '图灵样书列表';
            if (this.query.q !== null) {
                title = '搜索样书 - ' + this.query.q;
            }
            document.title = title;
        }
    });

    app.views.BooksView = BooksView;

})(jQuery, Backbone, _, app);
