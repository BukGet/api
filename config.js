module.exports = exports = {
  port: 9130, // Port that the webserver will run on
  address: '127.0.0.1', // Host that the webserver will bind to

  database: {
    host: 'mongodb://127.0.0.1/', // MongoDB host
    name: 'bukget', // MongoDB database name
    test_name: 'bukget_test' // MongoDB database name used for tests
  }
}