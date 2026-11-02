"""Render an SVG stats card from the GitHub GraphQL API.

Counts contributions the way the profile graph does (public + private when the
profile shows private contributions), instead of public commits only.
Usage: python stats_card.py <output.svg>
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from collections import OrderedDict
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "tahahasan01")
TOKEN = os.environ["GITHUB_TOKEN"]


def gql(query):
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": query}).encode(),
                                 headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        body = json.load(r)
    if "errors" in body:
        raise RuntimeError(body["errors"])
    return body["data"]["user"]


def collect():
    base = gql(f"""query {{ user(login: "{USER}") {{
      createdAt
      repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {{ totalCount }}
      contributionsCollection {{
        contributionYears
        contributionCalendar {{ totalContributions weeks {{ contributionDays {{ date contributionCount }} }} }}
      }} }} }}""")
    years = base["contributionsCollection"]["contributionYears"]
    per_year = gql("query { user(login: \"%s\") { %s } }" % (USER, " ".join(
        f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") '
        "{ contributionCalendar { totalContributions } totalCommitContributions restrictedContributionsCount }"
        for y in years)))
    cal = base["contributionsCollection"]["contributionCalendar"]
    months = OrderedDict()
    for week in cal["weeks"]:
        for day in week["contributionDays"]:
            months[day["date"][:7]] = months.get(day["date"][:7], 0) + day["contributionCount"]
    return {
        "since": dt.date.fromisoformat(base["createdAt"][:10]),
        "total": sum(v["contributionCalendar"]["totalContributions"] for v in per_year.values()),
        "last_year": cal["totalContributions"],
        "commits": sum(v["totalCommitContributions"] for v in per_year.values()),
        "private": sum(v["restrictedContributionsCount"] for v in per_year.values()),
        "repos": base["repositories"]["totalCount"],
        "months": list(months.items())[-12:],
    }


def render(s):
    W, H = 840, 300
    stats = [("Last 12 months", s["last_year"]), ("Public commits", s["commits"]),
             ("Private contributions", s["private"]), ("Public repos", s["repos"])]
    cells = "".join(
        f'<g transform="translate({330 + (i % 2) * 250},{78 + (i // 2) * 62})">'
        f'<text class="num" y="0">{v:,}</text><text class="lbl" y="22">{escape(k)}</text></g>'
        for i, (k, v) in enumerate(stats))
    peak = max(c for _, c in s["months"]) or 1
    bw, gap, x0, base_y, max_h = 52, 12, 42, 268, 64
    bars = []
    for i, (month, count) in enumerate(s["months"]):
        h = max(3, round(count / peak * max_h))
        x = x0 + i * (bw + gap)
        label = dt.date.fromisoformat(month + "-01").strftime("%b")
        bars.append(
            f'<rect class="bar" style="animation-delay:{i * 60}ms" x="{x}" y="{base_y - h}" width="{bw}" height="{h}" rx="4"/>'
            f'<text class="mon" x="{x + bw / 2}" y="{base_y + 16}">{label}</text>'
            f'<title>{count} contributions in {label}</title>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H + 6}" viewBox="0 0 {W} {H + 6}">
<defs>
  <linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#A78BFA"/><stop offset="1" stop-color="#22D3EE"/></linearGradient>
  <linearGradient id="b" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#4C1D95"/><stop offset="1" stop-color="#22D3EE"/></linearGradient>
</defs>
<style>
  text {{ font-family: 'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif; }}
  .big {{ font-size: 64px; font-weight: 800; fill: url(#g); }}
  .num {{ font-size: 26px; font-weight: 700; fill: #F0F6FC; }}
  .lbl, .sub {{ font-size: 13px; fill: #8B949E; }}
  .ttl {{ font-size: 15px; font-weight: 600; fill: #C9D1D9; letter-spacing: .5px; }}
  .mon {{ font-size: 11px; fill: #6E7681; text-anchor: middle; }}
  .bar {{ fill: url(#b); transform-box: fill-box; transform-origin: bottom; animation: grow .8s ease-out both; }}
  @keyframes grow {{ from {{ transform: scaleY(0); }} to {{ transform: scaleY(1); }} }}
</style>
<rect x="1" y="1" width="{W - 2}" height="{H + 4}" rx="12" fill="#0D1117" stroke="#30363D"/>
<text class="ttl" x="40" y="42">GITHUB ACTIVITY</text>
<text class="sub" x="{W - 40}" y="42" text-anchor="end">since {s["since"]:%b %Y}</text>
<text class="big" x="36" y="128">{s["total"]:,}</text>
<text class="lbl" x="40" y="154">total contributions</text>
{cells}
<line x1="40" x2="{W - 40}" y1="{base_y - max_h - 14}" y2="{base_y - max_h - 14}" stroke="#21262D"/>
{"".join(bars)}
</svg>
"""


if __name__ == "__main__":
    data = collect()
    assert data["months"], "no contribution calendar returned"
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        f.write(render(data))
    print({k: v for k, v in data.items() if k != "months"})
