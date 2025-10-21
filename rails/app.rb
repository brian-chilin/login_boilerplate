require "sinatra"
require "pg"
require "connection_pool"
require 'mustache'
require 'time'
require 'argon2'


set :bind, "0.0.0.0" 
set :port, 80      

# config
DB_CONFIG = Dir.glob("/etc/config/db/*").each_with_object({}) do |path, conf|
    if File.file?(path)
      key = File.basename(path)
      conf[key] = File.read(path).strip
    end
end

HTML_TEMPLATE = "/etc/config/html/html_template"
if File.file?(HTML_TEMPLATE)
  HTML_TEMPLATE = File.read(HTML_TEMPLATE).strip
else
  warn "FATAL: ❌ #{HTML_TEMPLATE} not found"
  exit(1)
end

# --- Connect to Postgres ---
DB_POOL = ConnectionPool.new(size: 5, timeout: 5) do
  PG.connect(
    host: DB_CONFIG["host"],
    dbname: DB_CONFIG["name"],
    user: DB_CONFIG["user"],
    password: DB_CONFIG["password"],
    port: DB_CONFIG["port"]
  )
end

begin
  DB_POOL.with do |conn|
    conn.exec("SELECT 1")
  end
  puts "✅ Postgres Connection pool ready."
rescue => e
  warn "FATAL: ❌ Postgres connection check failed: #{e.class} - #{e.message}"
  exit(1)
end


def get_values()
  vals = {
    "CURRENT_TIME" => Time.now(),
    # TABLE_CONTENTS => "",
    # FORM_USERNAME_VALUE => None,
    # REQUEST_RESULT => None,
    "STATUS" => "Ruby"
  }
  users = []
  DB_POOL.with do |conn|
      res = conn.exec("SELECT * FROM users ORDER BY id;")
      users = res.map { |r| "<tr> <td>#{r["id"]}</td> <td>#{r["username"]}</td> <td>#{r["password"]}</td> <td>#{r["raw_password"] || "NULL"}</td> </tr>" }
  end
  vals["TABLE_CONTENTS"] = users.join("")
  return vals
end

get "/" do
  start = Process.clock_gettime(Process::CLOCK_MONOTONIC)
  v = get_values()
  delta = Process.clock_gettime(Process::CLOCK_MONOTONIC) - start
  v["STATUS"] = "#{delta}s from Ruby"
  Mustache.render("#{HTML_TEMPLATE}", v)
end

post "/" do
  start = Process.clock_gettime(Process::CLOCK_MONOTONIC)
  v = get_values()
  delta = Process.clock_gettime(Process::CLOCK_MONOTONIC) - start
  v["STATUS"] = "#{delta}s from Ruby"

  if params["username"] and params["password"]
    v["FORM_USERNAME_VALUE"] = params["username"]
    v["REQUEST_RESULT"] = "❌ Invalid Credentials"
    DB_POOL.with do |conn|
      result = conn.exec_params("SELECT id, username, password FROM users WHERE username=$1;", [params["username"]])
      if result.ntuples> 0
        hashed_pass = result[0]["password"]
        if Argon2::Password.verify_password(params["password"], hashed_pass)
          v["REQUEST_RESULT"] = "✅ Credentials Verified"
        end
      end
    end
  end

  Mustache.render("#{HTML_TEMPLATE}", v)
end