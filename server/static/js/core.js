var Settings = {
    Core: {
        templates: '/static/templates/',
        runs: 0,
        poll: 60 // Minutes to refetch repo
    },
    
    Paging: {
        perPage: 15
    }
};

var Core = Class.$extend({
    __include__: [ Settings.Core ],
    
    __classvars__: {
      repo: '/repo.json',
      reply: '',
      json: '',
      polls: 0,
      timer: null,
      views: null,
      pubsub: false,
      runs: 0
    },
    
    __init__: function() {
        var me = this;
        
        // Routing
        if(Settings.Core.runs < 1) {
            this.$route("/", function(){
                me.setView(new Home());
                
                $('.s').keypress(function(e) {
                    console.log(e);
                    if(e.which == 13) {
                        var val = unescape($(this).val());
                        if(val && !val.isEmpty()) me.$navigate('/search', val, true);
                        e.preventDefault();
                        return false;
                    }
                    
                    return true;
                });
            });
        
            this.$route("/home", function(){
                me.setView(new Home());
                
                $('.s').keypress(function(e) {
                    console.log(e);
                    if(e.which == 13) {
                        var val = unescape($(this).val());
                        if(val && !val.isEmpty()) me.$navigate('/search', val, true);
                        e.preventDefault();
                        return false;
                    }
                    
                    return true;
                });
            });
            
            this.$route("/search/:query", function(query){
                me.setView(new Search(query));
                
                $('.s').keypress(function(e) {
                    console.log(e);
                    if(e.which == 13) {
                        var val = unescape($(this).val());
                        if(val && !val.isEmpty()) me.$navigate('/search', val, true);
                        e.preventDefault();
                        return false;
                    }
                    
                    return true;
                });
            });
            
            this.$route("/package/:pack", function(pack){
                me.setView(new Package(pack));
             });
                
            this.$route("/package/:pack/:version", function(pack, version){
                me.setView(new Package(pack, version));
            });
        }
        
        // Views
        this.$class.views = new Template();
        
        // Fetch repo
        this.pollRepo();
        
        if(Settings.Core.runs < 1) {
            // Timer Details
            this.$class.timer = new Timer().interval(1000 * 60); 
            
            // Setup Repo polling
            this.$class.timer.addCallback(this.pollRepo, this.poll);
            
            // Start timer
            this.$class.timer.start();
            
            // Route Setup
            Route.setup();
        }
        
        // Initialized
        Settings.Core.runs++;
    },
    
    register: function(what, obj) {
        this.$class[what] = obj;
    },
    
    setView: function(view) {
        this.$class.pubsub = true;
        publish('/view', [ view ]);
    },
    
    pollRepo: function() {
        var json = this.$json(this.$class.repo);
        var packages = new Packages(json);
        this.$class.reply = packages;
        this.$class.json = { packages: json };
        this.$class.polls++;
    }
});

var Finder = Core.$extend({
    __include__: [ Settings.Paging ],
    
    open: function() {
        
    },
    
    check: function() {
        if(!this.$class.reply)
            alert('[Error] Reply from repo was empty.');
    }
});

var Search = Core.$extend({
    __include__: [ Settings.Paging ],
    
    __init__: function(s) {
       this.$super(this);
       
        if(s) {
            this.packs = {};
            this.packs.packages = [];
            var x = this.packs.packages;
            var i = 0;
            
            for(var p in this.$class.json.packages) {
                var c = this.$class.json.packages[p];
                if(p == "contains") continue;
                
                if(c['name'].equals(s)) x[i] = c;
                if(c['name'].equalsIgnoreCase(s)) x[i] = c;
                if(c['name'].search(new RegExp(s, "gi")) != -1) x[i] = c;
                if(c['description'].search(new RegExp(s, "gi")) != -1) x[i] = c;
                if(this.ctag(c['categories'], s)) x[i] = c;
                i++;
            }
            
            this.packs.packages = x;
        }
    },
    
    open: function() {
        this.$class.views.path(Settings.Core.templates + 'packages.ms').html('.package-list').args(this.packs).parse();
        $('.package-list').show();
    },
    
    close: function() {
        $('.package-list').hide();
    },
    
    ctag: function (tags, against) {
        if(tags.length < 1) return false;
        if(tags.contains(against)) return true;
        if(tags.contains(against.toLowerCase())) return true;
        
        var items = [], tag = "";
        for(var c = 0; c < tags.length; c++){
            tag = tags[c];
            tag.trim();
            
            if(tag.equalsIgnoreCase(against)) return true;
            if(tag.equals(against)) return true;
            if(tag.contains("/")) {
                items = tag.split("/");
                if(items.contains(against)) return true;
                if(items.contains(against.toLowerCase())) return true;
            } else if(tag.contains("-")) {
                items = tag.split("-");
                if(items.contains(against)) return true;
                if(items.contains(against.toLowerCase())) return true;
            } else if(tag.contains(" ")) {
                items = tag.split(" ");
                if(items.contains(against)) return true;
                if(items.contains(against.toLowerCase())) return true;
            }
        }
        
        return false;
    },
});

var Home = Core.$extend({
    __include__: [ Settings.Paging ],
    
    __init__: function() {
       this.$super(this);
    },
    
    open: function() {
        this.$class.views.path(Settings.Core.templates + 'packages.ms').html('.package-list').args(this.$class.json).parse();
        
        $('.desc').each(function() {
            var data = $(this).text();
            
            if(data.length > 80)
                $(this).html(data.substring(0,80) + "...");
        });
        
        $('.package-list').show();
    },
    
    close: function() {
        $('.package-list').hide();
    }
});

var Package = Core.$extend({
    __init__: function(pack, version) {
        this.$super(this);
        
        if(version) this.version = version.replace(/\./g,'_');
        
        var packages = this.$class.reply;
        var p = packages.getPackage(pack), i = 0;
        p.versions.sort(function(a,b){ return a.version < b.version; });
        this.pack = p;
        
        for(var c in p.versions) {
            var v = p.versions[c];
            
            if(typeof v != "object")
                continue;
                
            v.version_u = v.getVersion().replace(/\./g,'_');
            if(i == 0 && !this.version){ this.version = v.version_u; }
            i++;
        }
    },
    
    open: function() {
        var me = this;
        
        if(this.pack) {
            this.$class.views.path(Settings.Core.templates + 'package.ms').html('.package-info').args(this.pack).parse();
            $('.package-info').show();
            
            if(this.version != null) {
                $('#info').hide();
                $('a#v').each(function(i,e){
                    $(this).removeClass('active');
                });
                
                $('.v' + this.version).show();
                // .css({ top: $('.' + this.version).position().top });
                $('.' + this.version).addClass('active');
            }
            
            var pack = this.pack['name'];
            
            $('a#v').click(function() {
                var v = $(this);
                var version = v.attr('version');
                me.$navigate("/package", pack, version, true);
            });
        }
    },
    
    close: function(view) {
        $('.package-info').hide();
    }
});

var View = Class.$extend({
    current: null,
    
    load: function(view) {
        if(this.current) this.unload();
        this.current = view;
        this.current.open();
    },
    
    unload: function() {
        this.current.close();
    }
});

var Pack = Class.$extend({

    __init__: function(name, website, categories, authors, maintainer, description, versions) {
        this.name = name;
        this.website = website;
        this.categories = categories;
        this.authors = authors;
        this.maintainer = maintainer;
        this.description = description;
        this.versions = versions;
    },
    
    getName: function() {
        return this.name;
    },
    
    getWebsite: function() {
        return this.website;
    },
    
    getAuthors: function() {
        return this.authors;
    },
    
    getMaintainer: function() {
        return this.maintainer;
    },
    
    getDescription: function() {
        return this.description;
    },
    
    getCategories: function() {
        return this.categories;
    },
    
    getVersions: function() {
        return this.versions;
    },
    
    getVersion: function(version) {
        for(var v in this.versions)
            if(v.getVersion().equalsIgnoreCase(version))
                return v;
                
        return false;
    },
    
    getLatestVersion: function() {
        function comparator(a, b) {
            return a["version"].compareTo(b["version"]);
        }
        
        this.versions.sort(comparator);
        
        return this.versions[0];
    },
    
    getLatestBranchVersion: function(branch) {
        
    }
});

var Version = Class.$extend({
    __init__: function(version, branch, checksum, url, dependencies, engines) {
        this.version = version;
        this.branch = branch;
        this.checksum = checksum;
        this.url = url;
        this.required_dependencies = dependencies.required;
        this.optional_dependencies = dependencies.optional;
        this.conflicts = dependencies.conflicts;
        this.engines = engines;
    },
    
    getVersion: function() {
        return this.version;
    },
    
    getBranch: function() {
        return this.branch;
    },
    
    getChecksum: function() {
        return this.checksum;
    },
    
    getUrl: function() {
        return this.url;
    },
    
    getDependencies: function() {
        return this.dependencies;
    },
    
    getRequiredDependencies: function() {
        return this.dependencies.required;
    },
    
    getOptionalDependencies: function() {
        return this.dependencies.optional;
    },
    
    hasEngine: function(name) {
        if(isEmpty(this.engines))
            return false;
            
        for(var e in this.engines)
            if(e.getName().equalsIgnoreCase(name))
                return true;
        
        return false;
    },
    
    getEngine: function(name) {
        if(isEmpty(this.engines))
            return false;
            
        for(var e in this.engines)
            if(e.getName().equalsIgnoreCase(name))
                return e;
        
        return false;
    }
});

var Engine = Class.$extend({

    __init__: function(name, min, max) {
        this.min = min;
        this.max = max;
        this.name = name;
    },
    
    getName: function() {
        return this.name;
    },
    
    getMin: function() {
        return this.min;
    },
    
    getMax: function() {
        return this.min;
    }
});

var Packages = Class.$extend({
    __classvars__: {
      dict: {}
    },
    
    __init__: function(packages) {
        for(var x in packages) {
            var p = packages[x];
            var name = p['name'];
            
            if(name.isEmpty())
                continue;
                
            var website = p['website'];
            var authors = p['authors'];
            var maintainer = p['maintainer'];
            var description = p['description'];
            var categories = p['categories'];
            var versions = [];
            
            for(var y in p['versions']) {
                var v = p['versions'][y];
                
                if(typeof v != 'object' || v === undefined)
                    continue;
                
                var version = v['version'], 
                branch = v['branch'],
                checksum = v['checksum'], 
                url = v['location'],
                dependencies = {
                    conflicts: v['conflicts'],
                    required: v['required_dependencies'],
                    optional: v['optional_dependencies']
                },
                engines = [];
                
                for(var z in v['engines']) {
                    var e = v['engines'][z];
                    engines[z] = new Engine(e['engine'], e['build_min'], e['build_max']);
                }
                
                versions[y] = new Version(version, branch, checksum, url, dependencies, engines);
            }
            this.$class.dict[name] = new Pack(name, website,categories, authors, maintainer, description, versions);
        }
        
        return this;
    },
    
    exists: function(name) {
        return this.$class.dict.contains(name);
    },
    
    getPackage: function(name) {
        return this.$class.dict[name];
    },
    
    getPackages: function() {
        return this.__classvars__.dict;
    }
});

$(function() {
    var Views = new View();
    var Watch = subscribe("/view", function(m){
        Views.load(m ? m : new Home());
    });
    
    var System = new Core();
    
    if(!System.$class.pubsub) System.setView(new Home());
    
    var Page = new Finder();
    Page.check();
});