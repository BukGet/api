module.exports = function(app, db, bleach, common) {
	function geninfo (req, res) {
	    size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size));
    	common.list_geninfo(size, function(callback) {
    		res.jsonp(callback);
    	});
	}

	app.get('/v3', function (req, res) {
		geninfo(req, res);
	});

	app.get('/v3/geninfo', function (req, res) {
		geninfo(req, res);
	});

	app.get('/v3/geninfo/:idnum', function (req, res) {
		common.get_geninfo(req.params.idnum, function (callback) {
			res.jsonp(callback);
		});
	});

	function plugin_list (req, res) {
		if (req.params.server == null) {
			req.params.server = undefined;
		}
	    fields = ((req.query.fields == null ? 'slug,plugin_name,description' : bleach.sanitize(req.query.fields)).split(','))
	    start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
	    size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
	    sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
		common.list_plugins(req.params.server, fields, sort, start, size, function (callback) {
			res.jsonp(callback);
		});
	}

	app.get('/v3/plugins', function (req, res) {
		plugin_list(req, res);
	});

	app.get('/v3/plugins/:server', function (req, res) {
		plugin_list(req, res);
	});

	function plugin_details (req, res) {
		fields = ((req.query.fields == null ? 'slug,plugin_name,description' : bleach.sanitize(req.query.fields)).split(','))
	    size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
		common.plugin_details(server, slug, version, fields, function (data) {
			if (data == null) {
				return res.send(404, "Plugin Does Not Exist");
			}
			if (size != undefined) {
				data['versions'].length = size;
			}
			res.jsonp(data);
		});
	}

	app.get('/v3/plugins/:server/:slug', function (req, res) {
		plugin_details(req, res);
	});

	app.get('/v3/plugins/:server/:slug/:version', function (req, res) {
		plugin_details(req, res);
	});

	app.get('/v3/plugins/:server/:slug/:version/download', function (req,res) {
		common.plugin_details(req.params.server, req.params.slug, req.params.version, {}, function (data) {
			if (data == null) {
				return res.send(404, "Plugin Does Not Exist");
			}

			if (version.toLowerCase() == "latest") {
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

	app.get('/v3/authors', function (req, res) {
		common.list_authors(function (callback) {
			res.jsonp(callback);
		});
	});


	function author_plugins (req, res) {
		if (req.params.server == null) {
			req.params.server = undefined;
		}
	    fields = ((req.query.fields == null ? 'slug,plugin_name,description' : bleach.sanitize(req.query.fields)).split(','))
	    start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
	    size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
	    sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
		common.list_author_plugins(req.params.server, req.params.name, fields, sort, start, size, function (callback) {
			res.jsonp(callback);
		});
	}

	app.get('/v3/authors/:name', function (req, res) {
		author_plugins(req, res);
	});

	app.get('/v3/authors/:server/:name', function (req, res) {
		author_plugins(req, res);
	});

	app.get('/v3/categories', function (req, res) {
		common.list_categories(function (callback) {
			res.jsonp(callback);
		});
	});

	function category_plugins (req, res) {
		if (req.params.server == null) {
			req.params.server = undefined;
		}
	    fields = ((req.query.fields == null ? 'slug,plugin_name,description' : bleach.sanitize(req.query.fields)).split(','))
	    start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
	    size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
	    sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
		common.list_category_plugins(req.params.server, req.params.name, fields, sort, start, size, function (callback) {
			res.jsonp(callback);
		});
	}

	app.get('/v3/categories/:name', function (req, res) {
		category_plugins(req, res);
	});

	app.get('/v3/categories/:server/:name', function (req, res) {
		category_plugins(req, res);
	});

	app.post('/v3/updates', function (req, res) {
        slugs = (req.body.slugs == null ? '' : bleach.clean(req.body.slugs)).split(',');
        server = req.body.server == null ? 'bukkit' : bleach.clean(req.body.server);
		common.plugins_up_to_date(slugs, server, function (callback) {
			res.jsonp(callback);
		});
	});

	app.get('/v3/updates', function (req, res) {
		slugs = (req.query.slugs == null ? '' : bleach.clean(req.query.slugs)).split(',');
        server = req.query.server == null ? 'bukkit' : bleach.clean(req.query.server);
		common.plugins_up_to_date(slugs, server, function (callback) {
			res.jsonp(callback);
		});
	});

	function search (req, res) {
	    filters = []
		if (req.method == 'GET') {
	    	fields = ((req.query.fields == null ? 'slug,plugin_name,description' : bleach.sanitize(req.query.fields)).split(','))
		    start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
		    size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
		    sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
		    field = bleach.clean(req.params.field);
		    value = bleach.clean(req.params.value);
		    filters = [
		        {'field': field, 'action': req.params.action, 'value': value}
		    ]	
		} else {
		    filters = request.body.filters == null ? [] : JSON.parse(request.body.filters);
			fields = ((req.body.fields == null ? 'slug,plugin_name,description' : bleach.sanitize(req.body.fields)).split(','))
		    start = req.body.start == null ? undefined : parseInt(bleach.sanitize(req.body.start))
		    size = req.body.size == null ? undefined : parseInt(bleach.sanitize(req.body.size))
		    sort = req.body.sort == null ? 'slug' : bleach.sanitize(req.body.sort)
		}
		common.plugin_search(filters, fields, sort, start, size, function (callback) {
			if(callback == null) {
				return res.send(400, '{"error": "invalid post"}')

			}
			res.jsonp(callback);
		});
	}

	app.post('/v3/search', function (req, res) {
		search (req, res);
	})

	app.get('/v3/search/:field/:action/:value', function (req, res) {
		search (req, res);
	})
}