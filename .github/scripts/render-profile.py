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
                                                   ~^          ~
                                              @@@@@@@@@@@@ @- :~.@@[]
                                         [  @@@@@@@@@ @@@@@}  @@]@~@@>  *
                                      *@  @@@@}@#@@@@@@@@@@@@@@@%@@@@@@@ ( %@>
                                   =@- +@@@@>%@@{<@<%@(#@@%[}%@{@@%%@@@@@@@~    -  .
                                   @  @@#@@@@@%{}%@#]]@<[@@)@@#{@@[}[{#%@@@@@@      .
                                 ^@)=#@@@@{{%@%@@@@@@@@[*@[]@*@#]{@@@@%@#@@@[@@@=     @]@@*:
                            >=+~[[ @@@@%@@@@@%[@]@@%@%@@@@@@[%@@@@@@#@}@%{@<[]@@@@@ @@  @ -@
                        ~  )  #] #@@%@{(@}@([{##{@@@@@@@@@@@@@@@@@@@%%{{#{@@#(]%#@@@  @@ : @@{
                       -   .*=@@@@@@@@>@@@{@#@@%@@{@)<%}#@@@@@@@@@@@@@@@%[{}<@@{%#{@@@@*@}@@@- -
                 ~  <@ ]@   @  @@@@@]{@{]{[{@@@@@^=)~~..-.   .   ~ %{@@@@@@(##@#[%%#@}@ %<@).    )
                    @] @@ @@@@@@{%%%@###%@#@(@}-*#[+~>=-~-~=++*^<~~+>@}@@#@@@]@@]{@[%@@@@@%@ @({(@
                }^  @@%@@@]}@@#^@}@{{^@@#@@{%##{]:><~)**~*>*-~^++^*(.(@@%@[#)[@@@@#}{#{){@@{@@@ :
                   @@@@@}%@#@@%]%%{{@@{@[])%}{}~@===:==+=^**++=++*~-:=%}@@%>(@#@%}[@##@@{#%@# )@@@=
                ~  @@ @@@%%%##@[(@[@#{@#@@@@@@@:~^. ~~=>+=++=+=:-::=*.@(@@@}}@}@]##{@@{}@#%]{@@@@@@@
                   @@ #:@@@%%@}]#@{#@#%@@{{@{*..~.-<~+*===~=-~~~~~:*:~~#@)@#@#@%{%}@#@#)##@[#@.#.:@@
                    @@@^@%{}#]%@(%{#((#@@@@@ {+=>=++^^^^^++*^*()(< >*^~~-:@@@{(@@]@@@%%%{@%[@@@@@@@@@@
                     @@{@}#{@@#[[{@}@@%@@ .<-*]({][(]<<)>(<<)((<])({((<=-~)@@@#%@@>)@#}{}{#{}[%#@@#@}
                     +@@[%@{@{#{@%%#%@#^~+<[=+^*.=~=+*+^++**+^:~-~-==~->=*::<@@@%]#%@{#<@@{%@@@@@: . @~
                  ) }( @#]@{%}@{{@]%@@[-~>*]-:          -*=-::         .~}...@@][@[#[@@%{}(@{<@ @ @~
                    @  @#@%@#@(@[}>@%]@^>@@@@@@@@@@@*-@- .~.:. @@@@@@@@@@@@@~ @@@@}@{{[#@@@{@@# @)@
                  @@( @@@@}@)@@@@{@[^]<@@@@@@@@@@@@@@-}~=:=:-)@@@@@@@{:}~^[%@@ %@@@@@@%%[}][{@%@
                   @@@@#{}%}{%{@@>@^@]@@--.       ...+@==* .=]^..           <@.~=@@@@@@#@@@@@@   )
                   *@@@{{%{}]@{{#@@>@>@@--.]@@@@@@@@%{}(]+=^*#~^@@@@@@%@%@..=+*-..>@{}#@#%[}%@@@
                   @@@@@@@@@@@@@@@@^[]#>^[@@@  @@@- }*#[(~:-*[^@<  @@@  [@][==)<=+^@@%{@%@%@@@@@
                     @@@#%#@@@@]@@>~^<~~><>%@@@> *{])[@]<~=~*<#=}%#<+^#}^<+++-**+=~@@@%@{@}#@@@
                       @[@@@)#@@^@#+<>^])(<=:..-~~-=@{>>>.~::+*]*  ...:.~+=>>*>+>=-@)@@@@@@@@@
                      .@@@@:...@%@)=<)[)><^=*+~-..>)}*+<<~==*=~+<<=~- ~ -:++-==^*+.@%@@..).@@@
                       #@(@@.*-~@@#*^]<==:+^.:^^*=*>(+(]]=**+[>+^*~+*+^**~-==~^==<==@@@ > @ @@-
                         @@@>^. @@%*)>***=-~**~**>)([{%(<=*^()[}<**=+~~-=-~~:>**~~{@@. =<[  %
                           @@.) @@@*><^<^+^-~=^-+<>%}*=+*>~~=^]%=**=<+~-~-~*=~+^-@@:)^( @ {
                            @@(->@@*>>^^^*>+==~*^<=]....        .>}=:--~+~~+=)~*>~@@^@(-@)
                             @@-^ @^(^>^^***^^=~+#{+<@@#]:=**#@%%^}*+==*++++~~=^<+). .: @
                              @-}>[[<>>^^**>-**^*+*+{#}%>[%[({[}^=~*~^++~~+=^==**#>@@[-@@  (~
                            .^@=   )()>>^*>*<<)~=-)>=+.:-. -~.~+)^]^=<~*^^~*+=*<-+     @@(   :
                              @@@]@~+<^**>*>][~:}=*~:=~=-)}(+--.... <+.]^*+^^^>^.@@@@@@@@  - -
                      @    @:@@@@@@@->>^<**))(>=<^-=](]{(=]()]=:~+[(-]***^=~^. @#(@@@@
                      @@ @^@@@]@@@@@:~(=<>^+(-=)%@@@@%}<)*]^*]{@@@@@[~***=+>+)- @@@@@@
                      @@@@@@@@@@%#%@@.=*^(^<=~~~+=--+->-.^+*=-::...:~:=:==<^~..@@@}@     @
                         @    +@@@%#@@^<<>>++>+-=+)*.:.*=.=*::..~=*:++^>^>+~=+@@@@@{@=@:@ @@
                              @}@{@%@@>(*^><^^+<^^^^^*+^~~^=+*^<++=>**+**=.^%-@@{{@%@@@@@@@@
                            @  @{##[@@-}@[(>+*>^<>^+=**>()]}]<==*^<<**+~=+@@= @@@%@@@#@@@@
                          *    @@%@@@@-*)]@[(>=~<>~>++^=--:: :-=^=*>~.++%@^*-.@#@#@@@@@@
                               @}#@%@@=<>>]{@%(*~~~=^+...~:=:.-~+-.*:<@@#(+=~.@}@#}@
                              @@@{#@@]+*><*^^%@@}]^]=~*~~>++=+]==(){@@] (~~>~~:@@%#}@@
                            @@@{{{{@@*(>^(*(**(]@@@}%]=:. .~ )*<]@@{(^**>**=+++@@##{}@@
                       @@@@@@@{{{{[}@*]>^~=^+>^^)*<^{}@@@@@@@@@}(*=~^^:=>==+^])@{#}@%@@.@
                   @@@@@@#@ @{#@##%{@{]>)*^~=*~+)<^-~-:.  .:   ~~><(-*-=+==+(>%@{}]}}#@@@@@@@@@@
               +@@@@%##@%%@ @#{%]}}{{@<++^=>=-~:+~()=>=~.--:-=<}*+:-+-*+>=^<[~@%{{%}###@@ @@[{#@@@@
           @@@@@@%%%@@}%{%@ @@#]@%@#{@@+<>++-*+~-<~+)^%]^ :<(-+->~<~=.=>+++]*>{@{[%{%}{(@% @}{#{]%@@@@
       @@@@@%#{{%{{{{{{%{#@ @#{(#{%]{%@-*>>~~^~~*>:***^+}<)~*<--^==.~.*.^+^^.@@%{@}[#{%[@@ @@##{#{[@#@@@@@@
@@@@@@@@@[%%###%{{#{{##%#{@@@{#%#{{}{{%@.~<*+*-*==**>=>~^+=^*~+=*~~^+*<>*<^~@)#[[{#[[@}@]@  @{{{{{#}{##(@{@@@@@
@@@@@%%#}#######{{##}##{{#{%@@@#[@{}}#%##@@.^>**):+=-->^=~-+*++^<**~.-.+->+=~:@}@%#[@]@%]{{{@  @}{#%%{##%@##}@}}@:
>%%#{{##%##{##{%#%}##{#{{#}#@ @}%#%%}}[@##@@..^*=:=)^:=^++=*=+:~-==~<]+=)-~{#@%}#]@]@]@{}{@  @@%}{{{#}{[#{#{%##*
<%%{#{%#{@{#%#{{#%##%}#%}%{{@@@%({[%%%#]}%%@@.~^<]-+.+-*-~~+^+=>::@=~>=*++-^{@#](@]@[[{{#}{@@  @%}#{#}{%%{{{%%{%>
<#{#{##%{##%#{%##]%[{{{{#{{{{@@@#]#}{[#{{%[@@@ .-<=~*^==*=+~+^+^^:.:+*+>. ^(@%}{}#]{##{[{}%[@  @#[%{%{#}#%#{}{}{>
<##%@{%}{%{}##%{#{%%{%{[{#%%}{#@@%%#%%}}{#%{{@@+ :.--=-=>*.~:-++-==+-:.  {@@@]}%[@]##%}{{}{#@  @@{}{@{}%%{##@]@#>
<#{}[{}#%%#%#%###%[#%#{{@{[#{{{#@@[%}]}{()]]]%@@@[.  -~+*=*+>*~-:-:. .:>@@#<@}{{#[@}##{%%{{}@  *@{@#{{#}#}%%{}@%>
)@{%@@#%%}{[#{{%}@{%{#%%#%%%@{#{%}%%#@%@@@@@%{]%(@@~ . :..-~~~-=:. *^(@@#[][[}{[][{[)([(][[}@  %@#}}%[%#{}}#}{}@*
>#}{}{#}{%%@{##{{{}#{#}{}[][[{@}{#}@}@%@@%@@@@##(#}@@[...=..-:--=*<}@@@@@@@%[@@@@}@#@%@%@@{@@@@@%#{%{##}}@%{@%(#+
){{@}{{%%[[@##%{}@{}%{[%%@@%}}%##[#}[]{][[}[%{{@@@@@ -@@-<..~=+*. @@@@@@@@@@@@%#}#%(%{#%{#%[{)@}}@{}{{{##{]#}[#@*
)}}@##%%#}@}#{##{@[}#@%%{](%@%)#@{#%}}@}@%@}@@@}#[#@@@@@ @{)+*: @@@         @%]#(}%{}]#[(}{]%#{#{[@%}@{{{###@{@[(
""".strip("\n").splitlines()

THEMES = {
    "dark": {
        "bg": "#161b22", "border": "#30363d", "text": "#c9d1d9", "muted": "#6e7d8f",
        "key": "#ffa657", "value": "#a5d6ff", "add": "#3fb950", "remove": "#ff6b60",
    },
    "light": {
        "bg": "#f6f8fa", "border": "#d0d7de", "text": "#24292f", "muted": "#718096",
        "key": "#953800", "value": "#0a3069", "add": "#1a7f37", "remove": "#b42318",
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
        "contributed": len(contributed),
        "stars": sum(repo["stargazers_count"] for repo in repositories),
        "followers": account["followers"]["totalCount"],
        "commits": commits,
        "additions": additions,
        "deletions": deletions,
    }


def render_card(login, profile, palette, font):
    units = font["units_per_em"]
    glyphs = font["glyphs"]
    used = set()
    body = []
    description = []
    left = 416
    columns = 84
    size = 16.5
    advance = glyphs[" "][0] * size / units

    def draw(x, y, text, color, font_size=size):
        scale = font_size / units
        elements = []
        for char in text:
            char_advance, path = glyphs[char]
            if path:
                used.add(char)
                elements.append(f'<use xlink:href="#g{ord(char)}" transform="translate({x:.3f}) scale({scale:.5f})"/>')
            x += char_advance * scale
        if elements:
            body.append(f'<g fill="{palette[color]}" transform="translate(0 {y})">'
                        + "".join(elements) + "</g>")

    def line(y, *segments):
        x = left
        for text, color in segments:
            draw(x, y, text, color)
            x += len(text) * advance

    def heading(y, label):
        line(y, (label, "text"))
        start = left + (len(label) + 2) * advance
        end = left + columns * advance
        body.append(f'<path d="M{start:.2f} {y - 5}H{end:.2f}" stroke="{palette["text"]}"/>')

    def row(y, label, *values):
        prefix = f"{label}:"
        value = "".join(text for text, _ in values)
        description.append(f"{label}: {value}")
        leaders = columns - len(prefix) - len(value) - 4
        if leaders < 1:
            raise ValueError(f"Row exceeds {columns} columns: {label}")
        line(y, ("· ", "muted"), (prefix, "key"), (" " + "." * leaders + " ", "muted"), *values)

    heading(39, f"jelsin@{login.lower()}")
    row(64, "OS", ("Windows, macOS, Android, Linux", "value"))
    row(86, "Uptime", ("4 Years", "value"))
    row(108, "Host", ("KÖSTEBEK TEKNOLOJİ YAZILIM BİL. EĞT. DAN. ARGE TİC. LTD. ŞTİ.", "value"))
    row(130, "Kernel", ("Software Developer", "value"))
    row(152, "IDE", ("Neovim, Zed", "value"))

    row(188, "Languages.Programming", ("TypeScript, JavaScript, Python, C/C++, Dart, Rust, Go", "value"))
    row(210, "Frameworks", ("React, Next.js, Flutter, Electron", "value"))
    row(232, "Languages.Real", ("Spanish, English, Turkish", "value"))
    row(268, "Hobbies.Software", ("REA, Web Development, Optimization", "value"))
    row(290, "Hobbies.Hardware", ("Circuits, Robotics, Embedded Systems", "value"))
    row(312, "Projects", ("Vigilanty, WebAR-Sandbox, 6502-CPU", "value"))

    heading(351, "- Contact")
    row(376, "Email.Personal", ("jelsimsanchez@gmail.com", "value"))
    row(398, "Email.Work", ("jelsin@kostebekteknoloji.com", "value"))
    row(420, "LinkedIn", ("jelsin-sanchez", "value"))
    row(442, "Portfolio", ("jelsin-portfolio.vercel.app", "value"))

    heading(481, "- GitHub Stats")
    row(506, "Repos", (str(OWNED_REPOSITORIES), "value"),
        ("  {Public: ", "text"), (f'{profile["repos"]:,}', "value"),
        (", Contributed: ", "text"), (f'{profile["contributed"]:,}', "value"),
        ("}  |  ", "text"), ("Stars: ", "key"), (f'{profile["stars"]:,}', "value"))
    row(528, "Contributions", (f'{profile["contributions"]:,}', "value"), ("  (Last 12 Months)", "text"))
    row(550, "Public Commits", (f'{profile["commits"]:,}', "value"), ("  |  ", "text"),
        ("Followers: ", "key"), (f'{profile["followers"]:,}', "value"))
    net = profile["additions"] - profile["deletions"]
    row(572, "Public Lines of Code", (f'{net:,}', "value"), ("  (", "text"),
        (f'{profile["additions"]:,}++', "add"), (",  ", "text"),
        (f'{profile["deletions"]:,}--', "remove"), (")", "text"))

    description.append(f"Total owned repositories verified on {OWNED_REPOSITORIES_AS_OF}.")
    description.append("Public commits and lines are counted on default branches of tracked public repositories. Merge commits are excluded from line counts.")
    for index, chars in enumerate(PORTRAIT):
        draw(18, 32 + index * 8.85, chars, "text", 6.75)

    paths = "\n".join(f'<path id="g{ord(char)}" d="{glyphs[char][1]}"/>' for char in sorted(used))
    content = "\n  ".join(body)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1130 601" width="1130" height="601" role="img" aria-labelledby="title description">
  <title id="title">Jelsin Sanchez ({escape(login)}) · Terminal Profile in Iosevka</title>
  <desc id="description">{escape(". ".join(description))}</desc>
  <rect x="1" y="1" width="1128" height="599" rx="14" fill="{palette["bg"]}" stroke="{palette["border"]}"/>
  <defs>
    {paths}
  </defs>
  {content}
</svg>
"""


def main():
    login = os.environ["PROFILE_LOGIN"]
    profile = collect_profile(login)
    font = json.loads(Path(__file__).with_name("iosevka-outlines.json").read_text(encoding="utf-8"))
    output = Path("profile")
    output.mkdir(exist_ok=True)
    for theme, palette in THEMES.items():
        (output / f"stats-{theme}.svg").write_text(
            render_card(login, profile, palette, font), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
