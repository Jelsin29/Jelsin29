"""Generate the two SVGs embedded in the profile README."""

import json
import os
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape


ACCOUNT_QUERY = """
query($login: String!, $endCursor: String) {
  user(login: $login) {
    id
    createdAt
    followers { totalCount }
    repositoriesContributedTo(first: 100, after: $endCursor, privacy: PUBLIC,
                              includeUserRepositories: false) {
      nodes { nameWithOwner isPrivate }
      pageInfo { hasNextPage endCursor }
    }
  }
}
"""

PORTRAIT = """
                  .;rrsi;;;;;.
               ,;2HS####ShHSGhX:,.
            .;i3#999999BB99B999#hs.   .
          .;X3G99BBB&&B999BBB&BB#9SX;2X;,
       .,:r5SB9999BB9#SSS###BBBB9999SH353.
     .sA3AhSBB99BB9Gh5AXXAA23SB&999999S#3si
     iGS##9#999B99GhAXXsXssXX3SB#9B99999#G3;
     ;GSBBB9999B9S3AsssssssssA3S9BBBBB9999#H:
      2S9BB99B9#H32AAXXXXXXXAAA3#BBB9B9999Shr
      AS9BB99B#HMh2AsssssrrssA5hh#9999B99G5s,
     sS9BBBB9#S#SHMMHM2srs3HHh33HHGBBBB99h;.
     ,SBBBBBBSGM3hhHh53AsA52HG55A32MBBBBBh.
      AS&&&&BMh53h2h253AsX525225AXA39&BBBh
       AB93G9h32AXsXA35AsXAAsrsssXA59#hG9,
        :G339h5AXssX235AsX2AXsrrrsA3#22sr
         .M5Sh5AXXsX222srsAAAsrrssA3h2h,
          rh5h52AAAXA22AXA2AXssssXA522S.
       ..,A9SH52A2AAAAAAAXXXXXXXXX2#S#M.
       GHG#B&&h52AX5352AAAA22AXXAAHBSi.,
       .;;rSB&#h52AAAXssXssXXXXA23BBS3MG;
          :MB&#hh322AXXXXssXAAA53M&B##M,
          .SB&S33hh32AXsssXA2332AH&9h,
       iXhS99BG322253552222552AXAMB9#3i:.
   :AM#99H9999#3AXXXAAAssXXXXssX2M9###Sh##5r.
2M#999999S9##99h2XssXXAXsXssssXA5G#####rS####
999999999G9####S5AXsssXsssssssXAM######Xh####
999999#999999###GAXsrssssssssXX3S######3X####
9999999999B99####G2XrrrrrrrssXh########S:####
999999999999999999#G2rrrrrsAhS##9######Sr####
""".strip("\n").splitlines()

THEMES = {
    "dark": ("#101811", "#354a39", "#d8eedc", "#8da996", "#99efa6", "#94c9a0", "#ff9292"),
    "light": ("#f6f8f0", "#bccabd", "#223b2b", "#526957", "#16592b", "#326346", "#a22828"),
}


def github_api(*args):
    return json.loads(subprocess.check_output(["gh", "api", *args], text=True))


def collect_commits(repositories, author):
    commits = {}
    pending = [(name, None) for name in sorted(repositories)]
    while pending:
        batch, pending = pending[:5], pending[5:]
        query = ["query($author: ID!) {"]
        for index, (name, cursor) in enumerate(batch):
            owner, repo = name.split("/", 1)
            after = f", after: {json.dumps(cursor)}" if cursor else ""
            query.append(f"""
              repo{index}: repository(owner: {json.dumps(owner)}, name: {json.dumps(repo)}) {{
                isPrivate
                defaultBranchRef {{
                  target {{
                    ... on Commit {{
                      history(first: 50, author: {{id: $author}}{after}) {{
                        pageInfo {{ hasNextPage endCursor }}
                        nodes {{ oid additions deletions parents(first: 1) {{ totalCount }} }}
                      }}
                    }}
                  }}
                }}
              }}
            """)
        query.append("}")
        data = github_api(
            "graphql", "-f", "query=" + "\n".join(query), "-f", f"author={author}"
        )["data"]
        for index, (name, _) in enumerate(batch):
            repo = data[f"repo{index}"]
            if not repo or repo["isPrivate"] or not repo["defaultBranchRef"]:
                continue
            history = repo["defaultBranchRef"]["target"]["history"]
            for commit in history["nodes"]:
                if commit["parents"]["totalCount"] <= 1:
                    commits[commit["oid"]] = (commit["additions"], commit["deletions"])
                else:
                    commits[commit["oid"]] = (0, 0)
            page = history["pageInfo"]
            if page["hasNextPage"]:
                pending.append((name, page["endCursor"]))
    return len(commits), sum(a for a, _ in commits.values()), sum(d for _, d in commits.values())


def collect_profile(login):
    accounts = [
        page["data"]["user"]
        for page in github_api(
            "graphql", "--paginate", "--slurp", "-f", f"query={ACCOUNT_QUERY}",
            "-f", f"login={login}",
        )
    ]
    account = accounts[0]
    contributed = {
        repo["nameWithOwner"]
        for page in accounts
        for repo in page["repositoriesContributedTo"]["nodes"]
        if repo and not repo["isPrivate"]
    }
    repositories = [
        repo
        for page in github_api(
            "--paginate", "--slurp", f"users/{login}/repos?type=owner&per_page=100"
        )
        for repo in page
        if not repo["private"]
    ]
    tracked = {repo["full_name"] for repo in repositories} | contributed
    commits, additions, deletions = collect_commits(tracked, account["id"])
    return {
        "created": date.fromisoformat(account["createdAt"][:10]),
        "repos": len(repositories),
        "contributed": len(contributed),
        "stars": sum(repo["stargazers_count"] for repo in repositories),
        "followers": account["followers"]["totalCount"],
        "commits": commits,
        "additions": additions,
        "deletions": deletions,
    }


def render_card(login, profile, palette, today):
    background, border, foreground, muted, accent, portrait_color, red = palette
    output = []
    description = []

    def span(value, color):
        return ((value, color),)

    def svg_text(x, y, value, color, size):
        text = escape(value).replace(" ", "&#160;")
        return (f'<text x="{x:.2f}" y="{y}" font-family="Menlo, Consolas, monospace" '
                f'font-size="{size}" fill="{color}">{text}</text>')

    def line(y, parts, x=382):
        for value, color in parts:
            output.append(svg_text(x, y, value, color, 12.5))
            x += 7.53 * len(value)

    def row(y, name, value, extra=(), plain_extra=""):
        dots = "." * (26 - len(name))
        description.append(f"{name}: {value}{plain_extra}")
        line(y, span(name, accent) + span(f" {dots} ", muted) + span(value, foreground) + extra)

    def heading(y, title):
        line(y, span(title, accent))
        output.append(f'<path d="M382 {y + 10}h535" stroke="{border}"/>')

    account_age = (today - profile["created"]).days
    years = today.year - profile["created"].year
    if (today.month, today.day) < (profile["created"].month, profile["created"].day):
        years -= 1
    uptime = f"{years} {'year' if years == 1 else 'years'} on GitHub"
    if not years:
        uptime = f"{account_age} {'day' if account_age == 1 else 'days'} on GitHub"

    line(37, span(f"jelsin@{login.lower()}:~$", accent) + span(" whoami", foreground), 24)
    heading(89, "SYSTEM / JELSIN SANCHEZ")
    row(119, "OS", "macOS, Windows, Android")
    row(141, "Uptime", uptime)
    row(163, "Host", "İstanbul Medeniyet University")
    row(185, "Kernel", "Computer Engineering Student")
    row(207, "IDE", "Neovim")
    row(229, "Languages.Programming", "TypeScript, JavaScript, Python, Java, C/C++")
    row(251, "Languages.Computer", "HTML, CSS, JSON, YAML")
    row(273, "Languages.Real", "Spanish, English, Turkish")
    row(295, "Hobbies.Software", "Web development, AI, quantum computing")

    heading(331, "CONTACT")
    row(361, "LinkedIn", "linkedin.com/in/jelsin-sanchez")
    row(383, "Discord", "discord.gg/latinoperodecente")
    row(405, "Portfolio", "jelsin-portfolio.vercel.app")

    heading(441, "GITHUB / PUBLIC ACTIVITY")
    row(471, "Repos", f'{profile["repos"]:,}',
        span('  /  ', muted) + span('Contributed', accent) + span(f' {profile["contributed"]:,}', foreground)
        + span('  /  ', muted) + span('Stars', accent) + span(f' {profile["stars"]:,}', foreground),
        f', contributed to {profile["contributed"]:,}, {profile["stars"]:,} stars')
    row(493, "Commits", f'{profile["commits"]:,}',
        span('  /  ', muted) + span('Followers', accent) + span(f' {profile["followers"]:,}', foreground),
        f', {profile["followers"]:,} followers')
    net = profile["additions"] - profile["deletions"]
    row(515, "Lines of Code", f'{net:,}',
        span(f'  +{profile["additions"]:,}', accent) + span(f'  -{profile["deletions"]:,}', red),
        f', {profile["additions"]:,} added and {profile["deletions"]:,} deleted')
    description.append("Commits and lines are measured on default branches of public repositories tracked by GitHub. Merge commits are excluded from line counts.")

    portrait = "\n".join(
        svg_text(24, 76 + index * 15, chars, portrait_color, 11.5)
        for index, chars in enumerate(PORTRAIT)
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 545" width="950" height="545" role="img" aria-labelledby="title description">
  <title id="title">Jelsin Sanchez's terminal profile and ASCII portrait</title>
  <desc id="description">{escape("; ".join(description))}</desc>
  <rect x="1" y="1" width="948" height="543" rx="12" fill="{background}" stroke="{border}"/>
  <path d="M1 52h948M354 70v445" stroke="{border}"/>
  <g aria-hidden="true">
    {portrait}
  </g>
  {"".join(output)}
</svg>
"""


def main():
    login = os.environ["PROFILE_LOGIN"]
    profile = collect_profile(login)
    today = datetime.now(timezone.utc).date()
    output = Path("profile")
    output.mkdir(exist_ok=True)
    for theme, palette in THEMES.items():
        (output / f"stats-{theme}.svg").write_text(
            render_card(login, profile, palette, today), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
