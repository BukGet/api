var settings = {
    repo: 'repo.json',
    
    // Used for the load-more
    paging: {
        current: 0,
        next: 0,
        per: 2,
        max: 0,
        jumping: false,
        already: false
    },
    
    // Currently unused.
    colors: {
        taupe: '#EBE8E0',
        black: '#000000',
        grey: '#141414',
        ltgrey: '#252525',
        silver: '#444444',
        blue: '#00597B',
        pink: '#FF1D8E',
        white: '#FFFFFF'
    },
    
    // Below this is all pertained to url data.
    search: {
        title: '',
        tag: '',
        author: '',
        term: ''
    },
    
    viewing: {
        plugin: '',
        version: ''
    }
};

var system = {
    init: function() {
        $('#plugin-info').css({ 'display': 'none' });
        $('#plugin-list').css({ 'opacity': 0 });
        $('#more').hide();
        
        if(settings.search.title.isEmpty() && settings.search.tag.isEmpty() && settings.search.author.isEmpty() && settings.search.term.isEmpty()) {
            system.search(false);
        }
    },
    
    setHash: function(full) {
        location.href = "#/" + full;
    },

    getTemplate: function (name) {
        return unescape($('#' + name).html());
    },
    
    checkTags: function (tags, against) {
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
    
    search: function (reload) {
        if(reload) {
            settings.paging.current = 0;
            settings.paging.max = 0;
        }
        
        $.post(settings.repo, function (source) {
            var data = [], i = [];
            
            if(!settings.search.term.isEmpty()) {
                for(var c = 0; c < source.length; c++){
                    i = source[c];
                    
                    if(i['name'].contains(settings.search.term)) data[c] = i;
                    if(i['description'].search("/" + settings.search.term + "/i")) data[c] = i;
                }
            } else {
                data = source;
            }
            
            if(data.length < 1) {
                $("#plugins").html("No results found");
                $("#more").hide();
                return;
            }
            
            settings.paging.max = data.length;
            if(!settings.paging.jumping) settings.paging.next = settings.paging.current + settings.paging.per;
            
            if(settings.paging.next > settings.paging.max) settings.paging.next = settings.paging.max; 
            if(settings.paging.current == settings.paging.max) return;

            system.setHash('list/' + settings.paging.next);
            
            $("#plugins").animate({ "opacity": 0 }, 200, function () {
                var m = "", t = system.getTemplate('plugin-small');
                for(var c = settings.paging.current; c < settings.paging.next; c++){
                    p = data[c];
                    
                    m += t.bind({
                        'name': p['name'], 
                        'desc': p['description'].substring(0,62) + "...", 
                        'author': p['author'],
                        'website': p['website']
                    });
                }
                
                settings.paging.current = c;
                
                if(!m.isEmpty()){
                    if(settings.paging.current == settings.paging.per || $("#plugins").html().equalsIgnoreCase("no results") || $("#plugins").html().isEmpty()) {
                        $("#plugins").html(m);
                        $("#more").show();
                        $("#more").html(system.getTemplate("load-more").bind({ 'amount': settings.paging.per }));
                    } else {
                        $("#plugins").append(m);
                    }
                    
                    settings.paging.jumping = false;
                } else {
                    $("#plugins").html("<div id='error'>No results found</div>");
                    $("#more").hide();
                }
                
                if(settings.paging.current == settings.paging.max || settings.paging.max == 0 || settings.paging.next >= settings.paging.max) {
                    $("#more").hide();
                }
                
                $("#plugins").animate({ "opacity": 1 }, 200);
            });
        }, "json");
    },
    
    update: function (id, value) {
        // settings[id.trim()] = value.trim();
        // $("#" + id.trim()).val(value.trim());
    },
    
    open: {
        search: function() {
            $('#search').fadeIn();
        }
    },
    
    view: {
        version: function(version) {
        
        },
        
        plugin: function(){
            
        },
        
        search: function(f) {
            console.log("doing search with: " + f);
            settings.search.term = f.trim();
            system.search(true);
        },
        
        list: function(f) {
            if(!isNumber(f)) return;
            settings.paging.next = parseInt(f);
            settings.paging.jumping = true;
        }
    }
};

function isNumber(n) {
  return !isNaN(parseFloat(n)) && isFinite(n);
}

Array.prototype.contains = function (element) {
    for (var i = 0; i < this.length; i++) {
        if (this[i] == element) {
            return true;
        }
    }
    return false;
}