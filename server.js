module.exports = function (database, callback) {
  //Imports
  var restify = require('restify');
  var cors = require('cors');

  //Connect to database
  var db = require('monk')(database);
  var plugins = db.get('plugins');
  var webstats = db.get('webstats');
  var geninfo = db.get('geninfo');
  var authors = db.get('authors');
  var categories = db.get('categories');

  // Search Type Map
  var types = {
    '=': function (item, sub, reference) {
      reference[item['field']] = item['value'];
    },

    '!=': function (item, sub, reference) {
      reference[item['field']] = {
        '$ne': item['value']
      };
    },

    '<': function (item, sub, reference) {
      reference[item['field']] = {
        '$lt': item['value']
      };
    },

    '<=': function (item, sub, reference) {
      reference[item['field']] = {
        '$lte': item['value']
      };
    },

    '>': function (item, sub, reference) {
      reference[item['field']] = {
        '$gt': item['value']
      };
    },

    '>=': function (item, sub, reference) {
      reference[item['field']] = {
        '$gte': item['value']
      };
    },

    'like': function (item, sub, reference) {
      reference[item['field']] = new RegExp(item['value'], 'i');
    },

    'exists': function (item, sub, reference) {
      reference[item['field']] = {
        '$exists': Boolean(item['value'])
      };
    },

    'in': function (item, sub, reference) {
      var list = [];
      for (i in item['value']) {
        list.push(new RegExp('^' + item['value'][i] + '$', 'i'));
      }
      if (Object.prototype.toString.call(item['value']) === '[object Array]') {
        reference[item['field']] = {
          '$in': list
        }
      }
    },

    'not in': function (item, sub, reference) {
      var list = [];
      for (i in item['value']) {
        list.push(new RegExp('^' + item['value'][i] + '$', 'i'));
      }
      if (Object.prototype.toString.call(item['value']) === '[object Array]') {
        reference[item['field']] = {
          '$nin': list
        }
      }
    },

    'all': function (item, sub, reference) {
      var list = [];
      for (i in item['value']) {
        list.push(new RegExp('^' + item['value'][i] + '$', 'i'));
      }
      if (Object.prototype.toString.call(item['value']) === '[object Array]') {
        reference[item['field']] = {
          '$all': list
        }
      }
    },

    'and': function (item, sub, reference) {
      if (Object.prototype.toString.call(item['value']) === '[object Array]' && item['field'] == '') {
        reference['$and'] = (item['value'] == null ? sub : item['value']);
      }
    },

    'or': function (item, sub, reference) {
      if (Object.prototype.toString.call(item['value']) === '[object Array]' && item['field'] == '') {
        reference['$or'] = (item['value'] == null ? sub : item['value']);
      }
    },

    'likeor': function (item, sub, reference) {
      reference['$or'] = [];
      for (i in item['value']) {
        var key = Object.keys(item['value'][i])[0];
        reference['$or'][i] = {};
        reference['$or'][i][key] = new RegExp(item['value'][i][key], 'i');
      }
    },

    'nor': function (item, sub, reference) {
      if (Object.prototype.toString.call(item['value']) === '[object Array]' && item['field'] == '') {
        reference['$nor'] = (item['value'] == null ? sub : item['value']);
      }
    },

    'not': function (item, sub, reference) {
      if (Object.prototype.toString.call(item['value']) === '[object Object]') {
        reference[item['field']] = { '$not' : (item['value'] == null ? sub : item['value']) };
      }
    } 
  };

  // Aliases
  types['equals'] = types['='];
  types['not-equals'] = types['!='];
  types['less'] = types['<'];
  types['less-equal'] = types['<='];
  types['more'] = types['>'];
  types['more-equal'] = types['>='];

  //Common methods
  var common = {
    fieldgen: function (fields, callback) {
      // Generates the field listing based on the include and exclude lists.
      var f = [
        '-_id'
      ]

      fields.forEach(function (field) {
        if (field != '' && f.indexOf(field) === -1) {
          f.push(field)
        }
      })

      callback(f);
    },

    list_geninfo: function (size, callback) {
      // Retrieves the last X number of generations based on the value of the size variable.
      if (size == undefined) {
        size = 1;
      }

      geninfo.find({}, { limit: 5, sort: { '_id': -1 } }, function (error, docs) {
        for (var i in docs) {
          docs[i]['id'] = docs[i]['_id'];
          delete docs[i]['_id'];
        }

        callback(docs);
      });
    },

    get_geninfo: function (idnum, callback) {
      // Returns a specific generation ID's information.
      geninfo.findOne({
        '_id': geninfo.id(idnum)
      }, function (error, document) {
        if (document != null) {
          document['id'] = document['_id'];
          delete document['_id'];
        } else {
          document = {};
        }

        callback(document);
      })
    },

    query: function (filters, fields, sort, start, size, callback) {
      // Generic query function to centralize querying the database.
      var d = 1;

      if (sort.charAt(0) == '-') {
        sort = sort.substr(1);
        d = -1;
      }

      common.fieldgen(fields, function (generated_fields) {
        var the_sort = {}
        the_sort[sort] = d

        var options = {
          fields: generated_fields,
          sort: the_sort
        }

        if (size != undefined) {
          if (start == undefined) {
            start = 0;
          }

          options.skip = start;
          options.limit = size;

          plugins.find(filters, options, function (error, docs) {
            callback(docs);
          });
        } else {
          plugins.find(filters, options, function (error, docs) {
            if (error || docs == null) {
              return callback(null);
            }

            callback(docs);
          });
        }
      });
    },

    list_plugins: function (server, fields, sort, start, size, callback) {
      // Returns a list of plugins with the field specified, the list can be narrowed down to specific server binary compatability by setting it to other than undefined.
      var filters = {
        'deleted': {
          '$exists': false
        }
      };

      if (server != undefined) {
        filters['server'] = server
      }

      common.query(filters, fields, sort, start, size, function (the_callback) {
        callback(the_callback);
      })
    },

    list_author_plugins: function (server, author, fields, sort, start, size, callback) {
      // Returns the plugin list for a given author. Can be filtered by server binary compatability using the server variable.
      var filters = {
        'authors': author
      };

      if (server != undefined) {
        filters['server'] = server
      }

      common.query(filters, fields, sort, start, size, function (the_callback) {
        callback(the_callback)
      })
    },

    list_category_plugins: function (server, category, fields, sort, start, size, callback) {
      // Returns the plugin list for a given category. Can be filtered by server binary compatability using the server variable.
      var filters = {
        'categories': category
      };

      if (server != undefined) {
        filters['server'] = server
      }

      common.query(filters, fields, sort, start, size, function (the_callback) {
        callback(the_callback)
      })
    },

    ca_convert: function (data, callback) {
      // Reformats the data to what the API should be returning.
      var dset = [];
      var item;

      for (var i = 0, dlen = data.length; i < dlen; i++) {
        item = data[i];

        dset.push({
          'name': item['_id'],
          'count': item['value']
        });
      }

      return callback(dset);
    },

    list_authors: function (callback) {
      // Returns a list of plugin authors and the number of plugins each one has created/worked on.
      authors.find({}, { sort: '_id' }, function (error, docs) {
        common.ca_convert(docs, function (the_callback) {
          callback(the_callback);
        })
      })
    },

    list_categories: function (callback) {
      // Returns a list of plugin categories and the count of plugins that fall under each category.
      categories.find({}, { sort: '_id' }, function (error, docs) {
        common.ca_convert(docs, function (the_callback) {
          callback(the_callback);
        })
      })
    },

    plugin_details: function (server, plugin, version, fields, callback) {
      // Returns the plugin details for a given plugin. Optionally will also return a specific version of the plugin in the versions list if something other than undefined is specified in the version variable.
      var filters = {
        'slug': plugin,
        'server': server
      };

      if (version != undefined && (version == 'release' || version == 'alpha' || version == 'beta')) {
        filters['versions.type'] = (version.charAt(0).toUpperCase() + version.slice(1));

        if (fields != '' && fields != null && fields.length != 0) {
          fields.push('versions.type');
        }
      }

      common.fieldgen(fields, function (callback) {
        fields = callback;
      });

      plugins.findOne(filters, fields, function (error, p) {
        if (error || p == null) {
          return callback(null);
        }
        var found = false;
        var the_versions = p['versions'];

        if (version != undefined && p['versions'] != null) {
          if (version.toLowerCase() == 'latest') {
            the_versions = [p['versions'][0]];
          } else if (version.toLowerCase() == 'alpha' || version.toLowerCase() == 'beta' || version.toLowerCase() == 'release') {
            for (var i = 0, versionsLen = p['versions'].length; i < versionsLen; i++) {
              if (p['versions'][i]['type'].toLowerCase() == version.toLowerCase()) {
                the_versions = [p['versions'][i]];
                found = true;
                break;
              }
            }

            if (!found) {
              the_versions = [];
            }
          } else {
            for (var i = 0, versionsLen = p['versions'].length; i < versionsLen; i++) {
              if (p['versions'][i]['version'] == version) {
                the_versions = [p['versions'][i]];
                found = true;
                break;
              }
            }

            if (!found) {
              the_versions = [];
            }
          }
        }

        p['versions'] = the_versions;
        callback(p);
      });
    },

    plugins_up_to_date: function (plugins_list, hash_list, file_list, server, extra_fields, extra_version_fields, callback) {
      // Takes a list of plugin slugs and returns an array of objects with the plugin and most recent version.
      var data = [];
      var slugs = [];

      if (plugins_list != '') {
        for (var i = 0; i < plugins_list.length; i++) {
          slugs.push({
            'slug': plugins_list[i]
          });
        }
      }

      if (hash_list != '') {
        for (var i = 0; i < hash_list.length; i++) {
          slugs.push({ 'versions' : { '$elemMatch': { 'md5': hash_list[i] } } });
        }
      }

      if (file_list != '') {
        for (var i = 0; i < file_list.length; i++) {
          slugs.push({ 'versions' : { '$elemMatch': { 'filename': file_list[i] } } });
        }
      }

      plugins.find({
        '$or': slugs,
        'server': server
      }, function (error, docs) {
        var doc, versions, version;

        if (docs == null) {
          return callback([]);
        }
        for (var i = 0, docLen = docs.length; i < docLen; i++) {
          doc = docs[i];
          versions = doc['versions'];

          var entry = {
            'slug': doc['slug'],
            'plugin_name': doc['plugin_name'],
            'versions': {
              'latest': {'version': versions[0]['version'], 'download': versions[0]['download'], 'md5': versions[0]['md5'] }
            },
          }

          for (var i in extra_fields) {
            entry[extra_fields[i]] = doc[extra_fields[i]];
          }

          for (var i in extra_version_fields) {
            entry['versions']['latest'][extra_version_fields[i]] = versions[0][extra_version_fields[i]];
          }

          if (hash_list && hash_list[i]) {
            entry.hash = hash_list[i];
          }
          if (file_list && file_list[i]) {
            entry.file = file_list[i];
          }

          for (var x = 0, versionLen = versions.length; x < versionLen; x++) {
            version = versions[x];

            if (version['type'] == 'Release' || version['type'] == 'Beta' || version['type'] == 'Alpha') {
              if (entry['versions'][version['type'].toLowerCase()] == null) {
                entry['versions'][version['type'].toLowerCase()] = { 'version': version['version'], 'download': version['download'], 'md5': version['md5'] };
                for (var i in extra_version_fields) {
                  entry['versions'][version['type'].toLowerCase()][extra_version_fields[i]] = version[extra_version_fields[i]];
                }
              }
            }
            if (hash_list && hash_list[i] && hash_list[i] == version['md5']) {
              entry['versions']['current'] = { 'version': version['version'], 'download': version['download'], 'md5': version['md5'] };
              for (var i in extra_version_fields) {
                entry['versions']['current'][extra_version_fields[i]] = version[extra_version_fields[i]];
              }
            }
          }

          data.push(entry);
        }

        callback(data);
      })
    },

    plugin_search: function (filters, fields, sort, start, size, sub, callback) {
      // A generalized sort function for the database. 
      // Returns a list of plugins with the fields specified in the inclusion and exclusion variables.
      
      var f = {};
      var item;
      var action;

      if (sub == undefined) {
        sub = false;
      }

      for (var i = 0, filterLen = filters.length; i < filterLen; i++) {
        item = filters[i];
        action = item['action'];

        if (types[action]) {
          types[action](item, sub, f);
        }
      }

      if (sub) {
        return callback(f);
      }

      common.query(f, fields, sort, start, size, function (the_callback) {
        callback(the_callback);
      });
    }
  };

  //Initialize express app
  var app = restify.createServer();

  app.pre(restify.pre.userAgentConnection());
  app.pre(restify.pre.sanitizePath());

  //Middleware
  app.use(cors());
  app.use(restify.queryParser());
  app.use(restify.bodyParser())
  app.use(restify.jsonp());
  app.use(restify.gzipResponse());

  //Include api handlers
  require('./v3')(app, common);

  //Redirect
  app.get('/', function (req, res, next) {
    res.header('Location', '/3');
    res.send(302);
    next();
  });

  //Handle stats requests
  app.get('/stats/naughty_list', function (req, res, next) {
    plugins.find({ '_use_dbo': { '$exists': true } }, { 
      fields: [
        '-_id',
        'slug',
        'plugin_name',
        'authors',
      ]
    }, function (error, docs) {
      if (error) {
        res.send(500);
        return next();
      }

      res.send(docs);
      next();
    });
  });

  app.get('/stats/todays_trends', function (req, res, next) {
    plugins.find({}, { 
      fields: [
        'slug',
        'versions.version'
      ]
    }, function (error, plugins) {
      if (error) {
        res.send(500);
        return next();
      }

      var pcount = plugins.length;
      var vcount = 0;

      for (plugin in plugins) {
        vcount += plugins[plugin]['versions'].length;
      }

      res.send({
        'plugin_count': pcount,
        'version_count': vcount
      });
      next();
    });
  });

  app.get('/stats/trend/:days', function (req, res, next) {
    var fields = [
      '-_id',
      '-plugins'
    ]

    if (req.query.plugins) {
      if (req.query.plugins == 'all') { 
        fields = ['-_id']
      } else {
        fields = ['-_id', 'timestamp']
        var plugins = req.query.plugins.split(',');

        for (var index = 0, pluginsLen = plugins.length; index < pluginsLen; index++) {
          fields.push('plugins.' + plugins[index])
        }
      }
    }

    var days = (new Date().getTime() / 1000) - (86400 * req.params.days);
    var options = {
      fields: fields,
      limit: parseInt(req.params.days),
      sort: { '_id': -1 }
    }

    webstats.find({ timestamp: { $gte: days } }, options, function (error, docs) {
      if (error) {
        res.send(500);
        return next();
      }

      res.send(docs);
      next();
    });
  });

  //Deprecation stuff
  app.get('/2/bukkit/plugins', function (req, res, next) {
     res.send(['API', 'Deprecated', 'Please', 'update', 'your', 'software']);
     next();
  });

  app.get('/2/authors', function (req, res, next) {
    res.send(['API', 'Deprecated', 'Please', 'update', 'your', 'software']);
    next();
  });

  app.get('/2/categories', function (req, res, next) {
    res.send(['API', 'Deprecated', 'Please', 'update', 'your', 'software']);
    next();
  });

  app.get('/api2/bukkit/plugins', function (req, res, next) {
     res.send(['API', 'Deprecated', 'Please', 'update', 'your', 'software']);
     next();
  });

  app.get('/api2/authors', function (req, res, next) {
    res.send(['API', 'Deprecated', 'Please', 'update', 'your', 'software']);
    next();
  });

  app.get('/api2/categories', function (req, res, next) {
    res.send(['API', 'Deprecated', 'Please', 'update', 'your', 'software']);
    next();
  });

  app.get('/favicon.ico', function (req, res, next) {
    res.writeHead(204);
    res.end();
  });

  app.on('NotFound', function (req, res, next) {
    res.send(404, { error: 'Invalid route' });
  });

  if (process.send != null) {
    app.on('after', function (req, res, route, error) {
      process.send({ res: { statusCode : res.statusCode }, req: { url: req.url }, route: route, error: error });
    });
  }

  if (process.env.NODE_ENV === 'development') {
    app.on('uncaughtException', function (req, res, route, error) {
      console.log(error.stack)
      console.log(route)
      res.send(500, { error: 'Internal server error' })
    })
  }

  callback(app);
}
