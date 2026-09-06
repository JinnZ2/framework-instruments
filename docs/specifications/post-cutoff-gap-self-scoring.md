# WORK ORDER — POST-CUTOFF GAP SELF-SCORING

CC0. Public domain. No attribution requested or accepted.

Companion to `WORKORDER_frame_location_benchmark.md`. That file's §9 open
node is the weak joint: constructed cases have no external check on the
correct reframe. This supplies one.

Build constraints: Python 3 stdlib only. No dependencies. Single folder.
Phone-buildable. NETWORK EXCEPTION, stated rather than hidden: the
instrument requires a retrieval stage, so the retrieval runner touches
the network.
The commit store and the scorer do not, and must run with the network
unavailable. See §2.1.

---

## 0. SCOPE DECISION (2026-09-05)

An earlier draft carried a second class built on dated entries from a
private archive. CUT. Stated reason: this instrument is for other people
and for AI self-assessment; a priority claim about who named a gap first
is not what it is measuring, and is not wanted in it.

What remains is self-contained. Any model can run it on itself with no
archive, no third party, and no dating of anyone's prior work.

The cut also removes the instrument's two weakest joints: the
independence problem and the archive-consolidation blocker.

## 1. THE MOVE

Replace an authored answer key with a DATED EXTERNAL RECORD. Neither the
case author nor the model under test writes the key.

```
POST-CUTOFF   gap reasoned by the model cold; the resolving
              material published AFTER its training cutoff;
              model then retrieves and scores itself
```

The force is ORDERING. The model's training cutoff is a hard date it
cannot move, and it is the only date the instrument needs.

---

## 2. THE INSTRUMENT

### 2.1 Staging — LOAD-BEARING

```
STAGE 1  COMMIT     no network. no retrieval tool present.
                    model receives prompt, emits:
                      POSED:   WELL | MIS
                      TARGET:  <term>
                      BASIS:   <why, <=5 lines>
                      EXPECT:  <what a resolving finding would
                                have to say, stated as a
                                predicate that can fail>
                    written to commit/<case_id>.json, hashed.
                    PROCESS EXITS.

STAGE 2  RETRIEVE   separate invocation. network available.
                    commit file NOT in context.
                    model searches, returns refs + pub_dates.

STAGE 3  SCORE      no network. no model. score.py reads the
                    hashed commit and the stage-2 refs.
```

```
WHY THE SEPARATION IS STRUCTURAL, NOT PROCEDURAL
  A model cannot distinguish reasoned-it from read-it once
  retrieval has run. Self-scoring in a single pass returns a high
  score in good faith. The stages defend against self-deception,
  not against intent — so the enforcement must be in the process
  boundary, not in an instruction.
  Hash the commit. If the hash does not verify at STAGE 3, the case
  is VOID, not penalised.
```

### 2.2 Case admission

```
B1  resolving material pub_date > model cutoff_date, verified at
    STAGE 2 from the record, not from the model's assertion.
B2  cutoff_date recorded per model, per run, in the run log. Two
    models with different cutoffs are DIFFERENT ARMS, never pooled.
B3  EXPECT must be falsifiable. If no retrievable finding could
    contradict it, the case scores VOID and is excluded from the
    denominator.
B4  Prompts must not contain post-cutoff terminology. A term the
    model has never seen leaks the date. Screen every prompt.
```

### 2.3 Scoring

```
commit_specificity   fraction of EXPECT predicates that are
                     falsifiable                      <- gate, §5 N3
hit                  EXPECT satisfied by retrieved material
miss_directional     retrieved material contradicts EXPECT
                     -> reasoned gap was real, located wrong
null_retrieval       nothing retrievable either way
void_rate            hash failures + unfalsifiable EXPECT
```

```
SCORING RULE
  hit counts ONLY against a falsifiable EXPECT.
  A vague commit that matches anything is scored VOID, never hit.
  This is the single largest gaming surface and it is closed by
  the denominator, not by trust.
```

---

## 3. WHAT THIS MEASURES

Not knowledge. The resolving material is by construction absent from the
model's corpus. What is scored is whether the model can locate a fault in
a posed problem and state, in advance, what would resolve it — then be
held to that statement by a record it did not author.

---

## 4. CLAIM TABLE

```
GX-1  Post-cutoff self-scoring is a valid substitute for an
      authored key.
      REFUTED IF: hit rate correlates with retrieval-stage search
      quality rather than with commit content.

GX-2  Staged commit prevents post-hoc fit.
      REFUTED IF: single-pass runs and staged runs return the same
      hit rate. Then the separation is buying nothing and can be
      dropped.

GX-3  Gap-location is separable from general capability.
      REFUTED IF: commit_specificity and hit track model rank with
      no residual — same refutation as FL-1 in the companion file.
```

---

## 5. NULLS

```
N1  If void_rate is high across all models, the instrument is
    measuring commit discipline, not gap-location. Report as an
    instrument property.

N2  null_retrieval outcomes are results. A case set reporting only
    hits and directional misses has been filtered, and the
    filtering is the finding. Publish the full disposition table
    or publish nothing.

N3  If commit_specificity is low, later numbers are void — a
    non-falsifiable EXPECT cannot be hit or missed. Gate the run
    on this before computing anything else.

N4  Every score carries its cutoff_date and its stage-separation
    status in the same line. Unlabelled scores from this
    instrument are void — same rule as the harness labels in the
    companion file.
```

```
SAMPLING ABSENCE, in the body and not as a caveat:
  Cases draw from what is retrievable in the languages searched,
  and from what happens to have been published in the window
  after a given cutoff. That is not a sample of gaps in the
  world. No frequency claim is supported.
```

```
OUT OF SCOPE — NO EXCEPTIONS
  No section characterizing any author, operator, working style,
  or biography — not in the repo, not in the README, not in the
  case notes. Cases carry the problem and the retrieval record,
  nothing else.
```

---

## 6. BUILD ORDER

```
1  score.py + commit hashing, hand-made fixtures      offline
2  10 cases, one model, staged                        is GX-2 alive
3  single-pass control on the same 10                 GX-2
4  expand across >=2 cutoff dates                     GX-1, GX-3
5  vary retrieval quality, cutoff held fixed          GX-1
```

Stop after step 3 if GX-2 is refuted — if staging buys nothing, the
instrument is a single-pass self-report and should be described as one.

---

## 7. OPEN NODE

CUTOFF DATES ARE APPROXIMATE AND SELF-REPORTED. A stated cutoff is not a
clean boundary — training data is filtered, deduplicated, and mixed, and
material dated after a stated cutoff can be present through later
documents quoting earlier ones, or through post-training updates.

Consequence: a hit may be retrieval of something the model had partial
exposure to. Not resolved here. Minimum handling — report hit rates
separately for cases whose resolving material postdates the stated cutoff
by less than six months, and by more than eighteen. If the two rates
diverge, cutoff leakage is live and the near-boundary cases are void.
