# Does each line range PR-Agent cites fall inside a new-side hunk of the diff
# it was given? Nothing in PR-Agent checks this; this is the after-the-fact check.
#
#   python cite_check.py   (run from evidence/public-tools/; needs pyyaml)
import json, re
import yaml

def ranges(diff):
    r, f = {}, None
    for l in open(diff):
        if l.startswith('+++ b/'):
            f = l[6:].strip()
        m = re.match(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', l)
        if m and f:
            s, n = int(m.group(1)), int(m.group(2) or 1)
            r.setdefault(f, []).append((s, s + max(n, 1) - 1))
    return r

def verdict(R, f, a, b):
    if f not in R:
        return 'file-not-in-diff'
    return 'inside-hunk' if any(s <= a and b <= e for s, e in R[f]) else 'outside-hunks'

def answer(call):
    t = json.load(open(f'pr-agent-live/gateway/{call}.response.json'))['choices'][0]['message']['content']
    return yaml.safe_load(re.sub(r'^```(yaml)?\n|```\s*$', '', t.strip(), flags=re.M))

for fx in ['2c0f3e7', 'ab3a477', '701751b']:
    R = ranges(f'pr-agent/{fx}.diff')
    review = json.load(open(f'pr-agent-live/{fx}.review.result.json'))['review']
    for i in review.get('key_issues_to_review') or []:
        f = str(i['relevant_file']).strip()
        print(fx, 'review', f, i['start_line'], i['end_line'],
              verdict(R, f, int(i['start_line']), int(i['end_line'])))

# improve's line ranges come from its self-reflection call (011, 701751b);
# the other fixtures returned no suggestions.
R = ranges('pr-agent/701751b.diff')
for s in answer('011')['code_suggestions']:
    f = str(s['relevant_file']).strip()
    a, b = int(s['relevant_lines_start']), int(s['relevant_lines_end'])
    print('701751b', 'improve', f, a, b, verdict(R, f, a, b))
