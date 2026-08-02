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
