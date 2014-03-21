var should = require('should'); 
var request = require('supertest');  
var mongode = require('mongode');
var config = require('../config');
var ObjectID = require('mongode').ObjectID;

var instance;
var db = mongode.connect(config.database.host + config.database.test_name);
db.collection('plugins');
db.collection('webstats');
db.collection('geninfo');
db.collection('authors');
db.collection('categories');
//Cleanup when testing locally to make sure it's not DB related
db.plugins.remove({}, function callback (err, res) {});
db.webstats.remove({}, function callback (err, res) {});
db.geninfo.remove({}, function callback (err, res) {});
db.authors.remove({}, function callback (err, res) {});
db.categories.remove({}, function callback (err, res) {});

require('../server')(config.database.host + config.database.test_name, function (callback) { instance = callback; }); 
var plugin = { "_use_dbo" : true, "website": "http://dev.bukkit.org/bukkit-plugins/clearthechat", "dbo_page": "http://dev.bukkit.org/bukkit-plugins/clearthechat", "main": "com.iAlexak.ClearTheChat.ClearTheChat", "description": "", "curse_id": 48244, "versions": [ { "status": "Semi-normal", "commands": [ { "usage": "/<command>", "permission": "", "command": "clearchat", "permission-message": "", "aliases": [ ] } ], "changelog": "PGRpdiBjbGFzcz0iY29udGVudC1ib3gtaW5uZXIiPgo8aDM+CiBDaGFuZ2UgbG9nCjwvaDM+Cjxz\nZWN0aW9uIGNsYXNzPSJ0b2MgZXhwYW5kaW5nLW1vZHVsZSIgZGF0YS1leHBhbmQtYnk9InRvYyIg\nZGF0YS1leHBhbmQtZGVmYXVsdD0ib3BlbiI+CiA8ZGl2IGNsYXNzPSJjb250ZW50LWJveCI+CiAg\nPGRpdiBjbGFzcz0iY29udGVudC1ib3gtaW5uZXIiPgogICA8aDM+CiAgICBUYWJsZSBvZiBjb250\nZW50cwogICA8L2gzPgogICA8b2wgY2xhc3M9InRvYy1sZXZlbCB0b2MtbGV2ZWwtMSI+CiAgICA8\nbGk+CiAgICAgPGEgaHJlZj0iI3ctdmVyc2lvbi0xLTAiPgogICAgICA8c3BhbiBjbGFzcz0idG9j\nLW51bWJlciI+CiAgICAgICAxCiAgICAgIDwvc3Bhbj4KICAgICAgPHNwYW4gY2xhc3M9InRvYy10\nZXh0Ij4KICAgICAgIFZlcnNpb24gMS4wCiAgICAgIDwvc3Bhbj4KICAgICA8L2E+CiAgICAgPG9s\nIGNsYXNzPSJ0b2MtbGV2ZWwgdG9jLWxldmVsLTIiPgogICAgICA8bGk+CiAgICAgICA8YSBocmVm\nPSIjdy1yZWxlYXNlIj4KICAgICAgICA8c3BhbiBjbGFzcz0idG9jLW51bWJlciI+CiAgICAgICAg\nIDEuMQogICAgICAgIDwvc3Bhbj4KICAgICAgICA8c3BhbiBjbGFzcz0idG9jLXRleHQiPgogICAg\nICAgICArIFJlbGVhc2UKICAgICAgICA8L3NwYW4+CiAgICAgICA8L2E+CiAgICAgIDwvbGk+CiAg\nICAgPC9vbD4KICAgIDwvbGk+CiAgIDwvb2w+CiAgPC9kaXY+CiA8L2Rpdj4KPC9zZWN0aW9uPgo8\naDIgaWQ9InctdmVyc2lvbi0xLTAiPgogVmVyc2lvbiAxLjAKPC9oMj4KPGg0IGlkPSJ3LXJlbGVh\nc2UiPgogKyBSZWxlYXNlCjwvaDQ+CjwvZGl2Pg==\n", "game_versions": [ "CB 1.4.5-R0.2" ], "filename": "ClearTheChat_-_Version_1.0__GER_.jar", "hard_dependencies": [ ], "date": 1355009738, "version": "1.0", "link": "http://dev.bukkit.org/bukkit-plugins/clearthechat/files/2-clear-the-chat-version-1-0-deutsche-version/", "file_id": 655365, "md5": "4bbe4c806f5ffc9547d2db95f76175f6", "download": "http://dev.bukkit.org/media/files/655/365/ClearTheChat_-_Version_1.0__GER_.jar", "dbo_version": "1.0", "type": "Release", "slug": "2-clear-the-chat-version-1-0-deutsche-version", "soft_dependencies": [ ], "permissions": [ ] }, { "status": "Semi-normal", "commands": [ { "usage": "/<command>", "permission": "", "command": "clearchat", "permission-message": "", "aliases": [ ] } ], "changelog": "PGRpdiBjbGFzcz0iY29udGVudC1ib3gtaW5uZXIiPgo8aDM+CiBDaGFuZ2UgbG9nCjwvaDM+Cjxz\nZWN0aW9uIGNsYXNzPSJ0b2MgZXhwYW5kaW5nLW1vZHVsZSIgZGF0YS1leHBhbmQtYnk9InRvYyIg\nZGF0YS1leHBhbmQtZGVmYXVsdD0ib3BlbiI+CiA8ZGl2IGNsYXNzPSJjb250ZW50LWJveCI+CiAg\nPGRpdiBjbGFzcz0iY29udGVudC1ib3gtaW5uZXIiPgogICA8aDM+CiAgICBUYWJsZSBvZiBjb250\nZW50cwogICA8L2gzPgogICA8b2wgY2xhc3M9InRvYy1sZXZlbCB0b2MtbGV2ZWwtMSI+CiAgICA8\nbGk+CiAgICAgPGEgaHJlZj0iI3ctdmVyc2lvbi0xLTAiPgogICAgICA8c3BhbiBjbGFzcz0idG9j\nLW51bWJlciI+CiAgICAgICAxCiAgICAgIDwvc3Bhbj4KICAgICAgPHNwYW4gY2xhc3M9InRvYy10\nZXh0Ij4KICAgICAgIFZlcnNpb24gMS4wCiAgICAgIDwvc3Bhbj4KICAgICA8L2E+CiAgICAgPG9s\nIGNsYXNzPSJ0b2MtbGV2ZWwgdG9jLWxldmVsLTIiPgogICAgICA8bGk+CiAgICAgICA8YSBocmVm\nPSIjdy1yZWxlYXNlIj4KICAgICAgICA8c3BhbiBjbGFzcz0idG9jLW51bWJlciI+CiAgICAgICAg\nIDEuMQogICAgICAgIDwvc3Bhbj4KICAgICAgICA8c3BhbiBjbGFzcz0idG9jLXRleHQiPgogICAg\nICAgICArIFJlbGVhc2UKICAgICAgICA8L3NwYW4+CiAgICAgICA8L2E+CiAgICAgIDwvbGk+CiAg\nICAgPC9vbD4KICAgIDwvbGk+CiAgIDwvb2w+CiAgPC9kaXY+CiA8L2Rpdj4KPC9zZWN0aW9uPgo8\naDIgaWQ9InctdmVyc2lvbi0xLTAiPgogVmVyc2lvbiAxLjAKPC9oMj4KPGg0IGlkPSJ3LXJlbGVh\nc2UiPgogKyBSZWxlYXNlCjwvaDQ+CjwvZGl2Pg==\n", "game_versions": [ "CB 1.4.5-R0.2" ], "filename": "ClearTheChat_-_Version_1.0__ENG_.jar", "hard_dependencies": [ ], "date": 1355009707, "version": "1.0", "link": "http://dev.bukkit.org/bukkit-plugins/clearthechat/files/1-clear-the-chat-version-1-0-english-version/", "file_id": 655364, "md5": "018cb6d144fa1e2cb98600b3ad75ed0d", "download": "http://dev.bukkit.org/media/files/655/364/ClearTheChat_-_Version_1.0__ENG_.jar", "dbo_version": "1.0", "type": "Release", "slug": "1-clear-the-chat-version-1-0-english-version", "soft_dependencies": [ ], "permissions": [ ] } ], "popularity": { "monthly": 0, "daily": 0, "weekly": 0 }, "plugin_name": "ClearTheChat", "server": "bukkit", "curse_link": "http://www.curse.com/bukkit-plugins/minecraft/clearthechat", "logo_full": "http://dev.bukkit.org/media/images/48/819/Paper.png", "authors": [ "iAlexak" ], "logo": "http://dev.bukkit.org/thumbman/images/48/819/100x100/Paper.png.-m1.png", "slug": "clearthechat", "categories": [ "Chat Related", "Admin Tools" ], "stage": "Alpha" }
var webstat = { "bukkitdev": 1409, "unique": 8731, "api1": 40189, "api2": 139654, "api3": 24332, "timestamp": Math.round(new Date().getTime() / 1000), "total": 384421, "plugins": { "monsterflight": { "total": 1, "unique": 1 }, "dynmap": { "total": 1, "unique": 1 } } }
var webstat_no_plugins = { "bukkitdev": webstat.bukkitdev, "unique": webstat.unique, "api1": webstat.api1, "api2": webstat.api2, "api3": webstat.api3, "timestamp": webstat.timestamp, "total": webstat.total }
var webstat_specific_plugin = { "timestamp": webstat.timestamp, "plugins": { "dynmap" : webstat.plugins["dynmap"] } }
var webstat_multiple_plugins = { "timestamp": webstat.timestamp, "plugins": webstat.plugins }

describe('Stats', function() {
  var naughty_plugin;
  var webstat_test;
  before(function (done) {
    db.plugins.insert(plugin, {safe: true}, function (err, records) {
      db.webstats.insert(webstat, {safe: true}, function (err, records) {
        naughty_plugin = [{
          'plugin_name': plugin.plugin_name,
          'authors': plugin.authors,
          'slug': plugin.slug
        }]
        delete webstat["_id"];
        done();
      });
    });
  })
  it('returns proper naughty list', function (done) {
    request(instance)
      .get('/stats/naughty_list')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify(naughty_plugin));
        done();
      });
  })
  it('returns todays_trends', function (done) {
    request(instance)
      .get('/stats/todays_trends')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify({"plugin_count": 1, "version_count": plugin.versions.length}));
        done();
      });
  })
  it('returns webstats within date range', function (done) {
    request(instance)
      .get('/stats/trend/1')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([webstat_no_plugins]));
        done();
      });
  })
  it('returns webstats within date range with all plugins', function (done) {
    request(instance)
      .get('/stats/trend/1?plugins=all')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([webstat]));
        done();
      });
  })
  it('returns webstats within date range with specific plugin', function (done) {
    request(instance)
      .get('/stats/trend/1?plugins=dynmap')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([webstat_specific_plugin]));
        done();
      });
  })
  it('returns webstats within date range with multiple plugins', function (done) {
    request(instance)
      .get('/stats/trend/1?plugins=monsterflight,dynmap')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([webstat_multiple_plugins]));
        done();
      });
  })
  after(function (done) {
    db.plugins.remove({}, function callback (err, res) { 
       db.webstats.remove({}, function callback (err, res) { done(); })
    });
  })
})

describe('Geninfo', function() {
  var test_data = [{"timestamp":1391688444,"parser":"bukkit","changes":[{"version":"2.4.8","plugin":"notebook"},{"version":"0.3","plugin":"playerbar"},{"version":"0.4","plugin":"pvpessentials"},{"version":"0.0.4","plugin":"saveonempty"},{"version":"1.1.6","plugin":"contrabanner"},{"version":"3.8.2","plugin":"craftbook"},{"version":"1.2","plugin":"exp-2-money"},{"version":"1.1","plugin":"monitorfishing"},{"version":"1.0","plugin":"googlesave"}],"duration":441,"type":"speedy","_id": ObjectID("52f37afcaab9e60332667aa2") }]; 
  before(function (done) {
    db.geninfo.insert(test_data, {safe: true}, function (err, records) {
      test_data[0]["id"] = test_data[0]["_id"];
      delete test_data[0]["_id"];
      done();
    });
  })
  it('returns list of geninfo', function (done) {
    request(instance)
      .get('/3/geninfo')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify(test_data));
        done();
      });
  })
  it('returns specific geninfo', function (done) {
    request(instance)
      .get('/3/geninfo/' + test_data[0].id.toString())
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify(test_data[0]));
        done();
      });
  })
  after(function (done) {
    db.geninfo.remove({}, function callback(err, res) { done(); });
  })
})