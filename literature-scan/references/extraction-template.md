# Tier-1 Paper Extraction Template

For each closest-competitor paper, fill in this 7-row table. Filling pre-defined cells is faster than deciding what to extract on the fly, and it makes the cross-paper comparison table for §2 Related Work nearly automatic.

## The 7 rows

| # | Row | What to capture | Why it matters |
|---|---|---|---|
| 1 | **Tasks** | Count, types, granularity. Are tasks atomic ("pick object") or composite ("retrieve medication from pharmacy to ward 3 within 5 min")? | Defines the unit of evaluation — the most-cited dimension of a benchmark. |
| 2 | **Success criteria** | Hard pass/fail or graded? Single criterion or multi (success + time + collisions)? Per-task or per-episode? | Shapes how you'll design yours. Soft criteria invite reviewer pushback unless justified. |
| 3 | **Metrics** | Which metrics, how reported (mean / median / stderr / CI / per-task / aggregate). Statistical treatment? | This is where most benchmarks under-deliver. Strong stats = strong paper. |
| 4 | **Baselines** | Count, types (heuristic / learned / oracle / human). What's the spread between best and worst? | A benchmark with one baseline is weak; reviewers want to see the axis exercised. |
| 5 | **Scenes / splits** | How scenes are generated (hand-crafted / procedural / mined). Train/val/test policy. Held-out variations. | Determines whether the benchmark measures generalization or memorization. |
| 6 | **Evaluation protocol** | Trials per task, seed control, reproducibility (code/leaderboard/eval server). | The "Datasets & Benchmarks" track at NeurIPS literally reviews this. |
| 7 | **Differentiation paragraph** | One paragraph stating *how our work differs* from this paper. | The deliverable for §2 — one of these per Tier-1 paper. |

## How to use it

1. Read the paper's abstract + intro + §3 (or wherever the benchmark/method is described) + §4 (experiments).
2. Fill cells. Quote short phrases where helpful.
3. Move on — don't try to read the whole paper end-to-end on the first pass.

A skilled reader can fill this for one paper in ~30–45 min.

## Comparison table for §2

Once you have 4–5 of these filled in, the §2 table is just a transpose:

| Aspect | Paper A | Paper B | Paper C | Paper D | **Ours** |
|---|---|---|---|---|---|
| Tasks | ... | ... | ... | ... | ... |
| Success criteria | ... | ... | ... | ... | ... |
| ... | | | | | |

Plus the per-paper differentiation paragraph below the table.

## Quality checklist

Before declaring a paper "extracted":
- [ ] Tasks row has both count and type.
- [ ] Success criteria row says HARD or SOFT.
- [ ] Metrics row names *specific* metrics (not "they report performance").
- [ ] Baselines row has a count.
- [ ] Differentiation paragraph names ≥1 concrete axis where we differ.
- [ ] You wrote down ≥1 thing you'd steal (good idea worth borrowing).
