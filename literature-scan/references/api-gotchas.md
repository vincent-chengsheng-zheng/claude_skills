# Academic API Gotchas — Field Notes

Lessons captured from real lit-scan sessions. Update this file when a new gotcha surfaces.

---

## arXiv API

**Endpoint:** `https://export.arxiv.org/api/query` (https, NOT http — http redirects but is sometimes treated as abuse)

**Two query modes:**

1. **ID verification (reliable):**
   ```
   ?id_list=2306.11565,2504.15418&max_results=10
   ```
   Use this to confirm a list of IDs resolve and grab titles. Almost never rate-limits unless you're hammering.

2. **Keyword search (rate-limited):**
   ```
   ?search_query=all:"hospital"+AND+all:"mobile manipulation"&max_results=20&sortBy=relevance
   ```
   - Quote multi-word phrases with `%22...%22` (URL-encoded).
   - `all:` searches title+abstract+full-text. Use `ti:` for title-only if you want stricter matching.
   - Boolean: `AND` `OR` `ANDNOT`. Group with parentheses.

**Rate limit reality:**
- Documented as "1 request per 3 seconds." In practice the first 3–4 requests work, then bursts of `429 Too Many Requests` arrive in waves for several minutes.
- Backoff strategy that works: 5s baseline between requests, exponential backoff (10s, 20s, 40s) on 429, give up after 3 retries.
- Different endpoints share the bucket. Hammering `id_list` while running search queries gets you 429'd faster.
- A 503 from `export.arxiv.org` means upstream Varnish is overloaded — wait 60s+.

**Response format:** Atom XML. Each `<entry>` has `<id>`, `<title>`, `<summary>`, `<published>`, `<author>`, `<category>`. The `<id>` is the URL form `http://arxiv.org/abs/<id>v<N>` — strip the version with `re.sub(r"v\d+$", "", id_str)` to get the canonical ID.

**Sorting:** `sortBy=relevance` (default), `submittedDate`, or `lastUpdatedDate`. Combined with `sortOrder=ascending|descending`. **Default ranking is keyword-match-based, NOT citation-based** — be aware this isn't the same as "most relevant academically."

---

## Semantic Scholar API

**Endpoint:** `https://api.semanticscholar.org/graph/v1/...`

**The unauthenticated reality:**
- Anonymous requests share a **global** rate-limit pool with every other anonymous user on the planet. That pool is essentially always saturated. Expect `429 Too Many Requests` on essentially every call from a shared IP.
- The 429 isn't your fault — it's the pool's fault. Adding `User-Agent` or `Accept` headers doesn't help.
- **Strong recommendation: request a free API key.** Form: <https://www.semanticscholar.org/product/api>. Approval is usually <24h. With a key you get ~5000 req/5min, plus access to `paper/batch` (POST up to 500 IDs at once).

**Key endpoints (with API key in `x-api-key` header):**

```
GET /paper/<id-or-DOI-or-arXiv:xxxx.xxxxx>
    ?fields=title,year,authors,venue,citationCount,externalIds,abstract
GET /paper/<id>?fields=references.title,references.year,references.externalIds
GET /paper/<id>?fields=citations.title,citations.year,citations.externalIds
GET /paper/search?query=<urlencoded>&limit=20&fields=...
POST /paper/batch  body: {"ids": [...]}, query: ?fields=...
```

**Field selection:** Always specify `fields=...` — by default S2 returns minimal data. Use `references.externalIds` to get arXiv IDs of referenced papers, then traverse.

**Why S2 matters for lit scans:** It's the only free API with broad coverage of the *references* and *citations* graph across robotics conferences, journals, and arXiv preprints in one place. OpenAlex's coverage is comparable but its preprint references are often empty (see below). Without S2 (or a Crossref-based stack), the citation graph step has to fall back to OpenAlex `cites:`, which only catches a fraction.

---

## OpenAlex API

**Endpoint:** `https://api.openalex.org/works/...` and `https://api.openalex.org/works?filter=...`

**Always include `?mailto=<your_email>`** — moves you into the "polite pool" with higher limits (~10 req/sec) and better priority. No key needed.

**Resolving arXiv → OpenAlex work:**
```
GET /works/doi:10.48550/arXiv.<arxiv_id>?mailto=...
```
arXiv preprints get OpenAlex IDs of the form `W<digits>`. The conference/journal version is sometimes a *separate* work — OpenAlex doesn't always merge them. Search by title if the DOI lookup gives a sparse record.

**Reference data — the big trap:**
- `referenced_works` is *frequently empty* for arXiv preprints, because OpenAlex relies on Crossref to parse the PDF references and Crossref's arXiv coverage is incomplete.
- For published-venue versions (ICRA, NeurIPS), `referenced_works` is usually populated. Same paper, different work ID.

**Citing-papers (works well):**
```
GET /works?filter=cites:<work_id>&per-page=50&select=id,title,publication_year,cited_by_count,doi,primary_location&mailto=...
```
Paginated; check `meta.count` to know total. Returns up to 200/page. Even when `referenced_works` is empty for the seed, `cites:<seed>` works because OpenAlex indexes citation edges from the citing side.

**Coverage caveat:** recent (<1 year) preprints often show low `cited_by_count` not because they're uncited, but because OpenAlex hasn't indexed the citing papers yet. Don't conclude "this paper is unimportant" from a low count.

---

## Crossref (alternative for references)

Not used in the original test but worth knowing:
- `https://api.crossref.org/works/<DOI>` — returns full reference list when the publisher submitted them. Good for IEEE/ACM/Springer papers.
- Free, polite pool with `mailto=` param.
- Doesn't cover arXiv preprints directly; need to use the published-version DOI.

---

## PDF bibliography mining

The most under-rated step. When a recent survey or major related paper covers your area:

```bash
pdftotext paper.pdf paper.txt
# locate bibliography:
grep -nE "^References$|^Bibliography$" paper.txt
# extract entries:
grep -nE "^\[[0-9]+\]" paper.txt | head -50
```

The bibliography of a single well-curated survey often gives you 50+ relevant references in 5 minutes — no rate limits, no API keys.

Look for:
- Tables/figures listing "datasets and benchmarks" by category.
- Section structure that maps to your axes.
- Numerical citation markers (`[123]`) in those sections; trace back to the bibliography for full info.

---

## Google Scholar

- **No free programmatic API.** Scrapers exist (`scholarly`, `serpapi`) but they get rate-limited / CAPTCHA'd quickly and may violate ToS.
- The user must do this step manually. 30 minutes on Scholar with 2–3 well-formed queries (compound terms in quotes) often catches what every API missed, especially older conference proceedings.
- Sort by relevance (default) first, then re-sort by date for recent work that hasn't accumulated citations.

---

## Hallucination patterns to watch for

When auditing a prior LLM-generated scan:

- **Fabricated arXiv IDs**: The number is plausibly formatted (YYMM.NNNNN) but doesn't resolve. Always verify with `id_list`.
- **Mismatched titles**: ID exists, but the title in the citation is wrong (paper next-door in arXiv).
- **Misranked relevance**: a "closest competitor" claim that, on inspection, only matches 1 of 5 axes. Re-score against pillars explicitly.
- **Phantom benchmarks**: a "benchmark" that's actually a method paper or position paper. Check the abstract for "we propose a benchmark/dataset/protocol" vs "we propose a method."
- **Date drift**: claims a paper is from 2024 when it's 2022 (or vice versa). Compare claim against arXiv's `<published>` field.

---

## What to do when everything is rate-limited

In order of preference:
1. **Wait an hour and retry.** Most academic API rate limits reset within 15–60 min.
2. **Switch tool.** arXiv 429'd? Try OpenAlex search. OpenAlex slow? Try Crossref.
3. **Drop to PDF mining.** Survey + closest competitor's related-work sections need no API.
4. **Document the limit and tell the user.** Honest "I couldn't complete the citation-graph step because S2 was rate-limited and OpenAlex has sparse preprint refs" is far better than a confident incomplete scan.
