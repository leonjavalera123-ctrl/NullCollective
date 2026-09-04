"""
bootcamp.py  --  Level 0: a gentle "never coded before?" training mission.
==========================================================================

This is for someone who has NEVER written a line of code. There is no villain
and no pressure -- just your ally ECHO walking you through the absolute basics:
what code is, what the terminal does, print(), variables, and a little math.

It reuses the same screens as the rest of the game:
    - a LESSON (BOOTCAMP_LESSON below) shown on the paged info screen
    - a LAB   (BOOTCAMP_CHALLENGES below) in the real Python terminal

The challenges here are deliberately TINY and very forgiving -- the goal is a
first win and a confidence boost, not a test.
"""

# ---------------------------------------------------------------------------
# THE LESSON CARDS  (plain English, zero assumptions)
# ---------------------------------------------------------------------------
BOOTCAMP_LESSON = [
    {"heading": "Welcome, recruit. I'm ECHO.",
     "body": "Before you fight hackers, you need to speak the computer's language: "
             "code. Don't worry -- you don't need to be 'good at computers'. Code is "
             "just a list of instructions you give the machine, one line at a time, "
             "in plain steps. If you can write a recipe, you can do this.",
     "code": None},
    {"heading": "What is the 'terminal'?",
     "body": "The terminal is a plain text box where you type one instruction, press "
             "Enter, and the computer does it right away and shows the result. In the "
             "next screen you'll get a real one. The >>> is just the computer saying "
             "'I'm ready -- type something.'",
     "code": ">>> 2 + 2\n4"},
    {"heading": "print(): make the computer talk",
     "body": "print() shows something on the screen. You put what you want to show "
             "inside the round brackets. Text goes inside quotes. That's it -- this "
             "is the most-used instruction in all of coding.",
     "code": "print(\"hello world\")     # shows:  hello world"},
    {"heading": "Variables: the computer's memory",
     "body": "A variable is a name you give to a value so the computer remembers it. "
             "The = sign means 'store this'. After the first line below, the name "
             "'agent' stands for the text 'you', and you can use it later.",
     "code": "agent = \"you\"\nprint(agent)     # shows:  you"},
    {"heading": "Computers are great at math",
     "body": "You can do math directly: + add, - subtract, * multiply, / divide. "
             "You can store the answer in a variable too. The computer never makes "
             "an arithmetic mistake -- that's part of why they're so powerful.",
     "code": "total = 5 + 7\nprint(total)     # shows:  12"},
    {"heading": "That's everything you need to start",
     "body": "print to show things, variables to remember things, math to calculate. "
             "Every hacker tool is built from these same small pieces. In the lab, "
             "try each tiny task -- use Hint and Show solution as much as you like. "
             "There are no wrong moves here. Ready?",
     "code": None},
]


# ---------------------------------------------------------------------------
# THE LAB CHALLENGES  (tiny + forgiving; a first win is the whole point)
# ---------------------------------------------------------------------------
def _said_something(t):
    # Pass if they produced ANY real output (and it wasn't an error message).
    out = t.last_run.strip()
    return out != "" and "Error" not in out

def _made_variable(t):
    # Pass if they created a variable named `me` holding anything at all.
    return "me" in t.ns

def _did_math(t):
    # Pass if they stored any number in a variable named `total`.
    val = t.ns.get("total")
    return isinstance(val, (int, float)) and not isinstance(val, bool)

BOOTCAMP_CHALLENGES = [
    {"title": "Make the computer talk",
     "goal": "Use print() to show a message. Type print, then your words inside "
             "round brackets and quotes. For example:  print(\"hello\")",
     "intro": ["# Type a print() line and press Enter.",
               "# Anything in quotes will appear below."],
     "hint": "print(\"I am learning to code\")",
     "solution": "print(\"hello world\")",
     "check": _said_something,
     "success": "You just made the computer talk. That's real code!"},
    {"title": "Remember something",
     "goal": "Create a variable named `me` and store anything in it -- your name, a "
             "word, a number. Use the = sign. For example:  me = \"vigilante\"",
     "intro": ["# Store a value under the name `me` using = .",
               "# Then type  me  and press Enter to see what it holds."],
     "hint": "me = \"vigilante\"",
     "solution": "me = \"vigilante\"",
     "check": _made_variable,
     "success": "The computer now remembers `me`. Variables are its memory."},
    {"title": "Be a calculator",
     "goal": "Add two numbers and store the answer in a variable named `total`. "
             "For example:  total = 5 + 7",
     "intro": ["# Do some math and save it in `total`.",
               "# Then type  total  to see the answer."],
     "hint": "total = 5 + 7",
     "solution": "total = 5 + 7",
     "check": _did_math,
     "success": "You stored a calculation. You're ready for Level 1 -- go get 'em."},
]


# ===========================================================================
# BOOT CAMP II  --  "FIELD NOTES"
# ===========================================================================
# The second on-ramp, and completely optional.
#
# Boot Camp I gets you as far as print(), variables and a bit of maths. Level 1
# then asks for lists AND loops AND if-statements, all in one mission. That is a
# lot of new ideas at once, and it's the most likely place for somebody to bounce
# off the game.
#
# So this exists: the same three ideas, one at a time, with nothing else going
# on. Nobody is ever made to play it, and nothing is gated behind it.
# ---------------------------------------------------------------------------

BOOTCAMP2_LESSON = [
    {"heading": "ECHO again. Nothing is wrong.",
     "body": "If Level 1 came at you fast, that isn't you being slow -- it "
             "introduces three new ideas at once. So we'll take them one at a "
             "time instead: a list, a decision, and a loop. That's the whole "
             "session. You can come back here whenever you like.",
     "code": None},
    {"heading": "A list holds several things at once",
     "body": "A variable holds one thing. A list holds a row of things, written "
             "inside square brackets with commas between them. It can hold text "
             "or numbers, and len() tells you how many are in there.",
     "code": "kit = [\"badge\", \"laptop\", \"pass\"]\nlen(kit)     # -> 3"},
    {"heading": "Reaching into a list",
     "body": "You pull one item out by its position, in square brackets. The "
             "catch that trips up everybody at first: counting starts at ZERO. "
             "So the first item is [0] and the second is [1]. Nobody finds that "
             "obvious. You just get used to it.",
     "code": "kit[0]      # -> 'badge'   (the FIRST one)\n"
             "kit[1]      # -> 'laptop'"},
    {"heading": "if / else: making a decision",
     "body": "`if` runs some code only when something is true, and `else` covers "
             "every other case. The line ends in a colon, and whatever belongs "
             "inside is indented -- pushed in by four spaces. That indent is how "
             "Python knows which lines are part of the decision.",
     "code": "n = 3\nif n > 5:\n    print(\"big\")\nelse:\n    print(\"small\")\n"
             "# shows: small"},
    {"heading": "for: doing something to every item",
     "body": "A for-loop takes each item in a list, one at a time, and runs the "
             "indented code with it. You choose the name for the current item -- "
             "here it is `thing`. The loop stops on its own when the list runs "
             "out, so you never have to count anything.",
     "code": "for thing in kit:\n    print(thing)\n"
             "# shows badge, then laptop, then pass"},
    {"heading": "The two together, which is the whole trick",
     "body": "Put an `if` inside a `for` and you can look at every item and act "
             "only on the ones you care about. That one shape -- go through "
             "everything, react to what matters -- is most of what security code "
             "does all day. You have now met every piece of it.",
     "code": "for thing in kit:\n    if thing == \"badge\":\n"
             "        print(\"found it\")"},
    {"heading": "That's the lot. Come back any time.",
     "body": "Three ideas: a list holds many things, an if decides, a for "
             "repeats. Try them below. Nothing here can break and nothing is "
             "scored. When they feel less strange, Level 1 will read very "
             "differently.",
     "code": None},
]


def _made_list(t):
    # Pass on any list of 2+ items called `kit`. What's in it is up to them.
    val = t.ns.get("kit")
    return isinstance(val, list) and len(val) >= 2


def _took_first(t):
    # Compare against THEIR list, so it works whatever they put in it.
    kit = t.ns.get("kit")
    if not isinstance(kit, list) or not kit:
        return False
    return "first" in t.ns and t.ns.get("first") == kit[0]


def _counted(t):
    # Three of the five preloaded words are shorter than six characters.
    return t.ns.get("weak") == 3


BOOTCAMP2_CHALLENGES = [
    {"title": "Make a list",
     "goal": "A list goes in square brackets with commas between the items. "
             "Make one called `kit` with at least two things in it -- anything "
             "you like. For example:  kit = [\"badge\", \"laptop\"]",
     "intro": ["# Square brackets, commas between the items.",
               "#   kit = [\"badge\", \"laptop\"]",
               "# Then type  kit  on its own to look at it."],
     "hint": "Start with  kit =  then open a square bracket, put your items in "
             "quotes with commas between them, and close the bracket.",
     "solution": "kit = [\"badge\", \"laptop\", \"pass\"]",
     "check": _made_list,
     "success": "That's a list: one name, holding several things at once."},
    {"title": "Take the first one out",
     "goal": "Pull the FIRST item out of `kit` and store it in a variable named "
             "`first`. Remember that counting starts at zero, so the first item "
             "sits at position 0.",
     "seed": lambda: {"kit": ["badge", "laptop", "pass"]},
     "intro": ["# `kit` is already made for this one:",
               "#   [\"badge\", \"laptop\", \"pass\"]",
               "# The first item lives at position 0."],
     "hint": "Put square brackets straight after the list's name, with the "
             "position number inside them.",
     "solution": "first = kit[0]",
     "check": _took_first,
     "success": "Position 0 is the first one. That off-by-one catches everybody "
                "once, and then never again."},
    {"title": "Look at every one, react to some",
     "goal": "`words` holds five passwords. Count how many are shorter than 6 "
             "characters and store the total in `weak`. Start `weak` at 0, loop "
             "over `words`, and add 1 whenever len(w) is less than 6.",
     "seed": lambda: {"words": ["cat", "sunshine", "dog", "password1", "sun"]},
     "intro": ["# words = [\"cat\", \"sunshine\", \"dog\", \"password1\", \"sun\"]",
               "# Type these four lines, then press Enter on a BLANK line:",
               "#   weak = 0",
               "#   for w in words:",
               "#       if len(w) < 6:",
               "#           weak += 1"],
     "hint": "Three moving parts: start the counter at 0, loop with `for`, and "
             "put an `if` inside the loop that adds 1.",
     "solution": "weak = 0\nfor w in words:\n    if len(w) < 6:\n        weak += 1",
     "check": _counted,
     "success": "Three short ones. A loop with an if inside it -- that shape is "
                "most of security code, and you just wrote it."},
]


# ===========================================================================
# THE EXTRA MODULES TABLE
# ===========================================================================
# Boot camps are not part of the campaign: no boss, no villain, nothing gated
# behind them. But the rest of the game addresses everything by level number, so
# they need one.
#
# Rather than sprinkle `if level == 0` through the codebase -- and then add a
# second one for 29 -- everything that isn't a campaign mission lives in this
# table. pykernel.py and main.py look here first and fall back to the campaign.
#
# The numbers look odd (0 before the start, 29 past the end) and that is fine.
# The number decides nothing about WHEN you meet a module; the office's ticket
# list does that. FIELD NOTES is offered on the first floor, right beside the
# mission it exists to soften.
EXTRA_MODULES = {
    0: {
        "title": "BOOT CAMP",
        "brief": "New-hire competency check. Nothing here is graded, and "
                 "nothing here can go wrong.",
        "lesson": BOOTCAMP_LESSON,
        "challenges": BOOTCAMP_CHALLENGES,
    },
    29: {
        "title": "FIELD NOTES",
        "brief": "Optional refresher. Lists, decisions and loops -- one at a "
                 "time, with nothing else going on.",
        "lesson": BOOTCAMP2_LESSON,
        "challenges": BOOTCAMP2_CHALLENGES,
    },
}
