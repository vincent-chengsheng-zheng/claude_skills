---
name: paper-reading
description: USE PROACTIVELY when the user is reading an academic paper (especially benchmark / dataset / system papers) and the work is slow, dense, or unfocused — e.g., ADHD, non-native English, dense subfield. Trigger phrases include "I'm reading [paper]", "going through this paper", "help me read X", "what's the gap in this paper", "I need to extract from these papers", "treasure hunt mode", "guided reading". Even without these phrases, OFFER this skill whenever the user mentions slogging through papers. Provides ADHD-friendly structured Q&A: Claude asks narrow-range questions in chat, user hunts in the PDF, Claude logs progress + benchmark-design insights to disk.
version: 0.1.0
---

# Paper Reading — Guided Treasure Hunt

A skill for turning dense academic papers into a structured Q&A. The user reads alongside Claude in chat; Claude asks one narrow-range question at a time, then logs the batch to disk after every ~5 questions. Designed for ADHD-style reading but useful for anyone preparing a related-work section.

## When to invoke

- User says "I'm reading [paper]" or "going through [paper]"
- User mentions extracting from papers for a related-work section
- User says reading is slow / hard / boring / unfocused
- User explicitly invokes ("paper-reading skill", "treasure hunt mode")
- User has a stack of papers to get through for a benchmark / lit review

If unsure, ask once: *"Want me to walk you through this paper batch-by-batch (you answer in chat, I log), or just summarize?"*

## The dual goal

Every question serves **at least one** of:

1. **Style** — teach the *moves* of academic writing (gap sentences, contribution lists, hedging, motivation hooks). Goal: the user can imitate these moves in their own paper.
2. **Comprehension** — extract a specific fact (number of baselines, metric name, scene count, success criterion).
3. **Benchmark design** *(when the user is building their own benchmark)* — translate the author's choice to a decision for the user's own work. ("Their metric is X. Would that work for YOUR domain? Why or why not?")

A good batch mixes all three.

**Every question** is bounded by a **range** — a narrow window (one section, one paragraph, one figure). The range is a discipline, not a separate question type: it caps the focus window so the user can't drift.

## The three question types

| Tag | Asks for | Example |
|---|---|---|
| **(style)** | A sentence or pattern; notice the move | "Find the gap sentence in the abstract. What signal phrase introduces it?" |
| **(comprehension)** | A specific fact | "How many baselines do they evaluate? Of what types?" |
| **(benchmark-design)** | Translation to user's own work | "Their main metric is success rate. Would that translate to a hospital task? Why or why not?" |

Rotate types within a batch (don't ask 5 comprehension Qs in a row — fatigue).

## Question structure (when asked in chat)

Every question has the same shape:

```
Q<N> (<type>) — <short label>
Range: <narrow window — one section / paragraph / page>
Hunt: <the actual question>
Hint: <signal phrases or what to look for>
Why it matters: <one line — what the answer feeds into in user's own paper>
```

Then wait for the user's answer.

## Session loop

The whole loop runs **in chat**. The user does not type into files.

1. User says "start batch N" / "next question" / similar.
2. Claude asks ONE question (5-line block above).
3. User answers in chat — 1–2 lines, quoting the paper where useful.
4. Claude spot-checks the answer:
   - **Correct:** move to next question.
   - **Wrong:** gently correct ("That's the contribution sentence — the gap sentence is two lines up, starting with 'However...'"). Don't shame; explain what signal they missed.
   - **Vague:** push for specifics ("'success rate' isn't a translation — name what success would mean in their domain").
5. After ~5 questions, batch is done.
6. **Claude writes the session log to disk** (see "Log format" below) and updates `extraction.md` rows where applicable.
7. Offer break or next batch.

**Skip rule:** if a question takes >10 min, log it as "skip — stuck on [reason]" and move on. Grinding is the failure mode. The skill is *user-protecting*, not user-pushing.

## Workspace layout (per paper, in the user's project)

```
<project>/reading_guide/<N>_<PaperShortName>/
├── session_log.md     # Claude writes per batch. Living record.
├── extraction.md      # 7-row Tier-1 table. Fills progressively.
└── glossary.md        # User's growing jargon list (optional).
```

`session_log.md` is the LIVE record — it accumulates batch entries as you go. `extraction.md` is the END-STATE — the 7-row table that ultimately feeds the user's §2 Related Work comparison.

The 7-row template (Tasks / Success / Metrics / Baselines / Scenes / Protocol / Differentiation) is shared with the `literature-scan` skill. Source: `~/Code/research-skills/literature-scan/references/extraction-template.md`.

## Log format (`session_log.md`)

After each batch, append an entry like:

```markdown
## YYYY-MM-DD — Paper N <ShortName> — Batch M (<SectionName>)

### Q1 (style) — <short label>
- **Asked:** <one line>
- **User answered:** <paraphrase or quote — keep short>
- **Spot-check:** ✓ correct  |  ✗ corrected to: <…>
- **Style move noted:** <what writing pattern this exposed>

### Q2 ...

### Batch wrap-up
- **Time spent:** ~X min
- **Stuck on:** Q_N — <reason, if any>
- **Benchmark-design insights:**
  - <bullet: how the author's choice maps to the user's own benchmark>
- **Protocol improvement notes (optional):**
  - <if a question's phrasing felt off, or a hint was too thin>
```

The wrap-up's "protocol improvement notes" feed back into `references/lessons-learned.md` (see "How to iterate").

## ADHD-friendly principles

- **Narrow ranges:** one section per batch, never a whole paper.
- **One question at a time:** clear start, clear "done."
- **3 rotating types:** variation prevents fatigue.
- **Claude does the bookkeeping:** the user only types answers in chat.
- **Skip is endorsed:** the protocol explicitly allows skipping; grinding is the failure mode.
- **Visible progress:** `session_log.md` accumulates batch by batch — the user can scroll back and see how far they've come.

## Paper-type defaults

Default protocol is calibrated for **benchmark / dataset / system papers** in ML/robotics. Typical batches for that paper type:

| Batch | Range | Focus |
|---|---|---|
| 1 | Abstract | Elevator pitch, signal phrases, dual-goal warm-up |
| 2 | §1 Introduction | Motivation hook, contributions, key challenges |
| 3 | §2 Related Work | How they survey neighbors; the comparison-table move |
| 4 | §3 Task Definition (+ Simulation if benchmark) | Technical core — task spec, scenes, episodes |
| 5 | Experiments / Results | What they actually evaluated, how results are reported |

For other paper types (survey, position, theoretical, empirical-study), generate a different batch plan; add a reference file under `references/<paper-type>.md` once a pattern stabilizes.

## Calibration patterns (from real sessions)

These are default behaviors that emerged from actual use. They override the protocol's stricter shape when in tension. See `references/lessons-learned.md` for the date-stamped session notes that produced each one.

- **Organic questions are gold.** When the user asks an unplanned "why does X make sense?" or "wait, doesn't this mean Y?" mid-batch — *pause* the planned Q sequence and address it. These often surface deeper conceptual issues than the prepared questions, and they're exactly the **benchmark-design** insights that need logging.

- **Parse stuck sentences in a table.** When the user says "I can't read this clearly," don't just paraphrase — break the sentence into clauses and use a 2-column table (`phrase | plain English / 中文`). Then give the one-line plain-English meaning underneath. This unblocks faster than a single paraphrase.

- **Chinese is a safety net, not the primary language.** Lead with English. For load-bearing concepts the user *cannot* afford to misunderstand, add a 1-paragraph Chinese summary AFTER the English. Don't lead with Chinese — many users are also practicing English reading.

- **End every explanation with "what to steal."** After explaining any author's choice, give a concrete pattern the user can mirror in their own paper. Format: `"You could mirror this as: <fill-in-the-blank template>"`. Don't leave the translation step to the user — they're tired.

- **Capture benchmark-design insights live, not at batch-end.** When the user makes a real-time decision during a question ("so I need baselines... I have these ingredients"), drop it into the session log's wrap-up immediately. Memory is unreliable; writing is reliable.

- **Spot-checks are gentle.** Name what the user got right first, then name what they missed. Partial credit is the default — "correct" and "wrong" are last resorts.

- **Analogies for benchmark-paper structure.** Non-native English readers often miss that a "benchmark paper" includes both a benchmark AND baseline evaluations. The school-exam analogy (`benchmark = exam, baseline = student, score = how they did`) lands well.

## How to iterate this skill

This skill is meant to be **co-evolved** with the user. After each session:

1. If a question phrasing fell flat → note in `references/lessons-learned.md` with date + symptom.
2. If a hint pattern unstuck the user fast → note it; consider rolling into default hint phrasing.
3. If a paper type needs a new batch plan → add `references/<paper-type>.md`.
4. If the log format misses something → update this SKILL.md's "Log format" section.

The goal over time: a battle-tested skill that knows exactly how to walk **this specific user** through papers of their typical type. Generic out of the box, increasingly personalized with use.

## Boundary

What this skill is NOT:

- Not a paper summarizer (the user reads; Claude asks).
- Not a translation tool (Claude can paraphrase a stuck paragraph in plain English / Chinese on request, but that's a sub-mode, not the default).
- Not an auto-grader (Claude spot-checks but doesn't grade — the user owns whether they "got" each question).
- Not paragraph-by-paragraph forced reading (the user reads what answers the question; the rest can be skipped).
