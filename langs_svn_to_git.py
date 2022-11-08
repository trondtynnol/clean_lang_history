#!/usr/bin/env python3
import glob
import os
import subprocess
import sys
import datetime

# Script to fix histories of langs from https://gtsvn.uit.no/langtech/trunk


def svn_to_est_utee(work_directory):
    replacements = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "replacements.txt"
    )
    git_svn = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "replace_git_svn.py"
    )
    mailmappath = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "all-repos.mailmap"
    )
    here = os.path.abspath(os.path.dirname(__file__))
    commands = [
        (
            f"git svn clone -r85001:191058 --authors-file {here}/svn2git-authors.txt "
            "https://gtsvn.uit.no/langtech/trunk/langs/est est-x-utee-mirror",
            work_directory,
        ),
        (
            "git filter-repo "
            "--force "
            "--prune-empty always "  # remove empty commits, e.g. svn-ignores and such
            "--strip-blobs-bigger-than 50M "  # strip files larger than githubs limit
            "--replace-refs delete-no-add "
            "--prune-degenerate always "
            f"--replace-message {replacements} "
            f"--message-callback {git_svn} "
            f"--mailmap {mailmappath}",
            f"{work_directory}/est-x-utee-mirror",  # the "lang"-mirror repos are cloned from this repo
        ),
    ]
    for command in commands:
        run(command[0], cwd=command[1])
    do_git_replace("lang-est-x-utee", "est-x-utee", work_directory)


def svn_to_est_plamk(work_directory):
    replacements = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "replacements.txt"
    )
    git_svn = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "replace_git_svn.py"
    )
    mailmappath = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "all-repos.mailmap"
    )
    here = os.path.abspath(os.path.dirname(__file__))
    commands = [
        (
            f"git svn clone -r67271:85000 --authors-file {here}/svn2git-authors.txt "
            "https://gtsvn.uit.no/langtech/trunk/langs/est est-x-plamk-mirror-old",
            work_directory,
        ),
        (
            f"git svn clone -r85000:191058 --authors-file {here}/svn2git-authors.txt "
            "https://gtsvn.uit.no/langtech/trunk/experiment-langs/est est-x-plamk-mirror",
            work_directory,
        ),
        (
            "git fetch ../est-x-plamk-mirror-old master:old",
            f"{work_directory}/est-x-plamk-mirror",
        ),
    ]
    for command in commands:
        run(command[0], cwd=command[1])

    old_head = subprocess.run(
        ["git", "log", "-n", "1", "--pretty=format:%H %aI", "old"],
        cwd=f"{work_directory}/est-x-plamk-mirror",
        encoding="utf-8",
        capture_output=True,
    ).stdout

    parent = old_head.split()[0]

    first_commit = (
        subprocess.run(
            ["git", "log", "--reverse", "--pretty=format:%H %aI"],
            cwd=f"{work_directory}/est-x-plamk-mirror",
            encoding="utf-8",
            capture_output=True,
        )
        .stdout.split("\n")[0]
        .split()[0]
    )

    commands = [
        (
            f"git replace --graft {first_commit} {parent}",
            f"{work_directory}/est-x-plamk-mirror",
        ),
        (
            "git filter-repo "
            "--force "
            "--prune-empty always "  # remove empty commits, e.g. svn-ignores and such
            "--strip-blobs-bigger-than 50M "  # strip files larger than githubs limit
            "--replace-refs delete-no-add "
            "--prune-degenerate always "
            f"--replace-message {replacements} "
            f"--message-callback {git_svn} "
            f"--mailmap {mailmappath}",
            f"{work_directory}/est-x-plamk-mirror",  # the "lang"-mirror repos are cloned from this repo
        ),
    ]
    for command in commands:
        run(command[0], cwd=command[1])
    do_git_replace("lang-est-x-plamk", "est-x-plamk", work_directory)


def main():
    if len(sys.argv) != 3:
        print(
            "usage: ./langs_svn_to_git.py <dir-where-giellalt-is-clone> <dir-where-work-is-done>"
        )
        sys.exit(1)

    work_directory = os.path.abspath(sys.argv[2])
    if not os.path.exists(os.path.join(work_directory, "lt")):
        try:
            prepare_old_svn(work_directory)
        except subprocess.CalledProcessError as error:
            print(error)

    git_repos_home = os.path.abspath(
        sys.argv[1]
    )  # run gut clone -o giellalt -r lang-* to populate this directory
    for git_repo_name in get_valid_repo_names(git_repos_home):
        if not os.path.exists(os.path.join(work_directory, git_repo_name)):
            try:
                fix_a_lang(git_repo_name, work_directory)
            except subprocess.CalledProcessError as error:
                print(error)
            except IndexError as error:
                print(error)

    svn_to_est_utee(work_directory)
    svn_to_est_plamk(work_directory)


def prepare_old_svn(work_directory):
    # 191058
    here = os.path.abspath(os.path.dirname(__file__))
    commands = [
        (
            f"git svn clone -r1:191058 --authors-file {here}/svn2git-authors.txt "
            "https://gtsvn.uit.no/langtech/trunk langtech_upto_removed_langs",
            work_directory,
        ),
        (
            "git clone --mirror --no-local langtech_upto_removed_langs lt",
            work_directory,
        ),
        (
            "git filter-repo "
            "--prune-empty always "  # remove empty commits, e.g. svn-ignores and such
            "--strip-blobs-bigger-than 50M",  # strip files larger than githubs limit
            f"{work_directory}/lt",  # the "lang"-mirror repos are cloned from this repo
        ),
    ]
    for command in commands:
        run(command[0], cwd=command[1])


def fix_a_lang(git_repo_name, work_directory):
    svn_elements = set(svn_lang_dirs(git_repo_name, work_directory))
    if len(svn_elements) < 2:
        # The language files have only lived in one svn directory.
        # The previous svn2git process has covered this case
        print("No need to process", git_repo_name)
    else:
        svn_lang = git_repo_name.split("-")[1]
        prepare_for_git_replace(git_repo_name, svn_elements, svn_lang, work_directory)
        if not os.path.exists(f"{work_directory}/{git_repo_name}"):
            do_git_replace(git_repo_name, svn_lang, work_directory)


def prepare_for_git_replace(git_repo_name, svn_directories, svn_lang, work_directory):
    # Find the directory where the language last lived in the svn repo by running
    # the git log commands found in svn_lang_dirs function and look at the dates.
    replacements = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "replacements.txt"
    )
    git_svn = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "replace_git_svn.py"
    )
    mailmappath = os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "all-repos.mailmap"
    )
    if not os.path.exists(f"{work_directory}/{svn_lang}-mirror"):
        paths = [f"--path {svn_directory}" for svn_directory in svn_directories]
        renames = [
            f"--path-rename {svn_directory}/:" for svn_directory in svn_directories
        ]
        commands = [
            (f"git clone --mirror --no-local lt {svn_lang}-mirror", work_directory),
            (
                f"git filter-repo  {' '.join(paths)} {' '.join(renames)}",
                f"{work_directory}/{svn_lang}-mirror",
            ),
        ]
        for command in commands:
            run(command[0], cwd=command[1])
    run(
        f"git filter-repo --force "
        f"--replace-message {replacements} "
        f"--message-callback {git_svn} "
        f"--mailmap {mailmappath}",
        cwd=f"{work_directory}/{svn_lang}-mirror",
    )


def do_git_replace(git_repo_name, svn_lang, work_directory):
    commands = [
        (f"git clone git@github.com:giellalt/{git_repo_name}", work_directory),
        (
            f"git fetch ../{svn_lang}-mirror master:old",
            f"{work_directory}/{git_repo_name}",
        ),
    ]
    for command in commands:
        run(command[0], cwd=command[1])

    # The last commit in the old history

    old_head = subprocess.run(
        ["git", "log", "-n", "1", "--pretty=format:%H %s", "old"],
        cwd=f"{work_directory}/{git_repo_name}",
        encoding="utf-8",
        capture_output=True,
    ).stdout

    commit_b = old_head.split()[0]
    print(f"commit_b {commit_b}")
    # The log history of main
    main_log_lines = subprocess.run(
        ["git", "log", "--pretty=format:%H %s", "main"],
        cwd=f"{work_directory}/{git_repo_name}",
        encoding="utf-8",
        capture_output=True,
    ).stdout.split("\n")

    with (open(f"{git_repo_name.split('-')[1]}-pre.log", "w")) as pre_stream:
        print(
            subprocess.run(
                ["git", "log", "--pretty=format:%s %aI", "main"],
                cwd=f"{work_directory}/{git_repo_name}",
                encoding="utf-8",
                capture_output=True,
            ).stdout,
            file=pre_stream,
        )
    needle = f"{old_head.replace(commit_b, '')}"

    # Find the old commit in main
    first_important_git_commit = [line for line in main_log_lines if needle in line][0]
    commit_a = first_important_git_commit.split()[0]
    print(f"commit_a {commit_a}")

    print(f"git replace {commit_a} {commit_b}")

    commands = [
        (f"git replace {commit_a} {commit_b}", f"{work_directory}/{git_repo_name}"),
        (
            "git filter-repo --replace-refs delete-no-add --force --prune-degenerate always",
            f"{work_directory}/{git_repo_name}",
        ),
    ]
    for command in commands:
        run(command[0], cwd=command[1])

    main_with_parents = subprocess.run(
        ["git", "log", "--pretty=format:%H %P", "main"],
        cwd=f"{work_directory}/{git_repo_name}",
        encoding="utf-8",
        capture_output=True,
    ).stdout.split("\n")

    children = "\n".join(
        [
            f"\t{child}"
            for main_line in main_with_parents
            if main_line.endswith(commit_b)
            for child in main_line.split()[:-1]
        ]
    )

    print(f"children of {commit_b}\n{children}")
    cleanup(git_repo_name, svn_lang, work_directory)


def cleanup(git_repo_name, svn_lang, work_directory):
    commands = [
        (
            f"git filter-repo --replace-refs delete-no-add --force --prune-degenerate always",
            f"{work_directory}/{git_repo_name}",
        ),
        (
            f"git remote add origin git@github.com:giellalt/{git_repo_name}",
            f"{work_directory}/{git_repo_name}",
        ),
    ]

    for command in commands:
        run(command[0], cwd=command[1])

    with (open(f"{svn_lang}-post.log", "w")) as pre_stream:
        print(
            subprocess.run(
                ["git", "log", "--pretty=format:%s %aI", "main"],
                cwd=f"{work_directory}/{git_repo_name}",
                encoding="utf-8",
                capture_output=True,
            ).stdout,
            file=pre_stream,
        )


def run(command, cwd=""):
    if cwd:
        print(f"cd {cwd}")
    print(f"{command}\n")
    subprocess.run(
        command.split(), cwd=cwd, check=True, encoding="utf-8", capture_output=True
    )


def get_valid_repo_names(git_repos_home):
    avoid_langs = [
        "lang-zul",  # lang-zul-x-experimental is the open one
        "lang-est-x-utee",  # must be manually fixed
        "lang-est-x-plamk",  # same goes for this
        "lang-esu",  # the work done in svn is not used in the github repo
        "lang-sjd-x-private",
    ]
    return [
        l.split("/")[-1]
        for l in sorted(glob.glob(f"{git_repos_home}/lang-*"))
        if (l.split("/")[-1] not in avoid_langs or l.endswith("nno-x-ext-apertium"))
    ]


def svn_lang_dirs(git_repo_name, work_directory):
    # Find all the places the language files have lived in gtsvn
    print(f"checking {git_repo_name}: {datetime.datetime.now()}")

    svn_name = git_repo_name.split("-")[1]

    lang_map = {"lut": ["slh", "lut"], "rmf": ["rom", "rmf"], "cor": ["kor", "cor"]}
    # rmf started up as rom, search in both rom and rmf history
    # lut started as slh, search for both slh and lut
    svn_names = lang_map.get(svn_name, [svn_name])
    for svn_lang_dir in [
        f"{svn_lang_dir_base}/{name}"
        for name in svn_names
        for svn_lang_dir_base in [
            "gt",
            "kt",
            "st",
            "experiment-langs",
            "startup-langs",
            "langs",
            "techdoc/lang",
            "gt/doc/lang",
            "gtlangs",
            "newinfra",
            "newinfra/gtlangs",
            "newinfra/langs",
        ]
    ]:
        o = subprocess.run(
            [
                "git",
                "log",
                "-n 1",
                '--pretty=format:"%H %an %ad"',
                "--date=short",
                "--",
                f"{svn_lang_dir}",
            ],
            cwd=f"{work_directory}/langtech_upto_removed_langs",
            encoding="utf-8",
            check=True,
            capture_output=True,
        )
        if o.stdout:
            yield svn_lang_dir


if __name__ == "__main__":
    main()

# https://github.com/giellalt/clean_lang_history/issues/1

# https://stackoverflow.com/questions/49563574/git-delete-one-of-two-parent-commits, answer two

# If the script reports about two children, open the lang-xxx in gitk,
# find the wonky commit and do
# git replace --edit <hash of wonky commit>
# In the editor, remove the suspicios parent
# then
# git filter-repo --replace-refs delete-no-add --prune-degenerate always

# The last manual command to run when having done checks:
# git push -f origin main:main_with_history_fixed

# cd lang-aka/ && git pl && git switch main_with_history_fixed && if [ "$(git log -n1 --pretty=format:"%s %aI")" == "$(git log -n1 --pretty=format:"%s %aI" main)" ]; then git-dag; else echo false; fi
# check that the last commit in main_with_history_fixed is the same as main
# if not, cherry-pick from main, to sync the last commits, then
# git push --force origin main_with_history_fixed:main && git push --force -d origin main_with_history_fixed

# 2022-11-04
# khk should not have been pushed: Sjur has to push his main again
# zul-exp no need to fix?

# not pushed to main
# bla -> alert contributors
# crk -> alert contributors
# est-x-plamk -> not up-to-date
# est-x-utee -> not up-to-date
# fao -> alert contributors
# fit -> alert contributors
# kal -> alert contributors
# nob -> alert contributors
# sma -> alert contributors
# sme -> alert contributors
# smj -> alert contributors
# smn -> alert contributors
# sms -> alert contributors

# 2022-11-07
# not pushed to main
# est-x-plamk -> alert contributors
# est-x-utee -> alert contributors

# 2022-11-08
# khk fixed
