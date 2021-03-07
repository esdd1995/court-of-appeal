var expect = require('chai').expect;
var Server = require('../../app/server/server');
var Database = require('../../app/store/database');
var Migrator = require('../../app/migrations/migrator');
var Truncator = require('../support/truncator');
var { execute } = require('../../app/libs/yop.postgresql');
var { request, localhost5000json } = require('../support/request');

describe('Form 2 update', function() {

    var server;
    var database;
    var update = localhost5000json({
        method: 'PUT',
        path: '/api/forms/1',
        body: { data: { field:'new value' } }
    });

    beforeEach(function(done) {
        server = new Server();
        database = new Database();
        server.useDatabase(database);
        var migrator = new Migrator();
        migrator.migrateNow(function() {
            var truncator = new Truncator();
            truncator.truncateTablesNow(function() {
                server.start(5000, 'localhost', done);
            });
        });
    });

    afterEach(function(done) {
        server.stop(done);
    });

    it('is a rest service', function(done) {
        var background = [
            'alter sequence person_id_seq restart',
            'alter sequence forms_id_seq restart',
            { sql: 'insert into person(login) values ($1)', params:['max'] },
            { sql: 'insert into forms(person_id, type, status, data) values($1, $2, $3, $4);', params:[1, 'crazy-max', 'new', JSON.stringify({field:'old value'})] },
        ];
        execute(background, (error, rows)=> {
            request(update, (err, response, body)=> {
                expect(response.statusCode).to.equal(200);
                expect(body).to.deep.equal(JSON.stringify({}));
                expect(response.headers.location).to.equal('/forms/1');

                let sql = `
                   SELECT data
                   FROM forms
                   WHERE forms.id=$1
                `;
                execute(sql, [1], function(err, rows) {
                    expect(rows.length).to.equal(1);

                    let { data } = rows[0];
                    expect(data).to.equal(JSON.stringify({ field:'new value' }));
                    done();
                });
            })
        });
    });

    it('it updates the modified time', function(done) {
        let yesterday = new Date();
        yesterday.setDate(yesterday.getDate()-1);
        let background = [
            'alter sequence person_id_seq restart',
            'alter sequence forms_id_seq restart',
            {sql: 'insert into person(login) values ($1)', params: ['max']},
            {
                sql: 'insert into forms(person_id, type, status, data, modified) values($1, $2, $3, $4, $5);',
                params: [1, 'crazy-max', 'new', JSON.stringify({field: 'old value'}), yesterday]
            },
        ];
        execute(background, (error, rows) => {
            request(update, (err, response, body)=> {
                expect(response.statusCode).to.equal(200);

                let sql = `
                    SELECT data, modified
                    FROM forms
                    WHERE forms.id=$1
                `;
                execute(sql, [1], function (err, rows) {
                    expect(rows.length).to.equal(1);
                    let {data, modified} = rows[0];
                    let timeUpdated = new Date(modified);

                    expect(timeUpdated).not.to.equal(yesterday);
                    done();
                });
            })
        });
    });
});
