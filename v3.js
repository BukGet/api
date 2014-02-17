module.exports = function (app, db, common) {
    function geninfo (req, res, next) {
        size = req.query.size == null ? undefined : parseInt(req.query.size);
        common.list_geninfo(size, function (callback) {
            res.send(callback);
            
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
            
        });
    });

    function plugin_list (req, res, next) {
        var fields = ((req.query.fields == null ? 'slug,plugin_name,description' : req.query.fields).split(','))
        var start = req.query.start == null ? undefined : parseInt(req.query.start)
        var size = req.query.size == null ? undefined : parseInt(req.query.size)
        var sort = req.query.sort == null ? 'slug' : req.query.sort
        common.list_plugins(req.params.server, fields, sort, start, size, function (callback) {
            res.send(callback);
            
        });
    }

    app.get('/3/plugins', function (req, res, next) {
        plugin_list(req, res, next);
    });

    app.get('/3/plugins/:server', function (req, res, next) {
        plugin_list(req, res, next);
    });

    function plugin_details (req, res, next) {
        if (req.params.server == null) {
            req.params.server = undefined;
        }
        if (req.params.version == null) {
            req.params.version = undefined;
        }
        var fields = ((req.query.fields == null ? '' : req.query.fields).split(','))
        var size = req.query.size == null ? undefined : parseInt(req.query.size)
        common.plugin_details(req.params.server, req.params.slug, req.params.version, fields, function(data) {
            if (data == null) {
                return res.send(404, "Plugin Does Not Exist");
            }
            if (size != undefined) {
                data['versions'].length = size;
            }
            res.send(data);
            
        });
    }

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
			}

			if (req.params.version.toLowerCase() == "latest") {
                res.header('Location', data['versions'][0]['download']);
                res.send(302);
			} else {
				for (var i = 0, il=data['versions'].length; i < il; i++) {
					if (data['versions'][i]['version'] == req.params.version) {
                        res.header('Location', data['versions'][i]['download']);
						res.send(302);
					}
				}
			}

			res.send(404, '{"error": "could not find version"}');
		});
    });

    app.get('/3/authors', function (req, res, next) {
        common.list_authors(function (callback) {
            res.send(callback);
        });
    });


    function author_plugins (req, res, next) {
        if (req.params.server == null) {
            req.params.server = undefined;
        }
        var fields = ((req.query.fields == null ? 'slug,plugin_name,description' : req.query.fields).split(','))
        var start = req.query.start == null ? undefined : parseInt(req.query.start)
        var size = req.query.size == null ? undefined : parseInt(req.query.size)
        var sort = req.query.sort == null ? 'slug' : req.query.sort
        common.list_author_plugins(req.params.server, req.params.name, fields, sort, start, size, function (callback) {
            res.send(callback);
        });
    }

    app.get('/3/authors/:name', function (req, res, next) {
        author_plugins(req, res, next);
    });

    app.get('/3/authors/:server/:name', function (req, res, next) {
        author_plugins(req, res, next);
    });

    app.get('/3/categories', function (req, res, next) {
        common.list_categories(function (callback) {
            res.send(callback);
        });
    });

    function category_plugins (req, res, next) {
        if (req.params.server == null) {
            req.params.server = undefined;
        }
        var fields = ((req.query.fields == null ? 'slug,plugin_name,description' : req.query.fields).split(','))
        var start = req.query.start == null ? undefined : parseInt(req.query.start)
        var size = req.query.size == null ? undefined : parseInt(req.query.size)
        var sort = req.query.sort == null ? 'slug' : req.query.sort
        common.list_category_plugins(req.params.server, req.params.name, fields, sort, start, size, function (callback) {
            res.send(callback);
        });
    }

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
        });
    });

    app.get('/3/updates', function (req, res, next) {
        var slugs = (req.query.slugs == null ? '' : req.query.slugs).split(',');
        var server = req.query.server == null ? 'bukkit' : req.query.server;
        common.plugins_up_to_date(slugs, server, function (callback) {
            res.send(callback);
        });
    });

    function search (req, res, next) {
        var filters = []
        if (req.method == 'GET') {
            var fields = ((req.query.fields == null ? 'slug,plugin_name,description' : req.query.fields).split(','))
            var start = req.query.start == null ? undefined : parseInt(req.query.start)
            var size = req.query.size == null ? undefined : parseInt(req.query.size)
            var sort = req.query.sort == null ? 'slug' : req.query.sort
            var field = req.params.field;
            var value = req.params.value;
            filters = [{
                'field': field,
                'action': req.params.action,
                'value': value
            }]
        } else {
            var filters = req.params.filters == null ? [] : JSON.parse(req.params.filters);
            var fields = ((req.params.fields == null ? 'slug,plugin_name,description' : req.params.fields).split(','))
            var start = req.params.start == null ? undefined : parseInt(req.params.start)
            var size = req.params.size == null ? undefined : parseInt(req.params.size)
            var sort = req.params.sort == null ? 'slug' : req.params.sort;
        }
        common.plugin_search(filters, fields, sort, start, size, false, function (callback) {
            if (callback == null) {
                return res.send(400, '{"error": "invalid post"}');
            }
            res.send(callback);
        });
    }

    app.post('/3/search', function (req, res, next) {
        search(req, res, next);
    });

    app.get('/3/search/:field/:action/:value', function (req, res, next) {
        search(req, res, next);
    });
}