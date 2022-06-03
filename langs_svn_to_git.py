#!/usr/bin/env python3
import subprocess
import os

# Find the commit where the github repos started their github history

# Get the pre-github history
# Check out langtech to the revision before the "langs" directory was removed, svn r191058
# Then run this script, giving that working directory as the base point to work from for this script
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
    langs = [
        # ("aka", "f1cf245"),
        # ("amh", "0ce51a6"),
        # ("apu", "14df469"),
        # ("ara", "7db2ee8"),
        # ("aym", "02ef116"),
        # ("bak", "5ced48c"),
        # ("bla", "dd451d6"),
        # ("bul", "cf69e73"),
        ("bxr", "2983d7f"),
        # ("ces", "f3185db"),
        # ("chp", "113e8f9"),
        # ("chr", "4514fc6"),
        # ("ciw", "7599214"),
        # ("ckt", "39044a9"),
        # ("cor", "4e3257d"),
        # ("crj", "aac6c44"),
        # ("crk", "7165a207"),
        # ("crl", "76dd46e"),
        # ("cwd", ""),
        # ("dan", ""),
        # ("deu", "6693a3d"),
        # ("dgr", "a2a2a17"),
        # ("eng", "95af006"),
        # ("epo", "65cfe2e"),
        # ("ess", "39c7770"),
        # ("est-x-plamk", "815fe034"),
        # ("est-x-utee", "f4db64a"),
        # ("esu", ""),
        # ("eus", "37c6aaf"),
        # ("evn", "251dca3"),
        # ("fao", "3f0fa1aa"),
        # ("fin", "2f37c19"),
        # ("fit", "3d6d326"),
        # ("fkv", "f3b59102"),
        # ("gle", "d6777b8"),
        # ("got", ""),
        # ("grn", "a88b4ba"),
        # ("hdn", "220f0d1"),
        # ("hin", "abdf753"),
        # ("hun", "d543259"),
        # ("iku", "733f289"),
        # ("ipk", "02c1014"),
        # ("isl", ""),
        # ("izh", "22f5320"),
        # ("kal", "a3944514"),
        # ("kca", "45f757b"),
        # ("kek", "b3edbb4"),
        # ("khk", "7f078a5"),
        # ("kio", "8477882"),
        # ("kjh", "55cc343"),
        # ("kmr", "fa791b0"),
        # ("koi", "c5c22ab"),
        # ("kpv", "153dbf5a"),
        # ("krl", "341844e"),
        # ("lav", "fbfa558"),
        # ("liv", "73568549"),
        # ("luo", "4ac25dd"),
        # ("lut", "65c99b4"),
        # ("mdf", "bfcdfc60"),
        # ("mhr", "a8a34b1"),
        # ("mns", "034f0a7"),
        # ("moe", "0f7f5f4"),
        # ("moh", "eea5424"),
        # ("mrj", "182f39f7"),
        # ("myv", "d258b5c7"),
        # ("ndl", "3bf2cf9"),
        # ("nds", "8fd7c7c"),
        # ("nio", "6f1b271"),
        # ("nno", "1f103d4"),
        # ("nno-x-ext-apertium", ""),
        # ("nob", "b572447"),
        # ("non", "811a457"),
        # ("nso", "03d3203"),
        # ("oji", "64dcf88"),
        # ("olo", "db0aa188"),
        # ("otw", "24256a3"),
        # ("quc-x-ext-apertium", ""),
        # ("rmf", "381c752"),
        # ("rmn", "93a0989"),
        # ("rmu", "e7a023a"),
        # ("rmy", "41f4cc5"),
        # ("ron", "f5642b2"),
        # ("rup", "7bd49ad"),
        # ("rus", "31eb8bb"),
        # ("sel", "8c3a987"),
        # ("sjd", "ec45987"),
        # ("sje", "3a16cf1f"),
        # ("sjt", "4f94ca5"),
        # ("skf", "e907aee"),
        # ("sma", "66e59da0"),
        # ("sme", "37dcbb27d"),
        # ("smj", "ca3d670f"),
        # ("smn", "ed3d1d758"),
        # ("sms", "61a49596"),
        # ("som", "536f1ef"),
        # ("spa-x-ext-apertium", ""),
        # ("sqi", "cc318f7"),
        # ("srs", "7166051"),
        # ("sto", "fcaadfe"),
        # ("swe", "7642ee8"),
        # ("tat", "7e05745"),
        # ("tau", "46b4d47"),
        # ("tel", "d6ca64c"),
        # ("tgl", "e7e070c"),
        # ("tir", "61aa79b"),
        # ("tku", "3626703"),
        # ("tlh", "9dbd161"),
        # ("tur-x-ext-trmorph", ""),
        # ("tuv", "22c291e"),
        # ("tyv", "df0f772"),
        # ("udm", "2cd4ee3"),
        # ("vep", "85a1628"),
        # ("vot", "530ce57"),
        # ("vot-x-ext-kkankain", ""),
        # ("vro", "ae7c8768"),
        # ("xal", "b4228d7"),
        # ("xwo", "3977c78"),
        # ("yrk", "6e99a71d"),
        # ("zul", ""),
        # ("zul-x-exp", "4b50118"),
        # ("zxx", "d90a1f0"),
    ]
    directories = ["st", "gt", "kt", "langs"]

    for langinfo in langs:
        lang = langinfo[0]
        paths = [f"--path {directory}/{lang}" for directory in directories]
        for command in [
            (
                f"git clone --mirror --no-local langtech_upto_removed_langs {lang}-mirror",
                os.getcwd(),
            ),
            (f"git filter-repo --prune-empty always", f"{lang}-mirror"),
            (f"git filter-repo {' '.join(paths)}", f"{lang}-mirror"),
            (f"git filter-repo --path-rename langs/{lang}:", f"{lang}-mirror"),
            (f"git clone {lang}-mirror {lang}-processed", os.getcwd()),
        ]:
            try:
                run(command[0], cwd=command[1])
            except subprocess.CalledProcessError as error:
                print(error)
                raise SystemExit(1)


if __name__ == "__main__":
    main()
