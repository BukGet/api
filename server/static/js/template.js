var Template = Class.$extend({
    data: '',
    vars: '',
    el: '',
    
    __init__: function(resource) {
        this.path(resource);
    },
    
    path: function(resource) {
        this.url = resource;
        return this;
    },
    
    on: function(fn) {
        this.fn = fn;
        return this;
    },
    
    html: function(on) {
        this.el = on;
        return this;
    },
    
    args: function(data) {
        this.vars = data;
        return this;
    },
    
    append: function() {
        if(!this.url || !this.on || !this.vars) return this;
        this.data = this.$fetch(this.url);
        if(this.el) $(this.el).append(Mustache.to_html(this.data, this.vars));
        return this;
    },
    
    parse: function() {
        if(!this.url || !this.on || !this.vars) return this;
        this.data = this.$fetch(this.url);
        if(this.el) $(this.el).html(Mustache.to_html(this.data, this.vars));
        return this;
    }
});