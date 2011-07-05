/* HashRoute
 *
 * Based on Spine, tied into Classy
 * Url Routing made easy. Finally.
 *
 * @author: Nijikokun <nijikokun@gmail.com>
 * @copyright: 2011
 * @version: 0.1.3
 */
var hashStrip = /^#*/;
var namedParam   = /:([\w\d]+)/g;
var splatParam   = /\*([\w\d]+)/g;
var escapeRegExp = /[-[\]{}()+?.,\\^$|#\s]/g;
var Routes = [];

var makeArray = function(args){
    return Array.prototype.slice.call(args, 0);
};

var Route = {
    historySupport: ("history" in window),
    history: false,
    routes: [],
    
    proxy: function(func){
      var thisObject = this;
      return(function(){ 
        return func.apply(thisObject, arguments); 
      });
    },
    
    proxyAll: function(){
      var functions = makeArray(arguments);
      for (var i=0; i < functions.length; i++)
        this[functions[i]] = this.proxy(this[functions[i]]);
    },
        
    add: function(path, callback){
      if (typeof path == "object") {
        for(var p in path) this.add(p, path[p]);
      } else {
        if (typeof path == "string") {      
          path = path.replace(escapeRegExp, "\\$&").replace(namedParam, "([^\/]*)").replace(splatParam, "(.*?)");
          path = new RegExp('^' + path + '$');
        }
        
        this.routes.push({ 'route': path, 'callback': callback });
      }
    },
    
    setup: function(options){
      if (options && options.history)
        this.history = this.historySupport && options.history;
        
      if ( this.history )
        $(window).bind("popstate", this.change);
      else
        $(window).bind("hashchange", this.change);
        
      this.change();
    },
    
    unbind: function(){
      if (this.history)
        $(window).unbind("popstate", this.change);
      else
        $(window).unbind("hashchange", this.change);
    },
    
    navigate: function(){
      var args = makeArray(arguments);
      var triggerRoutes = false;
      
      if (typeof args[args.length - 1] == "boolean") {
        triggerRoutes = args.pop();
      }
      
      var path = args.join("/");      
      if (this.path == path) return;
      
      if ( !triggerRoutes )
        this.path = path;
      
      if (this.history)
        history.pushState({}, 
          document.title, 
          this.getHost() + path
        );
      else
        window.location.hash = path;
    },
    
    match: function(path, route, callback){
      var match = route.exec(path);
      if ( !match ) return false;
      var params = match.slice(1);
      callback.apply(callback, params);
      return true;
    },
    
    // Private
    
    getPath: function(){
      return window.location.pathname;
    },
    
    getHash: function(){
      return window.location.hash;
    },
    
    getHost: function(){
      return((document.location + "").replace(
        this.getPath() + this.getHash(), ""
      ));
    },
    
    getFragment: function(){
      return this.getHash().replace(hashStrip, "");
    },
    
    change: function(e){
      var path = (this.history ? this.getPath() : this.getFragment());
      if (path == this.path) return;
      this.path = path;
      
      if(path.isEmpty())
        path = "/";
        
      for (var i=0; i < this.routes.length; i++) {
        var r = this.routes[i];
        if (this.match(path, r['route'], r['callback'])) return;
      }
    }
};

Route.proxyAll("change");

Class.$globals.$route = function(p, c){
  Route.add(p, Route.proxy(c));
};

Class.$globals.$routes = function(r){
  for(var p in r)
    Class.$globals.$route(p, r[p]);
};

Class.$globals.$navigate = function(){
  Route.navigate.apply(Route, arguments);
};