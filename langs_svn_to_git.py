#!/usr/bin/env python3
import glob
import os
import shutil
import subprocess
import sys

# Script to fix histories of langs from https://gtsvn.uit.no/langtech/trunk


def main():
    git_repos_home = os.path.abspath(
        sys.argv[1]
    )  # run gut clone -o giellalt -r lang-* to populate this directory
    work_directory = os.path.abspath(sys.argv[2])

    # try:
    #     prepare_old_svn(work_directory)
    # except subprocess.CalledProcessError as error:
    #     print(error)
    for git_repo_name in ["lang-sme"]:  # get_valid_repo_names(git_repos_home):
        # if os.path.exists(f"{work_directory}/{git_repo_name}"):
        #     print(git_repo_name, "has already been processed")
        # else:
        try:
            fix_a_lang(git_repo_name, work_directory)
        except subprocess.CalledProcessError as error:
            print(error)
        except IndexError as error:
            print(error)
    print("main done")


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
        # prepare_for_rebase(git_repo_name, svn_elements, svn_lang, work_directory)
        rebase_new_on_old(git_repo_name, svn_lang, work_directory)
        # cleanup(git_repo_name, svn_lang, work_directory)


def prepare_for_rebase(git_repo_name, svn_directories, svn_lang, work_directory):
    # The process stops here for some languages because of name change collisions.
    # Find the directory where the language last lived in the svn repo by running
    # the git log commands found in svn_lang_dirs function and look at the dates.
    # Remove all the --path-rename options from command found in the log
    # in the terminal window, except the one for the directory that was found,
    # then run that command.
    # Proceed with running the rest of the commands manually.
    paths = [f"--path {svn_directory}" for svn_directory in svn_directories]
    renames = [f"--path-rename {svn_directory}/:" for svn_directory in svn_directories]
    commands = [
        (f"git clone --mirror --no-local lt {svn_lang}-mirror", work_directory),
        (
            f"git filter-repo {' '.join(paths)} {' '.join(renames)}",
            f"{work_directory}/{svn_lang}-mirror",
        ),
        (f"git clone git@github.com:giellalt/{git_repo_name}", work_directory),
    ]
    for command in commands:
        run(command[0], cwd=command[1])


def rebase_new_on_old(git_repo_name, svn_lang, work_directory):
    # The last commit in the old history
    old_head = subprocess.run(
        ["git", "log", "-n", "1", '--pretty=format:"%H %an %ad"'],
        cwd=f"{work_directory}/{svn_lang}-mirror",
        encoding="utf-8",
        capture_output=True,
    ).stdout[1:-1]

    commit_b = old_head.split()[0]
    print(f"old_head: {old_head}")
    print(f"commit_b: {commit_b}")

    # The last commit in current history
    main_log_lines = subprocess.run(
        ["git", "log", '--pretty=format:"%H %an %ad"'],
        cwd=f"{work_directory}/{git_repo_name}",
        encoding="utf-8",
        capture_output=True,
    ).stdout.split("\n")
    print(f"len of main_log_lines: {len(main_log_lines)}")
    print(main_log_lines[0])
    # The github history starts at this commit
    needle = f"{old_head.replace(commit_b, '')}"
    first_important_git_commit = [
        line[1:-1] for line in main_log_lines if needle in line
    ][0]
    print(f"first_important: {first_important_git_commit}")
    commit_a = first_important_git_commit.split()[0]
    print(commit_a)

    commands = [
        (
            f"git fetch ../{svn_lang}-mirror master:old",
            f"{work_directory}/{git_repo_name}",
        ),
        (f"git switch -c main_with_history_fixed", f"{work_directory}/{git_repo_name}"),
        (f"git replace {commit_a} {commit_b}", f"{work_directory}/{git_repo_name}"),
        (f"git filter-repo --force", f"{work_directory}/{git_repo_name}")
        #     # The process stops at the rebase for some languages because of conflicts
        #     # If this is the case, then manually
        #     #   merge incoming changes each time the rebase stops
        #     #   `git add` files that have been fixed
        #     #   git rebase --continue (or git rebase --skip for empty commits)
        #     # the run switch -c command, followed by the ones in cleanup()
        #     (
        #         # merge histories, rebase the commits in the range from "first_import_git_commit" to "main_head"
        #         # onto the old history
        #         f"git rebase --onto {old_head} {first_important_git_commit}^ {main_head}",
        #         f"{work_directory}/{git_repo_name}",
        #     ),
    ]
    for command in commands:
        run(command[0], cwd=command[1])


def cleanup(git_repo_name, svn_lang, work_directory):
    commands = [(f"git branch -D old", f"{work_directory}/{git_repo_name}")]
    for command in commands:
        run(command[0], cwd=command[1])
    shutil.rmtree(f"{work_directory}/{svn_lang}-mirror")


def run(command, cwd=""):
    print(f"\n{command}")
    subprocess.run(command.split(), cwd=cwd, check=True, encoding="utf-8")


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
    print(f"checking {git_repo_name}")
    svn_name = git_repo_name.split("-")[1]

    # rmf started up as rom, search in both rom and rmf history
    svn_names = ["rom", "rmf"] if svn_name == "rmf" else [svn_name]
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
# fix names https://stackoverflow.com/questions/58263216/how-to-change-commit-author-for-multiple-commits-using-filter-branch
# author dates https://github.com/giellalt/giella-core/issues/20#issuecomment-1135506061

# cd repo
# git filter-repo --mailmap my-mailmap


# Parent rewriting

# To replace $commit_A with $commit_B (e.g. make all commits which had $commit_A as a parent instead have $commit_B for that parent), and rewrite history to make it permanent:

# git replace $commit_A $commit_B
# git filter-repo --force

# To create a new commit with the same contents as $commit_A except with different parent(s) and then replace $commit_A with the new commit, and rewrite history to make it permanent:

# git replace --graft $commit_A $new_parent_or_parents
# git filter-repo --force

# The reason to specify --force is two-fold: filter-repo will error out if no arguments are specified, and the new graft commit would otherwise trigger the not-a-fresh-clone check.

# ❯ grep 'Obsolete test' main.txt
# 239ea63d8 Obsolete test script, removed. Checked with Lene and Trond.
# dd1681737 Obsolete test script, removed. Checked with Lene and Trond.
