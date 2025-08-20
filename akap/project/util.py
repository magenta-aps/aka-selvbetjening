def strtobool(val, return_value_if_nonbool=False):
    if isinstance(val, bool):
        return val
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        if return_value_if_nonbool:
            return val
        raise ValueError("invalid truth value %r" % (val,))
