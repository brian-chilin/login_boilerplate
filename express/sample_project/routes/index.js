var express = require('express');
var router = express.Router();

const fs = require('fs');
const pg = require('pg');
const ms = require('mustache');

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

router.get('/', async (req, res, next) => {
  try {
    const result = await pool.query('SELECT * FROM users');
    //res.json(result.rows);
    
    const view = {
      STATUS: "hello world 123 :^)",
    }
    const rendered = ms.render(htmlTemplate, view);

    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.send(rendered);

  } catch (err) {
    console.error(err);
    res.status(500).send("Database error");
  }
});

module.exports = router;
