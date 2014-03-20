var should = require('should'); 
var request = require('supertest');  
var mongode = require('mongode');
var config = require('../config');

var instance;
var db = mongode.connect(config.database.host + config.database.name);
db.collection('plugins');
db.collection('webstats');
db.collection('geninfo');
db.collection('authors');
db.collection('categories');
require('../server')(function(callback){ instance = callback; }); 
describe('Get geninfo', function(){
  var test_data = [{"timestamp":1391688444,"parser":"bukkit","changes":[{"version":"2.4.8","plugin":"notebook"},{"version":"0.3","plugin":"playerbar"},{"version":"0.4","plugin":"pvpessentials"},{"version":"0.0.4","plugin":"saveonempty"},{"version":"1.1.6","plugin":"contrabanner"},{"version":"3.8.2","plugin":"craftbook"},{"version":"1.2","plugin":"exp-2-money"},{"version":"1.1","plugin":"monitorfishing"},{"version":"1.0","plugin":"googlesave"}],"duration":441,"type":"speedy","_id":"52f37afcaab9e60332667aa2"}]; 
  before(function(done) {
    db.geninfo.insert(test_data, {safe: true}, function(err, records){
      delete test_data[0]["_id"];
      test_data[0]["id"] = "52f37afcaab9e60332667aa2";
      done();
    });
  })
  it('return proper test data', function(done){
    request(instance)
      .get('/3')
      .set('Accept', 'application/json')
      .expect('Content-Type', /json/)
      .end(function(err,res) {
        if (err) {
          throw err;
        }
        JSON.stringify(res.res.body).should.equal(JSON.stringify(test_data));
        res.res.statusCode.should.equal(200);
        done();
      });
  })
})