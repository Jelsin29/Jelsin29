"""Render a terminal-style GitHub activity card in two color themes."""

import json
import os
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape


QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
    }
  }
}
"""

THEMES = {
    "dark": ("#0d1117", "#30363d", "#e6edf3", "#8b949e", "#79c0ff", "#56d364"),
    "light": ("#f6f8fa", "#d0d7de", "#1f2328", "#57606a", "#0969da", "#1a7f37"),
}


def github_api(*args):
    return json.loads(subprocess.check_output(["gh", "api", *args], text=True))


def collect_stats(login):
    account = github_api(
        "graphql", "-f", f"query={QUERY}", "-f", f"login={login}"
    )["data"]["user"]
    pages = github_api(
        "--paginate", "--slurp", f"users/{login}/repos?type=owner&per_page=100"
    )
    repositories = [repo for page in pages for repo in page if not repo["private"]]
    activity = account["contributionsCollection"]
    return [
        ("Public repositories", len(repositories)),
        ("Stars on public repositories", sum(repo["stargazers_count"] for repo in repositories)),
        ("Followers", account["followers"]["totalCount"]),
        ("Commits in the past year", activity["totalCommitContributions"]),
        ("Pull requests in the past year", activity["totalPullRequestContributions"]),
    ]


def render_card(login, stats, palette):
    background, border, foreground, muted, blue, green = palette
    rows = []
    for index, (label, count) in enumerate(stats):
        y = 115 + 35 * index
        rows.append(
            f'<circle cx="32" cy="{y - 5}" r="3" fill="{blue}"/>'
            f'<text x="47" y="{y}" fill="{foreground}">{escape(label)}</text>'
            f'<text x="608" y="{y}" fill="{foreground}" text-anchor="end">{count:,}</text>'
        )
    rows_markup = "\n  ".join(rows)
    summary = "; ".join(f"{label}: {count:,}" for label, count in stats)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 290" width="640" height="290" role="img" aria-labelledby="title description">
  <title id="title">{escape(login)}'s GitHub activity</title>
  <desc id="description">{escape(summary)}</desc>
  <rect x="1" y="1" width="638" height="288" rx="15" fill="{background}" stroke="{border}"/>
  <path d="M1 51h638" stroke="{border}"/>
  <circle cx="28" cy="26" r="4" fill="{muted}"/>
  <circle cx="43" cy="26" r="4" fill="{blue}"/>
  <circle cx="58" cy="26" r="4" fill="{green}"/>
  <g font-family="ui-monospace, SFMono-Regular, Consolas, monospace">
    <text x="320" y="31" text-anchor="middle" font-size="15" fill="{muted}">{escape(login)} / github</text>
    <text x="28" y="81" font-size="17" font-weight="bold" fill="{green}">&gt; GitHub activity</text>
    <g font-size="17">
      {rows_markup}
    </g>
  </g>
</svg>
"""


def main():
    login = os.environ["PROFILE_LOGIN"]
    stats = collect_stats(login)
    output = Path("profile")
    output.mkdir(exist_ok=True)
    for theme, palette in THEMES.items():
        (output / f"stats-{theme}.svg").write_text(
            render_card(login, stats, palette), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
