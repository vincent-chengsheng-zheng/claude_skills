---
name: literature-scan
description: Conduct a literature scan for academic / research work — find related papers, verify a benchmark's novelty, check whether a prior scan has gaps, or audit cited references. Use whenever the user asks to "find related papers", "do a lit review / lit scan", "check if X has been done before", "is this novel", "verify these citations", "search arXiv / Semantic Scholar / OpenAlex", or wants to assess recall of an existing scan. Also use proactively before claiming a research direction is novel.
version: 0.1.0
---

# Literature Scan

A protocol for academic literature searches that prioritizes **recall** (did we find everything that matters?) over **precision** (do our citations exist?). Both matter, but most failures come from recall gaps masked by confident-looking precision.

## When this applies

- User asks for a literature scan, related-work search, or novelty check.
- User questions whether an existing scan is complete.
- User is about to claim a benchmark/method is novel — pause and verify.
- User wants to verify a list of citations resolves (precision check).

## Core principle

**Web search ranking ≠ academic relevance ranking.** Google web search and the equivalent built-in tools are tuned for general queries, not citation centrality. A paper that's heavily cited in robotics but poorly SEO'd can be invisible to `WebSearch`. For real recall, use:

1. **The related-work sections of the 3–5 closest competitor papers.** Their authors already did the search, with publisher access and curation. Reading their related-work is the single highest-yield action in a literature scan.
2. **Citation graphs** (Semantic Scholar `references`/`citations`, OpenAlex `cites:` filter).
3. **Targeted academic-API queries** (arXiv, S2) — not generic web search.
4. **Manual Google Scholar pass** — irreplaceable; APIs don't replicate Scholar's ranking.

The biggest mistake is to do (3) alone via `WebSearch` and stop. That gives the *appearance* of a scan without recall confidence.

## Recommended workflow

### Step 0 — State the recall criteria

Before searching, write down the pillars/axes that define "related" for this scan. E.g., for a hospital retrieval benchmark: hospital domain + language-conditioned + multi-robot + retrieval + clinician-grounded + is-a-benchmark. Pillars determine how you score candidates later — without them, you'll drift into "anything mentioning the keyword."

### Step 1 — Verify any existing scan's citations (precision check)

For each cited arXiv ID in the prior scan, hit the arXiv API and confirm title matches:

```bash
bash scripts/verify_arxiv_ids.sh 2306.11565 2504.15418 ...
```

If a title doesn't match or 404s, the ID is hallucinated. Common with prior LLM-generated scans.

### Step 2 — Read closest competitors' related-work sections

Identify 3–5 closest papers (from the existing scan or one round of targeted queries). Download PDFs, extract their **Related Work** section, and harvest references. Any paper that appears in 2+ of those related-work sections and isn't in your scan is a likely miss. This step alone catches most recall gaps. See `references/extraction-template.md` for what to pull.

### Step 3 — Targeted academic-API queries

Run focused queries against arXiv (and S2 if API key available). Use 6–10 search strings, each combining 2–3 axes from Step 0. See `scripts/arxiv_search.py` — parameterized, dedupes against a known-IDs list, ranks candidates by how many queries surfaced them.

### Step 4 — Citation graph expansion

For 2–3 seed papers, fetch their citing papers and references. With Semantic Scholar key: `paper/<id>?fields=references.*,citations.*`. Without S2: OpenAlex `filter=cites:<work_id>` (works, but coverage of recent arXiv preprints is sparse). See `scripts/openalex_citing.py`.

### Step 5 — Survey bibliography mining (when applicable)

If a recent (≤2 years old) survey covers the area, **mine its bibliography directly** — `pdftotext` then grep for the bibliography section that corresponds to your axis. This is one of the highest-yield steps and has no rate limit. Section names vary ("Datasets and Benchmarks", "Methods", etc.) — look for the figure/table that enumerates the closest cluster to your target.

### Step 6 — Manual Google Scholar spot-check

Spend 20–30 min on Google Scholar with the 2–3 most central queries. Page 1–2. APIs can't replicate Scholar's ranking; if a paper jumps out here and isn't in your candidate list, it's a real miss. **This step is on the human, not Claude** — Scholar has no automatable free API.

### Step 7 — Triage candidates into tiers

For each new candidate:

- **Tier 1**: hits 3+ pillars AND is the kind of artifact you're building (benchmark/system/dataset). Must be discussed.
- **Tier 2**: hits 2 pillars OR strong on one and is in the same artifact class. Cite as context.
- **Tier 3**: keyword adjacency only. Note in raw list, don't cite.

Save the raw list (JSON) so the user can re-audit later. Pre-commit to which tier counts as "must read in full."

### Step 8 — Write the verification report

State precision results, recall confidence, queries actually run vs failed, what remains for human spot-check. Don't claim "complete" if any step was skipped — list the limits explicitly.

## API choice — quick reference

Detailed gotchas in `references/api-gotchas.md`. Short form:

| API | Use it for | Don't use it for | Auth |
|---|---|---|---|
| **arXiv** | Discovery by keyword, ID verification, recent preprints | Citation graph, cross-venue search | None (1 req per ≥3s) |
| **Semantic Scholar** | Citation graph, references, paper metadata across venues | Discovery without keys (anon pool is saturated) | Free key strongly recommended |
| **OpenAlex** | Citing-paper expansion, cross-venue metadata, no-auth use | Preprint references (often empty) | None (more generous with `?mailto=` |
| **Google Scholar** | Best general ranking, hard-to-find venue work | Automation (no free API) | Human-only |

## Common failure modes

1. **Hallucinated arXiv IDs in prior scans.** Always Step 1 first.
2. **"Closest competitor" loosely defined.** "Closest system" ≠ "closest benchmark" ≠ "most-cited adjacent." Disambiguate before claiming.
3. **Anchoring on recent arXiv.** HRI, CHI, ICRA proceedings work older than 1-2 years may not be on arXiv. The survey-mining step or Scholar pass catches these.
4. **Stopping after `WebSearch`.** This is the #1 way an LLM-generated lit scan misses important work. Web ranking isn't citation ranking.
5. **Claiming the gap is unique without naming what would invalidate it.** Always state "the claim would fail if a paper exists doing X+Y+Z."

## Output structure

When delivering results, produce a verification report with these sections:

```markdown
# Literature Scan — <topic>
**Date:** <YYYY-MM-DD>
**Scope:** <one sentence on what counts as related>

## TL;DR
- Precision: <verified | flagged>
- Recall: <high | medium | low>; what wasn't covered

## Methodology
- APIs used (and which failed)
- Queries run (list them)
- Skipped steps (manual Scholar, paywalled DBs)

## Verified IDs
Table mapping claimed → resolved title.

## Tier 1 — must read / discuss
## Tier 2 — context / cite
## Tier 3 — peripheral

## Does this change prior claims?
Specifically address any "no prior work has done X" assertions.

## Limitations of this pass
What didn't get done and why.

## Provenance
Scripts, raw JSON outputs, parameters.
```

## When to skip steps

- **One-off "is X a real paper?"**: only Step 1 needed.
- **Quick novelty check before writing**: Steps 0, 2, 6 (skip API marathon, rely on related-work mining).
- **Auditing someone else's scan**: Steps 1, 2, 5, plus one targeted Step 3 query.
- **Fresh scan, no prior work**: full Steps 0–8.

## Scripts in this skill

- `scripts/verify_arxiv_ids.sh` — confirm a list of arXiv IDs resolve and capture their titles.
- `scripts/arxiv_search.py` — run multiple targeted arXiv queries with rate-limit-aware backoff, dedupe, rank by query overlap.
- `scripts/openalex_citing.py` — pull citing-papers for seed works from OpenAlex, score candidates by overlap across seeds and a domain regex.

All scripts read parameters from CLI args / env vars — they are not project-specific.

## References

- `references/api-gotchas.md` — detailed lessons on each API's rate limits, query syntax, and where their data is sparse.
- `references/extraction-template.md` — the 7-row table to extract from each Tier-1 paper for §2 Related Work.
