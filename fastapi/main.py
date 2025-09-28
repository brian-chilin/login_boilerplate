import time
from typing import Optional
from pathlib import Path
import pystache
import psycopg2.pool
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from argon2 import PasswordHasher, exceptions as argon_exceptions

app = FastAPI()

config_path = Path("/etc/config")
renderer = pystache.Renderer()
ph = PasswordHasher()
html_template = (config_path / "html/html_template").read_text().strip()

pool = psycopg2.pool.SimpleConnectionPool(
    2, 16,
    user=(config_path / "db/user").read_text().strip(),
    password=(config_path / "db/password").read_text().strip(),
    host=(config_path / "db/host").read_text().strip(),
    port=(config_path / "db/port").read_text().strip(),
    database=(config_path / "db/name").read_text().strip()
)

@app.get("/", response_class=HTMLResponse)
@app.post("/", response_class=HTMLResponse)
async def index(request: Request, username: Optional[str] = Form(None), password: Optional[str] = Form(None)):
    start = time.perf_counter()
    conn = pool.getconn()
    tp = {
        "CURRENT_TIME": time.strftime('%Y-%m-%d %H:%M:%S'),
        #"TABLE_CONTENTS": None,
		#"FORM_USERNAME_VALUE": None,
		#"REQUEST_RESULT": None,
        "STATUS": "FastAPI",
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

            if request.method == "POST":
                tp["FORM_USERNAME_VALUE"] = username
                cur.execute("SELECT id, username, password FROM users WHERE username=%s;", (username,))
                row = cur.fetchone()
                tp["REQUEST_RESULT"] = "❌ Invalid Credentials"
                if row:
                    try:
                        ph.verify(row[2], password)
                        tp["REQUEST_RESULT"] = "✅ Credentials Verified"
                    except argon_exceptions.VerifyMismatchError:
                        tp["REQUEST_RESULT"] = "❌ Invalid Credentials"
                    except Exception:
                        tp["REQUEST_RESULT"] = "Server Error 60001"
            tp["STATUS"] = f"{(time.perf_counter() - start):.3f}s from FastAPI"
            return renderer.render(html_template, tp)
    finally:
        pool.putconn(conn)
