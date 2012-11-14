/*global Ember:true, DS:true, moment:true, hljs:true, marked:true */

(function () {

  "use strict";

  /* app, store and a helper */
  var Ajd = Ember.Application.create();

  Ajd.store = DS.Store.create({

    revision: 7,

    adapter: DS.RESTAdapter.create({
      namespace: 'api',
      bulkCommit: false,
      ajax: function (url, type, hash) {
        url = 'http://aldrincontent.appspot.com' + url; 
        //url = 'http://localhost:8084' + url;
        hash.error = function (qXHR, textStatus, errorThrown) {
          Ajd.get('router').send('gotoError');
        }
        this._super(url, type, hash);
      }
    })

  });

  Ajd.render = function (markdown) {
    if (markdown) {
      return marked(markdown, {
        gfm: true,
        highlight: function (code, lang) {
          if (lang) {
            return hljs.highlight(lang, code).value;
          }
        }
      });
    }
  };

  /* models */
  Ajd.Tag = DS.Model.extend({
    title: DS.attr('string'),
    summary: DS.attr('string'),
    pages: DS.hasMany('Ajd.Page'),
    parent: DS.belongsTo('Ajd.Tag'),
    children: DS.hasMany('Ajd.Tag'),
    content: DS.belongsTo('Ajd.Content'),
    weight: function () {
      return this.get('pages').get('length');
    }.property('pages'),
    hrefId: function () {
      return "#" + this.get('id');
    }.property('id'),
    preview: function () {
      return Ajd.render(this.get('summary'));
    }.property('summary')
  });

  Ajd.Page = DS.Model.extend({
    date: DS.attr('string'),
    title: DS.attr('string'),
    summary: DS.attr('string'),
    tags: DS.hasMany('Ajd.Tag'),
    content: DS.belongsTo('Ajd.Content'),
    hrefId: function () {
      return "#" + this.get('id');
    }.property('id'),
    when: function () {
      var d = this.get('date')
      if (d) {
        return moment(d, 'YYYY-MM-DD').format('MMM DD YYYY');
      }
      return moment().format('LL');
    }.property('date'),
    preview: function () {
      return Ajd.render(this.get('summary'));
    }.property('summary')
  });

  Ajd.Content = DS.Model.extend({
    matter: DS.attr('string'),
    rendered: function () {
      return Ajd.render(this.get('matter'));
    }.property('matter')
  });

  /* views */
  Ajd.HomeView = Ember.View.extend({
    templateName: 'home'
  });

  Ajd.TagView = Ember.View.extend({
    templateName: 'tag'
  });

  Ajd.PageView = Ember.View.extend({
    templateName: 'page'
  });

  Ajd.ErrorView = Ember.View.extend({
    templateName: 'error'
  });

  Ajd.ApplicationView = Ember.View.extend({
    templateName: 'application'
  });

  /* controller */
  Ajd.ApplicationController = Ember.ArrayController.extend({
    current: null,
    thisYear: function () {
      return moment().format("YYYY");
    }.property()
  });

  Ajd.TagController = Ember.ArrayController.extend({
    content: Ajd.Tag.find(),
    sortProperties: ['weight']
  });

  Ajd.PageController = Ember.ArrayController.extend({
    content: Ajd.Page.find(),
    sortProperties: ['date'],
    sortAscending: false
  });

  Ajd.Router = Ember.Router.extend({
    root: Ember.Route.extend({

      gotoTag: function (router, event) {
        router.transitionTo('tag', {
          tag: event.context
        });
      },

      gotoPage: function (router, event) {
        router.transitionTo('page', {
          page: event.context
        });
      },

      gotoError: function (router, event) {
        router.transitionTo('error');
      },

      home: Ember.Route.extend({
        route: '/',
        connectOutlets: function (router) {
          var controller = router.get('applicationController');
          controller.set('current', {
            'title': 'Aldrin\'s Notebook',
            'pages': router.get('pageController'),
            'isLoaded': true
          });
          controller.connectOutlet('tag');
        }
      }),

      page: Ember.Route.extend({
        route: '/:page',
        connectOutlets: function (router, context) {
          var controller = router.get('applicationController');
          controller.set('current', Ajd.Page.find(context.page));
          controller.connectOutlet('page');
        }
      }),

      tag: Ember.Route.extend({
        route: '/tag/:tag',
        connectOutlets: function (router, context) {
          var controller = router.get('applicationController');
          controller.set('current', Ajd.Tag.find(context.tag));
          controller.connectOutlet('tag');
        }
      }),

      error: Ember.Route.extend({
        route: '/sorry',
        connectOutlets: function (router, context) {
          var controller = router.get('applicationController');
          controller.connectOutlet('error');
        }
      })
    })
  });

  /* expose */
  window.Ajd = Ajd;
  Ajd.initialize();

  /* ensure that the title is in sync.*/
  Ajd.get('router.applicationController').addObserver('current', function () {
    var current = Ajd.get('router.applicationController.current.title');
    if (current) {
      document.title = "Aldrin's Notebook | " + current;
    }
  });

})();
