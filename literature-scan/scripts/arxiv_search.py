#!/usr/bin/env python3
"""
Run multiple arXiv keyword queries with rate-limit-aware backoff, dedupe, rank.

Usage:
  python3 arxiv_search.py --queries queries.txt --known known_ids.txt --out candidates.json
  python3 arxiv_search.py --query 'all:"hospital" AND all:"retrieval"' --out one_shot.json

queries.txt:
  one arXiv search_query string per line, '#' for comments

known_ids.txt:
  one arXiv ID per line (without version suffix), '#' for comments
  these are excluded from results (papers already in your scan)

Output JSON: list of {id, title, pub, summary, queries} ranked by query-overlap.
"""
import argparse, json, re, sys, time, urllib.parse, urllib.request


def parse_lines(path: str) -> list[str]:
    if not path:
        return []
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line)
    return out


def query_arxiv(query: str, max_results: int = 20, timeout: int = 60) -> list[dict]:
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
    })
    with urllib.request.urlopen(url, timeout=timeout) as r:
        txt = r.read().decode("utf-8", errors="replace")
    out = []
    for e in re.findall(r"<entry>(.*?)</entry>", txt, re.S):
        idm = re.search(r"<id>http://arxiv.org/abs/([^<]+)</id>", e)
        tm = re.search(r"<title>(.*?)</title>", e, re.S)
        pm = re.search(r"<published>(.*?)</published>", e)
        sm = re.search(r"<summary>(.*?)</summary>", e, re.S)
        if not idm:
            continue
        full_id = idm.group(1)
        base_id = re.sub(r"v\d+$", "", full_id)
        title = re.sub(r"\s+", " ", (tm.group(1) if tm else "").strip())
        pub = pm.group(1)[:10] if pm else "?"
        summary = re.sub(r"\s+", " ", (sm.group(1) if sm else "").strip())[:300]
        out.append({"id": base_id, "title": title, "pub": pub, "summary": summary})
    return out


def query_with_backoff(query: str, max_attempts: int = 3, base_wait: int = 10, **kwargs) -> list[dict]:
    for attempt in range(max_attempts):
        try:
            return query_arxiv(query, **kwargs)
        except Exception as e:
            wait = base_wait * (attempt + 1)
            print(f"  attempt {attempt + 1}/{max_attempts} failed: {e}; waiting {wait}s", file=sys.stderr)
            if attempt + 1 < max_attempts:
                time.sleep(wait)
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", help="File with one query per line")
    ap.add_argument("--query", help="Single query (alternative to --queries)")
    ap.add_argument("--known", help="File with known arXiv IDs to exclude (one per line)")
    ap.add_argument("--out", default="candidates.json", help="Output JSON path")
    ap.add_argument("--max-results", type=int, default=20)
    ap.add_argument("--spacing", type=int, default=5, help="Seconds between successful queries")
    args = ap.parse_args()

    if args.queries and args.query:
        sys.exit("Use --queries OR --query, not both")
    queries = [args.query] if args.query else parse_lines(args.queries) if args.queries else []
    if not queries:
        sys.exit("No queries supplied")
    known = set(parse_lines(args.known)) if args.known else set()

    seen: dict[str, dict] = {}
    for q in queries:
        print(f"\n# QUERY: {q}", file=sys.stderr)
        results = query_with_backoff(q, max_results=args.max_results)
        if not results:
            print("  GIVING UP on this query", file=sys.stderr)
            continue
        new = 0
        for r in results:
            if r["id"] in known:
                continue
            if r["id"] in seen:
                seen[r["id"]]["queries"].append(q[:60])
            else:
                seen[r["id"]] = {**r, "queries": [q[:60]]}
                new += 1
        print(f"  hits={len(results)} new={new}", file=sys.stderr)
        time.sleep(args.spacing)

    ranked = sorted(seen.values(), key=lambda r: (-len(r["queries"]), r["pub"]), reverse=False)
    ranked.sort(key=lambda r: (-len(r["queries"]), r["pub"]))

    with open(args.out, "w") as f:
        json.dump(ranked, f, indent=2)
    print(f"\nWrote {len(ranked)} unique candidates to {args.out}", file=sys.stderr)

    # Print top of ranked list to stdout for quick triage
    for r in ranked[:30]:
        print(f"[{r['pub']}] {r['id']}  hits={len(r['queries'])}")
        print(f"  {r['title']}")


if __name__ == "__main__":
    main()
