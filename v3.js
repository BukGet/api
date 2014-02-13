module.exports = function (app, db, bleach, common) {
    function geninfo (req, res) {
        size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size));
        common.list_geninfo(size, function (callback) {
            res.jsonp(callback);
        });
    }

    app.get('/3', function (req, res) {
        geninfo(req, res);
    });

    app.get('/3/geninfo', function (req, res) {
        geninfo(req, res);
    });

    app.get('/3/geninfo/:idnum', function (req, res) {
        common.get_geninfo(req.params.idnum, function (callback) {
            res.jsonp(callback);
        });
    });

    function plugin_list (req, res) {
        if (req.params.server == null) {
            req.params.server = undefined;
        }
        var fields = ((req.query.fields == null ? 'slug,plugin_name,description' : bleach.sanitize(req.query.fields)).split(','))
        var start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
        var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
        var sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
        common.list_plugins(req.params.server, fields, sort, start, size, function (callback) {
            res.jsonp(callback);
        });
    }

    app.get('/3/plugins', function (req, res) {
        plugin_list(req, res);
    });

    app.get('/3/plugins/:server', function (req, res) {
        plugin_list(req, res);
    });

    function plugin_details (req, res) {
        if (req.params.server == null) {
            req.params.server = undefined;
        }
        if (req.params.version == null) {
            req.params.version = undefined;
        }
        var fields = ((req.query.fields == null ? '' : bleach.sanitize(req.query.fields)).split(','))
        var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
        common.plugin_details(req.params.server, req.params.slug, req.params.version, fields, function(data) {
            if (data == null) {
                return res.send(404, "Plugin Does Not Exist");
            }
            if (size != undefined) {
                data['versions'].length = size;
            }
            res.jsonp(data);
        });
    }

    app.get('/3/plugins/:server/:slug', function (req, res) {
        plugin_details(req, res);
    });

    app.get('/3/plugins/:server/:slug/:version', function (req, res) {
        plugin_details(req, res);
    });

    app.get('/3/plugins/:server/:slug/:version/download', function (req, res) {
    	common.plugin_details(req.params.server, req.params.slug, req.params.version, {}, function(data) {
			if (data == null) {
				return res.send(404, "Plugin Does Not Exist");
			}

			if (req.params.version.toLowerCase() == "latest") {
				return res.redirect(data['versions'][0]['download']);
			} else {
				for (var i = 0; i < data['versions']; i++) {
					if (data['versions'][i]['version'] == req.params.version) {
						return res.redirect(data['versions'][i]['download'])
					}
				}
			}

			res.send(404, '{"error": "could not find version"}');
		});
    });

    app.get('/3/authors', function (req, res) {
        common.list_authors(function (callback) {
            res.jsonp(callback);
        });
    });


    function author_plugins (req, res) {
        if (req.params.server == null) {
            req.params.server = undefined;
        }
        var fields = ((req.query.fields == null ? 'slug,plugin_name,description' : bleach.sanitize(req.query.fields)).split(','))
        var start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
        var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
        var sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
        common.list_author_plugins(req.params.server, req.params.name, fields, sort, start, size, function (callback) {
            res.jsonp(callback);
        });
    }

    app.get('/3/authors/:name', function (req, res) {
        author_plugins(req, res);
    });

    app.get('/3/authors/:server/:name', function (req, res) {
        author_plugins(req, res);
    });

    app.get('/3/categories', function (req, res) {
        common.list_categories(function (callback) {
            res.jsonp(callback);
        });
    });

    function category_plugins (req, res) {
        if (req.params.server == null) {
            req.params.server = undefined;
        }
        var fields = ((req.query.fields == null ? 'slug,plugin_name,description' : bleach.sanitize(req.query.fields)).split(','))
        var start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
        var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
        var sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
        common.list_category_plugins(req.params.server, req.params.name, fields, sort, start, size, function (callback) {
            res.jsonp(callback);
        });
    }

    app.get('/3/categories/:name', function (req, res) {
        category_plugins(req, res);
    });

    app.get('/3/categories/:server/:name', function (req, res) {
        category_plugins(req, res);
    });

    app.post('/3/updates', function (req, res) {
        var slugs = (req.body.slugs == null ? '' : bleach.clean(req.body.slugs)).split(',');
        var server = req.body.server == null ? 'bukkit' : bleach.clean(req.body.server);
        common.plugins_up_to_date(slugs, server, function (callback) {
            res.jsonp(callback);
        });
    });

    app.get('/3/updates', function (req, res) {
        var slugs = (req.query.slugs == null ? '' : bleach.clean(req.query.slugs)).split(',');
        var server = req.query.server == null ? 'bukkit' : bleach.clean(req.query.server);
        common.plugins_up_to_date(slugs, server, function (callback) {
            res.jsonp(callback);
        });
    });

    function search (req, res) {
        var filters = []
        if (req.method == 'GET') {
            var fields = ((req.query.fields == null ? 'slug,plugin_name,description' : bleach.sanitize(req.query.fields)).split(','))
            var start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
            var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
            var sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
            var field = bleach.clean(req.params.field);
            var value = bleach.clean(req.params.value);
            filters = [{
                'field': field,
                'action': req.params.action,
                'value': value
            }]
        } else {
            var filters = request.body.filters == null ? [] : JSON.parse(request.body.filters);
            var fields = ((req.body.fields == null ? 'slug,plugin_name,description' : bleach.sanitize(req.body.fields)).split(','))
            var start = req.body.start == null ? undefined : parseInt(bleach.sanitize(req.body.start))
            var size = req.body.size == null ? undefined : parseInt(bleach.sanitize(req.body.size))
            var sort = req.body.sort == null ? 'slug' : bleach.sanitize(req.body.sort)
        }
        common.plugin_search(filters, fields, sort, start, size, function (callback) {
            if (callback == null) {
                return res.send(400, '{"error": "invalid post"}')

            }
            res.jsonp(callback);
        });
    }

    app.post('/3/search', function (req, res) {
        search(req, res);
    });

    app.get('/3/search/:field/:action/:value', function (req, res) {
        search(req, res);
    });
}