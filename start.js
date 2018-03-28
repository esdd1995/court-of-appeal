var port = process.env.OPENSHIFT_NODEJS_PORT || 8080;
var ip = process.env.OPENSHIFT_NODEJS_IP || '0.0.0.0';
var home = 'http://' + ip + ':' + port;

var Database = require('./app/store/database');
var database = new Database();
var Migrator = require('./app/migrations/migrator');
var migrator = new Migrator();

var Server = require('./app/server/server');
var server = new Server();
server.useTokenValidator(require('./tests/support/token.always.valid.js'));
server.useService(require('./tests/support/in.memory.service.js'));
server.useDatabase(database);

console.log('migrating...');
migrator.migrateNow(function() {
    console.log('migrations done');
    server.start(port, ip, function() {
        console.log(ip + ' listening on port ' + port);
    });
});

module.exports = server;
module.exports.port = port;
module.exports.ip = ip;
