var should = require('should'); 
var request = require('supertest');  
var config = require('../config');

var instance;
var db = require('monk')(config.database.host + config.database.test_name);
var plugins = db.get('plugins');
var webstats = db.get('webstats');
var geninfo = db.get('geninfo');
var authors = db.get('authors');
var categories = db.get('categories');
//Cleanup when testing locally to make sure it's not DB related
plugins.remove({}, function callback (err, res) {});
webstats.remove({}, function callback (err, res) {});
geninfo.remove({}, function callback (err, res) {});
authors.remove({}, function callback (err, res) {});
categories.remove({}, function callback (err, res) {});

authors.id = function (str) { return str; };
categories.id = function (str) { return str; };

require('../server')(config.database.host + config.database.test_name, function (callback) { instance = callback; }); 

var webstat = { 'bukkitdev': 1409, 'unique': 8731, 'api1': 40189, 'api2': 139654, 'api3': 24332, 'timestamp': Math.round(new Date().getTime() / 1000), 'total': 384421, 'plugins': { 'monsterflight': { 'total': 1, 'unique': 1 }, 'dynmap': { 'total': 1, 'unique': 1 } } }
var webstat_no_plugins = { 'bukkitdev': webstat.bukkitdev, 'unique': webstat.unique, 'api1': webstat.api1, 'api2': webstat.api2, 'api3': webstat.api3, 'timestamp': webstat.timestamp, 'total': webstat.total }
var webstat_specific_plugin = { 'timestamp': webstat.timestamp, 'plugins': { 'dynmap' : webstat.plugins['dynmap'] } }
var webstat_multiple_plugins = { 'timestamp': webstat.timestamp, 'plugins': webstat.plugins }

var plugin = { 'website': 'http://dev.bukkit.org/bukkit-plugins/clearthechat', 'dbo_page': 'http://dev.bukkit.org/bukkit-plugins/clearthechat', 'main': 'com.iAlexak.ClearTheChat.ClearTheChat', 'description': '', 'curse_id': 48244, 'versions': [ { 'status': 'Semi-normal', 'commands': [ { 'usage': '/<command>', 'permission': '', 'command': 'clearchat', 'permission-message': '', 'aliases': [ ] } ], 'changelog': 'PGRpdiBjbGFzcz0iY29udGVudC1ib3gtaW5uZXIiPgo8aDM+CiBDaGFuZ2UgbG9nCjwvaDM+Cjxz\nZWN0aW9uIGNsYXNzPSJ0b2MgZXhwYW5kaW5nLW1vZHVsZSIgZGF0YS1leHBhbmQtYnk9InRvYyIg\nZGF0YS1leHBhbmQtZGVmYXVsdD0ib3BlbiI+CiA8ZGl2IGNsYXNzPSJjb250ZW50LWJveCI+CiAg\nPGRpdiBjbGFzcz0iY29udGVudC1ib3gtaW5uZXIiPgogICA8aDM+CiAgICBUYWJsZSBvZiBjb250\nZW50cwogICA8L2gzPgogICA8b2wgY2xhc3M9InRvYy1sZXZlbCB0b2MtbGV2ZWwtMSI+CiAgICA8\nbGk+CiAgICAgPGEgaHJlZj0iI3ctdmVyc2lvbi0xLTAiPgogICAgICA8c3BhbiBjbGFzcz0idG9j\nLW51bWJlciI+CiAgICAgICAxCiAgICAgIDwvc3Bhbj4KICAgICAgPHNwYW4gY2xhc3M9InRvYy10\nZXh0Ij4KICAgICAgIFZlcnNpb24gMS4wCiAgICAgIDwvc3Bhbj4KICAgICA8L2E+CiAgICAgPG9s\nIGNsYXNzPSJ0b2MtbGV2ZWwgdG9jLWxldmVsLTIiPgogICAgICA8bGk+CiAgICAgICA8YSBocmVm\nPSIjdy1yZWxlYXNlIj4KICAgICAgICA8c3BhbiBjbGFzcz0idG9jLW51bWJlciI+CiAgICAgICAg\nIDEuMQogICAgICAgIDwvc3Bhbj4KICAgICAgICA8c3BhbiBjbGFzcz0idG9jLXRleHQiPgogICAg\nICAgICArIFJlbGVhc2UKICAgICAgICA8L3NwYW4+CiAgICAgICA8L2E+CiAgICAgIDwvbGk+CiAg\nICAgPC9vbD4KICAgIDwvbGk+CiAgIDwvb2w+CiAgPC9kaXY+CiA8L2Rpdj4KPC9zZWN0aW9uPgo8\naDIgaWQ9InctdmVyc2lvbi0xLTAiPgogVmVyc2lvbiAxLjAKPC9oMj4KPGg0IGlkPSJ3LXJlbGVh\nc2UiPgogKyBSZWxlYXNlCjwvaDQ+CjwvZGl2Pg==\n', 'game_versions': [ 'CB 1.4.5-R0.2' ], 'filename': 'ClearTheChat_-_Version_1.0__GER_.jar', 'hard_dependencies': [ ], 'date': 1355009738, 'version': '1.0', 'link': 'http://dev.bukkit.org/bukkit-plugins/clearthechat/files/2-clear-the-chat-version-1-0-deutsche-version/', 'file_id': 655365, 'md5': '4bbe4c806f5ffc9547d2db95f76175f6', 'download': 'http://dev.bukkit.org/media/files/655/365/ClearTheChat_-_Version_1.0__GER_.jar', 'dbo_version': '1.0', 'type': 'Release', 'slug': '2-clear-the-chat-version-1-0-deutsche-version', 'soft_dependencies': [ ], 'permissions': [ ] }, { 'status': 'Semi-normal', 'commands': [ { 'usage': '/<command>', 'permission': '', 'command': 'clearchat', 'permission-message': '', 'aliases': [ ] } ], 'changelog': 'PGRpdiBjbGFzcz0iY29udGVudC1ib3gtaW5uZXIiPgo8aDM+CiBDaGFuZ2UgbG9nCjwvaDM+Cjxz\nZWN0aW9uIGNsYXNzPSJ0b2MgZXhwYW5kaW5nLW1vZHVsZSIgZGF0YS1leHBhbmQtYnk9InRvYyIg\nZGF0YS1leHBhbmQtZGVmYXVsdD0ib3BlbiI+CiA8ZGl2IGNsYXNzPSJjb250ZW50LWJveCI+CiAg\nPGRpdiBjbGFzcz0iY29udGVudC1ib3gtaW5uZXIiPgogICA8aDM+CiAgICBUYWJsZSBvZiBjb250\nZW50cwogICA8L2gzPgogICA8b2wgY2xhc3M9InRvYy1sZXZlbCB0b2MtbGV2ZWwtMSI+CiAgICA8\nbGk+CiAgICAgPGEgaHJlZj0iI3ctdmVyc2lvbi0xLTAiPgogICAgICA8c3BhbiBjbGFzcz0idG9j\nLW51bWJlciI+CiAgICAgICAxCiAgICAgIDwvc3Bhbj4KICAgICAgPHNwYW4gY2xhc3M9InRvYy10\nZXh0Ij4KICAgICAgIFZlcnNpb24gMS4wCiAgICAgIDwvc3Bhbj4KICAgICA8L2E+CiAgICAgPG9s\nIGNsYXNzPSJ0b2MtbGV2ZWwgdG9jLWxldmVsLTIiPgogICAgICA8bGk+CiAgICAgICA8YSBocmVm\nPSIjdy1yZWxlYXNlIj4KICAgICAgICA8c3BhbiBjbGFzcz0idG9jLW51bWJlciI+CiAgICAgICAg\nIDEuMQogICAgICAgIDwvc3Bhbj4KICAgICAgICA8c3BhbiBjbGFzcz0idG9jLXRleHQiPgogICAg\nICAgICArIFJlbGVhc2UKICAgICAgICA8L3NwYW4+CiAgICAgICA8L2E+CiAgICAgIDwvbGk+CiAg\nICAgPC9vbD4KICAgIDwvbGk+CiAgIDwvb2w+CiAgPC9kaXY+CiA8L2Rpdj4KPC9zZWN0aW9uPgo8\naDIgaWQ9InctdmVyc2lvbi0xLTAiPgogVmVyc2lvbiAxLjAKPC9oMj4KPGg0IGlkPSJ3LXJlbGVh\nc2UiPgogKyBSZWxlYXNlCjwvaDQ+CjwvZGl2Pg==\n', 'game_versions': [ 'CB 1.4.5-R0.2' ], 'filename': 'ClearTheChat_-_Version_1.0__ENG_.jar', 'hard_dependencies': [ ], 'date': 1355009707, 'version': '1.0', 'link': 'http://dev.bukkit.org/bukkit-plugins/clearthechat/files/1-clear-the-chat-version-1-0-english-version/', 'file_id': 655364, 'md5': '018cb6d144fa1e2cb98600b3ad75ed0d', 'download': 'http://dev.bukkit.org/media/files/655/364/ClearTheChat_-_Version_1.0__ENG_.jar', 'dbo_version': '1.0', 'type': 'Release', 'slug': '1-clear-the-chat-version-1-0-english-version', 'soft_dependencies': [ ], 'permissions': [ ] } ], 'popularity': { 'monthly': 0, 'daily': 0, 'weekly': 0 }, 'plugin_name': 'ClearTheChat', 'server': 'bukkit', 'curse_link': 'http://www.curse.com/bukkit-plugins/minecraft/clearthechat', 'logo_full': 'http://dev.bukkit.org/media/images/48/819/Paper.png', 'authors': [ 'iAlexak' ], 'logo': 'http://dev.bukkit.org/thumbman/images/48/819/100x100/Paper.png.-m1.png', 'slug': 'clearthechat', 'categories': [ 'Chat Related', 'Admin Tools' ], 'stage': 'Release' }
var plugin_two = { 'website': 'http://dev.bukkit.org/bukkit-plugins/abitofrealism', 'dbo_page': 'http://dev.bukkit.org/bukkit-plugins/abitofrealism', 'main': 'com.mcheaven.abitofrealism.AbOR_Main', 'description': '', 'curse_id': 40285, 'versions': [ { 'status': 'Semi-normal', 'commands': [], 'changelog': 'PGRpdiBjbGFzcz0iY29udGVudC1ib3gtaW5uZXIiPgo8aDM+CiBDaGFuZ2UgbG9nCjwvaDM+Cjxw\nPgogPHN0cm9uZz4KICAwLjMuMQogPC9zdHJvbmc+CjwvcD4KPHVsPgogPGxpPgogIFJlbW92ZWQg\nRGVidWctTWVzc2FnZQogPC9saT4KPC91bD4KPHA+CiA8c3Ryb25nPgogIDAuMwogPC9zdHJvbmc+\nCjwvcD4KPHVsPgogPGxpPgogIEtlZXAgZWF0aW5nIFN1Z2FyIGFuZCBnZXQgZmFzdGVyISAoaXRz\nIGFkZGluZyB0aGUgdGltZSB5b3Ugc3RheSBmYXN0IHRvbykKIDwvbGk+CjwvdWw+CjxwPgogPHN0\ncm9uZz4KICAwLjIKIDwvc3Ryb25nPgo8L3A+Cjx1bD4KIDxsaT4KICBIZWFkc2hvdCBGZWF0dXJl\nIChBcnJvd3MpIGlmIGEgcGxheWVycyBzaG9vdHMgYW5vdGhlciBwbGF5ZXIgaW4gdGhlIGhlYWQs\nIHNlcnZlciBzYXlzIEhFQURTSE9UISBhbmQgaXQgZG9lcyBkb3VibGUgZGFtYWdlCiAgPHNwYW4g\nY2xhc3M9ImVtb3RlIGVtb3RlLXNtaWxlIiB0aXRsZT0iU21pbGUiPgogICA6KQogIDwvc3Bhbj4K\nICBQbGVhc2UgdGVzdCBpdCBvdXQgb2YgY291cnNlIEknbGwgY2hhbmdlIGRhbWFnZSBhbmQgbWVz\nc2FnZSBsYXRlci4uCiA8L2xpPgo8L3VsPgo8cD4KIDxzdHJvbmc+CiAgMC4xCiA8L3N0cm9uZz4K\nPC9wPgo8dWw+CiA8bGk+CiAgRmFsbCBEYW1hZ2UgJmd0OyBTbG93bmVzcwogIDxlbT4KICAgVGVz\ndCBpdCBvdXQhCiAgPC9lbT4KIDwvbGk+CiA8bGk+CiAgRWF0IFN1Z2FyICZndDsgU3BlZWQKICA8\nZW0+CiAgIFRlc3QgaXQgb3V0IQogIDwvZW0+CiA8L2xpPgo8L3VsPgo8L2Rpdj4=\n', 'game_versions': [ '1.2.5' ], 'filename': 'AbitOfRealism.jar', 'hard_dependencies': [], 'date': 1340493789, 'version': '0.3.1', 'link': 'http://dev.bukkit.org/bukkit-plugins/abitofrealism/files/4-abit-of-realism-0-3-1/', 'file_id': 599604, 'md5': '236c18df1d15e149fe91675c08efa8b5', 'download': 'http://dev.bukkit.org/media/files/599/604/AbitOfRealism.jar', 'dbo_version': '0.3.1', 'type': 'None', 'slug': '4-abit-of-realism-0-3-1', 'soft_dependencies': [], 'permissions': [] }, { 'status': 'Semi-normal', 'commands': [], 'changelog': 'PGRpdiBjbGFzcz0iY29udGVudC1ib3gtaW5uZXIiPgo8aDM+CiBDaGFuZ2UgbG9nCjwvaDM+Cjxw\nPgogPHN0cm9uZz4KICAwLjMKIDwvc3Ryb25nPgo8L3A+Cjx1bD4KIDxsaT4KICBLZWVwIGVhdGlu\nZyBTdWdhciBhbmQgZ2V0IGZhc3RlciEgKGl0cyBhZGRpbmcgdGhlIHRpbWUgeW91IHN0YXkgZmFz\ndCB0b28pCiA8L2xpPgo8L3VsPgo8cD4KIDxzdHJvbmc+CiAgMC4yCiA8L3N0cm9uZz4KPC9wPgo8\ndWw+CiA8bGk+CiAgSGVhZHNob3QgRmVhdHVyZSAoQXJyb3dzKSBpZiBhIHBsYXllcnMgc2hvb3Rz\nIGFub3RoZXIgcGxheWVyIGluIHRoZSBoZWFkLCBzZXJ2ZXIgc2F5cyBIRUFEU0hPVCEgYW5kIGl0\nIGRvZXMgZG91YmxlIGRhbWFnZQogIDxzcGFuIGNsYXNzPSJlbW90ZSBlbW90ZS1zbWlsZSIgdGl0\nbGU9IlNtaWxlIj4KICAgOikKICA8L3NwYW4+CiAgUGxlYXNlIHRlc3QgaXQgb3V0IG9mIGNvdXJz\nZSBJJ2xsIGNoYW5nZSBkYW1hZ2UgYW5kIG1lc3NhZ2UgbGF0ZXIuLgogPC9saT4KPC91bD4KPHA+\nCiA8c3Ryb25nPgogIDAuMQogPC9zdHJvbmc+CjwvcD4KPHVsPgogPGxpPgogIEZhbGwgRGFtYWdl\nICZndDsgU2xvd25lc3MKICA8ZW0+CiAgIFRlc3QgaXQgb3V0IQogIDwvZW0+CiA8L2xpPgogPGxp\nPgogIEVhdCBTdWdhciAmZ3Q7IFNwZWVkCiAgPGVtPgogICBUZXN0IGl0IG91dCEKICA8L2VtPgog\nPC9saT4KPC91bD4KPC9kaXY+\n', 'game_versions': [ '1.2.5' ], 'filename': 'AbitOfRealism.jar', 'hard_dependencies': [], 'date': 1339605762, 'version': '0.3', 'link': 'http://dev.bukkit.org/bukkit-plugins/abitofrealism/files/3-abit-of-realism-0-3/', 'file_id': 597975, 'md5': '49ab15446ae1bfce8801433cd75f8fc9', 'download': 'http://dev.bukkit.org/media/files/597/975/AbitOfRealism.jar', 'dbo_version': '0.3', 'type': 'Alpha', 'slug': '3-abit-of-realism-0-3', 'soft_dependencies': [], 'permissions': [] }, { 'status': 'Semi-normal', 'commands': [], 'changelog': 'PGRpdiBjbGFzcz0iY29udGVudC1ib3gtaW5uZXIiPgo8aDM+CiBDaGFuZ2UgbG9nCjwvaDM+Cjxw\nPgogPHN0cm9uZz4KICAwLjIKIDwvc3Ryb25nPgo8L3A+Cjx1bD4KIDxsaT4KICBIZWFkc2hvdCBG\nZWF0dXJlIChBcnJvd3MpIGlmIGEgcGxheWVycyBzaG9vdHMgYW5vdGhlciBwbGF5ZXIgaW4gdGhl\nIGhlYWQsIHNlcnZlciBzYXlzIEhFQURTSE9UISBhbmQgaXQgZG9lcyBkb3VibGUgZGFtYWdlCiAg\nPHNwYW4gY2xhc3M9ImVtb3RlIGVtb3RlLXNtaWxlIiB0aXRsZT0iU21pbGUiPgogICA6KQogIDwv\nc3Bhbj4KICBQbGVhc2UgdGVzdCBpdCBvdXQgb2YgY291cnNlIEknbGwgY2hhbmdlIGRhbWFnZSBh\nbmQgbWVzc2FnZSBsYXRlci4uCiA8L2xpPgo8L3VsPgo8cD4KIDxzdHJvbmc+CiAgMC4xCiA8L3N0\ncm9uZz4KPC9wPgo8dWw+CiA8bGk+CiAgRmFsbCBEYW1hZ2UgJmd0OyBTbG93bmVzcwogIDxlbT4K\nICAgVGVzdCBpdCBvdXQhCiAgPC9lbT4KIDwvbGk+CiA8bGk+CiAgRWF0IFN1Z2FyICZndDsgU3Bl\nZWQKICA8ZW0+CiAgIFRlc3QgaXQgb3V0IQogIDwvZW0+CiA8L2xpPgo8L3VsPgo8L2Rpdj4=\n', 'game_versions': [ '1.2.5' ], 'filename': 'AbitOfRealism.jar', 'hard_dependencies': [], 'date': 1338732054, 'version': '0.2', 'link': 'http://dev.bukkit.org/bukkit-plugins/abitofrealism/files/2-abit-of-realism-0-2/', 'file_id': 596426, 'md5': '9ab16c40a6cbff566965a37f137c25bf', 'download': 'http://dev.bukkit.org/media/files/596/426/AbitOfRealism.jar', 'dbo_version': '0.2', 'type': 'Beta', 'slug': '2-abit-of-realism-0-2', 'soft_dependencies': [], 'permissions': [] }, { 'status': 'Semi-normal', 'commands': [], 'changelog': 'PGRpdiBjbGFzcz0iY29udGVudC1ib3gtaW5uZXIiPgo8aDM+CiBDaGFuZ2UgbG9nCjwvaDM+Cjxw\nPgogPHN0cm9uZz4KICAwLjEKIDwvc3Ryb25nPgo8L3A+Cjx1bD4KIDxsaT4KICBGYWxsIERhbWFn\nZSAmZ3Q7IFNsb3duZXNzCiAgPGVtPgogICBUZXN0IGl0IG91dCEKICA8L2VtPgogPC9saT4KIDxs\naT4KICBFYXQgU3VnYXIgJmd0OyBTcGVlZAogIDxlbT4KICAgVGVzdCBpdCBvdXQhCiAgPC9lbT4K\nIDwvbGk+CjwvdWw+CjwvZGl2Pg==\n', 'game_versions': [ '1.2.5' ], 'filename': 'AbitOfRealism.jar', 'hard_dependencies': [], 'date': 1338663342, 'version': '0.1', 'link': 'http://dev.bukkit.org/bukkit-plugins/abitofrealism/files/1-abit-of-realism-0-1/', 'file_id': 596293, 'md5': '2458133b2813b66e2c162ce7bbdf5c18', 'download': 'http://dev.bukkit.org/media/files/596/293/AbitOfRealism.jar', 'dbo_version': '0.1', 'type': 'Release', 'slug': '1-abit-of-realism-0-1', 'soft_dependencies': [], 'permissions': [] } ], 'popularity': { 'monthly': 19, 'daily': 33, 'weekly': 9 }, 'plugin_name': 'AbitOfRealism', 'server': 'bukkit', 'curse_link': 'http://www.curse.com/bukkit-plugins/minecraft/abitofrealism', 'logo_full': '', 'authors': [ 'mcheaven' ], '_use_dbo': true, 'logo': '', 'slug': 'abitofrealism', 'categories': [ 'Fixes', 'Fun', 'General' ], 'stage': 'Release' }
var plugin_version_latest = { 'website': plugin_two.website, 'dbo_page': plugin_two.dbo_page, 'main': plugin_two.main, 'description': plugin_two.description, 'curse_id': plugin_two.curse_id, 'versions': [ plugin_two.versions[0] ], 'popularity': plugin_two.popularity, 'plugin_name': plugin_two.plugin_name, 'server': plugin_two.server, 'curse_link': plugin_two.curse_link, 'logo_full': plugin_two.logo_full, 'authors': plugin_two.authors, '_use_dbo': plugin_two._use_dbo, 'logo': plugin_two.logo, 'slug': plugin_two.slug, 'categories': plugin_two.categories, 'stage': plugin_two.stage }
var plugin_version_alpha = { 'website': plugin_two.website, 'dbo_page': plugin_two.dbo_page, 'main': plugin_two.main, 'description': plugin_two.description, 'curse_id': plugin_two.curse_id, 'versions': [ plugin_two.versions[1] ], 'popularity': plugin_two.popularity, 'plugin_name': plugin_two.plugin_name, 'server': plugin_two.server, 'curse_link': plugin_two.curse_link, 'logo_full': plugin_two.logo_full, 'authors': plugin_two.authors, '_use_dbo': plugin_two._use_dbo, 'logo': plugin_two.logo, 'slug': plugin_two.slug, 'categories': plugin_two.categories, 'stage': plugin_two.stage }
var plugin_version_beta = { 'website': plugin_two.website, 'dbo_page': plugin_two.dbo_page, 'main': plugin_two.main, 'description': plugin_two.description, 'curse_id': plugin_two.curse_id, 'versions': [ plugin_two.versions[2] ], 'popularity': plugin_two.popularity, 'plugin_name': plugin_two.plugin_name, 'server': plugin_two.server, 'curse_link': plugin_two.curse_link, 'logo_full': plugin_two.logo_full, 'authors': plugin_two.authors, '_use_dbo': plugin_two._use_dbo, 'logo': plugin_two.logo, 'slug': plugin_two.slug, 'categories': plugin_two.categories, 'stage': plugin_two.stage }
var plugin_version_release = { 'website': plugin_two.website, 'dbo_page': plugin_two.dbo_page, 'main': plugin_two.main, 'description': plugin_two.description, 'curse_id': plugin_two.curse_id, 'versions': [ plugin_two.versions[3] ], 'popularity': plugin_two.popularity, 'plugin_name': plugin_two.plugin_name, 'server': plugin_two.server, 'curse_link': plugin_two.curse_link, 'logo_full': plugin_two.logo_full, 'authors': plugin_two.authors, '_use_dbo': plugin_two._use_dbo, 'logo': plugin_two.logo, 'slug': plugin_two.slug, 'categories': plugin_two.categories, 'stage': plugin_two.stage }

var update_versions = { 'current': { 'version': plugin_two.versions[1]['version'], 'download': plugin_two.versions[1]['download'],'md5': plugin_two.versions[1]['md5'] }, 'latest': { 'version': plugin_two.versions[0]['version'], 'download': plugin_two.versions[0]['download'], 'md5': plugin_two.versions[0]['md5'] }};

var author = { '_id': 'iAlexak', 'value': 5 }
var category = { '_id': 'General', 'value': 1645 }

describe('Stats', function() {
  var naughty_plugin;
  var webstat_test;
  before(function (done) {
    plugins.insert(plugin_two, {safe: true}, function (err, records) {
      webstats.insert(webstat, {safe: true}, function (err, records) {
        naughty_plugin = [{
          'plugin_name': plugin_two.plugin_name,
          'authors': plugin_two.authors,
          'slug': plugin_two.slug
        }]
        delete webstat['_id'];
        done();
      });
    });
  });
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
  });
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
        JSON.stringify(res.res.body).should.equal(JSON.stringify({'plugin_count': 1, 'version_count': plugin_two.versions.length}));
        done();
      });
  });
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
  });
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
  });
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
  });
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
  });
  after(function (done) {
    plugins.remove({}, function callback (err, res) { 
       webstats.remove({}, function callback (err, res) { done(); });
    });
  });
});

describe('Misc', function() {
  var plugin_list;
  before(function (done) {
    plugins.insert(plugin, {safe: true}, function (err, records) {
      plugins.insert(plugin_two, {safe: true}, function (err, records) {
        plugin_list = [{
          'description': plugin_two.description,
          'plugin_name': plugin_two.plugin_name,
          'slug': plugin_two.slug
        },{
          'description': plugin.description,
          'plugin_name': plugin.plugin_name,
          'slug': plugin.slug
        }]
        done();
      });
    });
  });
  it('handle_parameters works properly', function (done) {
    request(instance)
      .get('/3/plugins/bukkit?size=1&start=1&sort=-slug&fields=slug,plugin_name')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'plugin_name': plugin_list[0].plugin_name, 'slug': plugin_list[0].slug }]));
        done();
      });
  });
  after(function (done) {
    plugins.remove({}, function callback(err, res) { done(); });
  });
});

describe('Geninfo', function() {
  var test_data = [{'timestamp':1391688444,'parser':'bukkit','changes':[{'version':'2.4.8','plugin':'notebook'},{'version':'0.3','plugin':'playerbar'},{'version':'0.4','plugin':'pvpessentials'},{'version':'0.0.4','plugin':'saveonempty'},{'version':'1.1.6','plugin':'contrabanner'},{'version':'3.8.2','plugin':'craftbook'},{'version':'1.2','plugin':'exp-2-money'},{'version':'1.1','plugin':'monitorfishing'},{'version':'1.0','plugin':'googlesave'}],'duration':441,'type':'speedy','_id': geninfo.id('52f37afcaab9e60332667aa2') }]; 
  before(function (done) {
    geninfo.insert(test_data, {safe: true}, function (err, records) {
      test_data[0]['id'] = test_data[0]['_id'];
      delete test_data[0]['_id'];
      done();
    });
  });
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
  });
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
  });
  after(function (done) {
    geninfo.remove({}, function callback(err, res) { done(); });
  });
});

describe('Plugins', function() {
  var plugin_list;
  before(function (done) {
    plugins.insert(plugin, {safe: true}, function (err, records) {
      delete plugin['_id'];
      plugins.insert(plugin_two, {safe: true}, function (err, records) {
        delete plugin_two['_id'];
        plugin_list = [{
          'description': plugin_two.description,
          'plugin_name': plugin_two.plugin_name,
          'slug': plugin_two.slug
        },{
          'description': plugin.description,
          'plugin_name': plugin.plugin_name,
          'slug': plugin.slug
        }]
        done();
      });
    });
  });
  it('returns list of plugins', function (done) {
    request(instance)
      .get('/3/plugins')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify(plugin_list));
        done();
      });
  });
  it('returns list of plugins with specific server', function (done) {
    request(instance)
      .get('/3/plugins/bukkit')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify(plugin_list));
        done();
      });
  });
  it('returns specific plugin', function (done) {
    request(instance)
      .get('/3/plugins/bukkit/abitofrealism')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify(plugin_two));
        done();
      });
  });
  it('returns specific version of specific plugin', function (done) {
    request(instance)
      .get('/3/plugins/bukkit/abitofrealism/0.3.1')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify(plugin_version_latest));
        done();
      });
  });
  it('returns latest version of specific plugin', function (done) {
    request(instance)
      .get('/3/plugins/bukkit/abitofrealism/latest')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify(plugin_version_latest));
        done();
      });
  });
  it('returns alpha version of specific plugin', function (done) {
    request(instance)
      .get('/3/plugins/bukkit/abitofrealism/alpha')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify(plugin_version_alpha));
        done();
      });
  });
  it('returns beta version of specific plugin', function (done) {
    request(instance)
      .get('/3/plugins/bukkit/abitofrealism/beta')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify(plugin_version_beta));
        done();
      });
  });
  it('returns release version of specific plugin', function (done) {
    request(instance)
      .get('/3/plugins/bukkit/abitofrealism/release')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify(plugin_version_release));
        done();
      });
  });
  it('redirects correctly for specific version download for specific plugin', function (done) {
    request(instance)
      .get('/3/plugins/bukkit/abitofrealism/0.3.1/download')
      .expect(302)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        res.header['location'].should.equal(plugin_two.versions[0].download);
        done();
      });
  });
  it('redirects correctly for latest version download for specific plugin', function (done) {
    request(instance)
      .get('/3/plugins/bukkit/abitofrealism/latest/download')
      .expect(302)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        res.header['location'].should.equal(plugin_two.versions[0].download);
        done();
      });
  });
  after(function (done) {
    plugins.remove({}, function callback(err, res) { done(); });
  });
});

describe('Authors', function() {
  before(function (done) {
    plugins.insert(plugin, {safe: true}, function (err, records) {
      authors.insert(author, {safe: true}, function (err, records) {
        done();
      });
    });
  });
  it('returns list of authors', function (done) {
    request(instance)
      .get('/3/authors')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'name': author._id, 'count': author.value }]));
        done();
      });
  });
  it('returns list of plugins made by author', function (done) {
    request(instance)
      .get('/3/authors/' + author._id)
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin.description, 'plugin_name': plugin.plugin_name, 'slug': plugin.slug }]));
        done();
      });
  });
  it('returns list of plugins made by author for specific server', function (done) {
    request(instance)
      .get('/3/authors/bukkit/' + author._id)
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin.description, 'plugin_name': plugin.plugin_name, 'slug': plugin.slug }]));
        done();
      });
  });
  after(function (done) {
    authors.remove({}, function callback(err, res) { 
      plugins.remove({}, function callback(err, res) { done(); });
    });
  });
});

describe('Categories', function() {
  before(function (done) {
    plugins.insert(plugin_two, {safe: true}, function (err, records) {
      categories.insert(category, {safe: true}, function (err, records) {
        done();
      });
    });
  });
  it('returns list of categories', function (done) {
    request(instance)
      .get('/3/categories')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'name': category._id, 'count': category.value }]));
        done();
      });
  });
  it('returns list of plugins in specific category', function (done) {
    request(instance)
      .get('/3/categories/' + category._id)
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  it('returns list of plugins in specific category for specific server', function (done) {
    request(instance)
      .get('/3/categories/bukkit/' + category._id)
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  after(function (done) {
    categories.remove({}, function callback(err, res) { 
      plugins.remove({}, function callback(err, res) { done(); });
    });
  });
});

describe('Updates', function() {
  before(function (done) {
    plugins.insert(plugin_two, {safe: true}, function (err, records) {
      var versions = plugin_two.versions;
      for (var x = 0, versionLen = versions.length; x < versionLen; x++) {
        var version = versions[x];

        if (version['type'] == 'Release' || version['type'] == 'Beta' || version['type'] == 'Alpha') {
          if (update_versions[version['type'].toLowerCase()] == null) {
            update_versions[version['type'].toLowerCase()] = { 'version': version['version'], 'download' : version['download'], 'md5': version['md5'] };
          }
        }
      }
      done();
    });
  });
  it('returns list of latest versions by md5', function (done) {
    request(instance)
      .get('/3/updates?hashes=49ab15446ae1bfce8801433cd75f8fc9')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        (res.res.body).should.eql([{ 'slug': plugin_two.slug, 'plugin_name': plugin_two.plugin_name, 'versions': update_versions, 'hash': plugin_two.versions[1]['md5'] }]);
        done();
      });
  });
  it('returns list of latest versions via get', function (done) {
    request(instance)
      .get('/3/updates?slugs=abitofrealism')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        if (update_versions.current) delete update_versions.current;
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'slug': plugin_two.slug, 'plugin_name': plugin_two.plugin_name, 'versions': update_versions }]));
        done();
      });
  });
  it('returns list of latest versions via post', function (done) {
    request(instance)
      .post('/3/updates?slugs=abitofrealism')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        if (update_versions.current) delete update_versions.current;
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'slug': plugin_two.slug, 'plugin_name': plugin_two.plugin_name, 'versions': update_versions }]));
        done();
      });
  });
  it('returns list of latest versions for specific server', function (done) {
    request(instance)
      .get('/3/updates?slugs=abitofrealism&server=bukkit')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        if (update_versions.current) delete update_versions.current;
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'slug': plugin_two.slug, 'plugin_name': plugin_two.plugin_name, 'versions': update_versions }]));
        done();
      });
  });
  it('returns list of latest versions by filename', function (done) {
    request(instance)
      .get('/3/updates?filenames=AbitOfRealism.jar')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        if (update_versions.current) delete update_versions.current;
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'slug': plugin_two.slug, 'plugin_name': plugin_two.plugin_name, 'versions': update_versions, 'file': plugin_two.versions[0].filename }]));
        done();
      });
  });
  it('returns extra fields correctly', function (done) {
    request(instance)
      .get('/3/updates?extra_fields=website&filenames=AbitOfRealism.jar')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        if (update_versions.current) delete update_versions.current;
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'slug': plugin_two.slug, 'plugin_name': plugin_two.plugin_name, 'versions': update_versions, 'website': plugin_two.website, 'file': plugin_two.versions[0].filename }]));
        done();
      });
  });
  it('returns extra version fields correctly', function (done) {
    request(instance)
      .get('/3/updates?extra_version_fields=status&filenames=AbitOfRealism.jar')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        if (update_versions.current) delete update_versions.current;
        for (i in update_versions) {
          update_versions[i]['status'] = plugin_two.versions[0]['status'];
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'slug': plugin_two.slug, 'plugin_name': plugin_two.plugin_name, 'versions': update_versions, 'file': plugin_two.versions[0].filename }]));
        done();
      });
  });
  after(function (done) {
    plugins.remove({}, function callback(err, res) { done(); });
  });
});

describe('Search', function() {
  before(function (done) {
    plugins.insert(plugin_two, {safe: true}, function (err, records) {
      plugins.insert(plugin, {safe: true}, function (err, records) {
        done();
      });
    });
  });
  it('basic get search', function (done) {
    request(instance)
      .get('/3/search/slug/equals/abitofrealism')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  it('basic post search', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'slug', 'action': 'equals', 'value': 'abitofrealism' }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  it('equals', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'slug', 'action': 'equals', 'value': 'abitofrealism' }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  it('does not equal', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'slug', 'action': 'not-equals', 'value': 'abitofrealism' }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin.description, 'plugin_name': plugin.plugin_name, 'slug': plugin.slug }]));
        done();
      });
  });
  it('less than', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'curse_id', 'action': 'less', 'value': 40286 }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  it('less than or equal to', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'curse_id', 'action': 'less-equal', 'value': 40285 }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  it('more than', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'curse_id', 'action': 'more', 'value': 40285 }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin.description, 'plugin_name': plugin.plugin_name, 'slug': plugin.slug }]));
        done();
      });
  });
  it('more than or equal to', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'curse_id', 'action': 'more-equal', 'value': 40285 }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }, { 'description': plugin.description, 'plugin_name': plugin.plugin_name, 'slug': plugin.slug }]));
        done();
      });
  });
  it('like', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'slug', 'action': 'like', 'value': 'abitof' }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  it('exists', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': '_use_dbo', 'action': 'exists', 'value': true }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  it('doesn\'t exist', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': '_use_dbo', 'action': 'exists', 'value': false }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin.description, 'plugin_name': plugin.plugin_name, 'slug': plugin.slug }]));
        done();
      });
  });
  it('in', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'slug', 'action': 'in', 'value': ['clearthechat'] }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin.description, 'plugin_name': plugin.plugin_name, 'slug': plugin.slug }]));
        done();
      });
  });
  it('not in', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'slug', 'action': 'not in', 'value': ['clearthechat'] }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  it('all', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'categories', 'action': 'all', 'value': [ 'Fixes', 'Fun', 'General' ] }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  it('and', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': '', 'action': 'and', 'value': [{ 'stage': 'Release'}, {'slug': 'abitofrealism' }] }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  it('or', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': '', 'action': 'or', 'value': [{ 'slug': 'abitofrealism' }, { 'slug': 'clearthechat'}] }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }, { 'description': plugin.description, 'plugin_name': plugin.plugin_name, 'slug': plugin.slug }]));
        done();
      });
  });
  it('likeor', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': '', 'action': 'likeor', 'value': [{ 'slug': 'freal' }, { 'main': 'exak.ClearTheChat.Cl'}] }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }, { 'description': plugin.description, 'plugin_name': plugin.plugin_name, 'slug': plugin.slug }]));
        done();
      });
  });
  it('nor', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': '', 'action': 'nor', 'value': [{ 'slug': 'clearthechat' }, { '_use_dbo': { '$exists': false } }] }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin_two.description, 'plugin_name': plugin_two.plugin_name, 'slug': plugin_two.slug }]));
        done();
      });
  });
  it('not', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'curse_id', 'action': 'not', 'value': { '$lt' : 48244 } }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin.description, 'plugin_name': plugin.plugin_name, 'slug': plugin.slug }]));
        done();
      });
  });
  it('multiple filters', function (done) {
    request(instance)
      .post('/3/search')
      .send({ 'filters': JSON.stringify([{'field': 'slug', 'action': 'equals', 'value': 'clearthechat' }, {'field': 'curse_id', 'action': 'equals', 'value': 48244 }]) })
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .expect(200)
      .end(function (err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify([{ 'description': plugin.description, 'plugin_name': plugin.plugin_name, 'slug': plugin.slug }]));
        done();
      });
  });
  after(function (done) {
    plugins.remove({}, function callback(err, res) { done(); });
  });
});
