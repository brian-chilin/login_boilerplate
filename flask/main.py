# import sys # useful for debug
from pathlib import Path
import time
from flask import Flask
from argon2 import PasswordHasher
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

@app.route('/')
def index():
	#print("index route entered", file=sys.stderr, flush=True) #debug
	start = time.perf_counter()
	conn = pool.getconn()
	try:
		with conn.cursor() as cur:
			cur.execute("SELECT * FROM users ORDER BY id;")
			s = "<table>"
			for a, b, c, d in cur.fetchall():
				s += "<tr>"
				s += "<td>" + str(a) + "</td>"
				s += "<td>" + str(b) + "</td>"
				s += "<td>" + str(c) + "</td>"
				s += "<td>" + str(d if d else "NULL") + "</td>"
				s += "</tr>"
			s+="</table>"
			return f"Current time is {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} <br>{s} <br><br>{(time.perf_counter()-start):.3f}s"
	except Exception as e:
		return f"server error:<br>{e} <br><br>{(time.perf_counter()-start):.3f}s", 500
	finally:
		pool.putconn(conn)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)
