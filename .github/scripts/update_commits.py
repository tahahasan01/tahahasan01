"""Rewrite the commits table in README.md between the COMMITS markers with live data."""
import json
import os
import re
import urllib.request

USER = os.environ.get("GH_USER", "tahahasan01")
TOKEN = os.environ.get("GITHUB_TOKEN")
README = os.path.join(os.path.dirname(__file__), "..", "..", "README.md")
START, END = "<!--START_SECTION:commits-->", "<!--END_SECTION:commits-->"


def api(path):
    req = urllib.request.Request(f"https://api.github.com/{path}", headers={"Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def rows():
    repos = api(f"users/{USER}/repos?sort=pushed&per_page=20")
    # skip forks and this profile repo, whose own commits are just these README updates
    repos = [r for r in repos if not r["fork"] and r["name"] != USER][:8]
    latest = []
    for r in repos:
        try:
            latest.append((r, api(f"repos/{r['full_name']}/commits?per_page=1")[0]))
        except Exception:  # empty repo
            continue
    # pushed_at counts pushes to any branch, so order by the default-branch commit date instead
    latest.sort(key=lambda rc: rc[1]["commit"]["author"]["date"], reverse=True)
    for r, c in latest[:6]:
        msg = c["commit"]["message"].splitlines()[0].replace("|", "\\|").replace("<", "&lt;")
        msg = msg if len(msg) <= 70 else msg[:67] + "..."
        yield (f"<tr>\n<td><a href=\"{r['html_url']}\">{r['name']}</a></td>\n"
               f"<td><a href=\"{c['html_url']}\">{msg}</a></td>\n"
               f"<td>{c['commit']['author']['date'][:10]}</td>\n</tr>")


def main():
    table = ("<table>\n<tr>\n<th align=\"left\">Repository</th>\n<th align=\"left\">Latest Commit</th>\n"
             "<th align=\"left\">Date</th>\n</tr>\n" + "\n".join(rows()) + "\n</table>")
    with open(README, encoding="utf-8") as f:
        text = f.read()
    assert START in text and END in text, "commit markers missing from README"
    new = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda _: f"{START}\n{table}\n{END}", text, flags=re.S)
    with open(README, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)


if __name__ == "__main__":
    main()
