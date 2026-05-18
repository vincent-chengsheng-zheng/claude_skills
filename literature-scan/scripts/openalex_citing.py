#!/usr/bin/env python3
"""
Fetch citing papers for seed works from OpenAlex; score candidates by overlap.

Usage:
  python3 openalex_citing.py \
      --seeds 2306.11565=HomeRobot 2504.15418=MRTA-Sim \
      --mail you@example.com \
      --domain-regex 'hospital|medic|clinical' \
      --out openalex_candidates.json

The --domain-regex is OPTIONAL — gives a relevance bonus when a citing-paper title matches.
Without it, ranking is purely by cross-seed overlap and citation count.
"""
import argparse, json, re, sys, time, urllib.parse, urllib.request


def resolve_arxiv(arxiv_id: str, mail: str) -> str | None:
    url = f"https://api.openalex.org/works/doi:10.48550/arXiv.{arxiv_id}?mailto={mail}"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            d = json.load(r)
        return (d.get("id") or "").rsplit("/", 1)[-1] or None
    except Exception as e:
        print(f"  resolve fail for {arxiv_id}: {e}", file=sys.stderr)
        return None


def fetch_citing(work_id: str, mail: str, max_pages: int = 4) -> list[dict]:
    out = []
    for page in range(1, max_pages + 1):
        url = (
            f"https://api.openalex.org/works?filter=cites:{work_id}"
            f"&per-page=50&page={page}"
            f"&select=id,title,publication_year,cited_by_count,doi,primary_location"
            f"&mailto={mail}"
        )
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                d = json.load(r)
        except Exception as e:
            print(f"  page {page} fail: {e}", file=sys.stderr)
            break
        results = d.get("results") or []
        if not results:
            break
        out.extend(results)
        time.sleep(0.4)
        if len(results) < 50:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", nargs="+", required=True,
                    help="seed list as ARXIV_ID=LABEL pairs, e.g. 2306.11565=HomeRobot")
    ap.add_argument("--mail", required=True, help="email for OpenAlex polite pool")
    ap.add_argument("--domain-regex", default=None,
                    help="optional regex; citing-papers whose title matches get +5 score")
    ap.add_argument("--retrieval-regex", default=r"retriev|fetch|navigation|manipulation|benchmark|dataset|multi[- ]robot",
                    help="regex for retrieval/benchmark-language relevance (+2 score)")
    ap.add_argument("--known", help="file with known arXiv/title patterns to exclude")
    ap.add_argument("--out", default="openalex_candidates.json")
    args = ap.parse_args()

    seeds = {}
    for s in args.seeds:
        if "=" not in s:
            sys.exit(f"bad seed format: {s} (expected ARXIV_ID=LABEL)")
        axid, label = s.split("=", 1)
        seeds[label] = axid

    known_lc = set()
    if args.known:
        with open(args.known) as f:
            for line in f:
                line = line.strip().lower()
                if line and not line.startswith("#"):
                    known_lc.add(line)

    domain_re = re.compile(args.domain_regex, re.I) if args.domain_regex else None
    retr_re = re.compile(args.retrieval_regex, re.I)

    overlap: dict[str, dict] = {}
    for label, axid in seeds.items():
        print(f"\n=== {label} (arXiv:{axid}) ===", file=sys.stderr)
        wid = resolve_arxiv(axid, args.mail)
        if not wid:
            continue
        print(f"  OAID: {wid}", file=sys.stderr)
        citing = fetch_citing(wid, args.mail)
        print(f"  citing papers: {len(citing)}", file=sys.stderr)
        for w in citing:
            title = (w.get("title") or "").strip()
            tlc = title.lower()
            if not title or tlc in known_lc:
                continue
            rec = overlap.setdefault(tlc, {
                "title": title,
                "year": w.get("publication_year"),
                "cited_by": w.get("cited_by_count"),
                "doi": w.get("doi"),
                "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
                "seeds": [],
            })
            rec["seeds"].append(label)
        time.sleep(0.4)

    ranked = []
    for rec in overlap.values():
        score = 3 * (len(rec["seeds"]) - 1)
        if domain_re and domain_re.search(rec["title"]):
            score += 5
        if retr_re.search(rec["title"]):
            score += 2
        if (rec.get("cited_by") or 0) >= 5:
            score += 1
        rec["score"] = score
        ranked.append(rec)
    ranked.sort(key=lambda r: (-r["score"], -(r.get("cited_by") or 0)))

    with open(args.out, "w") as f:
        json.dump(ranked, f, indent=2)
    print(f"\nWrote {len(ranked)} candidates to {args.out}", file=sys.stderr)

    print(f"\n=== TOP (score >= 5 or appears in 2+ seeds) ===")
    for rec in ranked:
        if rec["score"] >= 5 or len(rec["seeds"]) >= 2:
            print(f"\nscore={rec['score']:3}  [{rec.get('year')}]  cited_by={rec.get('cited_by'):>4}  seeds={rec['seeds']}")
            print(f"  {rec['title']}")
            print(f"  doi={rec.get('doi')}  venue={rec.get('venue')}")


if __name__ == "__main__":
    main()
