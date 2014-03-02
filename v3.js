module.exports = function (app, db, common) {

  // This could become a middleware in an ideal reality.
  // 
  // Ecmascript 6 would make this easier...
  // let [ fields, start, size, sort ] = handle_parameters(req);
  function handle_parameters (req, full, callback) {
    if (req.params.server == null) {
      req.params.server = undefined;
    }

    if (req.params.version == null) {
      req.params.version = undefined;
    }

    var fields;
    if (full) {
        fields = ((req.query.fields == null ? '' : req.query.fields.split(',')));
    } else {
        fields = ((req.query.fields == null ? 'slug,plugin_name,description' : req.query.fields).split(','));
    }
    var start = req.query.start == null ? undefined : parseInt(req.query.start);
    var size = req.query.size == null ? undefined : parseInt(req.query.size);
    var sort = req.query.sort == null ? 'slug' : req.query.sort;

    return callback(fields, start, size, sort);
  }

  function geninfo (req, res, next) {
    handle_parameters(req, false, function (fields, start, size, sort) {
      common.list_geninfo(size, function (callback) {
        res.send(callback);
        next();
      });
    });
  }

  function plugin_list (req, res, next) {
    handle_parameters(req, false, function (fields, start, size, sort) {
      common.list_plugins(req.params.server, fields, sort, start, size, function (callback) {
        res.send(callback);
        next();
      });
    });
  }

  function plugin_details (req, res, next) {
    handle_parameters(req, true, function (fields, start, size, sort) {
      common.plugin_details(req.params.server, req.params.slug, req.params.version, fields, function (data) {
        if (data == null) {
          res.send(404, "Plugin Does Not Exist");
          return next();
        }

        if (size != undefined && data['versions'] != null) {
          data['versions'].length = size;
        }

        res.send(data);
        next();
      });
    });
  }

  function author_plugins (req, res, next) {
    handle_parameters(req, false, function (fields, start, size, sort) {
      common.list_author_plugins(req.params.server, req.params.name, fields, sort, start, size, function (callback) {
        res.send(callback);
        next();
      });
    });
  }

  function category_plugins (req, res, next) {
    handle_parameters(req, false, function (fields, start, size, sort) {
      common.list_category_plugins(req.params.server, req.params.name, fields, sort, start, size, function (callback) {
        res.send(callback);
        next();
      });
    });
  }

  app.get('/3', function (req, res, next) {
    geninfo(req, res, next);
  });

  app.get('/3/geninfo', function (req, res, next) {
    geninfo(req, res, next);
  });

  app.get('/3/geninfo/:idnum', function (req, res, next) {
    common.get_geninfo(req.params.idnum, function (callback) {
      res.send(callback);
      next();
    });
  });

  app.get('/3/plugins', function (req, res, next) {
    plugin_list(req, res, next);
  });

  app.get('/3/plugins/:server', function (req, res, next) {
    plugin_list(req, res, next);
  });

  app.get('/3/plugins/:server/:slug', function (req, res, next) {
    plugin_details(req, res, next);
  });

  app.get('/3/plugins/:server/:slug/:version', function (req, res, next) {
    plugin_details(req, res, next);
  });

  app.get('/3/plugins/:server/:slug/:version/download', function (req, res, next) {
    common.plugin_details(req.params.server, req.params.slug, req.params.version, {}, function(data) {
      if (data == null) {
        res.send(404, "Plugin Does Not Exist");
        return next();
      }

      if (req.params.version.toLowerCase() == "latest") {
        res.header('Location', data['versions'][0]['download']);
        res.send(302);
        return next();
      } else {
        for (var i = 0, il = data['versions'].length; i < il; i++) {
          if (data['versions'][i]['version'] == req.params.version) {
            res.header('Location', data['versions'][i]['download']);
            res.send(302);
            return next();
          }
        }
      }

      res.send(404, {"error": "could not find version"});
      next();
    });
  });

  app.get('/3/authors', function (req, res, next) {
    common.list_authors(function (callback) {
      res.send(callback);
      next();
    });
  });

  app.get('/3/authors/:name', function (req, res, next) {
    author_plugins(req, res, next);
  });

  app.get('/3/authors/:server/:name', function (req, res, next) {
    author_plugins(req, res, next);
  });

  app.get('/3/categories', function (req, res, next) {
    common.list_categories(function (callback) {
      res.send(callback);
      next();
    });
  });

  app.get('/3/categories/:name', function (req, res, next) {
    category_plugins(req, res, next);
  });

  app.get('/3/categories/:server/:name', function (req, res, next) {
    category_plugins(req, res, next);
  });

  app.post('/3/updates', function (req, res, next) {
    var slugs = (req.params.slugs == null ? '' : req.params.slugs).split(',');
    var server = req.params.server == null ? 'bukkit' : req.params.server;
    common.plugins_up_to_date(slugs, server, function (callback) {
      res.send(callback);
      next();
    });
  });

  app.get('/3/updates', function (req, res, next) {
    var slugs = (req.query.slugs == null ? '' : req.query.slugs).split(',');
    var server = req.query.server == null ? 'bukkit' : req.query.server;

    common.plugins_up_to_date(slugs, server, function (callback) {
      res.send(callback);
      next();
    });
  });

  function search (req, res, next) {
    var filters = []

    if (req.method == 'GET') {
      var fields = ((req.query.fields == null ? 'slug,plugin_name,description' : req.query.fields).split(','));
      var start = req.query.start == null ? undefined : parseInt(req.query.start);
      var size = req.query.size == null ? undefined : parseInt(req.query.size);
      var sort = req.query.sort == null ? 'slug' : req.query.sort;
      var field = req.params[0];
      var value = req.params[2];
      filters = [{
        'field': field,
        'action': req.params[1],
        'value': value
      }];
    } else {
      var filters = req.params.filters == null ? [] : JSON.parse(req.params.filters);
      var fields = ((req.params.fields == null ? 'slug,plugin_name,description' : req.params.fields).split(','));
      var start = req.params.start == null ? undefined : parseInt(req.params.start);
      var size = req.params.size == null ? undefined : parseInt(req.params.size);
      var sort = req.params.sort == null ? 'slug' : req.params.sort;
    }

    common.plugin_search(filters, fields, sort, start, size, false, function (callback) {
      if (callback == null) {
        res.send(400, {
          "error": "invalid search"
        });
        return next();
      }

      res.send(callback);
      next();
    });
  }

  app.post('/3/search', function (req, res, next) {
    search(req, res, next);
  });

  app.get(/^\/3\/search\/([a-zA-Z0-9_\.~-]+)\/(\=|\!\=|\<|\<\=|\>|\>\=|[a-z]+)\/([a-zA-Z0-9_\.~-]+)/, function (req, res, next) {
    search(req, res, next);
  });
}