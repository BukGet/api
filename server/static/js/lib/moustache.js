var Mustache=function(){var j=function(){};j.prototype={otag:"{{",ctag:"}}",pragmas:{},buffer:[],pragmas_implemented:{"IMPLICIT-ITERATOR":!0},context:{},render:function(a,b,d,c){if(!c)this.context=b,this.buffer=[];if(!this.includes("",a))if(c)return a;else{this.send(a);return}a=this.render_pragmas(a);a=this.render_section(a,b,d);if(c)return this.render_tags(a,b,d,c);this.render_tags(a,b,d,c)},send:function(a){a!=""&&this.buffer.push(a)},render_pragmas:function(a){if(!this.includes("%",a))return a;
var b=this;return a.replace(RegExp(this.otag+"%([\\w-]+) ?([\\w]+=[\\w]+)?"+this.ctag),function(a,c,e){if(!b.pragmas_implemented[c])throw{message:"This implementation of mustache doesn't understand the '"+c+"' pragma"};b.pragmas[c]={};e&&(a=e.split("="),b.pragmas[c][a[0]]=a[1]);return""})},render_partial:function(a,b,d){a=this.trim(a);if(!d||d[a]===void 0)throw{message:"unknown_partial '"+a+"'"};if(typeof b[a]!="object")return this.render(d[a],b,d,!0);return this.render(d[a],b[a],d,!0)},render_section:function(a,
b,d){if(!this.includes("#",a)&&!this.includes("^",a))return a;var c=this;return a.replace(RegExp(this.otag+"(\\^|\\#)\\s*(.+)\\s*"+this.ctag+"\n*([\\s\\S]+?)"+this.otag+"\\/\\s*\\2\\s*"+this.ctag+"\\s*","mg"),function(a,g,i,f){a=c.find(i,b);if(g=="^")return!a||c.is_array(a)&&a.length===0?c.render(f,b,d,!0):"";else if(g=="#")return c.is_array(a)?c.map(a,function(a){return c.render(f,c.create_context(a),d,!0)}).join(""):c.is_object(a)?c.render(f,c.create_context(a),d,!0):typeof a==="function"?a.call(b,
f,function(a){return c.render(a,b,d,!0)}):a?c.render(f,b,d,!0):""})},render_tags:function(a,b,d,c){for(var e=this,g=function(){return RegExp(e.otag+"(=|!|>|\\{|%)?([^\\/#\\^]+?)\\1?"+e.ctag+"+","g")},i=g(),f=function(a,c,f){switch(c){case "!":return"";case "=":return e.set_delimiters(f),i=g(),"";case ">":return e.render_partial(f,b,d);case "{":return e.find(f,b);default:return e.escape(e.find(f,b))}},a=a.split("\n"),h=0;h<a.length;h++)a[h]=a[h].replace(i,f,this),c||this.send(a[h]);if(c)return a.join("\n")},
set_delimiters:function(a){a=a.split(" ");this.otag=this.escape_regex(a[0]);this.ctag=this.escape_regex(a[1])},escape_regex:function(a){if(!arguments.callee.sRE)arguments.callee.sRE=RegExp("(\\/|\\.|\\*|\\+|\\?|\\||\\(|\\)|\\[|\\]|\\{|\\}|\\\\)","g");return a.replace(arguments.callee.sRE,"\\$1")},find:function(a,b){var a=this.trim(a),d;b[a]===!1||b[a]===0||b[a]?d=b[a]:(this.context[a]===!1||this.context[a]===0||this.context[a])&&(d=this.context[a]);if(typeof d==="function")return d.apply(b);if(d!==
void 0)return d;return""},includes:function(a,b){return b.indexOf(this.otag+a)!=-1},escape:function(a){return String(a===null?"":a).replace(/&(?!\w+;)|["'<>\\]/g,function(a){switch(a){case "&":return"&amp;";case "\\":return"\\\\";case '"':return"&quot;";case "'":return"&#39;";case "<":return"&lt;";case ">":return"&gt;";default:return a}})},create_context:function(a){if(this.is_object(a))return a;else{var b=".";if(this.pragmas["IMPLICIT-ITERATOR"])b=this.pragmas["IMPLICIT-ITERATOR"].iterator;var d=
{};d[b]=a;return d}},is_object:function(a){return a&&typeof a=="object"},is_array:function(a){return Object.prototype.toString.call(a)==="[object Array]"},trim:function(a){return a.replace(/^\s*|\s*$/g,"")},map:function(a,b){if(typeof a.map=="function")return a.map(b);else{for(var d=[],c=a.length,e=0;e<c;e++)d.push(b(a[e]));return d}}};return{name:"mustache.js",version:"0.3.1-dev",to_html:function(a,b,d,c){var e=new j;if(c)e.send=c;e.render(a,b,d);if(!c)return e.buffer.join("\n")}}}();