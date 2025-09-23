# import sys # useful for debug
from pathlib import Path
import time
from flask import Flask, request
from argon2 import PasswordHasher, exceptions
import psycopg2.pool
import psycopg2

config_path = Path("/etc/config")
app = Flask(__name__)
ph = PasswordHasher()
pool = psycopg2.pool.SimpleConnectionPool(
    2, 16, # min, max
	user=(config_path / "db_user").read_text().strip(),
	password=(config_path / "db_password").read_text().strip(),
	host=(config_path / "db_host").read_text().strip(),
	port=(config_path / "db_port").read_text().strip(),
	database=(config_path / "db_name").read_text().strip()
)

@app.route('/', methods=["GET", "POST"])
def index():
	#print("index route entered", file=sys.stderr, flush=True) #debug
	start = time.perf_counter()
	conn = pool.getconn()
	raw_html = f"<p>Current time is {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}</p>"
	try:
		with conn.cursor() as cur:
			cur.execute("SELECT * FROM users ORDER BY id;")
			raw_html += "<table><tr><th>id</th><th>username</th><th>password</th><th>raw_password</th></tr>"
			for a, b, c, d in cur.fetchall():
				raw_html += "<tr>"
				raw_html += "<td>" + str(a) + "</td>"
				raw_html += "<td>" + str(b) + "</td>"
				raw_html += "<td>" + str(c) + "</td>"
				raw_html += "<td>" + str(d if d else "NULL") + "</td>"
				raw_html += "</tr>"

			request_result, username_value = "", ""
			if request.method == "POST":
				username_value = request.form['username']
				cur.execute(
					"SELECT id, username, password FROM users WHERE username=%s;",
					(request.form["username"],)
				)
				row = cur.fetchone()
				request_result = "❌ invalid credentials" #if not row --> username was wrong
				if row:
					try:
						ph.verify(row[2], request.form["password"])
						request_result = "✅ credentials verified"
					except exceptions.VerifyMismatchError:
						request_result = "❌ invalid credentials" #password was wrong
					except Exception as e:
						request_result = "server error"

			raw_html += "</table>"
			raw_html += f"""
				<form method="post">
					<table>
						<tr>
							<td><label>Username:</label></td>
							<td><input type="text" name="username" value="{username_value}" required></td>
						</tr><tr>
							<td><label>Password:</label></td>
							<td><input type="password" name="password" required></td>
						</tr>
					</table>
					<button type="submit">Verify</button>{request_result}
				</form>
			"""
			raw_html += f"<p>{(time.perf_counter()-start):.3f}s from Flask</p>"
			return raw_html
	except Exception as e:
		return f"<p>server error:<p></p>{e}</p> <p>{(time.perf_counter()-start):.3f}s from Flask</p>", 500
	finally:
		pool.putconn(conn)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)
