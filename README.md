# NULL Collective — an ethical-hacking adventure 🛡️

A small graphical game (built with **pygame**) where you play an ethical
vigilante taking down a hacker syndicate, **one cybersecurity skill at a time**.
It was built to teach **Python** and **cybersecurity** side by side — every level
is both a boss fight and a coding lesson.

---

## ▶️ How to run it

1. Make sure pygame is installed (only needed once):
   ```
   pip install pygame
   ```
2. From inside this `NullCollective` folder, run:
   ```
   python main.py
   ```
3. Click **START MISSION**. Press **ESC** any time to return to the menu.

---

## 🗺️ Each level is a 5-part mission

Every level runs in five stages so you *learn* the Python slowly, then *use* it:

1. **🛰️ Briefing** — the story setup for the mission.
2. **🔍 Intel** — explains *what the enemy hacker actually does*, showing the real
   Python an attacker would write, line by line.
3. **📘 Python Lesson** — *new!* a calm, example-first walkthrough of the exact
   Python concepts the Lab will use, one small card at a time. Nothing in the Lab
   comes as a surprise.
4. **💻 Terminal Lab** — a **real working Python interpreter inside the game**. You
   type real code, see real output and real errors, and solve 5 security-themed
   challenges (with a **Hint** and **Show solution** button on every one).
5. **🎯 Boss Fight** — the interactive challenge where you *apply* what you practiced.

So the flow per level is: **Brief → Intel → Lesson → Lab → Boss → Debrief**.

| Lvl | Boss | Security skill | Python you practice in the Lab |
|----|------|----------------|------------------|
| 1 | **The Cracker** | Strong passwords & brute-force | variables, strings, for-loops, `if` |
| 2 | **Cipher** | Cryptography (Caesar cipher) | functions, `ord`/`chr`, modulo `%` |
| 3 | **Mirage** | Phishing & social engineering | lists, dictionaries, `in`, counting |
| 4 | **Ghost** | Networks, ports & intrusion | dict lookups, `not in`, filtering a list |
| 5 | **The Injector** | Web security (SQL injection) | f-strings, detector functions |
| 6 | **Plague** | Malware identification | **classes**, objects, `.attributes` |
| 7 | **BRUTUS** | Passwords, going deeper | booleans, `any()`, verdict functions |
| 8 | **VEX** | Cryptography: the XOR trick | the `^` operator, reversible ciphers |
| 9 | **SCRIPTER** | Web security: XSS | `in`/`.replace()`, detector functions |
| 10 | **TRACE** | Networks: reading the logs | list-of-dicts, counting, thresholds |
| 11 | **LOCKJAW** | Malware: ransomware & backups | `.endswith()`, counting, recovery logic |
| 12 | **RIPPER** | Password hashing & cracking | the real `hashlib` library, hashing loops |
| 13 | **RELAY** | 2FA / one-time codes | modulo, `.zfill()`, generator functions |
| 14 | **NULL** | Final boss — all skills | capstone: combine everything |

The game is built to **grow toward ~30 levels**. New levels are added as pure
*data* (see `datalevels.py`) using two reusable boss types — a **Quiz** field test
and a **Flag-the-threats** hunt — so the campaign can expand without new screens.

There's also a **Boot Camp (Level 0)** on the menu — a friendly, villain-free
training mission run by your ally ECHO that teaches coding from absolute zero
(`print()`, variables, simple math) for anyone who has never written code before.

Everything is **simulated and ethical** — you defend systems, spot attacks, and
solve in-game puzzles. No real systems are ever touched.

### 💻 Using the Terminal Lab

It works just like the real Python prompt:

- Type code after `>>>` and press **Enter**. Expressions show their value (`2+2` → `4`).
- **Multi-line blocks** (for-loops, `if`, `def`): type the first line ending in `:`,
  press Enter, type the indented lines, then press **Enter on a blank line** to run.
- **Tab** inserts an indent. **↑ / ↓** recall past commands. Errors are shown in red
  to learn from — they won't crash the game.
- Stuck? Click **Hint**, then **Show solution**, or **Skip** to move on.

There are **33 challenges** in total — each level has 5 (two gentle warm-ups, then
the harder ones), and the final level adds a 3-part capstone.

### ⚡ Your code carries into the boss fights

Functions you write in a lab are collected into a **toolkit** and handed to the
boss fight. Where it fits, the boss actually *runs your code*:

- **Cipher** — your `enc()` is run to prove it reproduces NULL's cipher.
- **Plague** — your `is_double_ext()` auto-scans the filenames for you.
- **The Injector** — your `clean()` is run live to neutralize the attack you used.

Look for the cyan **"Powered by your Lab code"** line. (If you skip a lab, the boss
falls back to its own version — you'll never get stuck.)

---

## 🧭 The main menu

- **Continue** — resume at your next unfinished level (appears once you've cleared one).
  Your progress auto-saves to `savegame.json` after every level you beat.
- **New Game** — start fresh (also wipes your saved progress).
- **Select Level (replay)** — jump back into any level you've reached to retry it.
  Cleared levels and your next level are unlocked; later ones stay LOCKED until
  you get there.
- **Free Play (Sandbox)** — the Python terminal on its own, with sample data loaded,
  to experiment with no goal or pressure. Includes a **Clear Screen** button.
- **Glossary** — a scrollable, plain-English dictionary of **46 terms** across three
  sections: Python basics, cybersecurity, and real-life staying-safe tips (use a
  passphrase, turn on 2FA, think before you click…). Scroll with the wheel or ↑/↓.

Your progress is saved automatically to `savegame.json` after each level.

---

## 🎬 Sound, music & animation

- **Music** — a soft looping ambient track plays in the background.
- **Sound effects** — clicks, a success chime when you solve a challenge, a buzz
  when your code errors, and a fanfare when you beat a level.
- **Press `M`** anytime to mute / unmute everything.
- **Animation** — falling "matrix" code behind the menu, story screens, intel,
  lessons, labs, and sandbox; a pulsing title; and a smooth fade-in on every
  screen change. (Behind the labs it's kept faint so the terminal stays crisp.)

All audio is **synthesized from scratch** by `make_audio.py` (no downloads). If
you ever want to change a sound, edit that file and re-run `python make_audio.py`.
On a computer with no speakers the game just runs silently — nothing breaks.

---

## 📖 Suggested reading order (this is the real lesson)

You said you'd learn by reading, so read the files in this order. Each is
heavily commented and explains the "why" of every line:

1. **`engine.py`** — the toolkit. Learn `Button`, `TextInput`, drawing text, and
   the `Scene` blueprint that every level is built from. *Start here.*
2. **`main.py`** — the game loop and how scenes switch. The "conductor".
3. **`story.py`** — all the words. Easiest file; good confidence boost.
4. **`pyterminal.py`** — how the in-game Python interpreter actually runs your code
   (`compile`, `eval`, `exec`, capturing output). Fascinating once you've used it.
5. **`labscene.py`** — how the Intel pages and Lab challenges are presented.
6. **`levels/level1_passwords.py`** → **`level9_null.py`** — read them in order.
   Each file now also holds that level's `INTEL` (the hacker explainer) and
   `CHALLENGES` (the lab tasks, each with its `check` function). By Level 6 you'll
   meet your first `class` of your own.

---

## 🛠️ Easy things to try changing (great practice!)

- In `story.py`, change `HERO = "CIPHER-7"` to **your own codename**.
- In `level1_passwords.py`, change the win threshold `score >= 6` to make it
  harder or easier.
- In `level2_cipher.py`, change `PLAINTEXT` and `SECRET_SHIFT` to hide your own
  message.
- In `level3_phishing.py`, add a new email to the `EMAILS` list — copy an existing
  dictionary and edit it.
- In any level file, add a **new lab challenge**: copy a dictionary in `CHALLENGES`,
  change the `goal`, `solution`, and `check` — instant new coding puzzle.
- In `engine.py`, change a color in the `COLORS` dictionary and watch the whole
  game re-theme.

If you break something, the error message in the terminal usually names the file
and line number — read it, it's trying to help you.

---

## 📂 File map

```
NullCollective/
├── main.py                     ← run this
├── engine.py                   ← reusable toolkit (read first)
├── pyterminal.py               ← the in-game Python interpreter
├── labscene.py                 ← Intel pages + Lab challenge screens
├── lessons.py                  ← the beginner Python lesson cards (one set per level)
├── bootcamp.py                 ← Level 0 Boot Camp: lesson + tiny lab for total beginners
├── bosses.py                   ← reusable data-driven bosses (QuizBoss, FlagBoss)
├── datalevels.py               ← extra levels defined purely as data (the scalable path)
├── extras.py                   ← Free Play sandbox, Glossary, Level Select screens
├── save.py                     ← saves/loads your progress
├── audio.py                    ← plays sound effects + music
├── effects.py                  ← the matrix-rain background animation
├── story.py                    ← all narration
├── make_icon.py                ← (optional) regenerates the desktop icon
├── make_audio.py               ← (optional) regenerates the sound files
├── assets/icon.ico             ← the shield icon
├── assets/audio/*.wav          ← synthesized sounds + music
├── savegame.json               ← your progress (created automatically)
├── README.md                   ← you are here
└── levels/
    │   (each level file holds its INTEL, CHALLENGES, and boss Scene)
    ├── level1_passwords.py     ← The Cracker
    ├── level2_cipher.py        ← Cipher
    ├── level3_phishing.py      ← Mirage
    ├── level4_network.py       ← Ghost
    ├── level5_injection.py     ← The Injector
    ├── level6_malware.py       ← Plague
    ├── level7_hashing.py       ← RIPPER (password hashing)
    ├── level8_twofactor.py     ← RELAY (2FA / one-time codes)
    └── level9_null.py          ← NULL (final boss)
```

Have fun, vigilante. 🥷
