#!/usr/bin/env python3
"""Tiny promo-page API: /api/info, /api/lead, /api/status + static dist/.

Holds expire after offer.holdMinutes. Payment is a placeholder URL from offer.json —
this server never creates Stripe products or Payment Links.
"""
from __future__ import annotations
import json, os, time, uuid, threading
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
DIST = Path(os.environ.get("PROMO_DIST", str(ROOT / "dist")))
OFFER_PATH = Path(os.environ.get("PROMO_OFFER", str(ROOT / "offer.json")))

app = Flask(__name__, static_folder=None)
_lock = threading.Lock()
_state = {"taken": 0, "holds": {}}  # id -> {until, lead}


def load_offer():
    return json.loads(OFFER_PATH.read_text())


def purge(now=None):
    now = now or time.time()
    dead = [k for k, v in _state["holds"].items() if v["until"] <= now]
    for k in dead:
        _state["holds"].pop(k, None)


def snapshot(offer):
    purge()
    total = int(offer["offer"]["spotsTotal"])
    taken = int(_state["taken"])
    held = len(_state["holds"])
    left = max(0, total - taken - held)
    end = offer["offer"].get("deadline")
    # naive open check: parse ISO if possible
    open_ = left > 0
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        open_ = open_ and (datetime.now(dt.tzinfo) < dt if dt.tzinfo else True)
    except Exception:
        pass
    return {
        "ok": True,
        "price": offer["offer"].get("promoPrice"),
        "regular": offer["offer"].get("regularPrice"),
        "spots": total,
        "taken": taken,
        "held": held,
        "left": left,
        "ends": end,
        "open": open_,
        "holdMinutes": offer["offer"].get("holdMinutes", 15),
        "paymentLink": offer["offer"].get("paymentLink"),
    }


@app.get("/api/info")
def info():
    with _lock:
        return jsonify(snapshot(load_offer()))


@app.post("/api/lead")
def lead():
    data = request.get_json(force=True, silent=True) or {}
    if data.get("website"):
        return jsonify({"ok": True}), 200  # honeypot
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    email = (data.get("email") or "").strip()
    if not name or not phone or not email:
        return jsonify({"ok": False, "error": "Name, phone, and email are required."}), 400
    offer = load_offer()
    with _lock:
        snap = snapshot(offer)
        if not snap["open"] or snap["left"] <= 0:
            return jsonify({**snap, "ok": True, "open": False})
        hold_m = int(offer["offer"].get("holdMinutes") or 15)
        lid = uuid.uuid4().hex[:12]
        until = time.time() + hold_m * 60
        _state["holds"][lid] = {
            "until": until,
            "lead": {
                "name": name,
                "phone": phone,
                "email": email,
                "business": (data.get("business") or "").strip(),
            },
        }
        # Persist leads lightly for local/demo runs
        leads_path = DIST / "leads.jsonl"
        try:
            with leads_path.open("a") as f:
                f.write(json.dumps({"id": lid, "until": until, **_state["holds"][lid]["lead"]}) + "\n")
        except Exception:
            pass
        snap = snapshot(offer)
        pay = offer["offer"].get("paymentLink") or ""
        placeholder = (not pay) or ("PLACEHOLDER" in str(pay))
        return jsonify({
            **snap,
            "ok": True,
            "id": lid,
            "hold_until": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(until)),
            "pay": None if placeholder else {"url": pay},
            "placeholderPayment": placeholder,
        })


@app.get("/api/status")
def status():
    cid = request.args.get("c") or ""
    offer = load_offer()
    with _lock:
        purge()
        h = _state["holds"].get(cid)
        snap = snapshot(offer)
        return jsonify({
            **snap,
            "ok": True,
            "found": bool(h),
            "hold_until": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(h["until"])) if h else None,
        })


@app.get("/")
def index():
    return send_from_directory(DIST, "index.html")


@app.get("/<path:path>")
def static_proxy(path):
    return send_from_directory(DIST, path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5055"))
    app.run(host="0.0.0.0", port=port, debug=False)
