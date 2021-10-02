def print_result(stdout, stderr, expected=None):
    if expected:
        print(f"[expected]\n{expected}")

    if stdout:
        print(f"[stdout]\n{stdout}")

    if stderr:
        print(f"[stderr]\n{stderr}")
