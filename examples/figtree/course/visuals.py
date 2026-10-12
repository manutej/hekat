"""Concept visuals for the course companion: hand-composed, editable SVG in the teaching style.

These are not generated from specs; they explain one idea each for a non-technical reader, with
real example text from the class (a member's question, a line of the system prompt, a session id).
Every element has an id, text is wrapped with the critic's glyph widths so nothing overflows, and
the palette, font and arrowheads are the FigTree teaching preset, so they sit beside the generated
capstone figures without a seam.

    python examples/figtree/course/visuals.py   -> writes visuals/*.svg and scores them
"""

from __future__ import annotations

import html
import os
import sys
from typing import List, Optional, Sequence, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from figtree.icons import symbol_defs  # noqa: E402
from figtree.program import text_width  # noqa: E402

FONT = "IBM Plex Sans, Helvetica Neue, Arial, sans-serif"
C = {"processing": "#C9DCF0", "attention": "#F3C9A4", "residual": "#F6EFD2", "input": "#E6E8EC", "container": "#F8F9FB",
     "border": "#2B3A4A", "label": "#1C2630", "title": "#5B6B7C", "control": "#9A9A9A", "good": "#2F8F6B", "stop": "#B5472F", "white": "#FFFFFF"}
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "visuals")


def wrap(text: str, size: float, max_w: float, bold: bool = False) -> List[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_width(t, size, FONT, bold) * 1.08 <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, cid: str, w: int, h: int, title: str, desc: str):
        self.cid, self.w, self.h = cid, w, h
        self.parts: List[str] = []
        self.icons: set = set()
        self.n = 0
        self.title, self.desc = title, desc

    def nid(self, stem: str) -> str:
        self.n += 1
        return f"{self.cid}-{stem}{self.n}"

    def rect(self, x, y, w, h, fill, stroke=C["border"], rx=8, sw=1.4, dash="", role="block", extra=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<rect id="{self.nid("r")}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d} data-role="{role}"{extra}/>')

    def text(self, x, y, s, size=14, fill=C["label"], anchor="start", bold=False, kind="label", italic=False):
        fw = ' font-weight="600"' if bold else ""
        fs = ' font-style="italic"' if italic else ""
        self.parts.append(f'<text id="{self.nid("t")}" x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{fw}{fs} data-kind="{kind}">{html.escape(s)}</text>')

    def para(self, x, y, s, size=14, max_w=260, fill=C["label"], lh=1.35, bold=False, anchor="start", kind="annot") -> int:
        """Wrapped text; returns the y just below the last line."""
        lines = wrap(s, size, max_w, bold)
        for i, line in enumerate(lines):
            self.text(x, y + i * size * lh, line, size, fill, anchor, bold, kind)
        return int(y + (len(lines) - 1) * size * lh + size * 0.4)

    def icon(self, name, x, y, size=20, color=C["border"]):
        self.icons.add(name)
        self.parts.append(f'<use id="{self.nid("i")}" href="#icon-{name}" x="{x}" y="{y}" width="{size}" height="{size}" color="{color}" data-role="icon"/>')

    def arrow(self, pts: Sequence[Tuple[float, float]], flow="data", stroke=None, head=True, sw=1.6):
        d = " ".join(("M" if i == 0 else "L") + f"{x},{y}" for i, (x, y) in enumerate(pts))
        dash = ' stroke-dasharray="6 4"' if flow != "data" else ""
        col = stroke or (C["control"] if flow == "control" else C["border"])
        m = f' marker-end="url(#{self.cid}-arrow)"' if head else ""
        self.parts.append(f'<path id="{self.nid("a")}" d="{d}" fill="none" stroke="{col}" stroke-width="{sw}"{dash}{m} data-flow="{flow}"/>')

    def card(self, x, y, w, h, fill, title, body, icon=None, size=15, tone_bar=None):
        self.rect(x, y, w, h, fill)
        tx = x + 16
        if icon:
            self.icon(icon, x + 14, y + 14, 22)
            tx = x + 44
        self.text(tx, y + 31, title, size, bold=True)
        return self.para(x + 16, y + 56, body, 13, w - 32, C["title"])

    def bubble(self, x, y, w, text, who, left=True, fill=C["white"]):
        lines = wrap(text, 14, w - 28)
        h = 22 + len(lines) * 19 + 10
        tail = f"M{x + 20},{y + h} l-8,10 l14,-10 z" if left else f"M{x + w - 20},{y + h} l8,10 l-14,-10 z"
        self.parts.append(f'<path id="{self.nid("b")}" d="M{x},{y} h{w} v{h} h-{w} z {tail}" fill="{fill}" stroke="{C["border"]}" stroke-width="1.2" data-role="block"/>')
        self.text(x + 14, y + 18, who, 11, C["title"], kind="annot")
        for i, line in enumerate(lines):
            self.text(x + 14, y + 38 + i * 19, line, 14)
        return y + h + 12

    def svg(self) -> str:
        syms = symbol_defs(sorted(self.icons))
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" font-family="{FONT}" data-figtree="1" role="img" aria-labelledby="{self.cid}-title {self.cid}-desc">'
            f'<title id="{self.cid}-title">{html.escape(self.title)}</title><desc id="{self.cid}-desc">{html.escape(self.desc)}</desc>'
            f'<rect id="{self.cid}-background" x="0" y="0" width="{self.w}" height="{self.h}" fill="#FFFFFF" data-role="background"/>'
            f'<defs><marker id="{self.cid}-arrow" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L8,3 L0,6 z" fill="{C["border"]}"/></marker>{syms}</defs>'
            + "".join(self.parts) + "</svg>"
        )


# ----------------------------------------------------------------------------------------------
# Module 1
# ----------------------------------------------------------------------------------------------

def m1_script_vs_agent() -> str:
    c = Canvas("m1a", 960, 470, "A fixed script compared with an agent",
               "Top: a fixed script runs the same three steps for every message and stops when a question does not fit. Bottom: an agent reads the question, decides between answering from plan documents, asking a clarifying question, or handing to a person, then acts.")
    q = "My daughter turns 26 next month. What changes for her coverage?"
    # top lane: fixed script
    c.rect(24, 24, 912, 168, C["container"], stroke="#D5DBE4", rx=12, role="container")
    c.text(40, 48, "A fixed script", 15, C["title"], bold=True, kind="title")
    c.text(170, 48, "runs the same steps for every message", 13, C["title"], kind="annot")
    y = 62
    c.bubble(40, y, 250, q, "Member", left=True)
    steps = [("Check keyword list", "input"), ("Match a canned answer", "input"), ("Send it", "input")]
    x = 330
    for i, (s, tone) in enumerate(steps):
        c.rect(x, 88, 150, 44, C[tone])
        c.text(x + 75, 115, s, 13, anchor="middle")
        if i < 2:
            c.arrow([(x + 150, 110), (x + 174, 110)])
        x += 174
    c.arrow([(296, 110), (330, 110)])
    c.arrow([(x - 174 + 150, 110), (x - 174 + 150 + 16, 110)], stroke=C["stop"])
    c.rect(x - 174 + 150 + 16, 88, 96, 44, "#F6D9D2", stroke=C["stop"])
    c.text(x - 174 + 150 + 16 + 48, 115, "No match", 13, C["stop"], anchor="middle", bold=True)
    c.para(330, 162, "“dependent” is not on the list, so the member gets “Sorry, I did not understand” and calls instead.", 13, 540, C["title"])
    # bottom lane: agent
    c.rect(24, 212, 912, 236, C["container"], stroke="#D5DBE4", rx=12, role="container")
    c.text(40, 236, "An agent", 15, C["title"], bold=True, kind="title")
    c.text(118, 236, "reads, decides, then acts", 13, C["title"], kind="annot")
    c.bubble(40, 250, 250, q, "Member", left=True)
    c.rect(330, 262, 150, 56, C["attention"])
    c.icon("eye", 344, 280, 20)
    c.text(372, 286, "Reads it", 14, bold=True)
    c.text(372, 304, "whole question", 12, C["title"], kind="annot")
    c.arrow([(296, 298), (330, 298)])
    c.rect(520, 262, 150, 56, C["attention"])
    c.icon("split", 534, 280, 20)
    c.text(562, 286, "Decides", 14, bold=True)
    c.text(562, 304, "which path fits", 12, C["title"], kind="annot")
    c.arrow([(480, 290), (520, 290)])
    # three choices
    choices = [("Answer from plan documents", "good", "document"), ("Ask one clarifying question", "processing", "text"), ("Hand to a person", "processing", "user")]
    for i, (lab, tone, ic) in enumerate(choices):
        yy = 232 + i * 54
        fill = C["processing"] if tone != "good" else "#D5EBDD"
        c.rect(712, yy, 220, 42, fill, stroke=C["border"] if tone != "good" else C["good"])
        c.icon(ic, 722, yy + 11, 18)
        c.text(748, yy + 26, lab, 12.5, bold=(tone == "good"))
        c.arrow([(670, 290), (690, 290), (690, yy + 21), (712, yy + 21)], flow="control" if tone != "good" else "data", stroke=C["good"] if tone == "good" else None)
    c.para(40, 412, "The agent chooses the first path: the plan documents say a dependent is covered to the end of the month they turn 26, so it answers that, in the plan's own words.", 13, 860, C["title"])
    return c.svg()


def m1_anatomy() -> str:
    c = Canvas("m1b", 944, 470, "The four parts of your first agent, with what each one holds",
               "Chat Input holds the member's question. Prompt Template holds the standing instructions and the question. The Chat Model writes the answer. Chat Output shows it. A Knowledge Base of plan documents can feed passages into the prompt.")
    c.text(24, 36, "What each part holds for one real question", 16, C["title"], bold=True, kind="title")
    # four cards in a row
    cards = [
        ("Chat Input", "user", C["input"], "The member's words, exactly as typed:", "“Is an MRI covered on the Silver PPO?”"),
        ("Prompt Template", "edit-script", C["attention"], "The standing instructions, then the question:", "“You answer only from the plan documents provided. If the documents do not say, say so and offer a phone number.”"),
        ("Chat Model", "bolt", C["processing"], "Writes the answer from the prompt:", "Reads instructions, documents and question together; writes one reply."),
        ("Chat Output", "text", C["input"], "The reply the member sees:", "“Yes. On the Silver PPO an MRI needs prior authorisation and is covered at 80% in network.”"),
    ]
    x = 24
    for i, (name, ic, fill, lead, body) in enumerate(cards):
        c.rect(x, 64, 206, 236, fill)
        c.icon(ic, x + 14, 78, 22)
        c.text(x + 44, 96, name, 15, bold=True)
        y = c.para(x + 14, 126, lead, 12, 178, C["title"])
        c.rect(x + 14, y + 6, 178, 120, C["white"], stroke="#D5DBE4", rx=6, sw=1)
        c.para(x + 24, y + 28, body, 12.5, 158, C["label"])
        if i < 3:
            c.arrow([(x + 206, 180), (x + 230, 180)])
        x += 230
    # knowledge base below the prompt template
    c.rect(254, 340, 206, 96, C["residual"])
    c.icon("database", 268, 354, 22)
    c.text(298, 372, "Knowledge Base", 15, bold=True)
    c.para(268, 398, "Optional. Plan documents the agent may quote: the Silver PPO summary, the prior-auth list.", 12, 178, C["title"])
    c.arrow([(357, 340), (357, 300)])
    c.text(372, 326, "passages are added to the prompt", 11.5, C["title"], kind="annot")
    c.para(500, 372, "Only the Prompt Template is written by you. The other parts are standard components you drag onto the canvas and connect.", 13, 390, C["title"])
    return c.svg()


def m1_key_safety() -> str:
    c = Canvas("m1c", 944, 310, "Where the model key lives: on the class server, never in a browser",
               "The student's browser talks only to the class portal. The portal holds the model provider key in a safe and calls Langflow; Langflow calls the model provider. The key never travels to the browser.")
    c.text(24, 36, "Where the key lives", 16, C["title"], bold=True, kind="title")
    boxes = [("Student's browser", "user", C["input"], "Sends the question. Holds no key."), ("Class portal (server)", "database", C["attention"], "Holds the provider key. Adds the student's session id."),
             ("Langflow", "layers", C["processing"], "Runs the published flow."), ("Model provider", "bolt", C["processing"], "Receives the key with each call.")]
    x = 24
    for i, (name, ic, fill, body) in enumerate(boxes):
        c.rect(x, 64, 206, 150, fill)
        c.icon(ic, x + 14, 78, 22)
        c.text(x + 44, 96, name, 14.5, bold=True)
        c.para(x + 14, 124, body, 12.5, 178, C["title"])
        if i < 3:
            c.arrow([(x + 206, 139), (x + 230, 139)])
        x += 230
    # the key token drawn under the portal and the provider only
    for kx in (254 + 14, 714 + 14):
        c.rect(kx, 176, 110, 26, "#D5EBDD", stroke=C["good"], rx=13, sw=1.2)
        c.icon("check", kx + 8, 179, 18, C["good"])
        c.text(kx + 32, 194, "provider key", 12, C["good"], bold=True)
    # the crossed-out key under the browser
    c.rect(38, 176, 110, 26, "#F6D9D2", stroke=C["stop"], rx=13, sw=1.2)
    c.text(93, 194, "no key here", 12, C["stop"], anchor="middle", bold=True)
    c.para(24, 246, "Why it matters: anything in a browser can be copied. A key that stays on the server can be rotated in one place, and a student can never run up the bill from their laptop. The export you commit to git carries no key either.", 13, 820, C["title"])
    return c.svg()


def m1_journey() -> str:
    c = Canvas("m1d", 944, 330, "The journey of one question, in four beats",
               "Beat 1: the student types a question in the portal. Beat 2: the portal sends it to Langflow with the student's session id. Beat 3: Langflow runs the published flow. Beat 4: the reply comes back to the chat window.")
    c.text(24, 36, "The journey of one question", 16, C["title"], bold=True, kind="title")
    beats = [
        ("1", "Student types", "user", "“Do I need a referral to see a dermatologist?”", C["input"]),
        ("2", "Portal sends it on", "database", "with session id student:123 so the conversation stays this student's", C["attention"]),
        ("3", "Langflow runs it", "layers", "Chat Input → Prompt → Model → Chat Output, about two seconds", C["processing"]),
        ("4", "Reply appears", "text", "“On the Silver PPO, no referral is needed for in-network specialists.”", C["input"]),
    ]
    x = 24
    for i, (n, name, ic, body, fill) in enumerate(beats):
        c.rect(x, 64, 206, 190, fill)
        c.parts.append(f'<circle id="{c.nid("c")}" cx="{x + 24}" cy="86" r="12" fill="{C["border"]}"/>')
        c.text(x + 24, 91, n, 13, C["white"], anchor="middle", bold=True)
        c.icon(ic, x + 44, 75, 22)
        c.text(x + 74, 91, name, 14, bold=True)
        c.para(x + 14, 120, body, 12.5, 178, C["label"])
        if i < 3:
            c.arrow([(x + 206, 160), (x + 230, 160)])
        x += 230
    c.para(24, 284, "The student never sees Langflow. They see one chat window; everything between beat 1 and beat 4 is the agent you built.", 13, 820, C["title"])
    return c.svg()


def m1_good_answer() -> str:
    c = Canvas("m1e", 944, 250, "What a good answer looks like in this class",
               "Three checks for every reply: it comes from the plan documents, it says when it does not know, and it keeps PPO and HMO facts straight across turns.")
    c.text(24, 36, "Three checks for every reply", 16, C["title"], bold=True, kind="title")
    checks = [("Grounded", "document", "Every fact traces to a plan document. No guessing, no general internet advice."),
              ("Honest about gaps", "residual", "If the documents do not say, the reply says so and gives a phone number."),
              ("Consistent", "loop", "Turn 1 says PPO; turn 3 still answers for a PPO. Nothing contradicts the lab facts.")]
    x = 24
    for name, ic, body in checks:
        c.rect(x, 64, 282, 150, C["container"], stroke="#D5DBE4")
        c.icon(ic, x + 16, 80, 24, C["good"])
        c.text(x + 50, 98, name, 15, bold=True)
        c.para(x + 16, 128, body, 13, 250, C["title"])
        x += 294
    return c.svg()


MODULE_VISUALS = {
    "m1": [("m1-script-vs-agent", m1_script_vs_agent, "Script or agent?", "A fixed script stops when a question does not fit its list. An agent reads the whole question and chooses what to do."),
           ("m1-anatomy", m1_anatomy, "The four parts, with real contents", "What each component holds for one member question. Only the Prompt Template is written by you."),
           ("m1-key-safety", m1_key_safety, "Where the key lives", "The browser never holds the provider key. The class portal does, and adds the student's session id."),
           ("m1-journey", m1_journey, "One question, four beats", "From the student's chat window through the portal and Langflow and back, in about two seconds."),
           ("m1-good-answer", m1_good_answer, "What a good answer looks like", "Grounded, honest about gaps, consistent across turns.")],
}


def build_all() -> List[Tuple[str, str]]:
    os.makedirs(OUT, exist_ok=True)
    written = []
    for mod, items in MODULE_VISUALS.items():
        for vid, fn, _, _ in items:
            p = os.path.join(OUT, vid + ".svg")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(fn())
            written.append((vid, p))
    return written


if __name__ == "__main__":
    for vid, p in build_all():
        print("wrote", p)
