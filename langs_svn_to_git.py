#!/usr/bin/env python3
import os
import subprocess
import sys
from collections import namedtuple

# Find the commit where the github repos started their github history

# Get the pre-github history
# Check out langtech to the revision before the "langs" directory was removed, svn r191058
# Then run this script, giving that working directory as the base point to work from for this script

LangInfo = namedtuple(
    "LangInfo",
    [
        "langname",
        "first_important_git_commit",
        "start_directory",
        "final_directory",
        "has_full_history",
    ],
    defaults=[False],
)


def run(command, cwd=""):
    print(command)
    subprocess.run(command.split(), cwd=cwd, check=True, encoding="utf-8")


def main():
    # List produced (except where noted) by running:
    # for i in lang-*
    # do
    #   cd $i;
    #   hash=$(git log --oneline |grep 'Add initial CI configuration'|cut -f1 -d" ");
    #   lang=$(echo $i|cut -f2- -d'-');
    #   echo "('$lang', '$hash'),";
    #   cd ..;
    # done
    # in giellalt, where giellalt is the directory where gut has checked out giellat lang-* repos
    svnlanginfos = [
        # "langs": [
        LangInfo("chp", "113e8f9", "kt", "langs", True),  # ok
        # ("chr", "4514fc6"),  # this is in both startup-langs and langs
        # ("ciw", "7599214"),
        # ("cor", "4e3257d"),
        # ("crk", "7165a207"),
        # ("cwd", ""),
        # ("dan", ""), not in svn
        # ("deu", "6693a3d"),
        # ("est-x-plamk", "815fe034"),
        # ("esu", ""), not in svn
        # ("evn", "251dca3"),
        # ("fao", "3f0fa1aa"),
        # ("fin", "2f37c19"),
        # ("fit", "3d6d326"),
        # ("fkv", "f3b59102"),
        # # ("got", ""), not in svn
        # ("hdn", "220f0d1"),
        # ("hun", "d543259"),
        # ("ipk", "02c1014"),
        # ("isl", ""), not in svn
        # ("izh", "22f5320"),
        # ("kal", "a3944514"),
        # ("kca", "45f757b"),
        # ("koi", "c5c22ab"),
        # ("kpv", "153dbf5a"),
        # ("lav", "fbfa558"),
        # ("liv", "73568549"),
        # ("lut", "65c99b4"),
        # ("mdf", "bfcdfc60"),
        # ("mhr", "a8a34b1"),  # this is in both startup-langs and langs
        # ("mns", "034f0a7"),
        # ("mrj", "182f39f7"),
        # ("myv", "d258b5c7"),
        # ("nds", "8fd7c7c"),
        # ("nio", "6f1b271"),
        # ("nob", "b572447"),
        # ("oji", "64dcf88"),
        # ("olo", "db0aa188"),
        # ("otw", "24256a3"),
        # ("quc-x-ext-apertium", ""), not in svn
        # ("ron", "f5642b2"),
        # ("rus", "31eb8bb"),
        # ("sjd", "ec45987"),
        # ("sje", "3a16cf1f"),
        # ("sma", "66e59da0"),
        # ("sme", "37dcbb27d"),
        # ("smj", "ca3d670f"),
        # ("smn", "ed3d1d758"),
        # ("sms", "61a49596"),
        # ("som", "536f1ef"),
        # ("tat", "7e05745"),
        # ("tku", "3626703"),
        # ("udm", "2cd4ee3"),
        # ("vep", "85a1628"),
        # ("vot", "530ce57"),
        LangInfo(
            langname="vro",
            first_important_git_commit="ae7c8768",
            start_directory="kt",
            final_directory="langs",
        ),
        # ("yrk", "6e99a71d"),
        # ("zul", ""),
        # ],
        # "startup-langs": [
        # ("aka", "f1cf245"),
        # ("amh", "0ce51a6"),
        # ("apu", "14df469"),
        # ("aym", "02ef116"),
        # ("bla", "dd451d6"),
        # # ("chr", "4514fc6"),  # this is in both startup-langs and langs
        # ("ckt", "39044a9"),
        # ("crj", "aac6c44"),
        # ("crl", "76dd46e"),
        # ("dgr", "a2a2a17"),
        # ("epo", "65cfe2e"),
        # ("ess", "39c7770"),
        # ("eus", "37c6aaf"),
        # ("gle", "d6777b8"),
        # ("grn", "a88b4ba"),
        # ("hin", "abdf753"),
        # ("iku", "733f289"),
        # ("kek", "b3edbb4"),
        # ("khk", "7f078a5"),
        # ("kio", "8477882"),
        # ("kjh", "55cc343"),
        # ("kmr", "fa791b0"),
        # ("krl", "341844e"),
        # ("luo", "4ac25dd"),
        # # ("mhr", "a8a34b1"),  # this is in both startup-langs and langs
        # ("moe", "0f7f5f4"),
        # ("moh", "eea5424"),
        # ("ndl", "3bf2cf9"),
        # ("nno", "1f103d4"),
        # ("non", "811a457"),
        # ("nso", "03d3203"),
        # ("rmf", "381c752"),
        # ("rmn", "93a0989"),
        # ("rmu", "e7a023a"),
        # ("rmy", "41f4cc5"),
        # ("rup", "7bd49ad"),
        # ("sel", "8c3a987"),
        # ("skf", "e907aee"),
        # ("srs", "7166051"),
        # ("sto", "fcaadfe"),
        # ("swe", "7642ee8"),
        # ("tau", "46b4d47"),
        # ("tel", "d6ca64c"),
        # ("tgl", "e7e070c"),
        # ("tir", "61aa79b"),
        # ("tlh", "9dbd161"),
        # ("tuv", "22c291e"),
        # ("tyv", "df0f772"),
        # ("xal", "b4228d7"),
        # ("xwo", "3977c78"),
        # ("zul-x-exp", "4b50118"),
        # ],
        # "experimental-langs": [
        # ("ara", "7db2ee8"),
        # ("bul", "cf69e73"),
        # ("ces", "f3185db"),
        # ("eng", "95af006"),
        # ("est-x-utee", "f4db64a"),
        # ("sjt", "4f94ca5"),
        # ("sqi", "cc318f7"),
        # ("zxx", "d90a1f0"),
        # ],
        # "external-langs": [
        # ("nno-x-ext-apertium", ""),
        # ("spa-x-ext-apertium", ""),
        # ("tur-x-ext-trmorph", ""),
        # ("vot-x-ext-kkankain", ""),
        # ],
        # "closed-langs": [],
    ]

    if len(sys.argv) != 2:
        print("Please give a language to fix")
        usage(svnlanginfos)

    try:
        langinfo = [
            langinfo
            for langinfo in svnlanginfos
            if langinfo.langname == sys.argv[1] and not langinfo.has_full_history
        ][0]
    except IndexError:
        print("The given language either does not exist, or has already been fixed.")
        usage(svnlanginfos)

    fix_a_lang(langinfo)


def usage(svnlanginfos):
    print("You can choose from")
    print(
        "\n".join(
            [
                langinfo.langname
                for langinfo in svnlanginfos
                if not langinfo.has_full_history
            ]
        )
    )
    raise SystemExit(1)


def fix_a_lang(langinfo):
    directories = [langinfo.start_directory, langinfo.final_directory]
    svn_lang = langinfo.langname.split("-")[0]
    paths = [f"--path {directory}/{svn_lang}" for directory in directories]
    commands = [
        (f"git clone --mirror --no-local lt {svn_lang}-mirror", os.getcwd()),
        (f"git filter-repo --prune-empty always", f"{svn_lang}-mirror"),
        (f"git filter-repo {' '.join(paths)}", f"{svn_lang}-mirror"),
        (
            f"git filter-repo--path-rename {langinfo.final_directory}/{svn_lang}/:",
            f"{svn_lang}-mirror",
        ),
        (f"git clone git@github.com:giellalt/lang-{langinfo.langname}", os.getcwd()),
        (
            f"git fetch ../{svn_lang}-mirror master:main_with_fixed_history",
            os.path.join(os.getcwd(), f"lang-{langinfo.langname}"),
        ),
        (
            "git switch main_with_fixed_history",
            os.path.join(os.getcwd(), f"lang-{langinfo.langname}"),
        ),
        (
            f"git cherry-pick {langinfo.first_important_git_commit}^..HEAD --allow-empty",
            os.path.join(os.getcwd(), f"lang-{langinfo.langname}"),
        ),
        (
            f"git filter-repo --prune-empty always",
            os.path.join(os.getcwd(), f"lang-{langinfo.langname}"),
        ),
    ]
    for (index, command) in enumerate(commands, start=2):
        try:
            run(command[0], cwd=command[1])
        except subprocess.CalledProcessError as error:
            print(error)
            raise SystemExit(index)


if __name__ == "__main__":
    main()
