#!/usr/bin/env bash
# Verify a list of arXiv IDs resolve, print title and publication date for each.
# Usage: ./verify_arxiv_ids.sh 2306.11565 2504.15418 ...
# Or:    cat ids.txt | xargs ./verify_arxiv_ids.sh

set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <arxiv_id> [<arxiv_id> ...]" >&2
  exit 1
fi

# Join IDs with commas for a single batch request (more polite + faster than N requests)
joined=$(IFS=,; echo "$*")

curl -sL "https://export.arxiv.org/api/query?id_list=${joined}&max_results=$#" 2>/dev/null | \
python3 -c "
import sys, re
xml = sys.stdin.read()
entries = re.findall(r'<entry>(.*?)</entry>', xml, re.S)
if not entries:
    print('NO ENTRIES RETURNED — likely 429 or 503. Try again in 60s.', file=sys.stderr)
    sys.exit(2)
for e in entries:
    idm = re.search(r'<id>http://arxiv.org/abs/([^<]+)</id>', e)
    tm = re.search(r'<title>(.*?)</title>', e, re.S)
    pm = re.search(r'<published>(.*?)</published>', e)
    full_id = idm.group(1) if idm else '?'
    base_id = re.sub(r'v\d+$', '', full_id)
    title = re.sub(r'\s+', ' ', (tm.group(1) if tm else '').strip())
    pub = pm.group(1)[:10] if pm else '?'
    print(f'[{pub}] {base_id}')
    print(f'  {title}')
"
