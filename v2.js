module.exports = function (app, db, bleach, common) {
	function v2to3 (items, callback) {
		var convert = {
	        'plugname': 'plugin_name',
	        'name': 'slug',
	        'repo': 'server',
	        'link': 'dbo_page',
	        'slug': 'name',
	    }
	    var data = []
	    for (var i in items) {
	    	if (convert[items[i]] != null) {
				data.push(convert[items[i]]);
	        } else {
				data.push(items[i]);
	        }
	    }
	    callback(data);
	}

	function v3to2 (items, callback) {
	    var data = []
	    for (var i = 0; i < items.length; i++) {
	        if (items[i]['dbo_page'] != null) {
	            items[i]['link'] = items[i]['dbo_page']
	            delete items[i]['dbo_page'];
	        }
	        if (items[i]['server'] != null) {
	            items[i]['repo'] = items[i]['server']
	            delete items[i]['server'];
	        }
	        if (items[i]['plugin_name'] != null) {
	            items[i]['plugname'] = items[i]['plugin_name']
	            delete items[i]['plugin_name'];
	        }
	        if (items[i]['slug'] != null) {
	            items[i]['name'] = items[i]['slug']
	            delete items[i]['slug'];
	        }
	        if (items[i]['_use_dbo'] != null) { delete items[i]['_use_dbo']; }
	        if (items[i]['logo'] != null) { delete items[i]['logo']; }
	        if (items[i]['popularity'] != null) { delete items[i]['popularity']; }
	        if (items[i]['main'] != null) { delete items[i]['main']; }
	        if (items[i]['logo_full'] != null) { delete items[i]['logo_full']; }
	        if (data['curse_link'] != null) { delete data['curse_link']; }
	        if (data['curse_id'] != null) { delete data['curse_id']; }
	        if (items[i]['versions'] != null) {
	            var versions = [];
	        	for (var x = 0; x < items[i]['versions'].length; x++) {
	                if (items[i]['versions'][x]['slug'] != null) { delete items[i]['versions'][x]['slug']; }
	                if (items[i]['versions'][x]['dbo_version'] != null) { delete items[i]['versions'][x]['dbo_version']; }
	                if (items[i]['versions'][x]['changelog'] != null) { delete items[i]['versions'][x]['changelog']; }
	                if (items[i]['versions'][x]['file_id'] != null) { delete items[i]['versions'][x]['file_id']; }
	                versions.push(items[i]['versions'][x]);
	        	}
	            items[i]['versions'] = versions;
	        }
	        data.push(items[i]);
	    }
		callback(data);
	}

    function geninfo (req, res) {
        size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size));
        common.list_geninfo(size, function (callback) {
            res.jsonp(callback);
        });
    }

    app.get('/2', function (req, res) {
        geninfo(req, res);
    });

    app.get('/2/geninfo', function (req, res) {
        geninfo(req, res);
    });

    app.get('/2/:server/plugins', function (req, res) {
        if (req.params.server == null) {
            req.params.server = undefined;
        }
        var fields = ((req.query.fields == null ? 'name,plugname,description' : bleach.sanitize(req.query.fields)).split(','))
        v2to3(fields, function (callback) {
        	fields = callback;
        })
        var start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
        var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
        var sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
        common.list_plugins(req.params.server, fields, sort, start, size, function (callback) {
            res.jsonp(callback);
        });
    });

    function plugin_details (req, res) {
        var fields = ((req.query.fields == null ? '' : bleach.sanitize(req.query.fields)).split(','));
    	v2to3(fields, function (callback) {
        	fields = callback;
        })
        common.plugin_details(req.params.server, req.params.slug, req.params.version, fields, function(data) {
            if (data == null) {
                return res.send(404, "Plugin Does Not Exist");
            }
	        v3to2([data], function (callback) {
	        	data = callback[0];
        	})
            if (data['versions'] != null && data['versions'].length == 1) {
            	data['versions'] = data['versions'][0]
            }
            res.jsonp(data);
        });
    }

    app.get('/2/:server/plugin/:slug', function (req, res) {
        plugin_details(req, res);
    });

    app.get('/2/:server/plugin/:slug/:version', function (req, res) {
        plugin_details(req, res);
    });

    app.get('/2/:server/plugin/:slug/:version/download', function (req, res) {
        common.plugin_details(req.params.server, req.params.slug, req.params.version, {}, function(data) {
            if (data == null) {
                return res.send(404, "Plugin Does Not Exist");
            }

            if (req.params.version.toLowerCase() == "latest") {
                return res.redirect(data['versions'][0]['download']);
            } else {
                for (var i = 0; i < data['versions'].length; i++) {
                    if (data['versions'][i]['version'] == req.params.version) {
                        return res.redirect(data['versions'][i]['download']);
                    }
                }
            }

            res.send(404, '{"error": "could not find version"}');
        });
    });

    app.get('/2/authors', function (req, res) {
        common.list_authors(function (callback) {
        	var authors = [];
        	for (var i = 0; i < callback.length; i++) {
        		authors.push(callback[i]['name']);
        	}
            res.jsonp(authors);
        });
    });

    app.get('/2/:server/author/:name', function (req, res) {
        if (req.params.server == null) {
            req.params.server = undefined;
        }
        var fields = ((req.query.fields == null ? 'name,plugname,description' : bleach.sanitize(req.query.fields)).split(','))
        v2to3(fields, function (callback) {
        	fields = callback;
        })
        var start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
        var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
        var sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
        common.list_author_plugins(req.params.server, req.params.name, fields, sort, start, size, function (callback) {
	        v3to2(callback, function (the_callback) {
            	res.jsonp(the_callback);
        	})
        });
    });

    app.get('/2/categories', function (req, res) {
        common.list_categories(function (callback) {
        	var categories = [];
        	for (var i = 0; i < callback.length; i++) {
        		categories.push(callback[i]['name']);
        	}
            res.jsonp(categories);
        });
    });

    app.get('/2/:server/category/:name', function (req, res) {
        var fields = ((req.query.fields == null ? 'name,plugname,description' : bleach.sanitize(req.query.fields)).split(','))
        v2to3(fields, function (callback) {
        	fields = callback;
        })
        var start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
        var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
        var sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
        common.list_category_plugins(req.params.server, req.params.name, fields, sort, start, size, function (callback) {
	        v3to2(callback, function (the_callback) {
            	res.jsonp(the_callback);
        	})
        });
    });

    app.get('/2/search/:base/:field/:action/:value', function (req, res) {
        var fields = ((req.query.fields == null ? 'name,plugname,description' : bleach.sanitize(req.query.fields)).split(','))
    	v2to3(fields, function (callback) {
    		fields = callback;
    	});
        var start = req.query.start == null ? undefined : parseInt(bleach.sanitize(req.query.start))
        var size = req.query.size == null ? undefined : parseInt(bleach.sanitize(req.query.size))
        var sort = req.query.sort == null ? 'slug' : bleach.sanitize(req.query.sort)
        var field = bleach.sanitize(req.params.field);
        var value = bleach.sanitize(req.params.value);
        var base = bleach.sanitize(req.params.base);
        if (req.params.action == 'in') {
        	req.params.action = 'like';
        }
        if (base == 'version') {
        	field = 'versions.' + field
        }
        if (field == undefined) {
        	field = { field: true };
        }
    	v2to3([field], function (callback) {
    		field = callback[0];
    	})
        var filters = [{
            'field': field,
            'action': req.params.action,
            'value': value
        }]

        common.plugin_search(filters, fields, sort, start, size, false, function (callback) {
            if (callback == null) {
                return res.send(400, '{"error": "invalid search"}')
            }
	        v3to2(callback, function (the_callback) {
            	res.jsonp(the_callback);
        	})
        });
    });
}