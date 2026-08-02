"""
LEVEL 3  --  MIRAGE   (Phishing & social engineering)
=====================================================

Security idea you learn:
    The weakest part of any system is usually a human. "Phishing" is a fake
    message designed to trick someone into clicking a bad link or giving up a
    password. The classic red flags: a wrong/odd sender address, urgent threats
    ("act now or lose access!"), and links that don't match the real company.

Python you learn:
    - a LIST that holds many items, read in order with an index number
    - a DICTIONARY to bundle related facts about one email (sender, body, ...)
    - moving through the list by increasing an index variable
    - comparing the player's choice to the stored answer (True/False)

How the level plays:
    You triage NULL's inbox attack. For each message, decide PHISHING or SAFE.
    After each call you see the red flags. Get 4 of 5 right to clear the level.
"""

import pygame
from engine import Scene, Button, draw_text, COLORS, WIDTH, HEIGHT


# ===========================================================================
# INTEL  --  what Mirage does.
# ===========================================================================
INTEL = [
    {
        "heading": "What Mirage does",
        "body": "Mirage breaks no code -- Mirage breaks people. A 'phishing' email "
                "impersonates someone you trust and pressures you to click a link "
                "or hand over a password. Attackers send thousands at once with a "
                "simple loop, then wait for anyone to take the bait:",
        "code": "for victim in employee_list:\n"
                "    send_fake_email(victim, subject='URGENT: verify your account')",
    },
    {
        "heading": "Detecting it with Python",
        "body": "Defenders flag suspicious mail automatically. The `in` keyword "
                "checks if text contains something; .endswith() checks how a string "
                "finishes. Together they catch fake domains and panic words:",
        "code": "if not sender.endswith('@yourcompany.com'):\n"
                "    flag('sender is not internal')\n"
                "if 'verify your account' in body.lower():\n"
                "    flag('classic phishing phrase')",
    },
    {
        "heading": "Real scenario",
        "body": "In 2016 a single phishing email -- a fake 'change your password' "
                "notice -- led to a major political email breach. One click. The "
                "lab teaches you to read an email like data: pull it apart, check "
                "the sender, and count the threats.",
        "code": None,
    },
]


# ===========================================================================
# CHALLENGES
# ===========================================================================
def _check_sender(t):
    return t.ns.get("sender") == "support@amaz0n-verify.net"

def _check_isfake(t):
    return t.ns.get("is_fake") is True

def _check_count(t):
    return t.ns.get("count") == 3

def _check_lower(t):
    return t.ns.get("low") == "urgent: verify your account now"

def _check_has_word(t):
    return t.ns.get("has_urgent") is True

CHALLENGES = [
    {
        "title": "Read a dictionary",
        "goal": "`email` is a dictionary describing one message. Pull its 'sender' "
                "value out and store it in a variable named `sender`. Access a dict "
                "value with square brackets:  email['sender'].",
        "seed": lambda: {"email": {"sender": "support@amaz0n-verify.net",
                                   "subject": "URGENT: verify now",
                                   "body": "click here to verify your account"}},
        "intro": ["# `email` is a dict with keys: 'sender', 'subject', 'body'.",
                  "# Try:  email['subject']   then store the sender."],
        "hint": "sender = email['sender']",
        "solution": "sender = email['sender']",
        "check": _check_sender,
        "success": "That's how you read one labeled field out of a dictionary.",
    },
    {
        "title": "Make text lowercase",
        "goal": "Comparing text is easier when it's all one case. Use the .lower() "
                "method on `subject` and store the lowercase version in `low`.",
        "seed": lambda: {"subject": "URGENT: Verify Your Account NOW"},
        "intro": ["# `subject` has mixed capitals. Try:  subject.lower()",
                  "# Store the all-lowercase result in `low`."],
        "hint": "low = subject.lower()",
        "solution": "low = subject.lower()",
        "check": _check_lower,
        "success": "Lowercasing first means 'URGENT' and 'urgent' match. Handy for filters.",
    },
    {
        "title": "Does it contain a scare word?",
        "goal": "The `in` keyword checks if text contains something. Set "
                "`has_urgent` to True if the word 'urgent' appears anywhere in "
                "`subject` (lowercased first).",
        "seed": lambda: {"subject": "URGENT: Verify Your Account NOW"},
        "intro": ["# Phishing loves panic words. Is 'urgent' inside the subject?",
                  "# Try:  'urgent' in subject.lower()   -> True or False"],
        "hint": "has_urgent = 'urgent' in subject.lower()",
        "solution": "has_urgent = 'urgent' in subject.lower()",
        "check": _check_has_word,
        "success": "Caught the scare word. Real spam filters scan for exactly this.",
    },
    {
        "title": "Spot the fake domain",
        "goal": "The only trusted domain is '@yourcompany.com'. Set a variable "
                "`is_fake` to True if `sender` does NOT end with that domain. Use "
                "the .endswith() string method.",
        "seed": lambda: {"sender": "support@amaz0n-verify.net"},
        "intro": ["# `sender` is preloaded. Is it from @yourcompany.com?",
                  "# Tip:  sender.endswith('@yourcompany.com')  -> True/False"],
        "hint": "is_fake = not sender.endswith('@yourcompany.com')",
        "solution": "is_fake = not sender.endswith('@yourcompany.com')",
        "check": _check_isfake,
        "success": "Correct -- that address is impersonating a brand. is_fake is True.",
    },
    {
        "title": "Count the threats",
        "goal": "`inbox` is a list of email dicts, each with a 'phishing' key that's "
                "True or False. Loop over it and count how many are phishing, "
                "storing the total in `count`.",
        "seed": lambda: {"inbox": [
            {"subject": "lunch?", "phishing": False},
            {"subject": "URGENT verify", "phishing": True},
            {"subject": "gift cards now", "phishing": True},
            {"subject": "weekly digest", "phishing": False},
            {"subject": "reset your password", "phishing": True}]},
        "intro": ["# `inbox` = list of 5 email dicts, each has key 'phishing'.",
                  "# Start count = 0, loop, and add 1 when email['phishing'] is True."],
        "hint": "count = 0  /  for email in inbox:  /  if email['phishing']:  /  count += 1",
        "solution": "count = 0\nfor email in inbox:\n    if email['phishing']:\n"
                    "        count += 1",
        "check": _check_count,
        "success": "Three phishing emails caught by code. This is real-world triage.",
    },
]


# A list of emails. Each email is a dictionary -- a labeled bundle of facts.
# `phishing` is the correct answer; `why` explains it after the player chooses.
EMAILS = [
    {
        "sender": "it-support@your-company.com",
        "subject": "Scheduled maintenance this weekend",
        "body": "Hi team, our servers will reboot Saturday 2am. No action needed. "
                "Reach the helpdesk at ext. 4400 with questions. - IT",
        "phishing": False,
        "why": "Normal internal notice. Correct domain, no link, no urgency, no "
               "request for credentials.",
    },
    {
        "sender": "security@paypa1-alerts.com",
        "subject": "URGENT: Your account will be CLOSED in 24 hours!!!",
        "body": "We detected suspicious activity. Verify NOW at "
                "http://paypa1-alerts.com/login or lose access permanently.",
        "phishing": True,
        "why": "Look closely: 'paypa1' uses a ONE, not an L. Fake domain + panic "
               "deadline + a link asking you to 'verify' = classic phishing.",
    },
    {
        "sender": "newsletter@github.com",
        "subject": "Your weekly digest of repository activity",
        "body": "Here's what happened in your projects this week. Manage email "
                "preferences in your account settings.",
        "phishing": False,
        "why": "Routine newsletter from the real domain. It informs; it doesn't "
               "pressure you or ask for a password.",
    },
    {
        "sender": "ceo@your-company.com",
        "subject": "Quick favor - need this done quietly",
        "body": "I'm in a meeting and can't talk. Buy $500 in gift cards and send "
                "me the codes ASAP. Don't tell anyone, I'll explain later.",
        "phishing": True,
        "why": "The famous 'CEO gift-card scam'. Secrecy + urgency + an odd money "
               "request impersonating a boss. Real executives don't do this.",
    },
    {
        "sender": "no-reply@bank-secure-verify.net",
        "subject": "Confirm your identity to unlock your card",
        "body": "Click here to re-enter your full card number, PIN and password "
                "to restore service: http://bank-secure-verify.net/unlock",
        "phishing": True,
        "why": "No real bank asks for your PIN or full password by email. The "
               "look-alike domain and credential request give it away.",
    },
]


class Level3(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.index = 0            # which email we're showing (0 = the first)
        self.score = 0            # how many the player got right
        self.revealed = False     # have we shown the answer for THIS email yet?
        self.last_correct = False
        self.phish_btn = Button(120, 470, 220, 56, "PHISHING", color="red")
        self.safe_btn = Button(380, 470, 220, 56, "SAFE", color="green")
        self.next_btn = Button(WIDTH - 240, 470, 200, 56, "Next >")
        self.continue_btn = Button(WIDTH - 240, HEIGHT - 90, 200, 56, "Continue >")
        self.retry_btn = Button(60, 330, 200, 56, "Retry", color="amber")
        self.done = False

    def reset(self):
        """Put the level back to the very start (used after a failed attempt)."""
        self.index = 0
        self.score = 0
        self.revealed = False
        self.done = False

    def choose(self, player_says_phishing):
        """Record the player's decision for the current email."""
        email = EMAILS[self.index]                 # the dictionary at this index
        # The player is right when their guess matches the stored answer.
        self.last_correct = (player_says_phishing == email["phishing"])
        if self.last_correct:
            self.score += 1
        self.revealed = True

    def handle_event(self, event):
        if self.done:
            if self.score >= 4:
                if self.continue_btn.handle_event(event):
                    self.next_scene = self.return_to
            else:
                if self.retry_btn.handle_event(event):
                    self.reset()
            return
        if not self.revealed:
            # Before revealing, the two verdict buttons are live.
            if self.phish_btn.handle_event(event):
                self.choose(True)
            if self.safe_btn.handle_event(event):
                self.choose(False)
        else:
            # After revealing, a single Next button advances the list.
            if self.next_btn.handle_event(event):
                self.index += 1
                self.revealed = False
                if self.index >= len(EMAILS):       # ran past the last email?
                    self.done = True

    def draw(self, surface):
        surface.fill(COLORS["bg"])
        self.draw_header(surface, "LEVEL 3  //  MIRAGE")

        if self.done:
            passed = self.score >= 4
            draw_text(surface, f"Triage complete. Score: {self.score} / {len(EMAILS)}",
                      60, 200, size=28, color="cyan")
            if passed:
                draw_text(surface, "You spotted the attacks. Mirage's campaign fizzles.",
                          60, 250, size=22, color="green", max_width=880)
                self.continue_btn.draw(surface)
            else:
                draw_text(surface, "Too many got through. Mirage replays the attack...",
                          60, 250, size=22, color="red", max_width=880)
                draw_text(surface, "You need at least 4 of 5. Press Retry to try again.",
                          60, 290, size=18, color="gray")
                self.retry_btn.draw(surface)
            return

        email = EMAILS[self.index]
        draw_text(surface, f"Email {self.index + 1} of {len(EMAILS)}     "
                  f"Score: {self.score}", 60, 90, size=18, color="gray")

        # Draw the email like a real client: a panel with From / Subject / Body.
        panel = pygame.Rect(60, 125, WIDTH - 120, 320)
        pygame.draw.rect(surface, COLORS["panel"], panel, border_radius=10)
        pygame.draw.rect(surface, COLORS["gray"], panel, width=1, border_radius=10)
        draw_text(surface, "From:    " + email["sender"], 80, 145, size=20, color="white")
        draw_text(surface, "Subject: " + email["subject"], 80, 178, size=20, color="amber")
        pygame.draw.line(surface, COLORS["gray"], (80, 212), (WIDTH - 80, 212), 1)
        draw_text(surface, email["body"], 80, 228, size=20, color="white",
                  max_width=WIDTH - 200)

        if not self.revealed:
            self.phish_btn.draw(surface)
            self.safe_btn.draw(surface)
        else:
            verdict = "CORRECT!" if self.last_correct else "WRONG."
            vcolor = "green" if self.last_correct else "red"
            draw_text(surface, verdict, 80, 360, size=24, color=vcolor)
            draw_text(surface, email["why"], 80, 392, size=18, color="gray",
                      max_width=WIDTH - 200)
            self.next_btn.draw(surface)
