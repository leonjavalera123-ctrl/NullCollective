"""
datalevels.py  --  new levels defined entirely as DATA.
=======================================================

Thanks to the reusable bosses in bosses.py, a whole new level is now just a
dictionary: its story text, its INTEL/LESSON cards, its lab CHALLENGES, and a
boss described by data (a quiz or a threat-hunt). main.py slots these in before
the NULL finale automatically -- adding more later means appending to this list.

These five levels go DEEPER on topics the player has already met, giving extra
hands-on practice (the "more training per topic" goal).

Each challenge `check(t)` reads the terminal: t.ns (variables) + t.last_run (output).
"""
import hashlib

import base64
import random

# ===========================================================================
# CHECK FUNCTIONS  (kept near the top; each just inspects the terminal)
# ===========================================================================
# -- Passwords II --
def _c_isok(t):       return t.ns.get("is_ok") is False
def _c_types(t):      return t.ns.get("types") == 3
def _c_verdict(t):
    f = t.ns.get("verdict")
    try:    return callable(f) and f("a" * 12) == "strong" and f("abc") == "weak"
    except Exception: return False

# -- Crypto II (XOR) --
def _c_xor(t):        return t.ns.get("x") == 6
def _c_unxor(t):      return t.ns.get("orig") == 5
def _c_xcrypt(t):
    f = t.ns.get("xcrypt")
    try:    return callable(f) and f(f("Hi", 7), 7) == "Hi"
    except Exception: return False

# -- Web II (XSS) --
def _c_hasscript(t):  return t.ns.get("has_script") is True
def _c_escape(t):     return "<" not in str(t.ns.get("safe", "<"))
def _c_isxss(t):
    f = t.ns.get("is_xss")
    try:    return callable(f) and f("<SCRIPT>") is True and f("hello") is False
    except Exception: return False

# -- Networks II (logs) --
def _c_fails(t):      return t.ns.get("fails") == 3
def _c_badips(t):     return t.ns.get("bad_ips") == ["9.9.9.9", "9.9.9.9", "9.9.9.9"]
def _c_attack(t):
    f = t.ns.get("is_attack")
    try:    return callable(f) and f(7) is True and f(2) is False
    except Exception: return False

# -- Malware II (ransomware) --
def _c_locked(t):     return t.ns.get("locked") is True
def _c_count(t):      return t.ns.get("count") == 2
def _c_recover(t):
    f = t.ns.get("can_recover")
    try:    return callable(f) and f(True) is True and f(False) is False
    except Exception: return False


# -- Passwords III (VAULT: managers & passkeys) --
def _c_vault_pick(t):
    try:
        p = t.ns.get("pick")
        letters = t.ns.get("letters", "")
        return isinstance(p, str) and len(p) == 1 and p in letters
    except Exception:
        return False

def _c_vault_build(t):
    try:
        pw = t.ns.get("password")
        letters = t.ns.get("letters", "")
        if not isinstance(pw, str) or len(pw) != 16:
            return False
        for ch in pw:
            if ch not in letters:
                return False
        return True
    except Exception:
        return False

def _c_vault_store(t):
    try:
        vault = t.ns.get("vault")
        sites = t.ns.get("sites")
        letters = t.ns.get("letters", "")
        if not isinstance(vault, dict) or not isinstance(sites, list):
            return False
        if len(sites) == 0:
            return False
        made = []
        for site in sites:
            pw = vault.get(site)
            if not isinstance(pw, str) or len(pw) != 14:
                return False
            for ch in pw:
                if ch not in letters:
                    return False
            made.append(pw)
        if len(set(made)) != len(made):
            return False
        return t.ns.get("mail_pw") == vault[sites[0]]
    except Exception:
        return False
# -- Social Engineering: vishing (WHISPER) --
def _c_whisper_scary(t):
    return t.ns.get("scary") is True

def _c_whisper_count(t):
    return t.ns.get("count") == 3

def _c_whisper_score(t):
    f = t.ns.get("score")
    try:
        return (callable(f)
                and f(["read me the code", "act now"]) == 2
                and f(["read me the code", "do not hang up",
                       "act now"]) == 3
                and f(["hello", "thanks"]) == 0)
    except Exception:
        return False
# -- Web III (sessions & CSRF) --
def _c_forger_same(t):   return t.ns.get("same") is False
def _c_forger_size(t):   return t.ns.get("size") == 32
def _c_forger_valid(t):
    f = t.ns.get("is_valid")
    good = "k" * 20
    try:
        return (callable(f) and f(good, good) is True
                and f("short", "short") is False
                and f(good, "z" * 20) is False
                and f("k" * 16, "k" * 16) is True)
    except Exception:
        return False
def _c_sieve_in(t):
    return t.ns.get("is_allowed") is False

def _c_sieve_filter(t):
    return t.ns.get("safe") == ["png", "jpg", "gif"]

def _c_sieve_safe(t):
    f = t.ns.get("open_page")
    try:
        return (callable(f) and f("home") == "Welcome"
                and f("boom") == "Access denied")
    except Exception:
        return False
# -- Networks III (Wi-Fi / evil twins) --
def _c_beacon_sec(t):
    return t.ns.get("sec") == "open"

def _c_beacon_open(t):
    return t.ns.get("open_names") == ["Cafe_WiFi", "City_Free_WiFi"]

def _c_beacon_twin(t):
    f = t.ns.get("is_twin")
    real = {"name": "Cafe_WiFi", "security": "wpa2"}
    fake = {"name": "Cafe_WiFi", "security": "open"}
    other = {"name": "City_Free_WiFi", "security": "open"}
    try:
        return (callable(f) and f(fake, "Cafe_WiFi") is True
                and f(real, "Cafe_WiFi") is False
                and f(other, "Cafe_WiFi") is False)
    except Exception:
        return False
def _c_bastion_first(t):
    return t.ns.get("first_action") == "allow"


def _c_bastion_match(t):
    return t.ns.get("first_match") == {"port": 22, "action": "deny"}


def _c_bastion_decide(t):
    f = t.ns.get("decide")
    rules = [{"port": 443, "action": "allow"},
             {"port": 443, "action": "deny"},
             {"port": 22, "action": "deny"}]
    try:
        return (callable(f)
                and f(443, rules) == "allow"
                and f(22, rules) == "deny"
                and f(9999, rules) == "deny")
    except Exception:
        return False
def _c_herald_encode(t):
    v = t.ns.get("coded")
    try:
        if isinstance(v, str):
            v = v.encode()
        return base64.b64decode(v) == b"OPEN AT DAWN"
    except Exception:
        return False


def _c_herald_decode(t):
    try:
        return t.ns.get("plain") == "OPEN AT DAWN"
    except Exception:
        return False


def _c_herald_trip(t):
    f = t.ns.get("round_trip")
    try:
        return (callable(f) and f("HERALD") == "HERALD"
                and f("null tip") == "null tip")
    except Exception:
        return False
# -- Stego (VEIL) --
def _c_veil_spaces(t):
    return t.ns.get("hidden") == 5

def _c_veil_slice(t):
    return t.ns.get("secret") == "help"

def _c_veil_reveal(t):
    f = t.ns.get("reveal")
    try:
        return (callable(f) and f("high east lane park") == "help"
                and f("abcdefghij") == "af")
    except Exception:
        return False


# -- Public-key crypto (KEYSTONE) --
def _c_keystone_pow(t):
    try:
        return t.ns.get("answer") == 9
    except Exception:
        return False

def _c_keystone_lock(t):
    try:
        return t.ns.get("coded") == 26
    except Exception:
        return False

def _c_keystone_unlock(t):
    try:
        f = t.ns.get("decrypt")
        return (callable(f) and f(26, 7, 33) == 5
                and f(3, 7, 33) == 9
                and f(8, 7, 33) == 2
                and t.ns.get("plain") == 5)
    except Exception:
        return False
# -- Incident response (SIREN) --
def _siren_rank(alert):
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    return order.get(alert["severity"], 9)


def _c_siren_count(t):
    try:
        return t.ns.get("criticals") == 2
    except Exception:
        return False


def _c_siren_ids(t):
    try:
        return t.ns.get("critical_ids") == ["A-15", "A-17"]
    except Exception:
        return False


def _c_siren_triage(t):
    f = t.ns.get("triage")
    rows = [{"id": "B-1", "severity": "low"},
            {"id": "B-2", "severity": "critical"},
            {"id": "B-3", "severity": "medium"},
            {"id": "B-4", "severity": "high"}]
    if not callable(f):
        return False
    try:
        out = f(rows)
    except NameError:
        try:
            f.__globals__.setdefault("rank", _siren_rank)
            out = f(rows)
        except Exception:
            return False
    except Exception:
        return False
    try:
        if not isinstance(out, list) or len(out) != 4:
            return False
        got = []
        for r in out:
            got.append(r["id"])
        return got == ["B-2", "B-4", "B-3", "B-1"]
    except Exception:
        return False
# -- Threat modelling (CANARY) --
def _c_canary_risk(t):
    try:
        return t.ns.get("risk") == 15
    except Exception:
        return False


def _c_canary_scores(t):
    try:
        return (t.ns.get("scores") == [25, 12, 8, 5]
                and t.ns.get("top") == 25)
    except Exception:
        return False


def _c_canary_worst(t):
    try:
        f = t.ns.get("worst")
        a = [{"name": "Weak lock", "likelihood": 2, "impact": 2},
             {"name": "Shared login", "likelihood": 5, "impact": 3},
             {"name": "Flood", "likelihood": 1, "impact": 9}]
        b = [{"name": "Open port", "likelihood": 3, "impact": 9},
             {"name": "Lost badge", "likelihood": 1, "impact": 1}]
        return (callable(f) and f(a) == "Shared login"
                and f(b) == "Open port")
    except Exception:
        return False
# -- Backups & recovery (ARCHIVE) --
def _c_archive_gap(t):
    try:
        return t.ns.get("data_lost") == 19
    except Exception:
        return False


def _c_archive_offsite(t):
    try:
        return t.ns.get("offsite_count") == 2
    except Exception:
        return False


def _c_archive_survives(t):
    try:
        f = t.ns.get("survives")
        return (callable(f)
                and f(3, 1, True) is True
                and f(4, 2, True) is True
                and f(2, 1, True) is False
                and f(3, 0, True) is False
                and f(3, 1, False) is False)
    except Exception:
        return False
# -- Privacy: collect less, redact the rest (LEDGER) --
def _c_ledger_last4(t):
    try:
        return t.ns.get("last4") == "4471"
    except Exception:
        return False


def _c_ledger_masked(t):
    try:
        return t.ns.get("masked") == "**** **** **** 4471"
    except Exception:
        return False


def _c_ledger_redact(t):
    try:
        f = t.ns.get("redact")
        if not callable(f):
            return False
        rec = {"name": "Ada Vance", "card": "4024007182354471",
               "phone": "303-555-0142"}
        out = f(rec, ["name"])
        rec2 = {"name": "Ada Vance", "card": "4024007182354471",
                "phone": "303-555-0142"}
        out2 = f(rec2, ["name", "phone"])
        return (isinstance(out, dict)
                and len(out) == 3
                and out.get("name") == "Ada Vance"
                and out.get("card") == "****4471"
                and out.get("phone") == "****0142"
                and out2.get("phone") == "303-555-0142")
    except Exception:
        return False
# -- Forensics (MORTIS) --
_MORTIS_LOG = ("00:52 mail: attachment opened\n"
               "01:07 vpn: login from a new device\n"
               "02:08 admin: account svc_backup2 created")


def _mortis_by_time(e):
    return e["time"]


def _c_mortis_stamp(t):
    try:
        ev = t.ns.get("evidence")
        want = hashlib.sha256(ev.encode()).hexdigest()
        return t.ns.get("stamp") == want
    except Exception:
        return False


def _c_mortis_verify(t):
    try:
        ev = t.ns.get("evidence")
        want = hashlib.sha256(ev.encode()).hexdigest()
        return (t.ns.get("fresh_stamp") == want
                and t.ns.get("unchanged") is True)
    except Exception:
        return False


def _c_mortis_timeline(t):
    try:
        f = t.ns.get("by_time")
        if not callable(f) or f({"time": "07:00"}) != "07:00":
            return False
        events = t.ns.get("events")
        want = sorted(events, key=_mortis_by_time)
        if t.ns.get("timeline") != want:
            return False
        return t.ns.get("first") == want[0]["what"]
    except Exception:
        return False


# ===========================================================================
# THE LEVELS
# ===========================================================================
DATA_LEVELS = [

    # --------------------------------------------------------------- BRUTUS
    {"boss": "BRUTUS", "topic": "Passwords: Going Deeper",
     "brief": "BRUTUS is the Cracker's brutal cousin, running password audits on "
              "stolen accounts. Sharpen your password judgement: measure strength "
              "in code, then clear out every weak password before BRUTUS does.",
     "debrief": "Lesson: a strong password is long AND varied. Counting character "
                "types and length in code is exactly how real strength meters work.",
     "intel": [
        {"heading": "What BRUTUS does",
         "body": "BRUTUS automates password audits the attacker way: score every "
                 "account and pile effort onto the weak ones. Length and variety "
                 "decide who survives. You'll score passwords in Python, the same "
                 "way a real strength meter does.",
         "code": "weak = [a for a in accounts if len(a.password) < 12]"},
        {"heading": "Why it works",
         "body": "Short or common passwords are cracked in seconds; long, varied, "
                 "unpredictable ones effectively never. A few lines of Python can "
                 "tell the two apart instantly.",
         "code": None}],
     "lesson": [
        {"heading": "1. Booleans add up",
         "body": "True counts as 1 and False as 0, so sum([...]) over a list of "
                 "tests tells you how many passed. Great for 'how many character "
                 "types are present?'",
         "code": "sum([True, False, True])   # -> 2"},
        {"heading": "2. any() over the characters",
         "body": "any(c.isdigit() for c in pw) is True if the password has at least "
                 "one digit. Swap isdigit for islower/isupper to check other types.",
         "code": "any(c.isupper() for c in \"abcD\")   # -> True"},
        {"heading": "3. Return different answers",
         "body": "A function can return one thing or another with if/else, letting "
                 "you turn a rule into a reusable verdict.",
         "code": "def verdict(pw):\n    return \"strong\" if len(pw) >= 12 else \"weak\""}],
     "challenges": [
        {"title": "Reject short passwords",
         "goal": "Set `is_ok` to whether `pw` has at least 12 characters "
                 "(len(pw) >= 12).",
         "seed": lambda: {"pw": "sunshine"},
         "intro": ["# `pw` = 'sunshine' (8 letters). Is it 12+ characters?"],
         "hint": "is_ok = len(pw) >= 12",
         "solution": "is_ok = len(pw) >= 12",
         "check": _c_isok,
         "success": "'sunshine' is too short, so is_ok is False."},
        {"title": "Count the character types",
         "goal": "Count how many of these THREE are present in `pw`: a lowercase "
                 "letter, an uppercase letter, a digit. Store the total in `types` "
                 "using sum([...]) of three any(...) checks.",
         "seed": lambda: {"pw": "Abc12"},
         "intro": ["# `pw` = 'Abc12'. Count lower + upper + digit present.",
                   "# types = sum([any(c.islower() for c in pw), ... , ...])"],
         "hint": "types = sum([any(c.islower() for c in pw), "
                 "any(c.isupper() for c in pw), any(c.isdigit() for c in pw)])",
         "solution": "types = sum([any(c.islower() for c in pw), "
                     "any(c.isupper() for c in pw), any(c.isdigit() for c in pw)])",
         "check": _c_types,
         "success": "'Abc12' has lower, upper and digits -> 3 types."},
        {"title": "Write a verdict function",
         "goal": "Write `verdict(pw)` returning 'strong' if pw is 12+ characters, "
                 "else 'weak'.",
         "intro": ["# def verdict(pw): return 'strong' or 'weak' based on length."],
         "hint": "def verdict(pw):  return 'strong' if len(pw) >= 12 else 'weak'",
         "solution": "def verdict(pw):\n    return 'strong' if len(pw) >= 12 else 'weak'",
         "check": _c_verdict,
         "success": "A reusable strength verdict -- the heart of a password meter."}],
     "boss_kind": "flag",
     "boss_data": {
        "prompt": "Flag every WEAK password in the stolen audit, then run the check.",
        "scan_label": "Audit Passwords",
        "win": "Clean audit -- every weak password flagged. BRUTUS finds nothing to crack.",
        "items": [
            {"label": "sunshine", "detail": "8 chars",
             "bad": True, "reason": "Short and a common word -- cracked instantly."},
            {"label": "correct-horse-battery-staple", "detail": "28 chars",
             "bad": False, "reason": "Long passphrase of random words -- excellent."},
            {"label": "P@ss1", "detail": "5 chars",
             "bad": True, "reason": "Too short; symbols don't save a 5-char password."},
            {"label": "9xQ!vmZ2kLp7wR", "detail": "14 chars",
             "bad": False, "reason": "Long and fully random -- very strong."},
            {"label": "password123", "detail": "11 chars",
             "bad": True, "reason": "Common base word plus predictable digits."}]}},

    # ----------------------------------------------------------------- VEX
    {"boss": "VEX", "topic": "Cryptography: The XOR Trick",
     "brief": "VEX hides NULL's data with XOR -- a lightning-fast scramble used "
              "everywhere in real cryptography. Learn how one operator can both "
              "encrypt and decrypt, then prove your understanding to VEX.",
     "debrief": "Lesson: XOR is reversible -- applying the same key twice returns "
                "the original. It's a building block inside many real ciphers.",
     "intel": [
        {"heading": "What VEX does",
         "body": "VEX encrypts with XOR (the ^ operator). XOR has a magic property: "
                 "do it twice with the same key and you get back exactly what you "
                 "started with. That single fact is the whole trick.",
         "code": "secret = data ^ key       # encrypt\n"
                 "data   = secret ^ key     # same key -> decrypt"},
        {"heading": "Why it matters",
         "body": "XOR alone with a tiny key is weak, but XOR with a long, random "
                 "key (a 'one-time pad') is unbreakable, and XOR is a core piece of "
                 "serious ciphers. You'll build an XOR cipher in the lab.",
         "code": None}],
     "lesson": [
        {"heading": "1. The ^ operator",
         "body": "^ compares two numbers bit by bit and outputs 1 where they "
                 "differ. You don't need the bit details -- just that it combines "
                 "two numbers into a new one.",
         "code": "5 ^ 3     # -> 6"},
        {"heading": "2. XOR reverses itself",
         "body": "Because differences cancel out, XOR-ing twice with the same key "
                 "undoes the scramble. That's why one function can encrypt AND "
                 "decrypt.",
         "code": "c = 5 ^ 9     # -> 12 (encrypted)\nc ^ 9         # -> 5 (back again)"},
        {"heading": "3. XOR every character",
         "body": "Loop over a string, XOR each letter's number by the key, and "
                 "rebuild the text with chr(). Run it again with the same key to "
                 "decrypt.",
         "code": "\"\".join(chr(ord(c) ^ key) for c in text)"}],
     "challenges": [
        {"title": "XOR two numbers",
         "goal": "The ^ operator is XOR. Store the value of 5 ^ 3 in `x`.",
         "intro": ["# Try:  5 ^ 3   then store it in x."],
         "hint": "x = 5 ^ 3",
         "solution": "x = 5 ^ 3",
         "check": _c_xor,
         "success": "5 ^ 3 is 6. That's XOR."},
        {"title": "Undo an XOR",
         "goal": "`cipher` was made by XOR-ing a secret number with `key`. Recover "
                 "the original by XOR-ing again: orig = cipher ^ key.",
         "seed": lambda: {"cipher": 12, "key": 9},
         "intro": ["# cipher = 12, key = 9. XOR with the key again to decrypt.",
                   "# orig = cipher ^ key"],
         "hint": "orig = cipher ^ key",
         "solution": "orig = cipher ^ key",
         "check": _c_unxor,
         "success": "12 ^ 9 gives back 5 -- the same key both locks and unlocks."},
        {"title": "Build an XOR cipher",
         "goal": "Write `xcrypt(text, key)` that XORs every character of `text` by "
                 "`key` and returns the new text. Running it twice with the same "
                 "key should return the original.",
         "intro": ["# def xcrypt(text, key):",
                   "#   return ''.join(chr(ord(c) ^ key) for c in text)"],
         "hint": "def xcrypt(text, key):  return ''.join(chr(ord(c) ^ key) for c in text)",
         "solution": "def xcrypt(text, key):\n    return ''.join(chr(ord(c) ^ key) for c in text)",
         "check": _c_xcrypt,
         "success": "Encrypt and decrypt with ONE function -- the beauty of XOR."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "VEX challenges your grasp of how ciphers really work.",
        "win": "VEX's data is laid bare. Cryptography mastery confirmed.",
        "rounds": [
            {"q": "What makes XOR so handy for encryption?",
             "options": ["It is very slow",
                         "The same key applied twice gives back the original",
                         "It only works on letters", "It needs an internet connection"],
             "answer": 1},
            {"q": "Why is a simple Caesar cipher easy to break?",
             "options": ["There are only 25 shifts to try", "It uses XOR",
                         "It needs a password", "Computers cannot read it"],
             "answer": 0},
            {"q": "What keeps modern encryption safe?",
             "options": ["Very short keys", "A secret font",
                         "Keys so large that trying them all is impossible",
                         "Keeping the method hidden"],
             "answer": 2}]}},

    # ------------------------------------------------------------- SCRIPTER
    {"boss": "SCRIPTER", "topic": "Web Security: XSS",
     "brief": "SCRIPTER attacks websites a new way: 'cross-site scripting' (XSS). "
              "If a site shows your typed text back without cleaning it, an attacker "
              "can sneak in <script> code that runs in other visitors' browsers. "
              "Learn to detect and neutralize it.",
     "debrief": "Lesson: never show raw user input. Escaping dangerous characters "
                "(< becomes &lt;) stops typed text from turning into running code.",
     "intel": [
        {"heading": "What SCRIPTER does",
         "body": "SCRIPTER posts comments containing <script> tags. A careless site "
                 "displays them as-is, so the script runs for everyone who views the "
                 "page -- stealing logins and more. It's injection, but into the "
                 "browser instead of the database.",
         "code": "comment = \"<script>steal(cookies)</script>\"\n"
                 "page += comment      # oops -- now it RUNS for every visitor"},
        {"heading": "The fix",
         "body": "Treat user text as text, never code. 'Escaping' converts the "
                 "dangerous < into the harmless &lt; so the browser shows it instead "
                 "of running it.",
         "code": "safe = comment.replace(\"<\", \"&lt;\")"}],
     "lesson": [
        {"heading": "1. Searching inside text",
         "body": "The `in` keyword finds a substring; .lower() first makes the "
                 "search ignore capitalization, so <SCRIPT> and <script> both match.",
         "code": "\"<script\" in \"<SCRIPT>bad\".lower()   # -> True"},
        {"heading": "2. Replacing dangerous characters",
         "body": ".replace(old, new) swaps every occurrence. Turning < into &lt; "
                 "defuses an injected tag without deleting the user's text.",
         "code": "\"<b>hi\".replace(\"<\", \"&lt;\")   # -> '&lt;b>hi'"},
        {"heading": "3. A reusable detector",
         "body": "Wrap the check in a function that returns True/False so you can "
                 "scan any input the same way.",
         "code": "def is_xss(s):\n    return \"<script\" in s.lower()"}],
     "challenges": [
        {"title": "Spot a script tag",
         "goal": "Set `has_script` to True if `user` contains '<script' (use "
                 ".lower() so capital letters still match).",
         "seed": lambda: {"user": "<script>alert(1)</script>"},
         "intro": ["# Does `user` contain a script tag?",
                   "# Try:  \"<script\" in user.lower()"],
         "hint": "has_script = \"<script\" in user.lower()",
         "solution": "has_script = \"<script\" in user.lower()",
         "check": _c_hasscript,
         "success": "Caught the injected tag before it could run."},
        {"title": "Escape the danger",
         "goal": "Make `user` safe to display by replacing every '<' with '&lt;'. "
                 "Store the result in `safe`.",
         "seed": lambda: {"user": "<b>hi</b>"},
         "intro": ["# Replace '<' with '&lt;' so tags can't run.",
                   "# safe = user.replace('<', '&lt;')"],
         "hint": "safe = user.replace(\"<\", \"&lt;\")",
         "solution": "safe = user.replace(\"<\", \"&lt;\")",
         "check": _c_escape,
         "success": "No raw '<' survives -- the browser will SHOW the text, not run it."},
        {"title": "Write an XSS detector",
         "goal": "Write `is_xss(s)` returning True if `s` contains '<script' "
                 "(case-insensitive), else False.",
         "intro": ["# def is_xss(s): return whether '<script' is in s.lower()"],
         "hint": "def is_xss(s):  return \"<script\" in s.lower()",
         "solution": "def is_xss(s):\n    return \"<script\" in s.lower()",
         "check": _c_isxss,
         "success": "A reusable XSS filter -- exactly what a web app needs."}],
     "boss_kind": "flag",
     "boss_data": {
        "prompt": "These comments were submitted to a site. Flag the XSS attacks.",
        "scan_label": "Scan Comments",
        "win": "Every malicious comment caught. SCRIPTER's payloads never run.",
        "items": [
            {"label": "Great article, thanks!", "detail": "user comment",
             "bad": False, "reason": "Ordinary text -- harmless."},
            {"label": "<script>steal(cookies)</script>", "detail": "user comment",
             "bad": True, "reason": "Injects a script tag -- classic XSS."},
            {"label": "I love this, 5/5", "detail": "user comment",
             "bad": False, "reason": "Plain praise -- safe."},
            {"label": "<img src=x onerror=alert(1)>", "detail": "user comment",
             "bad": True, "reason": "An event handler that runs attacker code."},
            {"label": "check out my blog at example.com", "detail": "user comment",
             "bad": False, "reason": "Just a link -- no script."}]}},

    # ---------------------------------------------------------------- TRACE
    {"boss": "TRACE", "topic": "Networks: Reading the Logs",
     "brief": "Every attack leaves footprints in the logs. TRACE counts on nobody "
              "reading them. Learn to sift login records in Python -- counting "
              "failures and spotting the brute-force pattern -- then catch the "
              "intruder in the server logs.",
     "debrief": "Lesson: logs are an attacker's footprints. Counting events and "
                "watching for bursts of failures is how real intrusion detection works.",
     "intel": [
        {"heading": "What TRACE does",
         "body": "TRACE hammers a login page with thousands of password guesses. "
                 "Each try writes a line to the server log. A defender who counts "
                 "the failures per address sees the attack in seconds.",
         "code": "fails = [e for e in log if e['status'] == 'fail']\n"
                 "if len(fails) > 5: alert('brute force!')"},
        {"heading": "Why it works",
         "body": "Normal users fail a login once or twice. Fifty failures in ten "
                 "seconds from one address is unmistakable -- if someone is looking. "
                 "Python makes that 'looking' automatic.",
         "code": None}],
     "lesson": [
        {"heading": "1. Logs are lists of dictionaries",
         "body": "Each log line becomes a dict (who, what, result). A whole log is "
                 "a list of them -- loop through to analyze.",
         "code": "log = [{'ip': '9.9.9.9', 'status': 'fail'}, ...]"},
        {"heading": "2. Count what matters",
         "body": "Start a counter at 0 and add 1 each time a line meets your "
                 "condition. This is the core of every log analysis.",
         "code": "fails = 0\nfor e in log:\n    if e['status'] == 'fail':\n        fails += 1"},
        {"heading": "3. Turn a count into a decision",
         "body": "A simple threshold function decides when a count is suspicious -- "
                 "the seed of an intrusion-detection rule.",
         "code": "def is_attack(count):\n    return count >= 5"}],
     "challenges": [
        {"title": "Count the failed logins",
         "goal": "`logs` is a list of dicts, each with a 'status' of 'ok' or 'fail'. "
                 "Count the failures into `fails`.",
         "seed": lambda: {"logs": [{"ip": "1.1.1.1", "status": "ok"},
                                   {"ip": "9.9.9.9", "status": "fail"},
                                   {"ip": "9.9.9.9", "status": "fail"},
                                   {"ip": "1.1.1.1", "status": "ok"},
                                   {"ip": "9.9.9.9", "status": "fail"}]},
         "intro": ["# Loop `logs`, count entries whose 'status' is 'fail' -> `fails`."],
         "hint": "fails = 0  /  for e in logs:  /  if e['status'] == 'fail':  /  fails += 1",
         "solution": "fails = 0\nfor e in logs:\n    if e['status'] == 'fail':\n        fails += 1",
         "check": _c_fails,
         "success": "Three failures detected by your own code."},
        {"title": "Collect the attacker's IPs",
         "goal": "Build a list `bad_ips` of the 'ip' value from every log entry "
                 "whose status is 'fail'.",
         "seed": lambda: {"logs": [{"ip": "1.1.1.1", "status": "ok"},
                                   {"ip": "9.9.9.9", "status": "fail"},
                                   {"ip": "9.9.9.9", "status": "fail"},
                                   {"ip": "1.1.1.1", "status": "ok"},
                                   {"ip": "9.9.9.9", "status": "fail"}]},
         "intro": ["# Build `bad_ips` = the ip of each failed login.",
                   "# Start bad_ips = []  then append e['ip'] when status is 'fail'."],
         "hint": "bad_ips = []  /  for e in logs:  /  if e['status'] == 'fail':  /  bad_ips.append(e['ip'])",
         "solution": "bad_ips = []\nfor e in logs:\n    if e['status'] == 'fail':\n"
                     "        bad_ips.append(e['ip'])",
         "check": _c_badips,
         "success": "All three failures trace to 9.9.9.9 -- our intruder."},
        {"title": "Write the alarm rule",
         "goal": "Write `is_attack(count)` that returns True when `count` is 5 or "
                 "more failed logins, else False.",
         "intro": ["# def is_attack(count): return count >= 5"],
         "hint": "def is_attack(count):  return count >= 5",
         "solution": "def is_attack(count):\n    return count >= 5",
         "check": _c_attack,
         "success": "Your rule fires on a burst of failures -- intrusion detection in one line."}],
     "boss_kind": "flag",
     "boss_data": {
        "prompt": "Review the server log. Flag the lines that signal an attack.",
        "scan_label": "Analyze Log",
        "win": "Intruder isolated. TRACE's footprints lead straight to the door.",
        "items": [
            {"label": "203.0.113.5 - 1 failed login, then success",
             "detail": "log line", "bad": False,
             "reason": "A single typo then a normal login -- ordinary."},
            {"label": "45.66.77.88 - 60 failed logins in 10 seconds",
             "detail": "log line", "bad": True,
             "reason": "A rapid burst of failures -- textbook brute force."},
            {"label": "10.0.0.2 - successful login during office hours",
             "detail": "log line", "bad": False,
             "reason": "A normal employee at a normal time."},
            {"label": "45.66.77.88 - login from a new country at 3am",
             "detail": "log line", "bad": True,
             "reason": "Same attacker IP, impossible travel, odd hour."},
            {"label": "198.51.100.9 - 1 successful login",
             "detail": "log line", "bad": False,
             "reason": "Single clean login -- nothing unusual."}]}},

    # -------------------------------------------------------------- LOCKJAW
    {"boss": "LOCKJAW", "topic": "Malware: Ransomware & Backups",
     "brief": "LOCKJAW is ransomware: it encrypts every file it can reach and "
              "demands payment for the key. The only real defense is preparation. "
              "Learn to detect its damage in code, and prove you know how to "
              "survive an attack without paying a cent.",
     "debrief": "Lesson: backups beat ransomware. An offline, recent backup turns a "
                "catastrophe into an afternoon of restoring -- no ransom required.",
     "intel": [
        {"heading": "What LOCKJAW does",
         "body": "LOCKJAW encrypts your documents and renames them (often adding "
                 "an extension like .locked), then leaves a ransom note. Paying "
                 "rarely returns your files and funds the next attack.",
         "code": "for file in my_documents:\n    encrypt(file)\n"
                 "    rename(file, file + '.locked')"},
        {"heading": "The real defense",
         "body": "You can't un-encrypt the files -- but if you have a recent, "
                 "OFFLINE backup, you just wipe the machine and restore. The attack "
                 "becomes an inconvenience instead of a disaster.",
         "code": None}],
     "lesson": [
        {"heading": "1. Checking how text ends",
         "body": ".endswith() returns True if a string finishes with the given text "
                 "-- perfect for spotting files renamed by ransomware.",
         "code": "\"budget.xlsx.locked\".endswith(\".locked\")   # -> True"},
        {"heading": "2. Counting matches in a list",
         "body": "Loop a list of filenames and count how many end with '.locked' to "
                 "measure the damage.",
         "code": "count = 0\nfor f in files:\n    if f.endswith('.locked'):\n        count += 1"},
        {"heading": "3. A recovery decision",
         "body": "Survival comes down to one question: do you have a backup? A tiny "
                 "function captures the whole strategy.",
         "code": "def can_recover(has_backup):\n    return has_backup is True"}],
     "challenges": [
        {"title": "Detect an encrypted file",
         "goal": "Set `locked` to whether `filename` ends with '.locked' (use "
                 ".endswith()).",
         "seed": lambda: {"filename": "budget.xlsx.locked"},
         "intro": ["# Has this file been encrypted by ransomware?",
                   "# locked = filename.endswith('.locked')"],
         "hint": "locked = filename.endswith(\".locked\")",
         "solution": "locked = filename.endswith(\".locked\")",
         "check": _c_locked,
         "success": "That '.locked' ending is LOCKJAW's calling card."},
        {"title": "Count the hostage files",
         "goal": "`files` is a list of filenames. Count how many end with '.locked' "
                 "into `count`.",
         "seed": lambda: {"files": ["a.docx.locked", "b.jpg", "c.pdf.locked", "d.txt"]},
         "intro": ["# Loop `files`, count the ones ending in '.locked' -> `count`."],
         "hint": "count = 0  /  for f in files:  /  if f.endswith('.locked'):  /  count += 1",
         "solution": "count = 0\nfor f in files:\n    if f.endswith('.locked'):\n        count += 1",
         "check": _c_count,
         "success": "Two files taken hostage -- now you know the scope."},
        {"title": "The recovery rule",
         "goal": "Write `can_recover(has_backup)` that returns True when "
                 "`has_backup` is True, else False. (This is the whole survival plan.)",
         "intro": ["# def can_recover(has_backup): return whether has_backup is True"],
         "hint": "def can_recover(has_backup):  return has_backup is True",
         "solution": "def can_recover(has_backup):\n    return has_backup is True",
         "check": _c_recover,
         "success": "With a backup you recover for free. That's how you beat ransomware."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "LOCKJAW has struck. Show you know how to respond.",
        "win": "Files restored from backup, no ransom paid. LOCKJAW defeated.",
        "rounds": [
            {"q": "Your files are suddenly encrypted with a ransom note. Best move?",
             "options": ["Pay the ransom immediately", "Restore from a clean backup",
                         "Email the attacker to negotiate", "Ignore it and keep working"],
             "answer": 1},
            {"q": "What makes a backup able to survive ransomware?",
             "options": ["Keeping it on the same computer",
                         "Keeping an offline / offsite copy",
                         "Naming the folder 'safe'", "Zipping it"],
             "answer": 1},
            {"q": "How does ransomware usually get in?",
             "options": ["By magic", "A phishing email or malicious download",
                         "Using strong passwords", "Installing security updates"],
             "answer": 1}]}},
    {"boss": "VAULT", "topic": "Passwords: Managers & Passkeys",
     "brief": "VAULT does not crack passwords -- it collects them. One site "
              "leaks, and VAULT tries that same email and password on every "
              "other site you own. Reuse is the door it walks through. Build "
              "a password generator and a vault of your own, then shut that "
              "door.",
     "debrief": "Lesson: one unique password per site means one leak stays "
                "one leak. A manager invents and remembers them for you; a "
                "passkey removes the password from the site entirely.",
     "intel": [
        {"heading": "What VAULT does",
         "body": "VAULT buys a list of leaked email-and-password pairs from "
                 "an old breach, then replays every pair on banks, email and "
                 "shops. This is called credential stuffing. It works for "
                 "one reason: people reuse one password in many places.",
         "code": "for site in every_site:\n"
                 "    try_login(site, leaked_email, leaked_password)"},
        {"heading": "The fix: unique per site",
         "body": "A password manager is a program that invents a long "
                 "random password for each site and stores it for you, "
                 "locked behind one strong master password. You never "
                 "retype them, so they can be long and unmemorable -- "
                 "which is the point.",
         "code": "vault[\"bank.example\"] = make_pw(20)"},
        {"heading": "What a passkey replaces",
         "body": "A passkey removes the shared secret. Your device keeps a "
                 "private key that never leaves it, and proves who you are "
                 "with your fingerprint or PIN. The site stores no password, "
                 "so a breach there leaks nothing VAULT can replay.",
         "code": None}],
     "lesson": [
        {"heading": "1. import random",
         "body": "Python ships with extra toolboxes called modules. The line "
                 "`import random` loads the one that makes unpredictable "
                 "choices. random.choice(seq) then picks one item out of a "
                 "string or a list.",
         "code": "import random\n"
                 "random.choice(\"abc\")   # -> 'a' or 'b' or 'c'"},
        {"heading": "2. Grow a string in a loop",
         "body": "Start with an empty string \"\", then use += to glue one "
                 "more character onto the end each time round the loop. "
                 "range(n) runs the loop n times, so you finish with n "
                 "characters.",
         "code": "pw = \"\"\nfor i in range(4):\n    pw += \"x\"\n"
                 "# pw is now 'xxxx'"},
        {"heading": "3. A dictionary keyed by site name",
         "body": "A dictionary stores pairs: a key you look things up "
                 "by, and the value you get back. Using the site name as "
                 "the key is how a password manager finds the right "
                 "password for the page you are on.",
         "code": "vault = {}\nvault[\"bank.example\"] = \"k7Qm2\"\n"
                 "print(vault[\"bank.example\"])   # -> 'k7Qm2'"}],
     "challenges": [
        {"title": "Pick one random character",
         "goal": "The random toolbox is already loaded for this one. Store "
                 "ONE random character from the string `letters` in a "
                 "variable named `pick`, using random.choice(letters).",
         "seed": lambda: {"random": random,
                          "letters": "abcdefghijklmnopqrstuvwxyz0123456789"},
         "intro": ["# `letters` holds every character a password may use.",
                   "# `random` is already loaded here -- one line is enough:",
                   "# pick = random.choice(...)"],
         "hint": "pick = random.choice(letters)",
         "solution": "pick = random.choice(letters)",
         "check": _c_vault_pick,
         "success": "One unpredictable character -- the atom every generated "
                    "password is built from."},
        {"title": "Generate a whole password",
         "goal": "This time load the toolbox yourself with `import random`. "
                 "Then build a random password of `length` characters "
                 "(length is 16) and store it in `password`: start from an "
                 "empty string and += one random character from `letters` "
                 "each time round a loop over range(length).",
         "seed": lambda: {"letters": "abcdefghijklmnopqrstuvwxyz0123456789",
                          "length": 16},
         "intro": ["# `letters` = the allowed characters, `length` = 16.",
                   "# Line 1:  import random",
                   "# Then: password = \"\"  and a loop over range(length)."],
         "hint": "import random  /  password = \"\"  /  "
                 "for i in range(length):  /  password += "
                 "random.choice(letters)",
         "solution": "import random\npassword = \"\"\n"
                     "for i in range(length):\n"
                     "    password += random.choice(letters)",
         "check": _c_vault_build,
         "success": "Sixteen random characters, made by you -- no human "
                    "would ever have invented that one."},
        {"title": "Fill the vault and look one up",
         "goal": "`sites` lists three sites and `vault` is an empty "
                 "dictionary. Write `make_pw(n)` that returns a random "
                 "password of n characters, then loop the sites storing a "
                 "fresh 14-character password at vault[site]. Finally copy "
                 "the first site's password into `mail_pw`.",
         "seed": lambda: {"vault": {},
                          "sites": ["mail.nullcorp.io", "bank.example",
                                    "shop.example"],
                          "letters": "abcdefghijklmnopqrstuvwxyz0123456789"},
         "intro": ["# vault = {} (empty), sites = three site names.",
                   "# Write make_pw(n) the same way you built `password`,",
                   "# then: for site in sites:  vault[site] = make_pw(14)",
                   "# Last line: mail_pw = vault[\"mail.nullcorp.io\"]"],
         "hint": "def make_pw(n):  build n random characters and return "
                 "them. Then  for site in sites:  vault[site] = make_pw(14)",
         "solution": "import random\ndef make_pw(n):\n    pw = \"\"\n"
                     "    for i in range(n):\n"
                     "        pw += random.choice(letters)\n"
                     "    return pw\n"
                     "for site in sites:\n"
                     "    vault[site] = make_pw(14)\n"
                     "mail_pw = vault[\"mail.nullcorp.io\"]",
         "check": _c_vault_store,
         "success": "Three sites, three different passwords, each findable "
                    "by name. You have written a password manager."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "VAULT tests whether you understand why reuse is the real "
                  "danger.",
        "win": "Every account holds a different key. VAULT's stolen list "
               "opens nothing.",
        "rounds": [
            {"q": "A shop you once used is breached. Why does VAULT now "
                  "care about your bank?",
             "options": ["Banks and shops share one login system",
                         "If you reused that password, it opens the bank too",
                         "Breaches always spread across the network",
                         "Your bank stores its passwords at the shop"],
             "answer": 1},
            {"q": "What is the main job of a password manager?",
             "options": ["To shorten your passwords so you can type them",
                         "To email your passwords to you each month",
                         "To invent and store a different password per site",
                         "To hide your internet connection"],
             "answer": 2},
            {"q": "What does a passkey replace?",
             "options": ["The shared password stored by the website",
                         "Your internet connection",
                         "The website's encryption",
                         "The need to own a phone or laptop"],
             "answer": 0}]}},
    {"boss": "WHISPER", "topic": "Social Engineering: The Phone Call",
     "brief": "WHISPER never touches your computer. WHISPER phones you, "
              "sounds calm and official, and talks YOU into opening the "
              "door. This is called vishing -- voice phishing, an attack "
              "delivered by phone. Learn to hear the script behind the "
              "friendly voice, count its warning signs in Python, and end "
              "the call the one way that always works.",
     "debrief": "Lesson: a phone call proves nothing about who is calling. "
                "When a caller wants a code, a payment or a password, hang "
                "up and call the company back on a number you looked up "
                "yourself.",
     "intel": [
        {"heading": "What WHISPER does",
         "body": "WHISPER calls you pretending to be someone you would "
                 "trust -- your bank, your IT helpdesk, a delivery firm. "
                 "That invented identity is called a pretext: a believable "
                 "story that explains why this stranger needs something "
                 "from you right now. The words are rehearsed, and the "
                 "same lines come up call after call.",
         "code": "script = [\n"
                 "    \"Hello, this is IT support.\",\n"
                 "    \"Your account will be suspended today.\",\n"
                 "    \"Please read me the code we sent you.\",\n"
                 "]"},
        {"heading": "Why urgency plus authority works",
         "body": "Authority makes you want to cooperate: people help "
                 "someone who sounds like the boss or the bank. Urgency "
                 "removes your thinking time -- with ten seconds to act, "
                 "you cannot stop and check. Put the two together and a "
                 "careful person hands over a code they would never type "
                 "into a website. It is not stupidity. It is the script "
                 "working exactly as designed.",
         "code": None},
        {"heading": "The one defense that always works",
         "body": "You cannot tell who is really on a phone line. The "
                 "number shown on your screen (the caller ID) can be "
                 "faked, and a voice can be copied. So do not try to "
                 "judge the caller. Say you will call back, hang up, then "
                 "dial the number printed on your card, your bill or the "
                 "company's own website -- never a number the caller gave "
                 "you. A real employee will not mind. WHISPER cannot "
                 "survive it.",
         "code": None}],
     "lesson": [
        {"heading": "1. `in` asks 'is this inside?'",
         "body": "The word `in` checks whether one thing sits inside "
                 "another. It works on a string (is this word inside this "
                 "sentence?) and on a list (is this item in this list?). "
                 "It answers True or False. Adding .lower() to text makes "
                 "a copy in all lowercase first, so SUSPENDED and "
                 "suspended both match.",
         "code": "\"code\" in \"read me the code\"     # -> True\n"
                 "\"act now\" in [\"act now\", \"hi\"]    # -> True\n"
                 "\"urgent\" in \"URGENT\".lower()     # -> True"},
        {"heading": "2. Count the matches in a list",
         "body": "To measure how bad a call is, start a counter at 0 and "
                 "add 1 every time an item passes your test. The counter "
                 "keeps its value from one loop turn to the next, so at "
                 "the end it holds the total. `count += 1` is shorthand "
                 "for 'add one to count'.",
         "code": "said = [\"act now\", \"hello\"]\n"
                 "flags = [\"act now\", \"do not tell anyone\"]\n"
                 "count = 0\n"
                 "for p in said:\n"
                 "    if p in flags:\n"
                 "        count += 1\n"
                 "count      # -> 1"},
        {"heading": "3. A function that returns a number",
         "body": "A function can hand back a number instead of True or "
                 "False. That number is a risk score: the higher it is, "
                 "the more warning signs the call had. Doing the counting "
                 "inside a function means you can score any call with one "
                 "short line.",
         "code": "def risk(phrases):\n"
                 "    flags = [\"act now\"]\n"
                 "    total = 0\n"
                 "    for p in phrases:\n"
                 "        if p in flags:\n"
                 "            total += 1\n"
                 "    return total\n\n"
                 "risk([\"act now\"])   # -> 1"}],
     "challenges": [
        {"title": "Hear the scare phrase",
         "goal": "`call` holds one sentence the caller said. Set `scary` "
                 "to whether the word 'suspended' appears in it. Write "
                 "call.lower() so the shouted capitals still match.",
         "seed": lambda: {"call":
                          "This is IT support. Your account will be "
                          "SUSPENDED today."},
         "intro": ["# `call` is one line the caller said out loud.",
                   "# Try:  \"suspended\" in call.lower()",
                   "# Store that True/False answer in `scary`."],
         "hint": "Start the line with  scary =  and put the whole "
                 "\"suspended\" in call.lower() test after it.",
         "solution": "scary = \"suspended\" in call.lower()",
         "check": _c_whisper_scary,
         "success": "Caught it. 'Suspended' is a threat, and a threat is "
                    "there to stop you thinking."},
        {"title": "Count the red flags",
         "goal": "`said` is a list of the phrases from one call. "
                 "`red_flags` lists the phrases known to be warning "
                 "signs. Loop over `said` and count how many of its "
                 "phrases are in `red_flags`. Store the total in `count`.",
         "seed": lambda: {"said": ["this is it support",
                                   "read me the code",
                                   "do not tell anyone",
                                   "have a nice day"],
                          "red_flags": ["this is it support",
                                        "read me the code",
                                        "do not tell anyone",
                                        "act now"]},
         "intro": ["# `said` = what the caller said, phrase by phrase.",
                   "# `red_flags` = the phrases we already distrust.",
                   "# Start count = 0, loop `said`, add 1 for each match."],
         "hint": "count = 0  /  for p in said:  /  if p in red_flags:  /  "
                 "count += 1",
         "solution": "count = 0\nfor p in said:\n    if p in red_flags:\n"
                     "        count += 1",
         "check": _c_whisper_count,
         "success": "Three red flags in one call. Only 'have a nice day' "
                    "was innocent."},
        {"title": "Write the risk score",
         "goal": "Write `score(call_phrases)` that returns how many "
                 "phrases in the list `call_phrases` are red flags. "
                 "Inside the function build the list flags = ['read me "
                 "the code', 'do not hang up', 'act now'], count the "
                 "matches, and return the total.",
         "intro": ["# def score(call_phrases):",
                   "#   flags = ['read me the code', 'do not hang up',",
                   "#            'act now']",
                   "#   count the phrases that are in flags, return it"],
         "hint": "Same counting loop as before, wrapped in a def -- set "
                 "total = 0 first, and finish with return total.",
         "solution": "def score(call_phrases):\n"
                     "    flags = ['read me the code', 'do not hang up',"
                     " 'act now']\n"
                     "    total = 0\n"
                     "    for p in call_phrases:\n"
                     "        if p in flags:\n"
                     "            total += 1\n"
                     "    return total",
         "check": _c_whisper_score,
         "success": "Your own risk scorer. Any call, one number, no "
                    "guessing."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "WHISPER is on the line, calm and in a hurry. Answer "
                  "carefully.",
        "win": "You hung up and called back on your own number. WHISPER "
               "was talking to a dead line.",
        "rounds": [
            {"q": "A caller says he is your bank and needs the code they "
                  "texted you. What do you do?",
             "options": ["Read him the code, he already knew your name",
                         "Hang up and call the number on your bank card",
                         "Ask him to text the code again first",
                         "Read only the first three digits"],
             "answer": 1},
            {"q": "Why does a caller push you to act in the next minute?",
             "options": ["Phone lines are expensive",
                         "Their computer times out",
                         "Hurry stops you pausing to check",
                         "It is a legal requirement"],
             "answer": 2},
            {"q": "The number on your screen shows your bank's real "
                  "number. What does that prove?",
             "options": ["Nothing -- caller ID can be faked",
                         "It is definitely the bank",
                         "The call is recorded",
                         "The caller works in your branch"],
             "answer": 0}]}},
    # --------------------------------------------------------------- FORGER
    {"boss": "FORGER", "topic": "Web Security: Sessions & Cookies",
     "brief": "FORGER never steals a password. When you log in, the site "
              "hands your browser a session token -- a long secret string "
              "that means 'this is the person who logged in'. FORGER copies "
              "that token, or tricks your browser into sending it from his "
              "own page. Learn to measure a token and write the check that "
              "catches a fake.",
     "debrief": "Lesson: a session token IS your identity, so it must be "
                "long, random, and compared exactly. A site must also "
                "confirm that a request came from its own page.",
     "intel": [
        {"heading": "What FORGER does",
         "body": "After you log in, the site sends back a session token and "
                 "your browser keeps it in a cookie -- a small piece of text "
                 "the browser sends along with every later request. FORGER "
                 "copies that token off a machine and sends it from his own. "
                 "The site sees a valid token and answers as if he were "
                 "you. No password needed.",
         "code": "stolen = \"9f2c7a1e4b8d3c6a\"   # copied session token\n"
                 "request(\"/account\", cookie=stolen)   # site says 'you'"},
        {"heading": "The second trick: CSRF",
         "body": "CSRF is short for cross-site request forgery. FORGER hides "
                 "a form on his own page. When you visit, your browser sends "
                 "that form to your bank -- and attaches your bank cookie, "
                 "because attaching cookies is what browsers do. The bank "
                 "sees your token and obeys. You never clicked anything.",
         "code": "<form action=\"bank.example/transfer\" method=\"post\">\n"
                 "  <input name=\"to\" value=\"FORGER\">   <!-- sent -->"},
        {"heading": "The fixes",
         "body": "Make tokens long and unpredictable, so guessing is "
                 "hopeless. Compare them exactly. Then put a second secret "
                 "-- a CSRF token -- inside the site's own page, and refuse "
                 "any request that arrives without it. FORGER's page is not "
                 "allowed to read it.",
         "code": None}],
     "lesson": [
        {"heading": "1. == compares two strings exactly",
         "body": "== asks 'are these two values the same?' and hands back "
                 "True or False. For text the answer is exact: every "
                 "character must match, and a capital letter counts as "
                 "different from a small one. That strictness is what you "
                 "want when checking a token.",
         "code": "\"abc\" == \"abc\"   # -> True\n"
                 "\"abc\" == \"abC\"   # -> False"},
        {"heading": "2. len() measures the token",
         "body": "len() counts the characters in a string. Length is what "
                 "keeps a token safe: a 4-character token can be guessed, a "
                 "32-character random one cannot. Below, the random module "
                 "(a toolbox that ships with Python) picks characters one "
                 "at a time. Real sites use the secrets module -- the same "
                 "idea, built so the picks cannot be predicted.",
         "code": "import random\n"
                 "tok = \"\"\n"
                 "for i in range(32):\n"
                 "    tok += random.choice(\"0123456789abcdef\")\n"
                 "len(tok)   # -> 32"},
        {"heading": "3. `and` joins two rules into one answer",
         "body": "Put `and` between two tests and the result is True only "
                 "when BOTH are True. If either side is False, the whole "
                 "answer is False. Here a token has to match exactly AND be "
                 "long enough.",
         "code": "def is_valid(token, expected):\n"
                 "    return token == expected and len(token) >= 16"}],
     "challenges": [
        {"title": "Compare two tokens",
         "goal": "`sent_token` arrived with a request. `real_token` is the "
                 "one the site handed out. Using ==, store whether they are "
                 "equal in a variable named `same`.",
         "seed": lambda: {"sent_token": "9f2c7a1e4b8d3c6b",
                          "real_token": "9f2c7a1e4b8d3c6a"},
         "intro": ["# sent_token came in with a request.",
                   "# real_token is the one the site handed out.",
                   "# == asks: are these two exactly the same?"],
         "hint": "Put == between the two names, and store the True/False "
                 "answer under the name same.",
         "solution": "same = sent_token == real_token",
         "check": _c_forger_same,
         "success": "One character differs, so same is False -- the forged "
                    "token is turned away."},
        {"title": "Measure the token",
         "goal": "Count the characters in `token` and store that number in "
                 "a variable named `size`, using len().",
         "seed": lambda: {"token": "7f3a9c2e8b1d4a6f5e0c9b8a7d6e5f4c"},
         "intro": ["# `token` is a real session token. How long is it?",
                   "# len(...) counts the characters in a string.",
                   "# Store that count under the name size."],
         "hint": "len(token) gives the count. Save it as size.",
         "solution": "size = len(token)",
         "check": _c_forger_size,
         "success": "32 random characters. There are more possible tokens "
                    "than there are grains of sand on Earth."},
        {"title": "Write the token validator",
         "goal": "Write a function `is_valid(token, expected)` that returns "
                 "True only when `token` equals `expected` AND `token` is "
                 "at least 16 characters long. In every other case it "
                 "returns False.",
         "intro": ["# The site calls this on every request that arrives.",
                   "# Answer True only when BOTH rules hold:",
                   "#   1) token is exactly equal to expected",
                   "#   2) token is 16 characters or longer"],
         "hint": "One return line with `and` in the middle: the == test on "
                 "the left, the len(...) >= 16 test on the right.",
         "solution": "def is_valid(token, expected):\n"
                     "    return token == expected and len(token) >= 16",
         "check": _c_forger_valid,
         "success": "Exact match AND real length -- FORGER's short guesses "
                    "and near-misses both bounce."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "FORGER holds a stolen cookie. Show that you know how "
                  "sessions are really protected.",
        "win": "Session locked down. FORGER's stolen token is now worthless.",
        "rounds": [
            {"q": "What does a session token do after you log in?",
             "options": ["It stores your password inside the page",
                         "Whoever sends it is treated as the logged-in user",
                         "It makes the website load faster",
                         "It hides your screen from other people"],
             "answer": 1},
            {"q": "Why must session tokens be long and randomly generated?",
             "options": ["So they look impressive",
                         "So the server can sort them alphabetically",
                         "So an attacker cannot guess one or count up to a "
                         "real one",
                         "So they fit inside an email"],
             "answer": 2},
            {"q": "What stops a hidden form on an attacker's page from "
                  "acting as you?",
             "options": ["Renaming the cookie",
                         "Choosing a longer password",
                         "Checking a secret token that only the site's own "
                         "page contains",
                         "Turning off images in the browser"],
             "answer": 2}]}},
    {"boss": "SIEVE", "topic": "Secure Coding: Allow-lists",
     "brief": "SIEVE is NULL's input smuggler. It studies the list of "
              "things a program refuses -- the 'block-list' -- and then "
              "sends one thing nobody thought to write down. Your job is "
              "to flip the logic around: stop naming what is forbidden, "
              "and name only what is permitted.",
     "debrief": "Lesson: a block-list can always be slipped past, because "
                "you cannot list every bad thing. An allow-list names the "
                "few good values and refuses everything else by default.",
     "intel": [
        {"heading": "What SIEVE does",
         "body": "A block-list is a list of banned values. The program "
                 "checks input against it and rejects a match. SIEVE "
                 "sends something that is NOT on the list -- a different "
                 "spelling, a capital letter, a file type nobody "
                 "considered -- and walks straight through the gate.",
         "code": "banned = ['exe', 'bat']\n"
                 "if user_type not in banned:\n"
                 "    accept(upload)   # 'EXE' and 'cmd' sail right in"},
        {"heading": "The fix: name the good, refuse the rest",
         "body": "An allow-list is the mirror image. You write down the "
                 "handful of values you actually support, and anything "
                 "not on that list is refused -- including things you "
                 "never imagined. The list of good values is short, and "
                 "you already know what is on it.",
         "code": "allowed = ['png', 'jpg', 'gif']\n"
                 "if user_type in allowed:\n"
                 "    accept(upload)   # everything else is refused"},
        {"heading": "Fail closed, not open",
         "body": "When your code meets something it does not recognize, "
                 "it must pick a side. 'Fail open' means letting it "
                 "through when unsure. 'Fail closed' means refusing it "
                 "when unsure. Fail closed is the safe default, and it "
                 "is what you will build in the lab.",
         "code": None}],
     "lesson": [
        {"heading": "1. A list, and the `in` test",
         "body": "A list is several values written between square "
                 "brackets, separated by commas. The word `in` asks 'is "
                 "this value one of them?' and hands back True or False. "
                 "That one question is an allow-list check.",
         "code": "allowed = ['png', 'jpg', 'gif']\n"
                 "'png' in allowed    # -> True\n"
                 "'exe' in allowed    # -> False"},
        {"heading": "2. Keeping only what is allowed",
         "body": "To sift a whole list, start an empty list with = [], "
                 "walk the items one at a time with a for-loop, and use "
                 ".append(item) to add the ones that pass. Whatever is "
                 "never appended is quietly dropped.",
         "code": "safe = []\n"
                 "for f in uploads:\n"
                 "    if f in allowed:\n"
                 "        safe.append(f)"},
        {"heading": "3. try / except: catching an error",
         "body": "A dictionary stores values under keys, and asking for "
                 "a key it does not have raises an error named KeyError, "
                 "which stops your program. `try:` runs the risky line, "
                 "and `except KeyError:` runs instead when that error "
                 "happens -- so you can refuse politely rather than "
                 "crash. No extra module is needed for any of this.",
         "code": "pages = {'home': 'Welcome'}\n"
                 "try:\n"
                 "    print(pages['boom'])\n"
                 "except KeyError:\n"
                 "    print('Access denied')"}],
     "challenges": [
        {"title": "Ask the allow-list",
         "goal": "`allowed` lists the file types this site accepts. Set "
                 "`is_allowed` to whether `ext` is one of them, using "
                 "the `in` test.",
         "seed": lambda: {"ext": "exe",
                          "allowed": ["png", "jpg", "gif"]},
         "intro": ["# `ext` = 'exe'  and  `allowed` = ['png','jpg','gif']",
                   "# Try:  ext in allowed   then store it in is_allowed."],
         "hint": "The answer has the shape:  is_allowed = <value> in "
                 "<list>.",
         "solution": "is_allowed = ext in allowed",
         "check": _c_sieve_in,
         "success": "'exe' is not on the list, so is_allowed is False. "
                    "Nothing had to predict that .exe was dangerous."},
        {"title": "Sift the uploads",
         "goal": "`uploads` holds the file type of every uploaded file. "
                 "Build a list named `safe` holding only the types that "
                 "appear in `allowed`.",
         "seed": lambda: {"uploads": ["png", "exe", "jpg", "bat", "gif"],
                          "allowed": ["png", "jpg", "gif"]},
         "intro": ["# Keep only the uploads whose type is in `allowed`.",
                   "# Start:  safe = []   then loop and safe.append(f)."],
         "hint": "Four lines: safe = [], then a `for f in uploads:` "
                 "line, then an `if` line using `in`, then the "
                 ".append(f) line indented under the if.",
         "solution": "safe = []\nfor f in uploads:\n    if f in allowed:\n"
                     "        safe.append(f)",
         "check": _c_sieve_filter,
         "success": "Three good files kept, 'exe' and 'bat' dropped -- "
                    "and you never had to name them."},
        {"title": "Fail closed",
         "goal": "Write `open_page(name)`. Inside it, make a dictionary "
                 "`pages` holding 'home' -> 'Welcome' and 'help' -> "
                 "'How to'. Then `try:` returning pages[name], and on "
                 "`except KeyError:` return the text 'Access denied'.",
         "intro": ["# Known page names open. Every other name is refused.",
                   "# Shape:  def open_page(name):  ->  pages = {...}",
                   "#         then try: ... / except KeyError: ..."],
         "hint": "Indent `try:` and `except KeyError:` inside the "
                 "function, and put a `return` line under each of them.",
         "solution": "def open_page(name):\n"
                     "    pages = {'home': 'Welcome', 'help': 'How to'}\n"
                     "    try:\n"
                     "        return pages[name]\n"
                     "    except KeyError:\n"
                     "        return 'Access denied'",
         "check": _c_sieve_safe,
         "success": "Known pages open; anything else is refused instead "
                    "of crashing. That is failing closed."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "SIEVE tests whether you really trust your own gate.",
        "win": "Every unknown value refused. SIEVE has nothing left to "
               "smuggle in.",
        "rounds": [
            {"q": "A form should accept only a US state code. Safer?",
             "options": ["Block a list of known-bad codes",
                         "Allow only the 50 valid state codes",
                         "Accept anything and clean it later",
                         "Trust whatever the browser sends"],
             "answer": 1},
            {"q": "Why do block-lists keep failing in practice?",
             "options": ["They run too slowly",
                         "They need a database",
                         "You cannot list every bad value, so a new "
                         "variation slips through",
                         "They work on numbers only"],
             "answer": 2},
            {"q": "Your code meets a value it does not recognize. "
                  "'Fail closed' means:",
             "options": ["Let it through and write a log line",
                         "Crash the whole program",
                         "Ask the user to decide",
                         "Refuse it by default"],
             "answer": 3}]}},
    {"boss": "BEACON", "topic": "Networks: Wi-Fi & Evil Twins",
     "brief": "BEACON sits in the corner of a cafe with a laptop, "
              "broadcasting a Wi-Fi network that copies the cafe's name "
              "exactly -- but with no password. Phones join whichever "
              "signal is strongest, so half the room lands on BEACON "
              "instead. Learn to read a Wi-Fi scan in Python, pick out the "
              "unprotected networks, and unmask the twin.",
     "debrief": "Lesson: 'open' means no password and no scrambling of the "
                "radio signal, so anyone nearby can read the traffic. A "
                "duplicate name with no password is the classic evil twin "
                "-- and HTTPS is what still protects you when you cannot "
                "trust the network.",
     "intel": [
        {"heading": "What BEACON does",
         "body": "Every Wi-Fi network broadcasts a name (the SSID) and a "
                 "security setting. BEACON broadcasts the SAME name as the "
                 "real cafe network, with security set to open, from a "
                 "stronger antenna. Your phone remembers names, not "
                 "hardware, so it connects without complaint -- and every "
                 "request now travels through BEACON's laptop first.",
         "code": "fake = {\"name\": \"Cafe_WiFi\", \"security\": \"open\"}\n"
                 "broadcast(fake)   # same name, no password, louder"},
        {"heading": "Open vs WPA2 and WPA3",
         "body": "WPA2 and WPA3 are the two modern ways a network scrambles "
                 "the radio signal between your device and the router, "
                 "using the password as the key. WPA3 is the newer, "
                 "stronger one. 'Open' means no password and no scrambling "
                 "at all: your data crosses the room as plain radio that "
                 "anyone with the right software can pick up.",
         "code": None},
        {"heading": "Why HTTPS is what saves you",
         "body": "Even on BEACON's network, a site whose address starts "
                 "with https:// encrypts the page between your browser and "
                 "that site. BEACON can see WHICH site you visited, but not "
                 "your password or your messages. Avoid sending anything "
                 "private over a page without the https:// padlock, and "
                 "prefer your phone's own hotspot in a cafe.",
         "code": None}],
     "lesson": [
        {"heading": "1. A network is a dictionary",
         "body": "A dictionary stores values under labels. Square brackets "
                 "pull one value out by its label. Here one scanned network "
                 "becomes one dictionary with a 'name' and a 'security' "
                 "setting.",
         "code": "net = {\"name\": \"Cafe_WiFi\", \"security\": \"open\"}\n"
                 "net[\"name\"]      # -> 'Cafe_WiFi'"},
        {"heading": "2. A scan is a list of dictionaries",
         "body": "Nearby networks arrive as a list, one dictionary per "
                 "network. Loop over the list, test each one, and .append() "
                 "the ones you care about to a new list you started as [].",
         "code": "open_names = []\nfor n in scan:\n"
                 "    if n[\"security\"] == \"open\":\n"
                 "        open_names.append(n[\"name\"])"},
        {"heading": "3. Two conditions joined by and",
         "body": "`and` gives True only when BOTH sides are True. That is "
                 "the evil-twin test exactly: the name matches a network "
                 "you trust, AND the security is open.",
         "code": "same_name = net[\"name\"] == \"Cafe_WiFi\"\n"
                 "no_password = net[\"security\"] == \"open\"\n"
                 "same_name and no_password   # True only if BOTH"}],
     "challenges": [
        {"title": "Read one network's security",
         "goal": "`net` is a dictionary describing one nearby network. Read "
                 "its 'security' value with square brackets and store it in "
                 "a variable named `sec`.",
         "seed": lambda: {"net": {"name": "Cafe_WiFi", "security": "open",
                                  "signal": 91}},
         "intro": ["# `net` = {'name': 'Cafe_WiFi', 'security': 'open',",
                   "#          'signal': 91}",
                   "# Store the 'security' value in `sec`."],
         "hint": "Square brackets pull one value out: net['name'] gives the "
                 "name. Do the same with 'security'.",
         "solution": "sec = net['security']",
         "check": _c_beacon_sec,
         "success": "'open' means no password and no scrambling on the air."},
        {"title": "List the unprotected networks",
         "goal": "`scan` is a list of network dictionaries. Loop over it "
                 "and collect the 'name' of every network whose 'security' "
                 "is 'open' into a list called `open_names`.",
         "seed": lambda: {"scan": [
             {"name": "Cafe_WiFi", "security": "wpa2"},
             {"name": "Cafe_WiFi", "security": "open"},
             {"name": "City_Free_WiFi", "security": "open"},
             {"name": "HomeNet_5G", "security": "wpa3"}]},
         "intro": ["# `scan` lists 4 nearby networks, each a dictionary.",
                   "# Start with open_names = []  then loop over `scan`.",
                   "# Append n['name'] when that network is open."],
         "hint": "open_names = []  /  for n in scan:  /  if the security "
                 "equals 'open'  /  open_names.append(...)",
         "solution": "open_names = []\nfor n in scan:\n"
                     "    if n['security'] == 'open':\n"
                     "        open_names.append(n['name'])",
         "check": _c_beacon_open,
         "success": "Two open networks -- one borrows the cafe's own name."},
        {"title": "Unmask the evil twin",
         "goal": "Write a function `is_twin(net, real_name)` that returns "
                 "True when net's 'name' equals `real_name` AND net's "
                 "'security' is 'open', and False otherwise.",
         "intro": ["# def is_twin(net, real_name):",
                   "#     return <name matches> and <security is open>",
                   "# One return line joined by `and` is enough."],
         "hint": "Two tests joined by `and`: the name equals real_name, and "
                 "the security equals 'open'.",
         "solution": "def is_twin(net, real_name):\n"
                     "    return net['name'] == real_name and "
                     "net['security'] == 'open'",
         "check": _c_beacon_twin,
         "success": "Same name, no password -- that is the fake, and you "
                    "named it."}],
     "boss_kind": "flag",
     "boss_data": {
        "prompt": "You are in the cafe. The real network is 'Cafe_WiFi', "
                  "WPA2, password printed on the receipt. Flag the risky "
                  "networks, then scan.",
        "scan_label": "Scan The Air",
        "win": "Evil twin exposed and the bait ignored. BEACON gets nothing.",
        "items": [
            {"label": "Cafe_WiFi",
             "detail": "WPA2 -- password on the receipt", "bad": False,
             "reason": "The genuine network: password-protected and "
                       "scrambled."},
            {"label": "Cafe_WiFi",
             "detail": "open -- no password, strongest signal", "bad": True,
             "reason": "Same name as the real one but open: the evil twin. "
                       "Its loud signal is the bait."},
            {"label": "HomeNet_5G",
             "detail": "WPA3 -- a neighbor's home network", "bad": False,
             "reason": "Someone else's protected network -- not a threat."},
            {"label": "Free_HighSpeed_WiFi", "detail": "open -- no password",
             "bad": True,
             "reason": "An inviting name with no password and no "
                       "scrambling. Anyone nearby can read what you send."},
            {"label": "TP-LINK_9C4A",
             "detail": "WPA2 -- a router's default name", "bad": False,
             "reason": "A dull factory name, but password-protected and "
                       "scrambled."}]}},
    {"boss": "BASTION", "topic": "Networks: Firewall Rules",
     "brief": "BASTION guards NULL's servers with a firewall -- a list of "
              "rules that decides which traffic gets in. The firewall reads "
              "that list from the top down and stops at the FIRST rule that "
              "matches. BASTION hides a sloppy allow rule near the top and "
              "leaves no catch-all at the bottom. Learn to read the list in "
              "order, find the first match in Python, and close the hole "
              "BASTION left open.",
     "debrief": "Lesson: a firewall is an ordered list, the first matching "
                "rule wins, and a final deny-everything rule is what makes "
                "it safe.",
     "intel": [
        {"heading": "What BASTION does",
         "body": "A firewall is a list of rules. Each rule names some "
                 "traffic (here, a port number -- the numbered door a "
                 "service listens on) and an action: allow or deny. The "
                 "firewall walks the list from the top and obeys the FIRST "
                 "rule that matches, then stops looking. BASTION slips a "
                 "broad allow rule ABOVE the deny that was meant to block "
                 "it. The deny is still in the list, but it is never "
                 "reached.",
         "code": "rules = [\n"
                 "    {'port': 23, 'action': 'allow'},  # BASTION's rule\n"
                 "    {'port': 23, 'action': 'deny'},   # never reached\n"
                 "]"},
        {"heading": "The missing last rule",
         "body": "The second hole is what happens when NOTHING matches. If "
                 "the firewall shrugs and lets that traffic through, every "
                 "port nobody thought about is open. The fix is one rule at "
                 "the very bottom that denies everything left over -- it is "
                 "called default-deny. Traffic then gets in only when some "
                 "rule above it said yes on purpose.",
         "code": None}],
     "lesson": [
        {"heading": "1. A list of dictionaries",
         "body": "A dictionary holds labelled values: rule['port'] gives "
                 "the port number, rule['action'] gives 'allow' or 'deny'. "
                 "A firewall is a list of those dictionaries, and the order "
                 "of the list is the order they are read.",
         "code": "rules = [{'port': 443, 'action': 'allow'},\n"
                 "         {'port': 22, 'action': 'deny'}]\n"
                 "rules[0]['action']    # -> 'allow'"},
        {"heading": "2. Looping and stopping early",
         "body": "A for loop visits each rule in order. Once you find the "
                 "one you want, the word `break` leaves the loop right "
                 "away, so later rules are never looked at. Stopping at "
                 "the first hit IS first-match-wins.",
         "code": "for r in rules:\n"
                 "    if r['port'] == port:\n"
                 "        first_match = r\n"
                 "        break"},
        {"heading": "3. return ends a function instantly",
         "body": "Inside a function, `return` hands back an answer and "
                 "stops the function on the spot -- no break needed. A "
                 "line written AFTER the loop only runs when the loop "
                 "finished without returning, which makes it the right "
                 "place for the default answer.",
         "code": "def decide(port, rules):\n"
                 "    for r in rules:\n"
                 "        if r['port'] == port:\n"
                 "            return r['action']\n"
                 "    return 'deny'      # nothing matched"}],
     "challenges": [
        {"title": "Read the top rule",
         "goal": "`rules` is a list of dictionaries, read top to bottom. "
                 "rules[0] is the first one. Take its 'action' value and "
                 "store that text in a variable named `first_action`.",
         "seed": lambda: {"rules": [{"port": 443, "action": "allow"},
                                    {"port": 22, "action": "deny"},
                                    {"port": 3306, "action": "deny"}]},
         "intro": ["# `rules` is the firewall, read from the top down.",
                   "# Try:  rules[0]        then:  rules[0]['port']",
                   "# Now store rules[0]'s 'action' in `first_action`."],
         "hint": "first_action = rules[0][\"action\"]",
         "solution": "first_action = rules[0][\"action\"]",
         "check": _c_bastion_first,
         "success": "The top rule allows port 443 -- and the top rule is "
                    "the first one the firewall ever reads."},
        {"title": "Find the first matching rule",
         "goal": "Set `first_match` to None. Then loop over `rules`, and "
                 "when a rule's 'port' equals `port`, put that whole rule "
                 "into `first_match` and `break` out of the loop.",
         "seed": lambda: {"port": 22,
                          "rules": [{"port": 443, "action": "allow"},
                                    {"port": 22, "action": "deny"},
                                    {"port": 22, "action": "allow"}]},
         "intro": ["# `port` = 22, and TWO rules mention port 22.",
                   "# Only the first one counts -- break once you hit it.",
                   "# Start with:  first_match = None"],
         "hint": "first_match = None  /  for r in rules:  /  "
                 "if r['port'] == port:  /  first_match = r  /  break",
         "solution": "first_match = None\nfor r in rules:\n"
                     "    if r[\"port\"] == port:\n"
                     "        first_match = r\n        break",
         "check": _c_bastion_match,
         "success": "You stopped on the deny rule and never saw the allow "
                    "below it. That is first-match-wins in your own code."},
        {"title": "Write the firewall decision",
         "goal": "Write a function `decide(port, rules)`. Loop over "
                 "`rules`, and the moment a rule's 'port' equals `port`, "
                 "return that rule's 'action'. After the loop, return "
                 "'deny' so anything unmatched is blocked.",
         "seed": lambda: {"rules": [{"port": 443, "action": "allow"},
                                    {"port": 22, "action": "deny"}]},
         "intro": ["# def decide(port, rules):",
                   "#   loop the rules, return the first matching action,",
                   "#   then after the loop return 'deny' (the default).",
                   "# Test it:  decide(22, rules)   decide(80, rules)"],
         "hint": "def decide(port, rules):  /  for r in rules:  /  "
                 "if r['port'] == port:  /  return r['action']  /  "
                 "return 'deny'",
         "solution": "def decide(port, rules):\n    for r in rules:\n"
                     "        if r[\"port\"] == port:\n"
                     "            return r[\"action\"]\n"
                     "    return \"deny\"",
         "check": _c_bastion_decide,
         "success": "First match wins, and anything unknown is denied. "
                    "That last line is the whole reason a firewall is "
                    "safe -- BASTION's hole is closed."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "BASTION tests whether you really understand rule order.",
        "win": "Rules reordered, default-deny in place. BASTION is shut.",
        "rounds": [
            {"q": "A firewall reads its rules from the top down. Which "
                  "rule decides what happens to a packet?",
             "options": ["The last rule that matches",
                         "The first rule that matches",
                         "The shortest rule in the list",
                         "A matching rule picked at random"],
             "answer": 1},
            {"q": "'allow port 23' sits ABOVE 'deny port 23'. What "
                  "happens to traffic on port 23?",
             "options": ["It is denied, because deny always wins",
                         "It is allowed -- the allow rule matched first",
                         "Both rules run and cancel each other out",
                         "The firewall reports an error"],
             "answer": 1},
            {"q": "What should the very last rule in the list be?",
             "options": ["Allow everything, to avoid breaking things",
                         "Nothing -- an empty ending is fine",
                         "Deny everything not already allowed",
                         "A copy of the first rule"],
             "answer": 2}]}},
    {"boss": "HERALD", "topic": "Cryptography: Encoding vs Encryption",
     "brief": "HERALD is NULL's courier. It carries stolen data around in "
              "base64 -- text that looks like scrambled nonsense -- and "
              "tells everyone the data is 'encrypted'. It is not. Base64 "
              "needs no key, so anyone at all can undo it. Learn to encode, "
              "decode, and prove to HERALD that its disguise is only a "
              "disguise.",
     "debrief": "Lesson: encoding is a costume, encryption is a lock. "
                "Base64 and hex can be reversed by anyone in one line, so "
                "they never protect a secret -- only a real key does that.",
     "intel": [
        {"heading": "What HERALD does",
         "body": "HERALD takes data it has stolen and runs it through "
                 "base64. Base64 rewrites any data using 64 safe characters "
                 "(A-Z, a-z, 0-9, + and /). The result looks like gibberish, "
                 "so careless people assume it is protected and stop "
                 "worrying about it.",
         "code": "import base64\n"
                 "hidden = base64.b64encode(b\"pass=hunter2\")\n"
                 "# -> b'cGFzcz1odW50ZXIy'   looks safe. It is not."},
        {"heading": "Why the disguise fails",
         "body": "Encryption needs a secret key: without the key you cannot "
                 "get the original back. Base64 has no key at all -- the "
                 "recipe is public and built into Python. One line undoes "
                 "it, which is why storing passwords 'in base64' is a real "
                 "and famous mistake.",
         "code": "base64.b64decode(b\"cGFzcz1odW50ZXIy\")\n"
                 "# -> b'pass=hunter2'   no key was needed"},
        {"heading": "So what is base64 for",
         "body": "It has an honest job: carrying binary data (images, "
                 "files) through channels that only accept plain text, like "
                 "email. It is a delivery format, never a lock. When you "
                 "meet base64 in the wild, read it -- do not trust it.",
         "code": None}],
     "lesson": [
        {"heading": "1. import brings in a toolbox",
         "body": "Python ships with ready-made toolboxes called modules. "
                 "Writing `import base64` loads the base64 toolbox. After "
                 "that you reach a tool inside it with a dot: the module "
                 "name, a dot, then the tool's name. (The lab has already "
                 "run this line for you, so the name base64 is waiting "
                 "there.)",
         "code": "import base64\n"
                 "base64.b64encode      # a tool inside the toolbox"},
        {"heading": "2. Text and bytes are different",
         "body": "Text is what you read; bytes are the raw numbers "
                 "underneath. .encode() turns text into bytes, and .decode() "
                 "turns bytes back into text. Bytes print with a small b in "
                 "front of the quotes, like b'hi'. The base64 tools want "
                 "bytes, so .encode() comes first.",
         "code": "\"hi\".encode()      # -> b'hi'\n"
                 "b\"hi\".decode()     # -> 'hi'"},
        {"heading": "3. Calling a library function",
         "body": "b64encode takes bytes and hands back new bytes. b64decode "
                 "does the reverse. Notice there is nowhere to put a "
                 "password -- that missing key is the whole point of this "
                 "level.",
         "code": "c = base64.b64encode(\"hi\".encode())   # -> b'aGk='\n"
                 "base64.b64decode(c).decode()          # -> 'hi'"}],
     "challenges": [
        {"title": "Encode a message",
         "goal": "`message` holds some text. Store its base64 form in a "
                 "variable named `coded`, using "
                 "base64.b64encode(message.encode()).",
         "seed": lambda: {"base64": base64, "message": "OPEN AT DAWN"},
         "intro": ["# `import base64` has already been run for you here.",
                   "# `message` = 'OPEN AT DAWN'.",
                   "# Try it on other text first:",
                   "#     base64.b64encode(\"hi\".encode())   -> b'aGk='",
                   "# Now store the base64 form of `message` in `coded`."],
         "hint": "coded = base64.b64encode(message.encode())",
         "solution": "coded = base64.b64encode(message.encode())",
         "check": _c_herald_encode,
         "success": "The message now looks like nonsense -- and is still "
                    "completely readable to anyone."},
        {"title": "Undo it with no key",
         "goal": "`coded` holds the base64 bytes HERALD calls 'encrypted'. "
                 "Turn them back into readable text in a variable named "
                 "`plain`, using base64.b64decode(coded).decode().",
         "seed": lambda: {"base64": base64, "coded": b"T1BFTiBBVCBEQVdO"},
         "intro": ["# `import base64` has already been run for you here.",
                   "# `coded` = b'T1BFTiBBVCBEQVdO'. No password anywhere.",
                   "# b64decode gives you bytes, so add .decode() to get",
                   "# readable text back. Store that text in `plain`."],
         "hint": "Two steps on one line: base64.b64decode(coded) gives "
                 "bytes, then .decode() on the end turns bytes into text.",
         "solution": "plain = base64.b64decode(coded).decode()",
         "check": _c_herald_decode,
         "success": "You read HERALD's 'protected' message without a key. "
                    "That is why encoding is not encryption."},
        {"title": "Prove the round trip",
         "goal": "Write a function `round_trip(text)` that encodes `text` "
                 "to base64 and then decodes it straight back, returning "
                 "the result. Whatever text goes in must come back out "
                 "unchanged.",
         "seed": lambda: {"base64": base64},
         "intro": ["# `import base64` has already been run for you here.",
                   "# def round_trip(text):",
                   "#     ... encode text to base64 into a variable ...",
                   "#     ... return that variable decoded back to text ...",
                   "# Press Enter on a blank line to finish the block."],
         "hint": "Line 1 of the body: coded = base64.b64encode("
                 "text.encode()). Line 2: return base64.b64decode("
                 "coded).decode()",
         "solution": "def round_trip(text):\n"
                     "    coded = base64.b64encode(text.encode())\n"
                     "    return base64.b64decode(coded).decode()",
         "check": _c_herald_trip,
         "success": "Text in, same text out -- your function proves base64 "
                    "hides nothing at all."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "HERALD insists its base64 courier bags are encrypted. "
                  "Answer three questions and strip the disguise.",
        "win": "Disguise removed. HERALD's bags were never locked -- and "
               "now everyone knows it.",
        "rounds": [
            {"q": "A team stores customer passwords as base64. How "
                  "protected are those passwords?",
             "options": ["Fully encrypted -- nobody can read them",
                         "Not protected at all -- base64 needs no key",
                         "Protected for 24 hours, then they expire",
                         "Protected from everyone but the database owner"],
             "answer": 1},
            {"q": "What is the real difference between encoding and "
                  "encryption?",
             "options": ["Encoding produces longer text",
                         "Encryption needs a secret key; encoding does not",
                         "Encoding was invented more recently",
                         "There is no difference between them"],
             "answer": 1},
            {"q": "What is base64 actually FOR?",
             "options": ["Hiding secrets from attackers",
                         "Making files smaller",
                         "Carrying binary data through text-only channels",
                         "Checking whether a password is correct"],
             "answer": 2}]}},
    {"boss": "VEIL", "topic": "Cryptography: Hiding in Plain Sight",
     "brief": "VEIL never scrambles a message -- VEIL hides that there IS "
              "one. Its notes look like ordinary status lines and harmless "
              "street addresses, yet every one carries a payload nobody "
              "thinks to look for. Learn to measure the invisible and slice "
              "the hidden message back out.",
     "debrief": "Lesson: encryption hides what a message SAYS; steganography "
                "hides that a message EXISTS at all. You find it by "
                "measuring what should not be there.",
     "intel": [
        {"heading": "What VEIL does",
         "body": "Encryption shouts. A wall of scrambled characters tells "
                 "anyone watching that a secret is present, even when they "
                 "cannot read it. VEIL takes the opposite route, called "
                 "steganography: send something boring, and tuck the message "
                 "inside it. A favorite trick is trailing spaces -- spaces "
                 "added to the end of a line. Your screen shows nothing "
                 "there, so nobody counts them. Python can.",
         "code": "line = \"STATUS NOMINAL\" + \" \" * 5\n"
                 "# on screen it looks normal -- it carries a hidden 5"},
        {"heading": "The other hiding place: the last bit",
         "body": "A computer stores each color of a pixel as a number from 0 "
                 "to 255. bin() shows that number written as bits, the 1s "
                 "and 0s underneath. int(text, 2) reads bits back into a "
                 "number. Change only the LAST bit and the color moves by "
                 "one step: nothing your eye can catch, but a fine place to "
                 "park one bit of a secret. Thousands of pixels means "
                 "thousands of bits, and that is a whole message.",
         "code": "bin(200)            # -> '0b11001000'\n"
                 "int(\"11001001\", 2)  # -> 201  (one step brighter)"},
        {"heading": "How a defender finds it",
         "body": "Hidden data leaves a fingerprint: something is longer, or "
                 "noisier, than it has any reason to be. A line with 40 "
                 "spaces after the last word, or a photo whose last bits "
                 "look random instead of smooth, is worth a second look. "
                 "The fix on the sending side is to normalize what you "
                 "forward -- trim the ends of every line, and re-save "
                 "images, which throws the hidden bits away.",
         "code": None}],
     "lesson": [
        {"heading": "1. Counting the spaces you cannot see",
         "body": ".strip() hands back a copy of a string with the blank "
                 "space at each end removed. len() counts characters. "
                 "Subtract one length from the other and you have counted "
                 "something invisible.",
         "code": "line = \"hi   \"\n"
                 "len(line)          # -> 5\n"
                 "len(line.strip())  # -> 2\n"
                 "len(line) - len(line.strip())   # -> 3"},
        {"heading": "2. Slicing: taking a piece of text",
         "body": "Square brackets with a colon take a section of a string. "
                 "text[0:4] means 'from position 0 up to, but not "
                 "including, position 4'. Positions start counting at 0, "
                 "not 1.",
         "code": "text = \"vigilante\"\n"
                 "text[0:4]   # -> 'vigi'\n"
                 "text[4:9]   # -> 'lante'"},
        {"heading": "3. A slice with a step",
         "body": "A slice takes a third number, the step: how far to jump "
                 "each time. text[0::5] means 'start at position 0, run to "
                 "the end, take every 5th character'. An empty middle "
                 "number means 'all the way to the end'. Put that line "
                 "inside a function with def and you can point it at any "
                 "message you intercept.",
         "code": "text = \"abcdefghij\"\n"
                 "text[0::5]   # -> 'af'\n\n"
                 "def reveal(text):\n"
                 "    return text[0::5]"}],
     "challenges": [
        {"title": "Measure the invisible",
         "goal": "`line` is a status message VEIL padded with spaces on the "
                 "end that nothing displays. Store how many spaces there "
                 "are in a variable called `hidden`. Type: "
                 "hidden = len(line) - len(line.strip())",
         "seed": lambda: {"line": "STATUS NOMINAL     "},
         "intro": ["# `line` is a status message with invisible spaces on "
                   "the end.",
                   "# len(line) counts everything; len(line.strip()) counts "
                   "it trimmed.",
                   "# hidden = len(line) - len(line.strip())"],
         "hint": "hidden = len(line) - len(line.strip())",
         "solution": "hidden = len(line) - len(line.strip())",
         "check": _c_veil_spaces,
         "success": "Five spaces nobody could see -- and you counted them."},
        {"title": "Slice out the secret",
         "goal": "`carrier` is a delivery address VEIL sent to a courier. "
                 "The real message is every 5th character, starting at the "
                 "first one. Store it in `secret` using carrier[0::5].",
         "seed": lambda: {"carrier": "high east lane park"},
         "intro": ["# carrier = 'high east lane park'  -- an innocent "
                   "address.",
                   "# Take every 5th character:  secret = carrier[0::5]"],
         "hint": "secret = carrier[0::5]",
         "solution": "secret = carrier[0::5]",
         "check": _c_veil_slice,
         "success": "A harmless address that quietly spells 'help'."},
        {"title": "Build the reveal tool",
         "goal": "Write a function `reveal(text)` that returns every 5th "
                 "character of `text`, starting at the first one, so you "
                 "can unwrap any note VEIL sends without retyping the "
                 "slice.",
         "intro": ["# def reveal(text):",
                   "#     return text[0::5]",
                   "# Then reveal('abcdefghij') gives 'af'."],
         "hint": "def reveal(text):  return text[0::5]",
         "solution": "def reveal(text):\n    return text[0::5]",
         "check": _c_veil_reveal,
         "success": "One small tool, and every VEIL courier note opens up."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "VEIL insists there is nothing here to find. Prove "
                  "otherwise.",
        "win": "Every hidden channel found. VEIL has nowhere left to "
               "whisper.",
        "rounds": [
            {"q": "What does steganography hide?",
             "options": ["What a message says",
                         "That a message exists at all",
                         "The name of the sender",
                         "The size of the file"],
             "answer": 1},
            {"q": "Why are trailing spaces a useful hiding place?",
             "options": ["They are encrypted",
                         "They make text load faster",
                         "Screens do not show them, so nobody counts them",
                         "Only printers can read them"],
             "answer": 2},
            {"q": "You change the LAST bit of a pixel's color number. "
                  "What happens?",
             "options": ["The color shifts one step -- too small to see",
                         "The image will not open",
                         "The pixel turns black",
                         "The file doubles in size"],
             "answer": 0}]}},
    {"boss": "KEYSTONE", "topic": "Cryptography: Two Keys, Not One",
     "brief": "KEYSTONE never bothers breaking a cipher. It waits on the "
              "wire for the moment two people hand each other the shared "
              "secret, and it copies that secret as it goes past. Every "
              "lock you have built so far used ONE key that both sides "
              "must already hold -- and getting it there is the weak "
              "point. Learn the idea that removes the handover "
              "completely: a key made of two halves, where the half you "
              "publish and the half you hide undo each other.",
     "debrief": "Lesson: with a key pair, the half that locks can be "
                "public and the half that unlocks never travels. That is "
                "how your browser talks secretly to a shop it has never "
                "met, and how a signature proves who wrote something.",
     "intel": [
        {"heading": "What KEYSTONE does",
         "body": "A shared-secret cipher only works if both people already "
                 "have the same key. So somebody has to deliver it -- by "
                 "email, by message, by a line on a network. KEYSTONE does "
                 "not attack the maths at all. It sits quietly in the "
                 "middle, waits for the handover, and copies the key. From "
                 "that second on it reads everything, and neither side "
                 "notices anything is wrong.",
         "code": "shared = wire.read()          # the key, in transit\n"
                 "plain = unlock(msg, shared)   # now KEYSTONE reads all"},
        {"heading": "The chicken-and-egg problem",
         "body": "The first answer people reach for is to encrypt the key "
                 "before sending it. But encrypting it needs a key, and "
                 "that key has the same problem, and so on forever. Two "
                 "strangers on the internet have never met and share "
                 "nothing at all. With one secret between them, there is "
                 "no safe first move.",
         "code": None},
        {"heading": "The fix: a pair that undoes itself",
         "body": "Public-key cryptography gives you TWO keys, made "
                 "together as a pair. One is public: you may print it on a "
                 "poster. One is private: it never leaves your machine and "
                 "it is never sent, so KEYSTONE has nothing to copy. "
                 "Anyone can lock a message with your public key, and only "
                 "your private key opens it. Run it the other way -- lock "
                 "with your private key, and anyone can check it with your "
                 "public one -- and you have a digital signature: proof "
                 "the message came from you.",
         "code": "coded = pow(message, e, n)   # e, n = the public key\n"
                 "back = pow(coded, d, n)      # d = private, never sent"}],
     "lesson": [
        {"heading": "1. pow(a, b, m) in plain words",
         "body": "pow(a, b, m) does two steps in one call. First it raises "
                 "a to the power b -- that means a multiplied by itself b "
                 "times. Then it takes the remainder: what is left over "
                 "after dividing by m. That third number m is called the "
                 "modulus, and it is nothing more than the number you "
                 "divide by. The answer always lands below m, which is "
                 "what keeps these numbers a usable size.",
         "code": "pow(3, 2, 7)      # 3*3 = 9, and 9 leaves 2 over\n"
                 "pow(2, 5, 10)     # 32, and 32 leaves 2 over"},
        {"heading": "2. A key is a PAIR of numbers",
         "body": "In this toy example the public key is the two numbers e "
                 "and n, and the private key is d and n. n is shared by "
                 "both halves, e is the one you publish, d is the one you "
                 "guard. Here e is 3, d is 7 and n is 33. Real keys are "
                 "hundreds of digits long and nobody works them out by "
                 "hand -- these are tiny on purpose, so you can watch "
                 "what happens.",
         "code": "e, n = 3, 33      # public key -- give it to anyone\n"
                 "d = 7             # private key -- tell nobody"},
        {"heading": "3. One key undoes the other",
         "body": "Lock a number with the public half, then feed the result "
                 "through the private half, and the original number comes "
                 "back. Nothing else you can do to those numbers brings it "
                 "back. That round trip is the whole idea, and everything "
                 "your browser does with certificates is this, scaled up.",
         "code": "coded = pow(5, 3, 33)   # -> 26  (locked)\n"
                 "pow(coded, 7, 33)       # -> 5   (back again)"}],
     "challenges": [
        {"title": "Take a power, then a remainder",
         "goal": "Three numbers are preloaded: `base` is 7, `power` is 2 "
                 "and `modulus` is 10. Store what pow(base, power, "
                 "modulus) hands back in a variable named `answer`.",
         "seed": lambda: {"base": 7, "power": 2, "modulus": 10},
         "intro": ["# base = 7, power = 2, modulus = 10.",
                   "# pow(a, b, m) raises a to the power b, then takes the",
                   "# remainder -- what is left over after dividing by m.",
                   "# 7 to the power 2 is 49, and 49 divided by 10 leaves",
                   "# 9 over. One line stores that in `answer`."],
         "hint": "pow wants its three numbers in this order: the base, "
                 "then the power, then the modulus. Put the result under "
                 "the name `answer`.",
         "solution": "answer = pow(base, power, modulus)",
         "check": _c_keystone_pow,
         "success": "49, remainder 9. That one call is the engine "
                    "underneath every public key on the internet."},
        {"title": "Lock a number with the public key",
         "goal": "`message` is the number 5 you want to send. The public "
                 "key is `e` (3) and `n` (33) -- numbers KEYSTONE is "
                 "welcome to see. Store the locked form in a variable "
                 "named `coded` by raising `message` to the power `e` "
                 "with modulus `n`.",
         "seed": lambda: {"message": 5, "e": 3, "n": 33},
         "intro": ["# message = 5, e = 3, n = 33.",
                   "# e and n together ARE the public key. Anyone may hold",
                   "# them, so nothing is lost if they leak.",
                   "# Lock the message with the same pow call as before:",
                   "# coded = pow(..., ..., ...)"],
         "hint": "It is the same three-number pow. The base is the "
                 "message, the power is the public half e, and the "
                 "modulus is n.",
         "solution": "coded = pow(message, e, n)",
         "check": _c_keystone_lock,
         "success": "5 went in and 26 came out. Only the private half "
                    "turns that back."},
        {"title": "Unlock it with the private key",
         "goal": "`coded` is 26, `d` is 7 (the private key) and `n` is "
                 "33. Write a function `decrypt(c, d, n)` that returns c "
                 "raised to the power d with modulus n. Then call it on "
                 "the preloaded numbers and store what comes back in a "
                 "variable named `plain`.",
         "seed": lambda: {"coded": 26, "d": 7, "n": 33},
         "intro": ["# coded = 26, d = 7 (private), n = 33.",
                   "# def decrypt(c, d, n):",
                   "#     return ...one pow call...",
                   "# Press Enter on a blank line to end the block, then:",
                   "# plain = decrypt(coded, d, n)",
                   "# If `plain` comes back as 5, the round trip worked."],
         "hint": "The body is a single return line, and it is the same "
                 "pow call you have used twice -- handing it the "
                 "function's own c, d and n.",
         "solution": "def decrypt(c, d, n):\n"
                     "    return pow(c, d, n)\n"
                     "plain = decrypt(coded, d, n)",
         "check": _c_keystone_unlock,
         "success": "26 became 5 again. You sent a secret without ever "
                    "sending a secret -- KEYSTONE had nothing to steal."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "KEYSTONE is still listening on the wire, waiting for a "
                  "key to fly past. Answer three questions and leave it "
                  "with nothing.",
        "win": "Nothing secret ever crossed the wire. KEYSTONE listened "
               "to the whole conversation and learned exactly nothing.",
        "rounds": [
            {"q": "Two strangers want to talk secretly using ONE shared "
                  "key. What is the problem?",
             "options": ["The key would be too long to type",
                         "They must deliver that key first, and the "
                         "delivery can be copied",
                         "Shared keys expire after one message",
                         "One shared key can only encrypt numbers"],
             "answer": 1},
            {"q": "Which half of a key pair is safe to hand to anybody "
                  "who asks?",
             "options": ["The private key",
                         "The public key",
                         "Both halves, as long as they are long",
                         "Neither -- a key pair is always kept secret"],
             "answer": 1},
            {"q": "You want to prove a message really came from you. "
                  "What do you use?",
             "options": ["Your private key, because only you hold it",
                         "The reader's private key",
                         "A password you and the reader agreed on",
                         "Nothing -- you type your name at the bottom"],
             "answer": 0}]}},
    {"boss": "SIREN", "topic": "Incident Response: The First Hour",
     "brief": "SIREN does not break in quietly -- SIREN screams. It "
              "floods the alert feed with hundreds of harmless warnings "
              "so the one real break-in scrolls past unread, and the "
              "team burns the first hour arguing instead of acting. "
              "Learn the order of the first hour, then sort the noise "
              "into a queue with the worst alert on top.",
     "debrief": "Lesson: an incident has an order -- prepare, detect, "
                "contain, eradicate, recover, learn. Containment comes "
                "before cleanup, and the write-up at the end is what "
                "stops the same attack working twice.",
     "intel": [
        {"heading": "What SIREN does",
         "body": "An alert is a short note from a security tool saying "
                 "'something looked wrong here'. SIREN buries the real "
                 "one. It sets off hundreds of tiny, harmless alerts on "
                 "purpose, so the feed fills with junk and the single "
                 "alert that matters slides past. Responders get worn "
                 "down by alarms that mean nothing -- that has a name, "
                 "alert fatigue -- and the attack gets its quiet hour. "
                 "Panic costs more than the break-in did.",
         "code": "for i in range(200):\n"
                 "    raise_alert(\"low\", random_host())\n"
                 "# 200 harmless alarms to hide the one that matters"},
        {"heading": "The six steps, in order",
         "body": "Responders do not improvise. PREPARE is the work done "
                 "before anything happens: backups, a contact list, a "
                 "written plan. DETECT is noticing. CONTAIN is stopping "
                 "the spread -- pull the machine off the network. "
                 "ERADICATE is removing the attacker's foothold. "
                 "RECOVER is putting the service back. LEARN is writing "
                 "down what happened and what changes because of it.",
         "code": "steps = [\"prepare\", \"detect\", \"contain\",\n"
                 "         \"eradicate\", \"recover\", \"learn\"]"},
        {"heading": "Contain first, and never skip the last step",
         "body": "Cleanup before containment is the classic mistake: "
                 "you wipe one laptop while the attacker is already on "
                 "three more. Stop the bleeding first. Unplug the "
                 "network cable rather than powering the machine off, "
                 "because a shutdown throws away evidence you will want "
                 "later. And LEARN is not paperwork -- it is the step "
                 "that changes anything at all. An incident nobody "
                 "wrote up is an incident that happens again.",
         "code": None}],
     "lesson": [
        {"heading": "1. One alert is a dictionary",
         "body": "A dictionary stores values under labels, and square "
                 "brackets pull one value out by its label. One alert "
                 "becomes one dictionary. A whole feed is a list of "
                 "them, so a for-loop walks the feed one alert at a "
                 "time.",
         "code": "a = {\"id\": \"A-15\", \"severity\": \"critical\"}\n"
                 "a[\"severity\"]     # -> 'critical'"},
        {"heading": "2. Counting, then collecting",
         "body": "Two jobs you already know. .count() on a list hands "
                 "back how many times a value appears in it. To gather "
                 "the matching items instead of counting them, start an "
                 "empty list with [] and .append() to it inside the "
                 "loop.",
         "code": "levels = [\"low\", \"critical\", \"low\"]\n"
                 "levels.count(\"critical\")   # -> 1\n\n"
                 "feed = [{\"id\": \"A-1\", \"severity\": \"critical\"},\n"
                 "        {\"id\": \"A-2\", \"severity\": \"low\"}]\n"
                 "worst = []\n"
                 "for a in feed:\n"
                 "    if a[\"severity\"] == \"critical\":\n"
                 "        worst.append(a[\"id\"])\n"
                 "# worst -> ['A-1']"},
        {"heading": "3. sorted() with a key -- the new idea",
         "body": "sorted(items) hands back a NEW list in order and "
                 "leaves the original alone. Dictionaries have no "
                 "natural order, so you say what to sort BY: key= takes "
                 "the name of a function, and sorted calls that "
                 "function on each item to get a number. The smallest "
                 "number lands first. Write the name with no "
                 "parentheses after it -- rank means 'the function "
                 "itself', while rank(a) means 'call it right now'.",
         "code": "feed = [{\"id\": \"A-1\", \"severity\": \"low\"},\n"
                 "        {\"id\": \"A-2\", \"severity\": \"high\"}]\n\n"
                 "def rank(alert):\n"
                 "    order = {\"critical\": 0, \"high\": 1,\n"
                 "             \"medium\": 2, \"low\": 3}\n"
                 "    return order[alert[\"severity\"]]\n\n"
                 "sorted(feed, key=rank)   # A-2 first, then A-1"}],
     "challenges": [
        {"title": "Count the criticals",
         "goal": "`severities` is a plain list holding the severity of "
                 "each alert in tonight's feed. Count how many of them "
                 "are 'critical' with .count(), and store that number "
                 "in a variable named `criticals`.",
         "seed": lambda: {
             "severities": ["low", "critical", "medium", "critical",
                            "high"]},
         "intro": ["# `severities` is tonight's feed, one severity per",
                   "#   alert:",
                   "#   ['low', 'critical', 'medium', 'critical', "
                   "'high']",
                   "# Store how many are 'critical' in `criticals`."],
         "hint": "Lists have a .count() method. You hand it the value "
                 "you are looking for, and it hands back how many times "
                 "that value appears.",
         "solution": "criticals = severities.count('critical')",
         "check": _c_siren_count,
         "success": "Two criticals hiding in five lines -- and you have "
                    "the number before the panic starts."},
        {"title": "Write down which ones",
         "goal": "`alerts` is the feed, one dictionary per alert. Loop "
                 "over it and collect the 'id' of every alert whose "
                 "'severity' is 'critical' into a list named "
                 "`critical_ids`.",
         "seed": lambda: {"alerts": [
             {"id": "A-14", "severity": "low", "host": "printer-2"},
             {"id": "A-15", "severity": "critical", "host": "db-01"},
             {"id": "A-16", "severity": "medium", "host": "laptop-9"},
             {"id": "A-17", "severity": "critical", "host": "vpn-gw"},
             {"id": "A-18", "severity": "high", "host": "mail-01"}]},
         "intro": ["# `alerts` holds 5 dictionaries, each with an 'id',",
                   "#   a 'severity' and a 'host'.",
                   "# Try:  alerts[0]     then:  alerts[0]['severity']",
                   "# Start with:  critical_ids = []"],
         "hint": "Start the empty list BEFORE the loop. Inside the "
                 "loop, test one alert's 'severity', and .append() its "
                 "'id' only when that test passes.",
         "solution": "critical_ids = []\nfor a in alerts:\n"
                     "    if a['severity'] == 'critical':\n"
                     "        critical_ids.append(a['id'])",
         "check": _c_siren_ids,
         "success": "A-15 and A-17, named and written down. That list "
                    "is what containment works from."},
        {"title": "Queue the worst first",
         "goal": "Write a function `triage(alerts)` that returns the "
                 "alert list reordered worst-first. Use sorted() on "
                 "`alerts` with key set to the ready-made `rank` "
                 "function.",
         "seed": lambda: {"rank": _siren_rank, "alerts": [
             {"id": "A-14", "severity": "low", "host": "printer-2"},
             {"id": "A-15", "severity": "critical", "host": "db-01"},
             {"id": "A-16", "severity": "medium", "host": "laptop-9"},
             {"id": "A-17", "severity": "critical", "host": "vpn-gw"},
             {"id": "A-18", "severity": "high", "host": "mail-01"}]},
         "intro": ["# `rank` is already written for you. Hand it ONE",
                   "#   alert and it hands back a number:",
                   "#   critical -> 0, high -> 1, medium -> 2, low -> 3.",
                   "# Try:  rank(alerts[0])",
                   "# sorted() puts the smallest number first, so 0",
                   "#   means 'deal with me first'.",
                   "# Shape:  def triage(alerts):  ->  one return line.",
                   "# Press Enter on a blank line to finish the block."],
         "hint": "sorted() takes the list first, then key=. A function "
                 "name written with no parentheses after it means 'the "
                 "function itself', and that is what key= wants.",
         "solution": "def triage(alerts):\n"
                     "    return sorted(alerts, key=rank)",
         "check": _c_siren_triage,
         "success": "Worst alert on top, every time -- nobody has to "
                    "guess what to touch first."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "The alarms are all going off at once. SIREN is "
                  "counting on you to move in the wrong order. Three "
                  "calls, made calmly.",
        "win": "Contained, cleaned, recovered, written up. SIREN made "
               "noise and you made a plan.",
        "rounds": [
            {"q": "A laptop is spreading ransomware across the office "
                  "network right now. What do you do FIRST?",
             "options": ["Take that laptop off the network",
                         "Read every log file to find how it started",
                         "Reinstall the operating system on it",
                         "Write the incident report"],
             "answer": 0},
            {"q": "Why does CONTAIN come before ERADICATE?",
             "options": ["Cleanup tools need a reboot first",
                         "Stop the spread, or the damage grows while "
                         "you clean",
                         "Eradicate is an optional step",
                         "They are two names for the same step"],
             "answer": 1},
            {"q": "The attack is cleaned up and the service is running "
                  "again. What is the last step?",
             "options": ["Nothing -- the incident is over",
                         "Delete the logs so nobody sees them",
                         "Write up what happened and what to change",
                         "Wait and see whether it happens again"],
             "answer": 2}]}},
    {"boss": "CANARY", "topic": "Threat Modelling: Thinking Like the "
                                "Attacker",
     "brief": "CANARY does not break anything. CANARY reads how a team "
              "spends its week, notices they are guarding every door with "
              "the same thin effort, and walks in through the one they "
              "kept postponing. A team that defends everything equally "
              "defends nothing well. Learn to score threats in Python, "
              "rank them, and name the one that must be fixed first.",
     "debrief": "Lesson: risk is roughly likelihood times impact, and "
                "that number is how you choose what to fix first when you "
                "cannot fix everything. Ranking is the defence.",
     "intel": [
        {"heading": "What CANARY does",
         "body": "CANARY threat-models your team the way you should be "
                 "threat-modelling your own system. Every target gets a "
                 "score: how much CANARY gains, multiplied by how little "
                 "effort it takes. Then CANARY starts at the top of that "
                 "ranked list. The attacker is already ranking. If you "
                 "are not, you are the only one working from an unsorted "
                 "pile.",
         "code": "for tgt in targets:\n"
                 "    score = tgt['payoff'] * tgt['ease']\n"
                 "# CANARY tries the highest score first, every time"},
        {"heading": "The four questions",
         "body": "Threat modelling is four plain questions asked before "
                 "anything is built. What are we building? What can go "
                 "wrong? What are we going to do about it? Did we do a "
                 "good job? You do not need a diagram or a certificate to "
                 "ask them. You need to ask them early, while changing "
                 "the answer is still cheap.",
         "code": None},
        {"heading": "Risk is likelihood times impact",
         "body": "Likelihood is how often a thing is expected to happen. "
                 "Impact is how badly it hurts when it does. Score each "
                 "from 1 to 5 and multiply. An office fire is impact 5 "
                 "and likelihood 1, so it scores 5. A reused admin "
                 "password is 5 and 5, so it scores 25. Both are real. "
                 "One of them gets your Monday.",
         "code": None},
        {"heading": "The fix: rank, fix the top, then ask again",
         "body": "You will never have time to fix everything, and that is "
                 "not a failure. Score every threat you can name, sort by "
                 "the score, fix the highest one, then score again -- "
                 "because fixing the top item changes the ranking. That "
                 "loop is the whole defence, and it is why a short list "
                 "you actually work beats a long list you admire.",
         "code": None}],
     "lesson": [
        {"heading": "1. Multiplying two values out of a dictionary",
         "body": "A dictionary stores values under labels. Square "
                 "brackets pull one value out by its label. Pull two "
                 "numbers out and multiply them with * to get one score "
                 "from one threat.",
         "code": "threat = {\"name\": \"Weak lock\", \"likelihood\": 3,\n"
                 "          \"impact\": 5}\n"
                 "threat[\"likelihood\"] * threat[\"impact\"]   # -> 15"},
        {"heading": "2. A list of scores, one per threat",
         "body": "Several threats arrive as a list, one dictionary each. "
                 "Start an empty list with = [], walk the threats with a "
                 "for-loop, and .append() each score onto the end. You "
                 "finish with one number per threat, in the same order "
                 "as the threats.",
         "code": "scores = []\nfor th in threats:\n"
                 "    scores.append(th[\"likelihood\"] * th[\"impact\"])\n"
                 "# scores -> [25, 12, 8, 5]"},
        {"heading": "3. max() finds the worst one",
         "body": "max() is new. Hand it a list of numbers and it hands "
                 "back the largest one. Note what it does NOT hand back: "
                 "the name, or the position. So to get the name, find the "
                 "top score first, then loop over the threats again and "
                 "return the one whose score matches it.",
         "code": "max([25, 12, 8, 5])   # -> 25\n\n"
                 "top = max(scores)\nfor th in threats:\n"
                 "    if th[\"likelihood\"] * th[\"impact\"] == top:\n"
                 "        print(th[\"name\"])"}],
     "challenges": [
        {"title": "Score one threat",
         "goal": "`threat` is one dictionary with a 'likelihood' and an "
                 "'impact', each scored 1 to 5. Multiply those two values "
                 "together and store the result in a variable named "
                 "`risk`.",
         "seed": lambda: {"threat": {"name": "Reused admin password",
                                     "likelihood": 3, "impact": 5}},
         "intro": ["# `threat` = {'name': 'Reused admin password',",
                   "#             'likelihood': 3, 'impact': 5}",
                   "# Multiply the two numbers. Store it in `risk`."],
         "hint": "Square brackets pull one value out of a dictionary by "
                 "its label: threat['name'] hands back the text name. You "
                 "want the two NUMBER labels, with a * between them.",
         "solution": "risk = threat['likelihood'] * threat['impact']",
         "check": _c_canary_risk,
         "success": "One threat, one number -- now threats can be "
                    "compared."},
        {"title": "Score them all, then find the worst",
         "goal": "`threats` is a list of four threat dictionaries. Build "
                 "a list called `scores` holding likelihood * impact for "
                 "each one, in order. Then store the largest score in a "
                 "variable called `top` using max().",
         "seed": lambda: {"threats": [
             {"name": "Reused admin password", "likelihood": 5,
              "impact": 5},
             {"name": "Phishing email", "likelihood": 4, "impact": 3},
             {"name": "Old backup server", "likelihood": 2, "impact": 4},
             {"name": "Office fire", "likelihood": 1, "impact": 5}]},
         "intro": ["# `threats` lists 4 threats, each a dictionary with",
                   "# a 'name', a 'likelihood' and an 'impact'.",
                   "# Build `scores` with a loop, then find `top`.",
                   "# Press Enter on a blank line to finish the loop."],
         "hint": "Three tools, in order: an empty list to collect into, a "
                 "for-loop over `threats`, and .append() for each score. "
                 "When the list is full, max() reads the largest number "
                 "out of it.",
         "solution": "scores = []\nfor th in threats:\n"
                     "    scores.append(th['likelihood'] * th['impact'])\n"
                     "top = max(scores)",
         "check": _c_canary_scores,
         "success": "The office fire scores 5 and the reused password 25 "
                    "-- and now you can see the difference."},
        {"title": "Name what to fix first",
         "goal": "Write a function `worst(threats)` that takes a list of "
                 "threat dictionaries and returns the 'name' of the one "
                 "with the highest likelihood * impact. Find the top "
                 "score with max(), then loop again to find whose score "
                 "it was.",
         "intro": ["# def worst(threats):",
                   "#     build a list of scores, then top = max(scores)",
                   "#     loop the threats again and return the matching",
                   "#     name -- return inside a loop stops it there.",
                   "# Press Enter on a blank line to finish the block."],
         "hint": "max() hands you the number but never the name. Once you "
                 "hold the top number, a second loop can ask each threat "
                 "whether its score equals that number.",
         "solution": "def worst(threats):\n"
                     "    scores = []\n"
                     "    for th in threats:\n"
                     "        scores.append(th['likelihood'] * "
                     "th['impact'])\n"
                     "    top = max(scores)\n"
                     "    for th in threats:\n"
                     "        if th['likelihood'] * th['impact'] == top:\n"
                     "            return th['name']",
         "check": _c_canary_worst,
         "success": "A tool that answers the only question that matters "
                    "on Monday morning: which one first."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "CANARY says everything on your list looks equally "
                  "urgent. Rank it.",
        "win": "Ranked, fixed from the top, and scored again. CANARY "
               "finds no forgotten door.",
        "rounds": [
            {"q": "Risk is roughly what?",
             "options": ["Impact minus likelihood",
                         "Likelihood times impact",
                         "The number of threats on the list",
                         "How long the fix takes"],
             "answer": 1},
            {"q": "One threat is likelihood 5, impact 5. Another is "
                  "likelihood 1, impact 5. You can fix one this week. "
                  "Which one?",
             "options": ["The likelihood 1 one -- it sounds scarier",
                         "The likelihood 5 one -- it scores 25 to 5",
                         "Neither, until you can fix both",
                         "Whichever is quicker to type"],
             "answer": 1},
            {"q": "You call max(scores) on a list of numbers. What does "
                  "it hand back?",
             "options": ["The largest number in the list",
                         "The position of the largest number",
                         "The name of the threat",
                         "The list sorted from high to low"],
             "answer": 0}]}},
    {"boss": "ARCHIVE", "topic": "Resilience: Backups That Actually Work",
     "brief": "ARCHIVE does not want your files -- ARCHIVE wants your way "
              "back. It sits quietly on the network for weeks, finds every "
              "drive with the word 'backup' in the name, wipes those "
              "first, and only then locks the live machines. Learn the two "
              "numbers that decide whether a company survives that "
              "morning, and write the test that answers yes or no.",
     "debrief": "Lesson: three copies, on two kinds of media, one of them "
                "offsite and offline. An untested backup is a rumour, not "
                "a backup -- the restore is the only proof.",
     "intel": [
        {"heading": "What ARCHIVE does",
         "body": "ARCHIVE gets in days or weeks before anyone notices. It "
                 "looks at every drive the machine can reach and destroys "
                 "the ones that look like backups, because a backup is the "
                 "only thing that makes the ransom optional. A backup the "
                 "infected computer can reach and change is a backup "
                 "ARCHIVE can reach and change.",
         "code": "for drive in reachable_drives:\n"
                 "    if \"backup\" in drive.lower():\n"
                 "        wipe(drive)   # first -- lock the files after"},
        {"heading": "The 3-2-1 rule",
         "body": "Three copies of the data. On two different kinds of "
                 "storage, so one bad batch of drives cannot take both. "
                 "And one copy offsite AND offline -- somewhere a fire "
                 "cannot reach and a network cannot touch. Offline is the "
                 "part that stops ARCHIVE, because no software can delete "
                 "a disk that is unplugged.",
         "code": None},
        {"heading": "The two numbers, and the fix",
         "body": "Number one: how much data you can afford to lose. That "
                 "is the gap since the last backup. Back up every 24 "
                 "hours and you have agreed to lose up to 24 hours of "
                 "work. Number two: how long you can afford to be down. "
                 "That is how long a restore takes, from bare machine to "
                 "people working again. Both numbers are guesses until "
                 "somebody tests them. So schedule a real restore, time "
                 "it, and write the date down. An untested backup is a "
                 "rumour.",
         "code": None}],
     "lesson": [
        {"heading": "1. Subtraction measures a gap",
         "body": "Clock times can be plain whole numbers: 2 means 02:00 "
                 "and 21 means 21:00. Subtracting the earlier number from "
                 "the later one gives the hours between them. That gap IS "
                 "the work you would lose, because nothing after the "
                 "backup was ever saved anywhere else.",
         "code": "backup_hour = 2\n"
                 "crash_hour = 21\n"
                 "crash_hour - backup_hour   # -> 19 hours lost"},
        {"heading": "2. Counting the things that pass a test",
         "body": "To count, start a variable at 0, loop over the list, "
                 "and add 1 every time an item passes. `n += 1` is "
                 "shorthand for 'n = n + 1'. When the value stored under "
                 "a key is already True or False, it can go straight into "
                 "the if with nothing to compare it against.",
         "code": "offsite_count = 0\n"
                 "for c in copies:\n"
                 "    if c[\"offsite\"]:\n"
                 "        offsite_count += 1"},
        {"heading": "3. An if/else that hands back a decision",
         "body": "A function can end in a verdict. `and` gives True only "
                 "when every side of it is True, so several requirements "
                 "chain into one test. Put return True in the if branch "
                 "and return False in the else branch, and whoever calls "
                 "the function gets a straight answer.",
         "code": "def restore_ok(minutes, tested):\n"
                 "    if minutes <= 240 and tested:\n"
                 "        return True\n"
                 "    else:\n"
                 "        return False"}],
     "challenges": [
        {"title": "Measure what you would lose",
         "goal": "The nightly backup finished at hour `backup_hour`, and "
                 "ARCHIVE locked the server at hour `crash_hour`. Work "
                 "out how many hours of work vanished, and store that "
                 "number in a variable called `data_lost`. One line.",
         "seed": lambda: {"backup_hour": 2, "crash_hour": 21},
         "intro": ["# backup_hour = 2    -- the backup finished at 02:00",
                   "# crash_hour = 21    -- ARCHIVE struck at 21:00",
                   "# data_lost = <the later hour> - <the earlier hour>"],
         "hint": "One subtraction, nothing else. The gap runs from the "
                 "backup forward to the crash, so the earlier hour is "
                 "the one being taken away.",
         "solution": "data_lost = crash_hour - backup_hour",
         "check": _c_archive_gap,
         "success": "19 hours of work, gone -- that is what a nightly "
                    "schedule quietly agrees to lose."},
        {"title": "Count the copies out of reach",
         "goal": "`copies` is a list of dictionaries, one per copy of the "
                 "backup set. Count how many of them have an 'offsite' "
                 "value of True, and store that number in "
                 "`offsite_count`.",
         "seed": lambda: {"copies": [
             {"where": "office server", "media": "disk", "offsite": False},
             {"where": "usb in a desk drawer", "media": "usb",
              "offsite": False},
             {"where": "cloud bucket", "media": "cloud", "offsite": True},
             {"where": "tape in a bank box", "media": "tape",
              "offsite": True}]},
         "intro": ["# `copies` holds 4 copies. Each one is a dictionary",
                   "# with 'where', 'media' and 'offsite'.",
                   "# Count the ones whose 'offsite' is True.",
                   "# Put that number in offsite_count."],
         "hint": "This is the counting shape from lesson card 2: a "
                 "variable that starts at 0, a for-loop, and += 1 inside "
                 "an if. The 'offsite' value is already True or False, so "
                 "it can go straight into the if on its own.",
         "solution": "offsite_count = 0\nfor c in copies:\n"
                     "    if c['offsite']:\n"
                     "        offsite_count += 1",
         "check": _c_archive_offsite,
         "success": "Two copies ARCHIVE cannot walk to across the "
                    "network."},
        {"title": "Write the survival test",
         "goal": "Write a function `survives(copies, offsite, tested)`. "
                 "Here `copies` is a NUMBER -- how many copies exist -- "
                 "and `offsite` is a NUMBER too: how many of them are "
                 "offsite. `tested` is True or False. Return True only "
                 "when there are 3 or more copies, 1 or more of them "
                 "offsite, and tested is True. Return False in every "
                 "other case.",
         "intro": ["# survives(3, 1, True)  -> True   (3-2-1, and tested)",
                   "# survives(2, 1, True)  -> False  (too few copies)",
                   "# survives(3, 0, True)  -> False  (nothing offsite)",
                   "# survives(3, 1, False) -> False  (never restored)"],
         "hint": "Three requirements inside one if, joined by `and`. Use "
                 ">= for the two counts. `tested` is already True or "
                 "False, so it needs no comparison of its own.",
         "solution": "def survives(copies, offsite, tested):\n"
                     "    if copies >= 3 and offsite >= 1 and tested:\n"
                     "        return True\n"
                     "    else:\n"
                     "        return False",
         "check": _c_archive_survives,
         "success": "Three copies, one offsite, and a restore somebody "
                    "actually ran. That is a backup."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "ARCHIVE holds the live servers. Show that the "
                  "recovery plan was never a guess.",
        "win": "Copies spread, one offline, restore proven. ARCHIVE has "
               "nothing left to hold hostage.",
        "rounds": [
            {"q": "The backup runs at 02:00 every night. The servers are "
                  "locked at 21:00. How much work is gone?",
             "options": ["None -- there is a backup",
                         "19 hours of it",
                         "All of it, always",
                         "It depends on the internet speed"],
             "answer": 1},
            {"q": "What does the '1' in the 3-2-1 rule mean?",
             "options": ["One backup a year",
                         "One folder per computer",
                         "One copy kept offsite and offline",
                         "One person allowed to run a restore"],
             "answer": 2},
            {"q": "Why does a backup nobody has ever restored not count?",
             "options": ["Nobody knows whether it restores until they try",
                         "It takes up too much space",
                         "It slows the network down",
                         "It stops working after 30 days"],
             "answer": 0}]}},
    {"boss": "LEDGER", "topic": "Privacy: Collect Less, Redact The Rest",
     "brief": "LEDGER never breaks in. LEDGER waits. It runs the signup "
              "form that asks for your birthday, your address and your "
              "card, keeps every answer forever, and one day that pile "
              "leaks. Learn to take only the last four characters of a "
              "secret, build a masked string, and write the tool that "
              "hides every field you were never meant to keep.",
     "debrief": "Lesson: data you never collected cannot leak. Keep the "
                "smallest amount that does the job, mask what you must "
                "keep, and delete it when the reason for holding it ends.",
     "intel": [
        {"heading": "What LEDGER does",
         "body": "LEDGER's form asks for far more than an order needs: the "
                 "full card number, date of birth, home address, phone. "
                 "None of it is ever deleted, because deleting feels like "
                 "throwing away value. Years of answers sit in one table, "
                 "so a single stolen password hands the attacker "
                 "everything at once.",
         "code": "customers[email] = {\"card\": \"4024007182354471\",\n"
                 "                    \"dob\": \"1994-03-11\",\n"
                 "                    \"address\": \"9 Pier Road\"}"},
        {"heading": "Collect less: the cheapest control there is",
         "body": "Every field you do not ask for is a field that cannot "
                 "leak and costs nothing to protect. That idea has a name: "
                 "data minimization, meaning collect the least that still "
                 "does the job. Before adding a box to a form, ask what "
                 "breaks if it is not there. A shop needs to CHARGE a "
                 "card, not to store the number -- the payment company "
                 "keeps the number and hands the shop a stand-in code "
                 "that is worthless anywhere else.",
         "code": None},
        {"heading": "Mask what you keep, then let it expire",
         "body": "Sometimes you do need a trace: enough for a customer to "
                 "recognize their own card on a receipt. The last four "
                 "characters do that, and on their own they are useless "
                 "to a thief. Personal data also has a shelf life. When "
                 "the reason for holding it ends -- the order shipped, "
                 "the account closed -- delete it. Data kept past its "
                 "purpose is pure risk with no upside.",
         "code": "receipt = \"card ending \" + card[-4:]"}],
     "lesson": [
        {"heading": "1. Counting from the end",
         "body": "A position in a string is allowed to be negative, which "
                 "means 'count backwards from the end'. text[-1] is the "
                 "last character, text[-2] the one before it. Nothing new "
                 "to install -- the same square brackets you already use, "
                 "pointed the other way.",
         "code": "text = \"vigilante\"\n"
                 "text[-1]   # -> 'e'\n"
                 "text[-2]   # -> 't'"},
        {"heading": "2. A slice that starts from the end",
         "body": "You have sliced with text[0:4] before. A negative start "
                 "works the same way: text[-4:] means 'begin 4 characters "
                 "from the end, then run to the end'. An empty space after "
                 "the colon means 'all the way to the end'. That one "
                 "slice is how every receipt shows a card.",
         "code": "card = \"4024007182354471\"\n"
                 "card[-4:]   # -> '4471'\n"
                 "card[:-4]   # -> everything EXCEPT the last four"},
        {"heading": "3. Gluing the mask together",
         "body": "The + sign joins two strings into one. \"*\" * 4 repeats "
                 "a star four times, and you may also type the stars out "
                 "yourself, spaces and all. Put stars in front of the "
                 "last four characters and you have a value a customer "
                 "can recognize but a thief cannot spend.",
         "code": "card = \"4024007182354471\"\n"
                 "\"*\" * 4 + card[-4:]        # -> '****4471'\n"
                 "\"**** **** **** \" + card[-4:]"}],
     "challenges": [
        {"title": "Take the last four",
         "goal": "`card` holds a full card number LEDGER stored. Store "
                 "only its last four characters in a variable named "
                 "`last4`. Type: last4 = card[-4:]",
         "seed": lambda: {"card": "4024007182354471"},
         "intro": ["# `card` = '4024007182354471' -- far more than anyone",
                   "# needs to keep. A negative start counts from the end:",
                   "# last4 = card[-4:]"],
         "hint": "One slice with a negative start. Leave the space after "
                 "the colon empty, meaning 'to the end'.",
         "solution": "last4 = card[-4:]",
         "check": _c_ledger_last4,
         "success": "Four characters instead of sixteen -- and the other "
                    "twelve are now nobody's problem."},
        {"title": "Build the masked number",
         "goal": "`card` holds the same full number. Build the string "
                 "'**** **** **** 4471' and store it in a variable named "
                 "`masked`. Glue the stars in front of the last four with "
                 "the + sign.",
         "seed": lambda: {"card": "4024007182354471"},
         "intro": ["# `card` = '4024007182354471'",
                   "# Wanted:  '**** **** **** 4471'  in `masked`",
                   "# The stars are a plain string; + joins it to a slice"],
         "hint": "Type the three star groups as one string that ends in a "
                 "space, then + the negative slice from lesson card 2.",
         "solution": "masked = '**** **** **** ' + card[-4:]",
         "check": _c_ledger_masked,
         "success": "Recognizable to its owner, worthless to a thief. "
                    "That is what belongs in a database."},
        {"title": "Write the redactor",
         "goal": "Write a function `redact(record, keep)` where `record` "
                 "is a dictionary of fields and `keep` is a list of field "
                 "names to leave alone. Return a NEW dictionary: fields "
                 "named in `keep` copied unchanged, every other field "
                 "replaced by '****' plus its last four characters.",
         "seed": lambda: {"person": {"name": "Ada Vance",
                                     "card": "4024007182354471",
                                     "phone": "303-555-0142"}},
         "intro": ["# `person` is here so you can test your function:",
                   "#   redact(person, ['name'])",
                   "# Start with out = {}, then loop: for field in record:",
                   "# kept field -> copy it. Anything else -> '****' plus "
                   "the last four."],
         "hint": "`field in keep` is True when that name appears in the "
                 "keep list. Fill a fresh dictionary as you loop, then "
                 "return it at the end.",
         "solution": "def redact(record, keep):\n"
                     "    out = {}\n"
                     "    for field in record:\n"
                     "        if field in keep:\n"
                     "            out[field] = record[field]\n"
                     "        else:\n"
                     "            out[field] = '****' + record[field][-4:]\n"
                     "    return out",
         "check": _c_ledger_redact,
         "success": "One tool that leaves a record readable and a leak "
                    "worthless. LEDGER's pile is no longer worth "
                    "stealing."}],
     "boss_kind": "flag",
     "boss_data": {
        "prompt": "LEDGER's signup form for a one-off t-shirt order is on "
                  "screen. Flag every field it has no business "
                  "collecting, then audit.",
        "scan_label": "Audit The Form",
        "win": "The form now asks for what the order needs and nothing "
               "else. LEDGER's pile stops growing.",
        "items": [
            {"label": "Delivery address",
             "detail": "Where the t-shirt is posted", "bad": False,
             "reason": "The order cannot be delivered without it. Needed "
                       "now, and deletable once the parcel arrives."},
            {"label": "Date of birth",
             "detail": "Marked required on a t-shirt order", "bad": True,
             "reason": "Nothing about posting a shirt depends on a "
                       "birthday, and it is a favorite answer to "
                       "identity questions. Do not ask for it."},
            {"label": "Email address",
             "detail": "Used to send the order confirmation", "bad": False,
             "reason": "One clear purpose the customer expects: telling "
                       "them their order shipped."},
            {"label": "Full card number, stored after payment",
             "detail": "Kept in the orders table for convenience",
             "bad": True,
             "reason": "The payment is already done. Keep the last four "
                       "for the receipt and let the payment company hold "
                       "the rest."},
            {"label": "Government ID number",
             "detail": "Collected for an age check", "bad": True,
             "reason": "A permanent identifier nobody can change after a "
                       "leak, gathered to sell a shirt. The most "
                       "dangerous field on the form."}]}},
    {"boss": "MORTIS", "topic": "Forensics: Proving What Happened",
     "brief": "MORTIS does not break in -- MORTIS comes back afterwards "
              "and edits what the break-in left behind. One log line "
              "reworded, one deleted, one timestamp nudged, and nobody "
              "can prove a thing. Your job is the opposite: fingerprint "
              "the evidence so tampering shows, and put the events in "
              "order until the story tells itself.",
     "debrief": "Lesson: evidence is only worth something if you can "
                "prove it has not changed. Hash it the moment you "
                "collect it, and sort your events by time -- the order "
                "is the story.",
     "intel": [
        {"heading": "What MORTIS does",
         "body": "This is called anti-forensics: attacking the record "
                 "instead of the machine. A log is a plain text file, so "
                 "whoever holds admin rights can open it and rewrite it. "
                 "MORTIS deletes the line showing the login, and edits "
                 "the time on another so the events no longer line up. "
                 "The break-in still happened -- but the proof is gone.",
         "code": "line = \"01:07 vpn: login from a new device\"\n"
                 "line = line.replace(\"01:07\", \"11:07\")\n"
                 "# same file, different story"},
        {"heading": "Chain of custody: hashing as a seal",
         "body": "You met hashlib when you were cracking passwords. Here "
                 "the same tool works FOR you. A hash is a short "
                 "fingerprint of some text, and changing a single "
                 "character produces a completely different fingerprint. "
                 "So a responder hashes the evidence the moment they "
                 "take it, and writes that fingerprint down. Anyone can "
                 "hash the copy again later: same fingerprint means "
                 "untouched, a different one means somebody edited it. "
                 "That written record of who held the evidence, plus its "
                 "hash, is what investigators call chain of custody.",
         "code": "import hashlib\n"
                 "stamp = hashlib.sha256(evidence.encode()).hexdigest()\n"
                 "# write `stamp` down the moment you collect the file"},
        {"heading": "The fix: a timeline MORTIS cannot reach",
         "body": "Evidence arrives from everywhere -- mail server, VPN, "
                 "the laptop itself -- and none of it arrives in order. "
                 "Put every event on one line, sort by timestamp, and "
                 "cause and effect appear on their own. To keep MORTIS "
                 "away from it, ship logs off the machine as they are "
                 "written, to a separate log server where records can be "
                 "added but never edited. A copy MORTIS cannot reach is "
                 "a copy MORTIS cannot rewrite.",
         "code": None}],
     "lesson": [
        {"heading": "1. hashlib again -- this time as proof",
         "body": ".encode() prepares text for hashing and .hexdigest() "
                 "hands the fingerprint back as readable characters. The "
                 "same text always gives the same fingerprint, so a "
                 "fingerprint taken today can be checked tomorrow.",
         "code": "import hashlib\n"
                 "hashlib.sha256(\"case 41\".encode()).hexdigest()\n"
                 "# -> 'a3f1...'  (64 characters, same every time)"},
        {"heading": "2. Comparing two hashes is the whole check",
         "body": "== asks 'are these the same?' and answers True or "
                 "False. Compare the fingerprint you wrote down with a "
                 "fresh one taken now. That single True is your proof "
                 "the evidence was never touched.",
         "code": "old = hashlib.sha256(\"report\".encode()).hexdigest()\n"
                 "new = hashlib.sha256(\"report\".encode()).hexdigest()\n"
                 "old == new    # -> True"},
        {"heading": "3. sorted() puts events in order",
         "body": "sorted() hands back a NEW list, in order, and leaves "
                 "the original alone. When the items are dictionaries "
                 "you have to say WHICH value to order by: write a small "
                 "function that pulls out that one value, then pass its "
                 "NAME to sorted as key. Position [0] is then the "
                 "earliest item of all.",
         "code": "def by_time(e):\n"
                 "    return e[\"time\"]\n\n"
                 "order = sorted(items, key=by_time)\n"
                 "order[0]      # -> the earliest item"}],
     "challenges": [
        {"title": "Seal the evidence",
         "goal": "`evidence` is one log line you have taken off the "
                 "breached machine. Hash it and store the fingerprint in "
                 "a variable called `stamp`. Type: "
                 "stamp = hashlib.sha256(evidence.encode()).hexdigest()",
         "seed": lambda: {"hashlib": hashlib,
                          "evidence": "02:41 backup.zip copied to "
                                      "45.13.9.7"},
         "intro": ["# `hashlib` is loaded. `evidence` holds one log "
                   "line:",
                   "#   '02:41 backup.zip copied to 45.13.9.7'",
                   "# Store its fingerprint in `stamp`."],
         "hint": "Same recipe as the hashing mission: .encode() the "
                 "text, hand that to hashlib.sha256, then ask the "
                 "result for .hexdigest(). The whole thing goes into "
                 "`stamp`.",
         "solution": "stamp = hashlib.sha256(evidence.encode())"
                     ".hexdigest()",
         "check": _c_mortis_stamp,
         "success": "Evidence sealed. From this second on, any edit "
                    "shows."},
        {"title": "Prove nobody touched it",
         "goal": "`evidence` is the collected log and `stored_stamp` is "
                 "the fingerprint written down when it was seized. Hash "
                 "the evidence again into `fresh_stamp`, then set "
                 "`unchanged` to whether the two are equal.",
         "seed": lambda: {"hashlib": hashlib,
                          "evidence": _MORTIS_LOG,
                          "stored_stamp": hashlib.sha256(
                              _MORTIS_LOG.encode()).hexdigest()},
         "intro": ["# `evidence` holds the three collected log lines.",
                   "# `stored_stamp` is the fingerprint taken at "
                   "seizure.",
                   "# Make `fresh_stamp` now, then store the True or",
                   "# False of comparing them in `unchanged`."],
         "hint": "Two lines. The first repeats the hashing recipe on "
                 "`evidence`. The second asks == whether your new "
                 "fingerprint and `stored_stamp` are the same, and "
                 "keeps that answer.",
         "solution": "fresh_stamp = hashlib.sha256("
                     "evidence.encode()).hexdigest()\n"
                     "unchanged = fresh_stamp == stored_stamp",
         "check": _c_mortis_verify,
         "success": "Two matching fingerprints -- the log is exactly as "
                    "it was seized."},
        {"title": "Build the timeline",
         "goal": "`events` is a list of dictionaries, each with a "
                 "'time' and a 'what', collected out of order. Write a "
                 "function `by_time(e)` that returns e['time'], build a "
                 "sorted copy of `events` called `timeline`, then store "
                 "the 'what' of the earliest event in `first`.",
         "seed": lambda: {"events": [
             {"time": "02:41", "what": "backup.zip copied off-site"},
             {"time": "01:07", "what": "vpn login from a new device"},
             {"time": "03:15", "what": "night analyst raised the alarm"},
             {"time": "00:52", "what": "attachment invoice.pdf.exe "
                                       "opened"},
             {"time": "02:08", "what": "admin account svc_backup2 "
                                       "created"}]},
         "intro": ["# `events` holds 5 dictionaries, shuffled. Each has",
                   "# a 'time' like '02:41' and a 'what'.",
                   "# The shape of the tool looks like this:",
                   "#   def by_time(e):",
                   "#       return e['time']",
                   "#   order = sorted(items, key=by_time)"],
         "hint": "sorted() has to be told which value to order by, so "
                 "write the tiny function first and pass its NAME as "
                 "key= (no brackets after the name). Then reach into "
                 "position [0] of your sorted list and read its 'what'.",
         "solution": "def by_time(e):\n"
                     "    return e['time']\n"
                     "timeline = sorted(events, key=by_time)\n"
                     "first = timeline[0]['what']",
         "check": _c_mortis_timeline,
         "success": "The alarm was the last event, not the first -- it "
                    "started with an attachment at 00:52."}],
     "boss_kind": "quiz",
     "boss_data": {
        "prompt": "MORTIS has already been through the logs. Show that "
                  "you can still prove what happened.",
        "win": "Sealed evidence and an ordered timeline. MORTIS edited "
               "the file and the fingerprint gave it away.",
        "rounds": [
            {"q": "Why hash a piece of evidence the MOMENT you collect "
                  "it?",
             "options": ["It makes the file smaller",
                         "So hashing it later proves nobody altered it",
                         "It encrypts the file so nobody can read it",
                         "It undoes the attacker's changes"],
             "answer": 1},
            {"q": "You change one character in a log file and hash it "
                  "again. What happens?",
             "options": ["The hash changes by one character",
                         "The hash stays the same",
                         "The hash comes out completely different",
                         "Hashing refuses to run on edited files"],
             "answer": 2},
            {"q": "Why sort incident events by timestamp?",
             "options": ["Order shows what came first and what it led "
                         "to",
                         "It makes the log file open faster",
                         "Sorting removes duplicate events",
                         "Investigators are required to sort "
                         "alphabetically"],
             "answer": 0}]}},
]
