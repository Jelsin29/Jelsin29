"""Generate the two SVGs embedded in the profile README."""

import json
import os
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape


ACCOUNT_QUERY = """
query($login: String!, $endCursor: String) {
  user(login: $login) {
    id
    contributionsCollection { contributionCalendar { totalContributions } }
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


                                                .,-~~++=+-:,:----:---,
                                            .,-*>)([[[[[[[[(>^=^^<](>^=-,.
                                        .,,-+)[{%%%###%%####%[]}%{{%{}])^+-,...
                                     .,:-+>[%%#####@@@@@@@@@@###@@@#####%}(>*+-,.
                                   ,~+~=<[###@@@@@@@@####@@@@@@@@@@@@@@@@@#%%}<~:,.     .
                                 ,-=^^>]{##@@@@@@@@@@@@@@#@@#@@@@@@@@@@@@@@@###%]^-:,,:*<*=:.
                              .:~*^>(}%##@@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#####}>^*>)^)*+=-,
                           .::-+^^({#@@@@@@@@@#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#######%])]])*<>>*.
                      .,:-~~:~+*>[%@@@@@@@@@@@@@@@@%{}[[[[[[[[}}}{{%#@@@@@@@##@##@@@@@%{[[](}]*.
                    .:+=+<)=+*>)}#@@@@@@@@@@@@@@#{%]()>><<^^^^<<<>>([}#@@@@@@##@@@@@@@@#}}{%{(+:--,
                    ,*((]{[]][{####@@@@@@@@@@@##{}[()><^^*****^^^^<<>(}%@@@@@##@@@@@@@@@@@@@#(((]<+.
                   .~<{%%%{####@@##@@@@@@@@@@##%}](><^^^********^^^^^<(}%@@@###@@@@@@@@@@@@@#%{{>^=,
                    +)}{%##@@@@@@##@@@@@@@@@@#%}])<^*****************^<([%##%##@@@@@@@@@@@@@#%%####[*
                    -)%{%#@@@@@@###@@@@@@@@@##}]><^******************^^<)[%%#@@@@@@@@@@@@@#######%%{]+
                    .*{}{%@@@@@@@@##@@##@@###})><^^^^^^^^^****^^^^^^^^^<<)}%#@@@@@@@@@@@@@@@@@#####%}),
                     .=%%@@@@@@@@@@@@@@###%[])>><<<<<^^^^^^^^^^^^^^<<<<<<<)[%@@@@@@@@@@@@@@@@@##%{{])*-
                      :]#@@@@@@@@@@@@@@#%}((()>><^^^******************^^<>>)]%@@@#@@@@@#@@@@@@%#})<^==,
                     -)<{#@@@@@@@@@@@@@#{[][[])><^^**================*^<>)]](]{#@@@#@@@@@@@@@@%{])<*=,
                   .~)%}%@@@@@@@@@@###%%{}{#%%{{{{{}}]>^*===++=*>([}}{{{{}{{{}][#@@@@@@@@@@@@##[)^=-.
                    *{{#@@@@@@@@@@@@@%%{%@%}[]((((][}[])<^====^)][}[](><<>>)]}%]]{@@@@@@@@@@@##[^:
                    ,)@@@@@@@@@@@@@@@%%{#}])>>>))(((())()<^==*<>>))((]()><^^<)]]))[#@@@@@@@@@@@(:..
                    .<{#@@@@@@@@@@@@%{}{}]))]}{]}%#%>>((()^**^<)>)<^%%%(>}[(<<>>>>)]@@@@@@@@@@@%^.
                     +]%@@@@@@@@@@@@}[]]())([}]))[[(^>(](>^***<)))>^)]]>>(](><^^<<>(#@@@@@@@@@@}+
                      .*>#@@@@#@@@@@[(())))))>><<<<<>)(()>^***^<>><^^^^^^^^^^^^^^<>(##@@@@@@@@#(,
                       ,<#@@@}(((#@@[]()))><<^^****^<)()>>^***^^<<<**=====*****^^<>)#@@#[]}{@@{:
                        ,^]%@%)>({@@[(()><^^^*****^<>))))><^*^^<<<<^**========**^<>(##{])>(>@#^
                          .*%@]>>]@@[](>><^^*****^^<>)((><^***^<>><^^*========*^^<>]#%)^<>)-:^,
                            ,[%(>>%#}])>><^^*****^^<>))><^*===*^<>><^*========**^<>[#])><>[+.
                             :({()[#}])>><<^^****^<>>><<<*++++=*^^^><*=======***^<>([))><}>
                              :]]))([])>><<^^^^^^^<>>>>))><^^^<>)>><^**********^^<>))>>>)#+
                              ,>}(()(()>><<<<^<<^^^<<<>>>^***^^<<<^^^**********^^>>><><>{@^
                             .:=%{()]]()>><<<<><^^<<<<^^^^^^<^^******^^^*^^**^^^<>]}](]}@#<.
                       .,:,,:+<{@@@@@}()>><<<>><^<>><<<<<<<^^^^^^^^^^^^^^^^^^^^<<)@@@@@#}>-
                       *[[>)]{#@@@@@@@]))>>><><^<(]]]](()>>>>>>>))((((<^^^^^^^^<>{@@@@}<-.
                       :{@@@##%{@@@@@@{())>><<^^^<>>>><<^^^^^^^^^^^^^^****^^<^<>[@@@#):...~~,.
                         -==+~~>{@@@@@@{]()>><<^^^<<<^*********==**^***^^^^<<<)]@@@@@[)<<)]}<~.
                             .~*({@@@@@%[]())><<<<<<<^^***********^^^^^^^^<<>((}@@@@@@####@#<,
                              -=>%@@@@@%]][]()>><><<<^^*^^^^^^****^^^<^^<<>(())%@@@@@@###%<.
                               ,^#@@@@@{]((]]]()>>><^^^**=======**^^<<<>)(])>>)#@@@@{(((^,
                               .}#@@@@@}]())(]][]))>><<^*=******^^<<>)(]((><<<)@@@@##<,.
                             :~[###@@@#}]))))))(]]]())><^^^^^^^<<>>)(())><<<<<(%@@@##%*
                        :+^[##%#####@@#}])>><<<>>)))((((())))))))))>>><<^^^^<>]}@@#####[+~,
                   .-=)}#@@@@)#######@@}])><<^^^^<>><<<<<^^^^^^^^^<<<^^***^^<)][@@###%%%%[]%}[[]*.
                :*}######@@@@>########@%[)><^^***^^<<<<<^******^^^^^******^<>)]}####%#%%%%>)%%#%%%]<~.
           :=>[%#########@@@@(#########@}(><^*****^^^^<<<^****^*****===**^^<>(]{%###%#%%%%]-}%#####%%%]*-.
     :+^)}%##############@@@#}###########])><^*******^^^^^^^*******====**^<<)({%###%#%##%%{:<%%%########%%}])^~,
*>]}%#####################@@]############%)><^^*******************====**^^<>)}%#%%%#%%%%#%%~-%%###############%%
###########################@}{############{)<^^^**==*************===***^^^<>[{##%#%###%#%%%^:]%%################
@@@######@@@###############@@%@############{>^^^^**===*=***************^^<>]{%#%#%###%%%%%%]:*%%################
@@@@##@##@@@################@@@@@###########{>^^^**================****^^<[%#%%#%#%%%%%%%%%%--{%################
@@@@@@##@###@################@@@@############}(<^*=================***^^>[####%#%#%%%#####%%=:)%################
#######@@#####################@@@@############%}]<*================*^<)[%######%%%%##%%%##%%<:^#################
####@#@########################@@@@@@@@@@@@@@##%%%]<*============*^>(}%%##%%###%%%%%######%%^-^#################
@###################################@@@@@@@@@@#%)(}%})<***====**^>]{#######%#@################%#################
@##########################################@@@###%}][]][(<^*^^^<({%%%%%%%%%#@@##################################
##################################################@@@@#[](](>>){%]))(((((([@####################################
###################################################@@#####}]}}{)]%#@############################################
@####@##################################################@@@@}(]%################################################
@@#@#@###################################################@@[)%##################################################
#@#@#@#########@########################################@@)[####################################################
@@@##@@#################################################@][#####################################################
@#@##@#################################################@#)%#####################################################
""".strip("\n").splitlines()

# Dark colors come from the Ghostty Gentleman Kanagawa Blur palette.
THEMES = {
    "dark": {
        "bg": "#06080f", "border": "#263356", "text": "#f3f6f9", "muted": "#8a8fa3",
        "pink": "#ff8dd7", "lavender": "#ffaeea", "blue": "#7fb4ca",
        "teal": "#7aa89f", "yellow": "#ffe066", "green": "#b7cc85", "red": "#de8fa8",
    },
    "light": {
        "bg": "#faf7fc", "border": "#d5ccdf", "text": "#24213a", "muted": "#625771",
        "pink": "#8d326c", "lavender": "#794b84", "blue": "#285974",
        "teal": "#30655d", "yellow": "#735800", "green": "#496325", "red": "#9a3f57",
    },
}

# The authenticated owner inventory includes private repositories. A public
# workflow can refresh the public count, but the full total is a dated snapshot.
OWNED_REPOSITORIES = 91
OWNED_REPOSITORIES_AS_OF = "2026-11-22"


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
        "contributions": account["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "repos": len(repositories),
        "stars": sum(repo["stargazers_count"] for repo in repositories),
        "followers": account["followers"]["totalCount"],
        "commits": commits,
        "additions": additions,
        "deletions": deletions,
    }


def render_card(login, profile, palette):
    output = []
    description = []

    def svg_text(x, y, value, color, size):
        text = escape(value).replace(" ", "&#160;")
        return (f'<text x="{x:.2f}" y="{y}" font-family="Menlo, Consolas, monospace" '
                f'font-size="{size}" fill="{palette[color]}">{text}</text>')

    def line(y, *parts, x=514):
        for value, color in parts:
            output.append(svg_text(x, y, value, color, 13.5))
            x += 8.13 * len(value)

    def row(y, name, value, *suffix, section="blue"):
        description.append(f"{name}: {value}{''.join(word for word, _ in suffix)}")
        line(y, (f"{name}:", section), (" " * (19 - len(name)), "muted"),
             (value, "text"), *suffix)

    def heading(y, name, color):
        line(y, (name, color))
        output.append(f'<path d="M514 {y + 9}h499" stroke="{palette["border"]}"/>')

    line(43, ("jelsin@github", "pink"), ("  ~ $ neofetch", "muted"))
    heading(78, "JELSIN SANCHEZ", "lavender")
    row(108, "OS", "macOS, Windows, Android")
    row(130, "Uptime", "4 years")
    row(152, "Kernel", "Software Developer")
    row(174, "Work", "Köstebek Teknoloji")
    row(196, "Host", "İstanbul Medeniyet University")
    row(218, "IDE", "Neovim, Zed")
    row(240, "Programming", "TypeScript, JavaScript, Python, C/C++,")
    line(258, (" " * 20, "muted"), ("Dart, Rust, Go", "text"))
    description.append("Also programming in Dart, Rust and Go")
    row(282, "Frameworks", "React, Next.js, Flutter, Electron")
    row(304, "Languages", "Spanish, English, Turkish")
    row(326, "Hobbies.Software", "REA, Web Development, Optimization")
    row(348, "Hobbies.Hardware", "Circuits, computers, Ben Eater’s 6502")
    row(370, "Projects", "Vigilanty, WebAR-Sandbox, 6502-CPU")

    heading(408, "CONTACT", "pink")
    row(435, "Email.Work", "jelsin@kostebekteknoloji.com", section="lavender")
    row(457, "LinkedIn", "linkedin.com/in/jelsin-sanchez", section="lavender")

    heading(495, "GITHUB", "yellow")
    row(522, "Repositories", f"{OWNED_REPOSITORIES} total",
        (f' / {profile["repos"]:,} public', "muted"), section="green")
    row(544, "Contributions", f'{profile["contributions"]:,}',
        (" / last 12 months", "muted"), section="green")
    row(566, "Public commits", f'{profile["commits"]:,}',
        (f' / {profile["stars"]:,} stars / {profile["followers"]:,} followers', "muted"),
        section="green")
    net = profile["additions"] - profile["deletions"]
    row(588, "Public LOC", f'{net:,}',
        (f'  +{profile["additions"]:,}', "green"), (f'  -{profile["deletions"]:,}', "red"),
        section="green")

    description.append(f"Total owned repositories verified on {OWNED_REPOSITORIES_AS_OF}.")
    description.append("Contributions are from the GitHub profile calendar. Public commits and lines are counted on default branches of tracked public repositories. Merge commits are excluded from line counts.")
    portrait = "\n    ".join(
        svg_text(21, 76 + index * 7.85, chars, "blue", 6.9)
        for index, chars in enumerate(PORTRAIT)
        if chars.strip()
    )
    swatches = "\n    ".join(
        f'<rect x="{22 + 27 * index}" y="596" width="22" height="8" rx="1" fill="{palette[color]}"/>'
        for index, color in enumerate(("red", "green", "yellow", "blue", "pink", "teal", "text"))
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1040 623" width="1040" height="623" role="img" aria-labelledby="title description">
  <title id="title">Jelsin Sanchez ({escape(login)}) · Neofetch-style profile</title>
  <desc id="description">{escape(". ".join(description))}</desc>
  <rect x="1" y="1" width="1038" height="621" rx="10" fill="{palette["bg"]}" stroke="{palette["border"]}"/>
  <path d="M493 32v568" stroke="{palette["border"]}"/>
  <g aria-hidden="true">
    {portrait}
    {swatches}
  </g>
  {"".join(output)}
</svg>
"""


def main():
    login = os.environ["PROFILE_LOGIN"]
    profile = collect_profile(login)
    output = Path("profile")
    output.mkdir(exist_ok=True)
    for theme, palette in THEMES.items():
        (output / f"stats-{theme}.svg").write_text(
            render_card(login, profile, palette), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
