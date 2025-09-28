# import sys # useful for debug
from pathlib import Path
import time
import pystache
from flask import Flask, request
from argon2 import PasswordHasher, exceptions
import psycopg2.pool
import psycopg2

app = Flask(__name__)

config_path = Path("/etc/config")
renderer = pystache.Renderer()
ph = PasswordHasher()
html_template = (config_path / "html/html_template").read_text().strip()
pool = psycopg2.pool.SimpleConnectionPool(
    2, 16, # min, max
	user=(config_path / "db/user").read_text().strip(),
	password=(config_path / "db/password").read_text().strip(),
	host=(config_path / "db/host").read_text().strip(),
	port=(config_path / "db/port").read_text().strip(),
	database=(config_path / "db/name").read_text().strip()
)

@app.route('/', methods=["GET", "POST"])
def index():
	#print("index route entered", file=sys.stderr, flush=True) #debug
	start = time.perf_counter()
	conn = pool.getconn()
	# template parameters
	tp = {
		"CURRENT_TIME": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
		#"TABLE_CONTENTS": None,
		#"FORM_USERNAME_VALUE": None,
		#"REQUEST_RESULT": None,
		"STATUS": "Flask",
	}
	try:
		with conn.cursor() as cur:
			cur.execute("SELECT * FROM users ORDER BY id;")
			tp["TABLE_CONTENTS"] = "".join(
				f"""<tr>
						<td>{r_id}</td>
						<td>{r_username}</td>
						<td>{r_passhash}</td>
						<td>{r_passraw if r_passraw else "NULL"}</td>
					</tr>"""
				for r_id, r_username, r_passhash, r_passraw in cur.fetchall()
			)
			# for a, b, c, d in cur.fetchall():
			# 	table_contents += "<tr>"
			# 	table_contents += "<td>" + str(a) + "</td>"
			# 	table_contents += "<td>" + str(b) + "</td>"
			# 	table_contents += "<td>" + str(c) + "</td>"
			# 	table_contents += "<td>" + str(d if d else "NULL") + "</td>"
			# 	table_contents += "</tr>"
			# tp["TABLE_CONTENTS"] = table_contents

			if request.method == "POST":
				tp["FORM_USERNAME_VALUE"] = request.form['username']
				cur.execute(
					"SELECT id, username, password FROM users WHERE username=%s;",
					(request.form["username"],)
				)
				row = cur.fetchone()
				tp["REQUEST_RESULT"] = "❌ Invalid Credentials" #if not row --> username was wrong
				if row:
					try:
						ph.verify(row[2], request.form["password"])
						tp["REQUEST_RESULT"] = "✅ Credentials Verified"
					except exceptions.VerifyMismatchError:
						tp["REQUEST_RESULT"] = "❌ Invalid Credentials" #password was wrong
					except Exception as e:
						tp["REQUEST_RESULT"] = "Server Error 60001"
			tp["STATUS"] = f"{(time.perf_counter()-start):.3f}s from Flask"
			return renderer.render(html_template, tp)
	except Exception as e:
		tp["STATUS"] = f"Server Error 60000:\n{e}\n{(time.perf_counter()-start):.3f}s from Flask", 500
		return renderer.render(html_template, tp)
	finally:
		pool.putconn(conn)


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)
