var express = require('express');
var router = express.Router();

const fs = require('fs');
const pg = require('pg');
const ms = require('mustache');
const a2 = require('argon2');


function readConf(path) {
  try {
    return fs.readFileSync(path, "utf8").trim();
  } catch {
    console.error(`FATAL: failed to read config: ${path}`);
    process.exit(1);
  }
}

const confDir = "/etc/config";
const htmlTemplate = readConf(`${confDir}/html/html_template`)
const dbConfig = {
  host: readConf(`${confDir}/db/host`),
  user: readConf(`${confDir}/db/user`),
  password: readConf(`${confDir}/db/password`),
  database: readConf(`${confDir}/db/name`),
  port: readConf(`${confDir}/db/port`)
};
const pool = new pg.Pool(dbConfig);
console.log(`Successfully connected to postgresql://${dbConfig.user}@${dbConfig.host}:${dbConfig.port}/${dbConfig.database}`)

router.all('/', async (req, res, next) => {
  const start = process.hrtime.bigint();
  try {
    const fields = {
      CURRENT_TIME: new Date().toISOString(),
      //TABLE_CONTENTS: "",      
      //FORM_USERNAME_VALUE: "",
      //REQUEST_RESULT: "",
      STATUS: "Express",
    }
    
    const result = await pool.query('SELECT * FROM users ORDER BY id;');
    fields.TABLE_CONTENTS = "";
    for (let item of result.rows) {
      fields.TABLE_CONTENTS += "<tr>" 
      
      for (const column of ["id", "username", "password", "raw_password"]) {
        fields.TABLE_CONTENTS += "<td>"
        fields.TABLE_CONTENTS += item[column] === null ? "NULL" : item[column];
        fields.TABLE_CONTENTS += "</td>"
      }
      fields.TABLE_CONTENTS += "</tr>" 
      // `<td>${item.id}</td>\n<td>${item.username}</td>\n\<td>${item.password}</td>\n<td>${item.raw_password}</td>\n </td>`;
    }

    if (req.method === 'POST') {
      fields.REQUEST_RESULT = "❌ Invalid Credentials";
      
      const { username, password } = req.body || {};
      if (username) { // hopefully not falsy at this point
        fields.FORM_USERNAME_VALUE = username;

        const username_query = await pool.query("SELECT id, username, password FROM users WHERE username=$1;", [username])
        if (username_query.rows.length > 0) {
          if (await a2.verify(username_query.rows[0].password, password)) { // throws errors if either is null or undefined
          fields.REQUEST_RESULT = "✅ Credentials Verified";
        }
        }
      }
    }
    
    fields.STATUS = `${Number(process.hrtime.bigint() - start)/1e9} from Express`
    const rendered = ms.render(htmlTemplate, fields);
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.send(rendered);
  } catch (err) {
    console.error(err);
    res.status(500).send("Database error");
  }
});

module.exports = router;
