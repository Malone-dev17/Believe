"""M.A.R.C local server. Serves the dashboard and a small JSON API over your private data.

Binds to 127.0.0.1 only, so nothing outside this laptop can reach it.
  python scripts/server.py            # then open http://127.0.0.1:8765/MARC/
"""
import json
import sys
from datetime import date, timedelta
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, unquote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import jobs  # noqa: E402
import invest  # noqa: E402

ROOT = jobs.ROOT
PORT = 8765
STATUSES = {"queued", "approved", "dismissed", "applied", "viewed", "interview", "rejected", "offer"}
BLOCKED = ("/private", "/.venv", "/.git", "/.claude")
DOWNLOADABLE = ("/private/cv/out/",)


def jobs_view():
    out = []
    for j in jobs.load_json(jobs.STORE, []):
        if j["status"] in ("new", "discarded", "scored"):
            continue
        note = ""
        if j.get("note_file") and (ROOT / j["note_file"]).exists():
            note = (ROOT / j["note_file"]).read_text(encoding="utf-8")
        out.append({**j, "description": (j.get("description") or "")[:700], "note": note})
    return out


def stats():
    store = jobs.load_json(jobs.STORE, [])
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    applied = [j for j in store if j.get("applied")]
    responded = [j for j in applied if j["status"] in ("viewed", "interview", "rejected", "offer")]
    by = lambda s: sum(1 for j in store if j["status"] == s)
    days = [(today - timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
    daily = [{"date": d, "count": sum(1 for j in applied if j["applied"] == d)} for d in days]
    weekly = []
    for w in range(7, -1, -1):
        start = week_start - timedelta(weeks=w)
        end = start + timedelta(days=7)
        weekly.append({"week": start.isoformat(),
                       "count": sum(1 for j in applied if start.isoformat() <= j["applied"] < end.isoformat())})
    return {
        "daily": daily, "weekly": weekly,
        "viewed": by("viewed"), "rejected": by("rejected"),
        "found": len(store), "discarded": by("discarded"), "queued": by("queued"), "approved": by("approved"),
        "applied_today": sum(1 for j in applied if j["applied"] == today.isoformat()),
        "applied_week": sum(1 for j in applied if j["applied"] >= week_start.isoformat()),
        "applied_total": len(applied), "interviews": by("interview"), "offers": by("offer"),
        "response_rate": round(100 * len(responded) / len(applied)) if applied else 0,
        "follow_ups_due": sum(1 for j in store if j.get("follow_up") and j["follow_up"] <= today.isoformat()
                              and j["status"] in ("applied", "viewed")),
    }


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def log_message(self, fmt, *args):
        pass

    def _json(self, data, code=200):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        if path == "/api/status":
            k = jobs.keys()
            return self._json({"local": True, "reed": bool(k.get("REED_API_KEY")),
                               "adzuna": bool(k.get("ADZUNA_APP_ID") and k.get("ADZUNA_APP_KEY")),
                               "stats": stats()})
        if path == "/api/jobs":
            return self._json(jobs_view())
        if path == "/api/invest":
            prof = jobs.load_json(ROOT / "private" / "profile.json", {}).get("investing", {})
            cache = jobs.load_json(invest.INSTRUMENTS, {})
            return self._json({"cards": jobs.load_json(invest.CARDS, []), "profile": prof,
                               "t212_list": cache.get("fetched"), "t212_count": len(cache.get("instruments", []))})
        if path.startswith(BLOCKED) and not path.startswith(DOWNLOADABLE):
            return self.send_error(403)
        if path.startswith(DOWNLOADABLE) and ".." in path:
            return self.send_error(403)
        return super().do_GET()

    def do_POST(self):
        # Same-origin only: refuse requests a web page on another site could forge.
        origin = self.headers.get("Origin")
        if origin and origin not in (f"http://127.0.0.1:{PORT}", f"http://localhost:{PORT}"):
            return self.send_error(403)
        path = urlparse(self.path).path
        try:
            data = self._body()
            if path == "/api/jobs/update":
                return self._json(update(data))
            if path == "/api/invest/decide":
                return self._json(invest.decide(data["id"], data["decision"], data.get("reason", "")))
            if path == "/api/jobs/note":
                j = find(data["id"])
                (ROOT / j["note_file"]).write_text(data["text"], encoding="utf-8")
                return self._json({"ok": True})
            if path == "/api/jobs/add":
                added = jobs.add_link(data["url"], data["title"], data["company"], data.get("description", ""),
                                      data.get("source", "Manual"), data.get("location", ""))
                return self._json({"added": added})
            if path == "/api/run":
                step = data.get("step", "run")
                result = {}
                if step in ("fetch", "run"):
                    result["fetch"] = jobs.fetch()
                if step in ("score", "run"):
                    result["score"] = jobs.score()
                if step in ("tailor", "run"):
                    result["tailor"] = jobs.tailor()
                return self._json(result)
        except Exception as e:  # report to the dashboard instead of crashing
            return self._json({"error": str(e)}, 400)
        self.send_error(404)


def find(job_id):
    for j in jobs.load_json(jobs.STORE, []):
        if j["id"] == job_id:
            return j
    raise KeyError(job_id)


def update(data):
    status = data.get("status")
    if status and status not in STATUSES:
        raise ValueError(f"Unknown status {status}")
    ids = set(data["ids"])
    store = jobs.load_json(jobs.STORE, [])
    today = date.today().isoformat()
    for j in store:
        if j["id"] not in ids:
            continue
        if status:
            j["status"] = status
            j.setdefault("history", []).append({"status": status, "date": today})
            if status == "approved":
                j["approved"] = today
            if status == "applied" and not j.get("applied"):
                j["applied"] = today
                j["follow_up"] = (date.today() + timedelta(days=7)).isoformat()
        for field in ("notes", "follow_up", "company", "title"):
            if field in data:
                j[field] = data[field]
    jobs.save_json(jobs.STORE, store)
    return {"updated": len(ids)}


if __name__ == "__main__":
    print(f"M.A.R.C running at http://127.0.0.1:{PORT}/MARC/  (close this window to stop)")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
