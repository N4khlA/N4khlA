#!/usr/bin/env python3
"""Render the `> tail -f activity.log` cards from real GitHub data.

Writes two SVGs into the output dir:
  activity-grid.svg  contribution calendar, red squares by level + level bar
  top-langs.svg      most used languages across owned, non-fork public repos

With GITHUB_TOKEN set it uses the GraphQL API (what the workflow does);
without it, it falls back to the public calendar page and the REST API,
which is handy for running it locally.
"""

import html
import json
import os
import re
import sys
import urllib.request
from datetime import date

LOGIN = os.environ.get("GH_LOGIN", "N4khlA")
TOKEN = os.environ.get("GITHUB_TOKEN")
OUT = sys.argv[1] if len(sys.argv) > 1 else "dist"

# repos left out of the language stats (the profile repo only holds this script)
EXCLUDE_REPOS = {LOGIN}

BG = "#0d1117"
TEXT = "#c9d1d9"
MUTED = "#8b949e"
RED = "#ff4d4d"
LEVELS = ["#161b22", "#561414", "#8f1f1f", "#c93333", "#ff4d4d"]
LANG_COLORS = ["#ff4d4d", "#ffa3a3", "#c23030", "#8b949e", "#7a1a1a", "#d0d7de"]
FONT = "ui-monospace,SFMono-Regular,'JetBrains Mono',Menlo,Consolas,monospace"
LEVEL_NAMES = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
               "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def get(url, data=None, accept="application/json"):
    headers = {"User-Agent": "activity-log-svg", "Accept": accept}
    if TOKEN:
        headers["Authorization"] = f"bearer {TOKEN}"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode()


def graphql(query):
    body = json.dumps({"query": query, "variables": {"login": LOGIN}}).encode()
    res = json.loads(get("https://api.github.com/graphql", body))
    if res.get("errors"):
        sys.exit(f"graphql: {res['errors']}")
    return res["data"]["user"]


# --- data -------------------------------------------------------------------

def calendar():
    """Return (total, weeks) where weeks is a list of [(date, weekday, count, level)]."""
    if TOKEN:
        cal = graphql("""query($login:String!){user(login:$login){
          contributionsCollection{contributionCalendar{totalContributions
            weeks{contributionDays{date weekday contributionCount contributionLevel}}}}}}""")
        cal = cal["contributionsCollection"]["contributionCalendar"]
        weeks = [[(d["date"], d["weekday"], d["contributionCount"],
                   LEVEL_NAMES[d["contributionLevel"]]) for d in w["contributionDays"]]
                 for w in cal["weeks"]]
        return cal["totalContributions"], weeks

    page = get(f"https://github.com/users/{LOGIN}/contributions", accept="text/html")
    counts = {}
    for cell_id, text in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)', page):
        m = re.match(r"\s*(\d+) contribution", text)
        counts[cell_id] = int(m.group(1)) if m else 0
    weeks = {}
    for day, cell_id, level in re.findall(
            r'data-date="([\d-]+)" id="(contribution-day-component-\d+-\d+)" data-level="(\d)"', page):
        wd, wk = map(int, cell_id.rsplit("-", 2)[1:])
        weeks.setdefault(wk, []).append((day, wd, counts.get(cell_id, 0), int(level)))
    weeks = [sorted(weeks[k], key=lambda d: d[1]) for k in sorted(weeks)]
    return sum(d[2] for w in weeks for d in w), weeks


def languages():
    """Return [(name, bytes)] summed over owned, non-fork public repos, biggest first."""
    totals = {}
    if TOKEN:
        user = graphql("""query($login:String!){user(login:$login){
          repositories(first:100, ownerAffiliations:OWNER, isFork:false, privacy:PUBLIC){
            nodes{name languages(first:20){edges{size node{name}}}}}}}""")
        for repo in user["repositories"]["nodes"]:
            if repo["name"] in EXCLUDE_REPOS:
                continue
            for e in repo["languages"]["edges"]:
                totals[e["node"]["name"]] = totals.get(e["node"]["name"], 0) + e["size"]
    else:
        repos = json.loads(get(f"https://api.github.com/users/{LOGIN}/repos?per_page=100&type=owner"))
        for repo in repos:
            if repo["fork"] or repo["name"] in EXCLUDE_REPOS:
                continue
            for name, size in json.loads(get(repo["languages_url"])).items():
                totals[name] = totals.get(name, 0) + size
    return sorted(totals.items(), key=lambda kv: -kv[1])


# --- svg --------------------------------------------------------------------

def grid_svg(total, weeks):
    cell, pitch = 12, 16
    left, top = 36, 46
    width = left + len(weeks) * pitch + 12
    gy = top + 7 * pitch
    bar_y = gy + 18
    height = bar_y + 44

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t">',
           f'<title id="t">{total} contributions in the last year</title>',
           f'<style>text{{font-family:{FONT};fill:{MUTED};font-size:11px}}'
           f'.h{{fill:{TEXT};font-size:13px}}.h tspan{{fill:{RED};font-weight:700}}'
           f'.bar{{transform-origin:{left}px 0;animation:grow 1.4s ease-out both}}'
           '@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}</style>',
           f'<rect width="100%" height="100%" rx="6" fill="{BG}"/>',
           f'<text class="h" x="{left}" y="20"><tspan>&gt;</tspan> {total} contributions in the last year</text>']

    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="{left - 6}" y="{top + row * pitch + 10}" text-anchor="end">{name}</text>')

    last_month, last_col = None, -9
    for col, week in enumerate(weeks):
        month = date.fromisoformat(week[0][0]).strftime("%b")
        if month != last_month and col - last_col >= 3 and col < len(weeks) - 1:
            out.append(f'<text x="{left + col * pitch}" y="{top - 8}">{month}</text>')
            last_col = col
        last_month = month
        for day, wd, count, level in week:
            tip = f"{count} contribution{'s' * (count != 1)} on {day}"
            out.append(f'<rect x="{left + col * pitch}" y="{top + wd * pitch}" width="{cell}" '
                       f'height="{cell}" rx="2" fill="{LEVELS[level]}"><title>{tip}</title></rect>')

    # level bar: one segment per level, width = share of active days at that level
    bar_w = len(weeks) * pitch - (pitch - cell)
    per_level = [sum(1 for w in weeks for d in w if d[3] == lv) for lv in range(1, 5)]
    out.append(f'<rect x="{left}" y="{bar_y}" width="{bar_w}" height="10" fill="{LEVELS[0]}"/>')
    out.append('<g class="bar">')
    x, active = left, sum(per_level) or 1
    for lv, n in enumerate(per_level, start=1):
        w = bar_w * n / active
        if w:
            out.append(f'<rect x="{x:.1f}" y="{bar_y}" width="{w:.1f}" height="10" fill="{LEVELS[lv]}"/>')
        x += w
    out.append('</g>')

    ly = bar_y + 30
    lx = left + bar_w - 5 * 16 - 30
    out.append(f'<text x="{lx - 6}" y="{ly + 10}" text-anchor="end">less</text>')
    for i, c in enumerate(LEVELS):
        out.append(f'<rect x="{lx + i * 16}" y="{ly}" width="{cell}" height="{cell}" rx="2" fill="{c}"/>')
    out.append(f'<text x="{lx + 5 * 16 + 2}" y="{ly + 10}">more</text>')
    active_days = sum(per_level)
    out.append(f'<text x="{left}" y="{ly + 10}">{active_days} active day{"s" * (active_days != 1)}</text>')
    out.append('</svg>')
    return "\n".join(out)


def langs_svg(langs, count=6):
    top = langs[:count]
    total = sum(n for _, n in top) or 1
    width, pad, bar_w = 420, 25, 370
    rows = (len(top) + 1) // 2
    height = 82 + rows * 25

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t">',
           '<title id="t">Most used languages</title>',
           f'<style>text{{font-family:{FONT};fill:{TEXT};font-size:12px}}'
           f'.h{{fill:{RED};font-size:16px;font-weight:700}}</style>',
           f'<rect width="100%" height="100%" rx="6" fill="{BG}"/>',
           f'<text class="h" x="{pad}" y="32">Most Used Languages</text>',
           f'<clipPath id="c"><rect x="{pad}" y="48" width="{bar_w}" height="8" rx="4"/></clipPath>',
           f'<rect x="{pad}" y="48" width="{bar_w}" height="8" rx="4" fill="{LEVELS[0]}"/>',
           '<g clip-path="url(#c)">']
    x = pad
    for i, (_, n) in enumerate(top):
        w = bar_w * n / total
        out.append(f'<rect x="{x:.1f}" y="48" width="{w + 0.5:.1f}" height="8" fill="{LANG_COLORS[i]}"/>')
        x += w
    out.append('</g>')
    for i, (name, n) in enumerate(top):
        cx = pad + (i % 2) * 185
        cy = 82 + (i // 2) * 25
        out.append(f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{LANG_COLORS[i]}"/>')
        out.append(f'<text x="{cx + 16}" y="{cy}">{html.escape(name)} '
                   f'<tspan fill="{MUTED}">{100 * n / total:.1f}%</tspan></text>')
    out.append('</svg>')
    return "\n".join(out)


def main():
    os.makedirs(OUT, exist_ok=True)
    total, weeks = calendar()
    langs = languages()
    with open(os.path.join(OUT, "activity-grid.svg"), "w") as f:
        f.write(grid_svg(total, weeks))
    with open(os.path.join(OUT, "top-langs.svg"), "w") as f:
        f.write(langs_svg(langs))
    active = [(d[0], d[2]) for w in weeks for d in w if d[2]]
    print(f"{total} contributions, {len(weeks)} weeks, active days: {active}")
    print("languages:", ", ".join(f"{n} {s}" for n, s in langs[:6]))


if __name__ == "__main__":
    main()
