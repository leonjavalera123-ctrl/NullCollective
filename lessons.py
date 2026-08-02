"""
lessons.py  --  gentle, example-first Python lessons, one set per level.
========================================================================

These run on a NEW screen that appears between the Intel briefing and the Lab:

    Brief -> Intel (what the hacker does) -> LESSON (the Python, slowly) -> Lab

The goal is a calm, steady ramp for a total beginner. Each lesson is a list of
small "cards". Every card teaches ONE idea in plain words with a tiny runnable
example, so nothing in the Lab feels like a surprise.

`LESSONS[n]` is the list of cards for level n. A card is a dictionary:
    heading -> the idea's name
    body    -> a plain-English explanation
    code    -> a short example you could type yourself (or None)

The same screen class that shows Intel also shows these (see labscene.IntelScene),
just with a green "example" style instead of the red "attacker" style.
"""

LESSONS = {
    # ----------------------------------------------------------------- LEVEL 1
    1: [
        {"heading": "1. Variables: labeled boxes",
         "body": "A variable is a name that points at a value. The = sign means "
                 "'store the value on the right under the name on the left'. After "
                 "this, the name 'tries' stands for the number 0, and you can use "
                 "it anywhere.",
         "code": "tries = 0\nname = \"vigilante\"\nprint(name)   # -> vigilante"},
        {"heading": "2. Strings are text",
         "body": "Text goes inside quotes -- single ' ' or double \" \" both work. "
                 "len() tells you how many characters a string has. Length is the "
                 "single biggest factor in how strong a password is.",
         "code": "pw = \"sunshine\"\nlen(pw)        # -> 8"},
        {"heading": "3. Comparisons answer yes/no",
         "body": "A comparison like >= ('greater than or equal to') gives back a "
                 "boolean: True or False. == means 'are these equal?' (two equals "
                 "signs, because one equals sign already means 'store').",
         "code": "len(pw) >= 12     # -> False (sunshine is only 8)\n"
                 "pw == \"sunshine\"  # -> True"},
        {"heading": "4. Loops repeat work",
         "body": "A for-loop runs the same code once for every item in a list. This "
                 "is how an attacker tries thousands of passwords -- and how you'll "
                 "do it in the Lab. The indented line is what repeats.",
         "code": "for guess in [\"abc\", \"123\", \"letmein\"]:\n    print(guess)"},
    ],
    # ----------------------------------------------------------------- LEVEL 2
    2: [
        {"heading": "1. Functions: reusable recipes",
         "body": "A function is a named block of code you can run again and again. "
                 "You 'define' it with def, and 'call' it with its name and (). "
                 "return hands a value back to whoever called it.",
         "code": "def double(x):\n    return x * 2\n\ndouble(5)   # -> 10"},
        {"heading": "2. Letters are secretly numbers",
         "body": "Every character has a code number. ord() gives you the number for "
                 "a letter; chr() turns a number back into a letter. Ciphers do "
                 "math on these numbers to scramble text.",
         "code": "ord(\"A\")   # -> 65\nchr(66)    # -> 'B'"},
        {"heading": "3. Modulo (%) wraps around",
         "body": "The % operator gives the remainder after dividing. It's perfect "
                 "for looping back to the start: once you pass the 26th letter, "
                 "% 26 sends you back to the beginning of the alphabet.",
         "code": "27 % 26    # -> 1  (wrapped past Z back to the 2nd letter)\n"
                 "25 % 26    # -> 25 (still inside the alphabet)"},
    ],
    # ----------------------------------------------------------------- LEVEL 3
    3: [
        {"heading": "1. Lists hold many items in order",
         "body": "A list is a row of values inside square brackets. You read an "
                 "item by its position number, starting at 0. Lists are how we hold "
                 "a whole inbox of emails at once.",
         "code": "inbox = [\"hi\", \"sale\", \"urgent\"]\ninbox[0]    # -> 'hi'\n"
                 "len(inbox)  # -> 3"},
        {"heading": "2. Dictionaries label their values",
         "body": "A dictionary stores values under names (called 'keys') using curly "
                 "braces. You look a value up by its key. An email is naturally a "
                 "dictionary: a sender, a subject, a body.",
         "code": "email = {\"sender\": \"bob\", \"subject\": \"hi\"}\n"
                 "email[\"sender\"]   # -> 'bob'"},
        {"heading": "3. 'in' searches; '.lower()' evens the case",
         "body": "The word in checks whether something is contained in text or a "
                 "list. .lower() makes text all lowercase first, so 'URGENT' and "
                 "'urgent' match. Together they spot phishing scare-words.",
         "code": "\"urgent\" in \"URGENT sale\".lower()   # -> True"},
    ],
    # ----------------------------------------------------------------- LEVEL 4
    4: [
        {"heading": "1. Dictionaries as instant lookups",
         "body": "When you have a key and want its value fast, a dictionary is "
                 "ideal. Here the port number is the key and the service name is "
                 "the value -- one lookup turns 22 into 'SSH'.",
         "code": "services = {22: \"SSH\", 443: \"HTTPS\"}\nservices[22]   # -> 'SSH'"},
        {"heading": "2. 'in' and 'not in'",
         "body": "in asks 'is this present?'; not in asks the opposite. Defenders "
                 "keep a list of allowed ports and flag anything that is NOT in it.",
         "code": "known = [22, 443]\n31337 in known      # -> False\n"
                 "31337 not in known  # -> True (suspicious!)"},
        {"heading": "3. Build a list as you loop",
         "body": "Start with an empty list [], then .append() items onto it while "
                 "you loop. This is how you collect every suspicious port into a "
                 "results list to investigate.",
         "code": "bad = []\nfor p in [22, 31337]:\n    if p not in [22, 443]:\n"
                 "        bad.append(p)\nbad   # -> [31337]"},
    ],
    # ----------------------------------------------------------------- LEVEL 5
    5: [
        {"heading": "1. f-strings build text with values",
         "body": "Put an f before a string and you can drop variables right inside "
                 "{ } . It's super handy -- but gluing UNTRUSTED user input into a "
                 "database command this way is exactly how SQL injection happens.",
         "code": "user = \"alice\"\nf\"hello {user}\"   # -> 'hello alice'"},
        {"heading": "2. Strings can inspect themselves",
         "body": ".count() counts how many times something appears; .replace() swaps "
                 "one piece of text for another. Defenders use these to spot and "
                 "strip dangerous characters like the single quote ( ' ).",
         "code": "s = \"a'b'c\"\ns.count(\"'\")        # -> 2\n"
                 "s.replace(\"'\", \"\")   # -> 'abc'"},
        {"heading": "3. Functions that answer True/False",
         "body": "A function can return a boolean to act as a 'detector'. You call "
                 "it on some input and it reports whether the input is dangerous -- "
                 "a tiny, reusable security check.",
         "code": "def is_attack(text):\n    return \"or '1'='1\" in text.lower()\n\n"
                 "is_attack(\"' OR '1'='1\")   # -> True"},
    ],
    # ----------------------------------------------------------------- LEVEL 6
    6: [
        {"heading": "1. Objects bundle data together",
         "body": "An object is one 'thing' that holds several related facts. A file "
                 "object knows its name, its publisher, and whether it's malware. "
                 "You read each fact with a dot:  file.name.",
         "code": "# if f is a File object:\nf.name        # -> 'invoice.pdf.exe'\n"
                 "f.is_malware  # -> True"},
        {"heading": "2. A class is the blueprint",
         "body": "A class describes how to build objects of some kind. __init__ runs "
                 "when you create one and stores its data using self. You then make "
                 "as many objects from the blueprint as you like.",
         "code": "class File:\n    def __init__(self, name):\n        self.name = name\n\n"
                 "f = File(\"song.mp3\")\nf.name   # -> 'song.mp3'"},
        {"heading": "3. Splitting strings to inspect them",
         "body": ".split('.') chops a string wherever a dot appears, giving a list "
                 "of pieces. Taking the last piece with [-1] reveals a file's REAL "
                 "type -- how we catch a sneaky double extension.",
         "code": "\"invoice.pdf.exe\".split(\".\")     # -> ['invoice','pdf','exe']\n"
                 "\"invoice.pdf.exe\".split(\".\")[-1]  # -> 'exe'"},
    ],
    # ----------------------------------------------------------------- LEVEL 7
    7: [
        {"heading": "1. What is a hash?",
         "body": "A hash is a one-way scramble of text into a fixed-length code. The "
                 "same input ALWAYS gives the same hash, but you can't run it "
                 "backwards to get the text. That's why websites store the hash of "
                 "your password instead of the password itself.",
         "code": "# same input -> same hash, every time\n"
                 "# 'password' -> '5e884898da028...' (can't be reversed)"},
        {"heading": "2. Using a library: hashlib",
         "body": "Python comes with hashlib, a ready-made tool for hashing. You "
                 "'import' it, then call sha256 on your text. .encode() prepares the "
                 "text and .hexdigest() gives the hash as readable characters. Using "
                 "libraries means you don't reinvent the wheel.",
         "code": "import hashlib\n"
                 "hashlib.sha256(\"hello\".encode()).hexdigest()\n"
                 "# -> '2cf24dba5fb0a30e26e83b2ac5b9e29e...'"},
        {"heading": "3. How attackers crack hashes",
         "body": "Since a hash can't be reversed, attackers GUESS: they hash every "
                 "word in a list and look for a matching hash. A common password is "
                 "in their list, so it's found fast. A long, unusual password never "
                 "is. You'll write this exact loop in the lab.",
         "code": "for guess in wordlist:\n"
                 "    if myhash(guess) == stolen_hash:\n"
                 "        print('cracked:', guess)"},
    ],
    # ----------------------------------------------------------------- LEVEL 8
    8: [
        {"heading": "1. Two factors: know + have",
         "body": "A password is 'something you KNOW'. Two-factor authentication adds "
                 "'something you HAVE' -- a 6-digit code on your phone. An attacker "
                 "with your password still can't log in without that second factor.",
         "code": "# login needs BOTH:\n# 1) the password   2) the current 6-digit code"},
        {"heading": "2. The codes are just math",
         "body": "Your phone makes the code from a shared secret and a changing "
                 "counter, squeezed to 6 digits with modulo (%). If the number is "
                 "short, .zfill(6) pads it with zeros so it's always six digits.",
         "code": "code = (secret + counter) % 1000000\n"
                 "str(42).zfill(6)     # -> '000042'"},
        {"heading": "3. The one rule: never share your code",
         "body": "The math is unbreakable, so attackers attack YOU -- a fake message "
                 "asking you to 'verify' by sending the code. Real services never ask "
                 "for it. In the lab you'll build a code generator; in the boss "
                 "fight you'll refuse the trick and lock NULL out.",
         "code": None},
    ],
    # ----------------------------------------------------------------- LEVEL 9
    9: [
        {"heading": "1. any() checks a whole collection",
         "body": "any() is True if AT LEAST ONE item passes a test. Paired with a "
                 "quick loop inside it, it answers questions like 'does this password "
                 "contain any digit?' in a single line.",
         "code": "any(c.isdigit() for c in \"abc123\")   # -> True\n"
                 "any(c.isdigit() for c in \"abcdef\")   # -> False"},
        {"heading": "2. Small functions combine into tools",
         "body": "Everything you've learned -- variables, loops, ifs, lists, dicts, "
                 "functions -- snaps together. A real security tool is just several "
                 "small, clear functions working as a team.",
         "code": "def strength(pw):\n    score = 0\n    if len(pw) >= 12:\n"
                 "        score += 1\n    return score"},
        {"heading": "3. You're ready",
         "body": "The capstone asks you to write a couple of these little functions "
                 "yourself, then face NULL. Take it slow, read each goal, and lean "
                 "on Hint and Show solution whenever you want. You've got this.",
         "code": None},
    ],
}
