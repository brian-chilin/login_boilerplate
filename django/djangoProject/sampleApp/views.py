from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

import time
from pathlib import Path
import pystache
from argon2 import PasswordHasher, exceptions as argon_exceptions
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import User

config_path = Path("/etc/config")
renderer = pystache.Renderer()
ph = PasswordHasher()
html_template = (config_path / "html/html_template").read_text().strip()

@csrf_exempt
def index(request):
    start = time.perf_counter()
    tp = {
        "CURRENT_TIME": time.strftime('%Y-%m-%d %H:%M:%S'),
        "STATUS": "Django",
    }

    users = User.objects.all().order_by("id")
    tp["TABLE_CONTENTS"] = "".join(
        f"<tr><td>{u.id}</td><td>{u.username}</td><td>{u.password}</td><td>{u.raw_password if u.raw_password else 'NULL'}</td></tr>"
        for u in users
    )

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        tp["FORM_USERNAME_VALUE"] = username
        try:
            user = User.objects.get(username=username)
            ph.verify(user.password, password)
            tp["REQUEST_RESULT"] = "✅ Credentials Verified"
        except User.DoesNotExist:
            tp["REQUEST_RESULT"] = "❌ Invalid Credentials"
        except argon_exceptions.VerifyMismatchError:
            tp["REQUEST_RESULT"] = "❌ Invalid Credentials"
        except Exception:
            tp["REQUEST_RESULT"] = "Server Error 60001"

    tp["STATUS"] = f"{(time.perf_counter()-start):.3f}s from Django"
    return HttpResponse(renderer.render(html_template, tp))