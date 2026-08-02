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
]
