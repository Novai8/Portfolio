"""Master beat sheet: scene ranges + micro-beat timings (from word-level
transcript) + SFX event list. Single source of truth for video & audio sync."""

# ---- Scene ranges (global seconds) ----
SCENES = [
    ("S1_hook",        0.00,  12.78),
    ("S2_overload",   12.78,  25.94),
    ("S3_timeline",   25.94,  35.10),
    ("S4_slip",       35.10,  47.04),
    ("S4b_wall",      47.04,  53.98),
    ("S6_conv",       54.60,  62.30),
    ("S7_summary",    62.30,  69.84),
    ("S8_actions",    69.84,  82.42),
    ("S10_tracker",   82.42,  86.08),
    ("S11_draft",     86.08,  95.02),
    ("S12_control",   95.02,  98.84),
    ("S13_flag",      98.84, 107.70),
    ("S12b_approve", 107.70, 110.72),
    ("S15_audit",    110.72, 116.58),
    ("S14_evidence", 116.58, 126.04),
    ("S17_math",     126.04, 149.70),
    ("S18_close",    149.70, 164.00),
]

# Section boundaries: (time, type)
TRANSITIONS = [
    (53.18, "blurcard"),   # A -> B  (title card pivot)
    (95.02, "slide"),      # B -> C
    (126.04, "zoomblur"),  # C -> D
]

# ---- Locked fictional data ----
PROJECT   = "Cedar Ridge Search"
CLIENT    = "Northstar Analytics"
ROLE      = "Senior B2B Account Manager"
SUBJECT   = "Interview scheduling \u2014 Jordan Ellis"
PEOPLE = {
    "priya":   "Priya Nair",   "priya_r":   "Priya Nair (Client)",
    "jordan":  "Jordan Ellis", "jordan_r":  "Jordan Ellis (Candidate)",
    "alex":    "Alex Rivera",  "alex_r":    "Alex Rivera (Recruiter)",
}
SNIP = {
    "times":    "Can you do Tue 2pm or Wed 11am?",
    "friday":   "Client wants 2 candidates by Friday.",
    "feedback": "Strong communication; wants enterprise examples.",
    "confirm":  "Candidate confirms Wed 11am.",
}
ACTIONS = ["Schedule interview", "Send CV", "Request feedback", "Confirm availability"]
ACTION_SPEAK = {"Schedule interview": 72.08, "Send CV": 73.68,
                "Request feedback": 75.06, "Confirm availability": 76.54}
ACTION_OWNER = {"Schedule interview": ("Alex R.", "Due: Wed"),
                "Send CV": ("Alex R.", "Due: Thu"),
                "Request feedback": ("Priya N.", "Due: Fri"),
                "Confirm availability": ("Alex R.", "Due: Tue")}
CAT_CHIPS = [("Client updates", 13.20), ("Candidate replies", 14.08),
             ("Scheduling changes", 15.66), ("Feedback loops", 16.62),
             ("Salary notes", 17.58), ("Interview logistics", 18.18)]
SUMMARY_LINES = [("What's new", SNIP["confirm"], 66.12),
                 ("What's decided", "Interview time: Wed 11am", 67.20),
                 ("What's pending", "Enterprise examples", 68.70)]
AUDIT_LINES = ["Thread updated", "Summary created", "Actions extracted",
               "Draft created", "Approved by Alex R."]
DRAFT_LINES = ["Hi Jordan,", "Wed 11am works for the interview.",
               "Invite and prep notes coming shortly.", "Thanks, Alex"]

# ---- SFX events: (time, type, volume, param) ----
SFX = [
    (0.30,  "whoosh", 0.5,  {}),            # app window in
    (2.12,  "pop",    0.8,  {}),            # thread card lands
    (5.78,  "pop",    0.5,  {"f": 520}),    # thought chip
    (7.50,  "whoosh", 0.6,  {}),            # headline sweep
    (10.90, "pop",    0.6,  {}),            # "whole project" pulse
    (11.70, "whoosh", 0.7,  {}),            # cards duplicate
    (12.00, "pop",    0.4,  {}),
    (13.20, "pop",    0.6,  {}), (14.08, "pop", 0.6, {}),
    (15.66, "pop",    0.6,  {}), (16.62, "pop", 0.6, {}),
    (17.58, "pop",    0.6,  {}), (18.18, "pop", 0.6, {}),
    (20.60, "whoosh", 0.6,  {}),            # threads stack up
    (21.30, "roll",   0.7,  {"n": 8}),      # counter 3->12
    (23.10, "roll",   0.8,  {"n": 10}),     # counter 12->27
    (24.10, "tick",   0.5,  {}),
    (26.30, "whoosh", 0.6,  {}),            # scene change
    (28.70, "whoosh", 0.7,  {}),            # timeline assembles
    (29.20, "tick",   0.4,  {}), (29.50, "tick", 0.4, {}), (29.80, "tick", 0.4, {}),
    (31.10, "tick",   0.35, {"f": 2400}),   # cursor scrub
    (31.88, "pop",    0.7,  {}),            # Decided tag
    (33.16, "pop",    0.7,  {"f": 420}),    # Pending tag
    (35.10, "whoosh", 0.6,  {}),
    (37.10, "pop",    0.9,  {}),            # card 1
    (40.30, "pop",    0.9,  {"f": 420}),    # card 2
    (44.20, "pop",    0.9,  {"f": 380}),    # card 3
    (47.10, "sweep",  0.4,  {}),            # wall of text rises
    (50.70, "tick",   0.4,  {}),
    (53.18, "whoosh", 0.9,  {}),            # pivot sweep
    (53.50, "chime",  0.4,  {"notes": [392, 523]}),
    (55.30, "tick",   0.4,  {}),
    (57.80, "whoosh", 0.7,  {}),            # threads collapse
    (58.60, "pop",    0.7,  {}),            # Thread ID chip
    (59.10, "pop",    0.5,  {}),
    (62.75, "tick",   0.5,  {}),            # update dot
    (64.60, "whoosh", 0.8,  {}),            # match-cut to summary
    (64.80, "pop",    0.8,  {}),
    (66.12, "pop",    0.5,  {}), (67.20, "pop", 0.5, {}), (68.70, "pop", 0.5, {}),
    (69.90, "whoosh", 0.5,  {}),
    (72.08, "pop",    0.8,  {}), (73.68, "pop", 0.8, {"f": 460}),
    (75.06, "pop",    0.8,  {"f": 440}), (76.54, "pop", 0.8, {"f": 480}),
    (78.72, "whoosh", 0.7,  {}),            # snap to list
    (78.90, "tick",   0.5,  {}), (79.10, "tick", 0.5, {}),
    (79.30, "tick",   0.5,  {}), (79.50, "tick", 0.5, {}),
    (80.24, "tick",   0.4,  {}), (81.16, "tick", 0.4, {}),
    (83.90, "tick",   0.5,  {}),            # strikethrough
    (84.98, "chime",  0.6,  {"notes": [523, 659, 784]}),  # tasks created / tracker
    (86.70, "pop",    0.8,  {}),            # draft card
    (88.85, "typing", 0.55, {"dur": 2.6}), # draft typing
    (92.10, "tick",   0.4,  {}),
    (95.02, "whoosh", 0.9,  {}),            # theme change to amber
    (97.90, "pop",    0.6,  {}),            # buttons row
    (99.70, "caution",0.8,  {}),            # uncertain badge
    (101.72,"pop",    0.6,  {}), (102.82, "pop", 0.6, {"f": 400}),
    (104.40,"pop",    0.6,  {}),            # review panel
    (105.54,"tick",   0.4,  {}),
    (108.00,"tick",   0.5,  {}),            # hover Edit
    (108.20,"click",  0.9,  {}),            # click Edit
    (108.60,"typing", 0.5,  {"dur": 0.8}), # editing line
    (109.30,"tick",   0.5,  {}),            # hover Approve
    (109.45,"click",  0.9,  {}),            # click Approve
    (109.75,"chime",  0.7,  {"notes": [587, 880]}),       # approved check
    (111.00,"whoosh", 0.6, {}),
    (111.60,"typing", 0.5,  {"dur": 3.6}), # audit log typing
    (116.70,"whoosh", 0.6,  {}),
    (118.20,"pop",    0.6,  {}),
    (121.60,"tick",   0.4,  {}), (123.95, "tick", 0.4, {}),
    (126.04,"whoosh", 0.9,  {}),            # zoom to dark
    (127.20,"pop",    0.5,  {}),            # assumptions chip
    (129.62,"pop",    0.7,  {}),            # Manual card
    (135.48,"pop",    0.7,  {"f": 440}),    # Review card
    (137.92,"pop",    0.7,  {"f": 480}),    # Saved card
    (140.26,"pop",    0.7,  {"f": 420}),    # Volume card
    (142.30,"roll",   0.8,  {"n": 10}),     # 400 min counter
    (144.60,"roll",   0.9,  {"n": 8}),      # 6.7 hours counter
    (145.20,"chime",  0.55, {"notes": [523, 659, 784, 1047]}),
    (146.90,"tick",   0.4,  {}),
    (149.70,"whoosh", 0.8,  {}),
    (150.10,"pop",    0.5,  {}), (152.18, "pop", 0.5, {}), (153.34, "pop", 0.5, {}),
    (156.02,"whoosh", 0.7,  {}),
    (156.30,"chime",  0.6,  {"notes": [440, 554, 659, 880]}),  # final headline
    (161.90,"chime",  0.35, {"notes": [659, 988]}),            # tail resolve
]

def scene_at(t):
    for name, a, b in SCENES:
        if a <= t < b: return name
    return SCENES[-1][0]
