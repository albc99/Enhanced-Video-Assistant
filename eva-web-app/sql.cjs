const sql = require('mssql');

const config = {
    user: 'tsm-admin',
    password: 'EVAisAwesome!',
    server: 'evaserverstudent.database.windows.net',
    port: 1433,
    database: 'evaserverstudent',
    authentication: {
        type: 'default'
    },
    options: {
        encrypt: true, // on azure
        trustServerCertificate: false // change to true for local dev / self-signed certs
    }
};

async function connectAndQuery() {
    try {
        await sql.connect(config);

        const result = await sql.query('SELECT * FROM dbo.Users');

        console.log("Query Results:");
        result.recordset.forEach(row => {
            console.log(row);
        });

        await sql.close();
    } catch (err) {
        console.error('SQL error', err);
    }
}

connectAndQuery();
