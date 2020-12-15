def print_result(stdout, stderr, expected=None):
    if expected:
        print("[expected]\n{}".format(expected))

    if stdout:
        print("[stdout]\n{}".format(stdout))

    if stderr:
        print("[stderr]\n{}".format(stderr))
