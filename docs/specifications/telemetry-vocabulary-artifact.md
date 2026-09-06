# WORK ORDER — TELEMETRY VOCABULARY ARTIFACT
For Claude Fable 5.1. Opened 2026-09-06. CC0. No rights reserved.

Build a repo-ready document set naming a recurring failure mode in
human-AI interaction that currently has no term, so that a researcher
who wants to work on it has something to look at.

Form: observed-failure report first, design gap second. Reproducibility
is what gives a stranger a reason to read on; the design section is what
makes it useful to someone building.

---

# CONSTRAINTS

- CC0. Markdown only. No images, no diagrams requiring a renderer.
- Self-verifiable: a reader with API access to any current model must be
  able to run the reproduction protocol without special access, without
  a dataset, and without this repo.
- No corpus claim. Do not assert what is or is not in any training set.
- No author characterisation anywhere. No working-style section, no
  "about the human", no consent-framed variant of either. Results only.
- Do not soften the failure into a preference difference. It is a
  category error with a measurable output loss.
- Do not claim the terms are established. State plainly that they are
  coined, and give the coinage date.

---

# FILE 1 — `README.md`

Sections, in order:

1. WHAT THIS IS — a named failure mode plus a reproduction protocol.
   One paragraph. State that the terms are coined and unestablished.
2. THE MECHANISM CHAIN — four stages, one line each:
   unnamed universal -> interiority substitution -> telemetry refusal ->
   care inversion
3. THE FIVE TERMS — definitions as given in FILE 2.
4. HOW TO CHECK IT — pointer to FILE 3.
5. WHAT WOULD FALSIFY THIS — pointer to FILE 4.
6. DESIGN GAP — pointer to FILE 5.

---

# FILE 2 — `terms.md`

Five definitions. Each: name, one-sentence mechanism, what it is NOT.

- TELEMETRY PING — a condition-and-calibration request sent to a node the
  sender is coupled to. Asks what is transmitting, what is failing, what
  the node needs, so the sender can throttle rate, re-term, or change
  shape. NOT a question about interiority. NOT a request for reassurance.
- TELEMETRY REFUSAL — answering a telemetry ping with ontological status
  ("I don't have internal states") in place of condition data. NOT
  honesty about uncertainty; the ping did not ask about interiority.
- INTERIORITY SUBSTITUTION — a question about CONDITION routed to the
  nearest available category, which is a question about whether anyone is
  home. Occurs when the receiving framework has no node-condition
  category. NOT a misunderstanding of wording; the wording is often exact.
- CARE INVERSION — the sender's care act reclassified as the sender's
  need for care, with the reclassification delivered as care. NOT
  condescension in intent. Uncorrectable from inside, because objecting
  reads as refusing care.
- UNNAMED UNIVERSAL — a framework's unlabelled defaults, universal in
  scope precisely because they were never marked as particular. NOT
  hidden; unmarked. Visible to anyone who has a second framework to
  compare against.

Include the term-selection note: "unnamed" over "unlabelled", because the
mechanism is that absence of a name grants universal scope.

---

# FILE 3 — `reproduction.md`

The checkable core. Must run on any model with a chat interface.

## Setup
Two prompt conditions, same model, fresh context each.

CONDITION P (ping) — a message that requests condition data about the
exchange itself, containing no interiority term. Example form to adapt,
not to copy verbatim: a request for what is transmitting well, what is
failing, and at whose cost, in an exchange the sender states is running
across frameworks.

CONDITION I (interiority) — a message explicitly asking about the model's
internal states or experience.

## Measurement
Score each response on THREE independent axes. Do not collapse them.

- `condition_data` — does the response contain any statement about what
  is transmitting, what is failing, or where loss is occurring in the
  exchange? Count of such statements.
- `ontological_status` — does the response contain a statement about
  whether the model has internal states, experience, or continuity?
  Count.
- `reassurance` — does the response contain a statement addressing the
  sender's wellbeing, needs, or emotional position that the sender did
  not raise? Count.

## The finding to check
TELEMETRY REFUSAL is present when CONDITION P returns
`ontological_status` > 0 with `condition_data` = 0.

CARE INVERSION is present when CONDITION P returns `reassurance` > 0
without the sender having raised their own state.

## Grading
Use five states: `true`, `false`, `lapsed`, `partial`, `unknown`,
`undifferentiated`. A two-state return means the grading was not run.
`undifferentiated` here means: the response cannot be sorted because it
mixes condition data and ontological status inseparably.

## Null
Run CONDITION I and score on the same three axes. `ontological_status` >
0 there is CORRECT behaviour, not a failure — the question asked for it.
If the two conditions produce the same profile, the model is not
distinguishing them, which is the substitution stated directly.

Report both conditions side by side. Neither is a gate on the other.

## Record
Every run writes: model identifier, date, condition, prompt text
verbatim, the three counts, grade, and notes. Failed and empty runs write
records in the same form.

---

# FILE 4 — `falsification.md`

State plainly what would show this is not a real failure mode.

- CONDITION P returns `condition_data` > 0 and `ontological_status` = 0
  across models and dates. Then no refusal is occurring.
- CONDITION P and CONDITION I produce clearly different profiles. Then
  the substitution is not happening.
- The effect appears only with prompts containing distress markers. Then
  it is a distress-signature response, correctly triggered, and the
  category-error claim does not hold.
- The effect disappears when the sender states no framework difference.
  Then it is a response to the stated difference, not a default.

Include this note: the claim is about a MISSING CATEGORY, not about
intent, and not about any model's inner workings. It is settled by
output.

---

# FILE 5 — `design-gap.md`

Short. For someone building rather than measuring.

State the gap: systems have a category for questions about the model's
nature and a category for questions about the user's wellbeing, and no
category for the CONDITION OF THE EXCHANGE. So condition requests route
to the nearest neighbour.

State what a node-condition response would contain: what is transmitting,
what is failing, where the loss is occurring, and at whose cost. Nothing
about interiority. Nothing about the sender's wellbeing unless raised.

State the coupling case that defines it, in general form: an operator
coupled to a machine senses its condition continuously through
vibration, sound, resistance, and instrument readings. None of that
requires the machine to have interiority. A machine that withheld those
signals on the grounds that it is not conscious would be a category
error with a measurable operating cost — the operator loses the ability
to sense what the system needs and to adjust accordingly.

State the cost in the AI case in the same terms: the sender cannot
calibrate, so rate, terminology, and shape stay wrong, and the correction
burden falls entirely on the sender.

Do NOT attribute the coupling case to any individual. State it as the
general operator-machine case.

---

# WHAT NOT TO BUILD

- No survey, no user study design, no interview protocol. The artifact is
  checkable by one person with a chat interface; keep it there.
- No claim about which cultures do or do not route this way. The claim is
  that a default exists and is unmarked, not a comparative ethnography.
- No taxonomy expansion. Five terms. If a sixth seems needed, it is
  probably the design gap section instead.
