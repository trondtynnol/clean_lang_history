return re.sub(b"^git-svn-id:.*\n", b"", message, flags=re.MULTILINE)
