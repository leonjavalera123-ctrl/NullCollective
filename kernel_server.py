"""
kernel_server.py  --  lets the 3D office talk to the Python kernel.
===================================================================

Run it like this (the office does it for you):

    python kernel_server.py --port-file C:/path/port.txt

WHAT IT IS
    A tiny server on your own machine. Godot connects to it, sends a line of
    Python, and gets back the output. That's how the terminal can appear on the
    monitor inside the 3D world with no second window.

THE PROTOCOL, IN FULL
    One JSON object per line, in both directions. Newline-delimited JSON is used
    here because it needs no library on either side: Godot has JSON built in, and
    "read until \\n" is three lines of GDScript.

    ->  {"cmd": "hello"}                  <-  {"ok": true, "version": 1}
    ->  {"cmd": "start", "level": 4}      <-  {"ok": true, "title": "GHOST",
                                                "challenge": {...}}
    ->  {"cmd": "submit", "line": "x = 1"} <- {"ok": true, "lines": [...],
                                                "in_block": false, "solved": false}
    ->  {"cmd": "hint"} / {"cmd": "solution"}   (records that you used help)
    ->  {"cmd": "next"}                   <-  {"ok": true, "done": false,
                                                "challenge": {...}}
    ->  {"cmd": "report", "session": "s1"} <- {"ok": true, "report": {...}}
    ->  {"cmd": "bye"}                    <-  closes

SAFETY
    It binds to 127.0.0.1 only, so nothing outside this computer can reach it,
    and it exits on its own when the office disconnects.

WHY A PORT FILE
    Asking for port 0 lets the operating system hand us any free port, which
    means this can never clash with something else you're running. We write the
    number it chose into a small file, and Godot reads it.
"""

import sys
import json
import socket
import argparse
import traceback

import pykernel

VERSION = 1


def handle(session, msg):
    """Turn one request into one reply. `session` is a one-item list so we can
    replace the Session object from inside this function."""
    cmd = msg.get("cmd", "")

    if cmd == "hello":
        return {"ok": True, "version": VERSION}

    if cmd == "start":
        level = int(msg.get("level", 0))
        try:
            s = pykernel.Session(level)
        except Exception as e:
            return {"ok": False, "error": "could not load level %d: %s" % (level, e)}
        session[0] = s
        if not s.challenges:
            return {"ok": False, "error": "level %d has no lab challenges" % level}
        # The briefing rides along with the start reply, so Godot has everything
        # it needs to teach the level before the lab opens.
        return dict({"ok": True, "title": s.title, "level": level,
                     "challenge": s.current()},
                    **pykernel.briefing_for(level))

    s = session[0]
    if s is None:
        return {"ok": False, "error": "no session started"}

    if cmd == "submit":
        return dict({"ok": True}, **s.submit(str(msg.get("line", ""))))

    if cmd == "hint":
        s.mark_hint()
        return {"ok": True}

    if cmd == "solution":
        s.mark_solution()
        return {"ok": True}

    if cmd == "next":
        s.advance()
        # Three possible answers now: another challenge, the boss, or finished.
        return {"ok": True, "done": s.done, "phase": s.phase,
                "challenge": s.current(), "boss": s.boss_spec()}

    if cmd == "boss":
        # Ask for the current boss state without answering anything -- used when
        # the office opens the boss panel.
        return {"ok": True, "phase": s.phase, "boss": s.boss_spec()}

    if cmd == "boss_answer":
        out = s.boss_answer(msg.get("payload", {}))
        return dict({"ok": True, "phase": s.phase, "done": s.done,
                     "boss": s.boss_spec()}, **out)

    if cmd == "report":
        return {"ok": True, "report": s.report(str(msg.get("session", "")),
                                               int(msg.get("asked_level", s.level)))}

    return {"ok": False, "error": "unknown command: %s" % cmd}


def serve(port_file, port=0):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))         # 127.0.0.1 = this machine only
    srv.listen(1)
    chosen = srv.getsockname()[1]

    # Tell the office which port we landed on. Written last thing before we
    # start listening, so the file appearing means "ready".
    if port_file:
        with open(port_file, "w", encoding="utf-8") as f:
            f.write(str(chosen))
    print("kernel listening on 127.0.0.1:%d" % chosen, flush=True)

    conn, _ = srv.accept()
    conn_file = conn.makefile("rwb")
    session = [None]
    try:
        for raw in conn_file:
            raw = raw.strip()
            if not raw:
                continue
            try:
                msg = json.loads(raw.decode("utf-8"))
            except Exception:
                reply = {"ok": False, "error": "bad JSON"}
            else:
                if msg.get("cmd") == "bye":
                    break
                try:
                    reply = handle(session, msg)
                except Exception as e:
                    traceback.print_exc()
                    reply = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
            conn_file.write((json.dumps(reply) + "\n").encode("utf-8"))
            conn_file.flush()
    finally:
        try:
            conn_file.close()
            conn.close()
        except Exception:
            pass
        srv.close()
    print("kernel closed", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--port-file", default="")
    a = ap.parse_args()
    serve(a.port_file, a.port)
