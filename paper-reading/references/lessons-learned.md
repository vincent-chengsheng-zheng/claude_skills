# Paper-Reading Skill — Lessons Learned

Date-stamped record of what works and what doesn't. Add an entry whenever a session reveals something worth keeping. If broad enough to change defaults, also update `SKILL.md`.

**Format:** `YYYY-MM-DD — <one-line lesson> — [symptom / context]`

---

## Question phrasing

- **2026-05-18** — The gap-sentence question's hint should mention BOTH variants: "However, prior work..." AND "Even if X is solved, integration of X+Y is challenging..." — [user found a *challenge* statement as their gap guess in HomeRobot OVMM; needed clarification that both phrasings count. Some abstracts don't have an explicit "However" gap at all.]

## Hint patterns that work

- **2026-05-18** — **Table-parse for stuck sentences**: when the user says "I can't read this," put the sentence into a 2-column table `phrase | plain English / 中文`, then give the one-line meaning below. Unblocks fast. — [user couldn't parse "integration of the solutions to these sub-problems poses its own substantial challenges"; the table-parse worked.]

- **2026-05-18** — **School exam analogy** for benchmark-paper structure: `benchmark = exam, baseline = student, score = how they did`. Lands for non-native-English users confused about why a benchmark paper reports performance numbers. — [user thought 20% success rate meant their own robot wouldn't work; analogy + Chinese summary resolved it in one round.]

## Question types that fatigue fast

- *(none observed yet)*

## Paper-type-specific notes

- **2026-05-18** — Benchmark abstracts come in two gap-framing styles: (a) "However, prior work is limited to X" (explicit complaint) and (b) "Sub-problems exist but integration is hard" (challenge framing). HomeRobot OVMM uses (b). Question hints should accept both.

## Log format adjustments

- **2026-05-18** — Need a **live insights buffer** during a batch: capture benchmark-design realizations as they happen (mid-question), not just at batch wrap-up. The user's organic baseline question in Batch 1 generated 3 distinct insights worth separate bullets — would have been lost if batched up at the end.

## User-specific calibration

*Patterns specific to THIS user (vincent — hospital retrieval benchmark project).*

- **2026-05-18 — Strong subject knowledge, intermediate-academic English.** Reads English with full comprehension but slowly; sentences with nominalizations ("integration of the solutions...") trip them up.
- **2026-05-18 — Connects everything to own paper.** Every explanation of a paper choice should END with a "what to steal" template they can mirror. They do this instinctively in their head; making it explicit accelerates it.
- **2026-05-18 — Chinese summary as safety net, not primary.** Welcomes a Chinese 1-paragraph summary AFTER an English explanation of a hard concept. Does NOT want Chinese as the default language.
- **2026-05-18 — Asks deep "why" questions when something doesn't fit their model.** These organic moments are the most valuable in a session — more valuable than the prepared questions. Don't treat them as derailments; treat them as the real teaching opportunity.
- **2026-05-18 — Has ADHD.** Self-led tasks fail. One question at a time in chat, with Claude doing the bookkeeping, works. Visible progress (session log accumulating) helps.
