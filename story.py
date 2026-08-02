"""
story.py  --  All the words/narration of the game in one place.
===============================================================

We keep story text separate from game logic. That's a common, tidy habit:
"data" (the words) lives apart from "behavior" (the code that uses the words).
If you ever want to rewrite the story, you only touch THIS file.

Each entry below is just a string variable. Triple-quoted strings ( \"\"\" ... \"\"\" )
can span many lines, which is perfect for paragraphs.
"""

# The hero's codename. Change this to whatever handle you want!
HERO = "CIPHER-7"

INTRO = """The year is 2026. A hacker syndicate called the NULL COLLECTIVE has
gone to war with the digital world -- draining bank accounts, hijacking
hospitals, and selling people's secrets to the highest bidder.

The police can't keep up. The corporations are scared.

But in the shadows, one ethical vigilante answers the call. A defender who
fights hackers with their own tools -- and never crosses the line.

That's you. Codename: %s.

NULL has eight lieutenants, each a master of one dark art. Beat them all, and
their leader -- NULL itself -- will finally have to face you.

Suit up. The first attack is already underway.""" % HERO

# A short briefing shown before each level. Stored in a dictionary keyed by
# level number, so a level can ask for story.BRIEFINGS[1], etc.
BRIEFINGS = {
    1: ("THE CRACKER",
        "A bank vault's login is under attack. The Cracker brute-forces weak "
        "passwords by trying millions of guesses per second. Watch how fast a "
        "weak password falls -- then build one strong enough to lock NULL out."),
    2: ("CIPHER",
        "Cipher hides NULL's orders inside scrambled text. Their favorite trick "
        "is the Caesar cipher: every letter shifted down the alphabet by a secret "
        "amount. Crack the shift, read the message, expose their next target."),
    3: ("MIRAGE",
        "Mirage is a social engineer. No code is broken -- people are tricked into "
        "handing over passwords through fake 'phishing' emails. Your job: tell the "
        "real messages from the fakes before an employee clicks the wrong link."),
    4: ("GHOST",
        "Ghost slips through networks. Every computer has numbered 'ports' -- "
        "doors that services listen on. Ghost left a hidden backdoor on an unusual "
        "port. Scan the connections and find the intruder among the normal traffic."),
    5: ("THE INJECTOR",
        "The Injector attacks websites. A sloppy login form lets attackers type "
        "tricky input that the database mistakes for a command -- a 'SQL injection'. "
        "Use it to break into NULL's stolen-data server, then choose the fix."),
    6: ("PLAGUE",
        "Plague spreads malware -- malicious files disguised as harmless ones. "
        "An infected machine is full of suspicious files. Inspect each one, spot "
        "the red flags, and quarantine the malware without deleting safe files."),
    7: ("RIPPER",
        "RIPPER stole a password database -- but it only holds hashed (one-way "
        "scrambled) passwords. RIPPER cracks the weak ones by hashing common "
        "guesses until they match. Learn hashing, then flag which accounts are at "
        "risk before RIPPER gets to them."),
    8: ("RELAY",
        "RELAY can't beat two-factor authentication with code, so it tricks people "
        "into reading out the 6-digit codes on their phones. Learn how those codes "
        "work, refuse RELAY's phishing, and use your code to lock NULL out."),
    9: ("NULL",
        "This is it. NULL combines every trick its lieutenants used. Survive a "
        "gauntlet of all eight skills, then seal NULL away for good. Everything you "
        "learned comes down to this."),
}

# Shown after a level is beaten -- a short "what you just learned" debrief.
DEBRIEFS = {
    1: "Lesson: length beats complexity. A long passphrase is far harder to "
       "brute-force than a short 'P@ss1' -- every extra character multiplies the "
       "guesses an attacker needs.",
    2: "Lesson: the Caesar cipher is easy to break because there are only 25 "
       "possible shifts. Real encryption uses keys so large that trying them all "
       "would take longer than the age of the universe.",
    3: "Lesson: phishing preys on urgency and trust, not on broken code. Check the "
       "sender, hover before you click, and be suspicious of 'act now' pressure.",
    4: "Lesson: attackers hide on unusual ports. Defenders close every door they "
       "don't need and watch the ones they keep open.",
    5: "Lesson: never trust user input. Parameterized queries keep data and "
       "commands separate so typed text can't become a command.",
    6: "Lesson: malware hides behind familiar names and icons. Double extensions, "
       "unknown publishers, and 'too good to be true' files are classic red flags.",
    7: "Lesson: sites store one-way hashes, not passwords. Strong passwords survive "
       "a stolen database; common ones are cracked by a wordlist in seconds. (Real "
       "systems also add a random 'salt' so identical passwords don't share a hash.)",
    8: "Lesson: 2FA adds 'something you have' to 'something you know', stopping "
       "attackers who only have your password. The one weak point is you sharing "
       "the code -- so never do, no matter who asks.",
    9: "You did it. NULL is sealed away and all eight arts -- passwords, cryptography, "
       "phishing, networks, web security, malware, hashing, and 2FA -- are now yours "
       "to defend with.",
}

OUTRO = """NULL COLLECTIVE: DISMANTLED.

The banks are safe. The hospitals are back online. Somewhere, a hundred people
you'll never meet still have their savings because of what you did tonight.

You learned to think like an attacker -- so you could protect like a guardian.

That's what an ethical hacker is.

-- THE END --
Thanks for playing. Now go read the code: every level you beat is a Python
lesson waiting in the levels/ folder."""
