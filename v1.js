module.exports = function (app, db, bleach, common) {
    function geninfo (req, res) {
        size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size));
        common.list_geninfo(size, function (callback) {
            res.jsonp(callback);
        });
    }

    app.get('/1', function (req, res) {
        geninfo(req, res);
    });

    app.get('/1/geninfo', function (req, res) {
        geninfo(req, res);
    });

    app.get('/1/plugins', function (req, res) {
        common.list_plugins('bukkit', ['slug'], 'slug', undefined, undefined, function (callback) {
        	var plugins = [];
        	for (var i = 0; i < callback.length; i++) {
        		plugins.push(callback[i]['slug']);
        	}
            res.jsonp(plugins);
        });
    });

    function plugin_details (req, res) {
        if (req.params.version == null) {
            req.params.version = undefined;
        }
        var fields = ((req.query.fields == null ? 'slug,plugin_name,description' : bleach.sanitize(req.query.fields)).split(','))
        var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
        common.plugin_details('bukkit', req.params.slug, req.params.version, [], function(data) {
            if (data == null) {
                return res.send(404, "Plugin Does Not Exist");
            }

            delete data['slug'];
            delete data['dbo_page'];
            delete data['description'];
            delete data['logo'];
            delete data['logo_full'];
            delete data['server'];
            delete data['website'];
            delete data['popularity'];
            if (data['curse_link'] != null) { delete data['curse_link']; }
            if (data['curse_id'] != null) { delete data['curse_id']; }
            if (data['main'] != null) { delete data['main']; }
            if (data['_use_dbo'] != null) { delete data['_use_dbo']; }

            var versions = [];
            for(var i = 0; i < data['versions'].length; i++) {
                var version = data['versions'][i];
                version['dl_link'] = version['download'];
                version['name'] = version['version'];
                delete version['commands'];
                delete version['permissions'];
                delete version['changelog'];
                delete version['md5'];
                delete version['slug'];
                delete version['download'];
                if (version['file_id'] != null) { delete version['file_id']; }
                if (version['dbo_version'] != null) { delete version['dbo_version']; }
                versions.push(version);
            }

            data['versions'] = versions;

            res.jsonp(data);
        });
    }

    app.get('/1/plugin/:slug', function (req, res) {
        plugin_details(req, res);
    });

    app.get('/1/plugin/:slug/:version', function (req, res) {
        plugin_details(req, res);
    });

    app.get('/1/plugins/:server/:slug/:version/download', function (req, res) {
    	common.plugin_details(req.params.server, req.params.slug, req.params.version, {}, function(data) {
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

    app.get('/1/authors', function (req, res) {
        common.list_authors(function (callback) {
        	var authors = [];
        	for (var i = 0; i < callback.length; i++) {
        		authors.push(callback[i]['name']);
        	}
            res.jsonp(authors);
        });
    });

    app.get('/1/author/:name', function (req, res) {
    	var fields = ['slug']
        var start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
        var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
        var sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
        common.list_author_plugins(undefined, req.params.name, fields, sort, undefined, undefined, function (callback) {
        	if (size != undefined && start != undefined) {
        		callback = callback.slice(start, callback.length);
        		callback.length = size;
        	} 
        	var authors = [];
        	for (var i = 0; i < callback.length; i++) {
        		authors.push(callback[i]['slug']);
        	}
            res.jsonp(authors);
        });
    });

    app.get('/1/categories', function (req, res) {
        common.list_categories(function (callback) {
        	var categories = [];
        	for (var i = 0; i < callback.length; i++) {
        		categories.push(callback[i]['name']);
        	}
            res.jsonp(categories);
        });
    });

    app.get('/1/categories/:name', function (req, res) {
    	var fields = ['slug']
        var start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
        var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
        var sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
        common.list_category_plugins(undefined, req.params.name, fields, sort, undefined, undefined, function (callback) {
        	if (size != undefined && start != undefined) {
        		callback = callback.slice(start, callback.length);
        		callback.length = size;
        	} 
        	var categories = [];
        	for (var i = 0; i < callback.length; i++) {
        		categories.push(callback[i]['slug']);
        	}
            res.jsonp(categories);
        });
    });

    app.get('/1/search/:field/:action/:value', function (req, res) {
    	var fields = ['slug'];
        var start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
        var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
        var sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
        var field = bleach.clean(req.params.field);
        var value = bleach.clean(req.params.value);
        var filters = [{
            'field': field,
            'action': req.params.action,
            'value': value
        }]

        common.plugin_search(filters, fields, sort, undefined, undefined, function (callback) {
            if (callback == null) {
                return res.send(400, '{"error": "invalid search"}')

            }
        	if (size != undefined && start != undefined) {
        		callback = callback.slice(start, callback.length);
        		callback.length = size;
        	} 
        	var plugins = [];
        	for (var i = 0; i < callback.length; i++) {
        		plugins.push(callback[i]['slug']);
        	}
            res.jsonp(plugins);
        });
    });
}