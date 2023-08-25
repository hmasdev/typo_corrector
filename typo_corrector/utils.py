
def pipeline(*funcs):
    """Pipeline of functions

    Args:
        *funcs: functions to be executed in order

    Returns:
        _pipeline: function that executes the functions in order

    Examples:
        >>> def add_one(x):
        ...     return x + 1
        >>> def add_two(x, *args, **kwargs):
        ...     return x + 2
        >>> def add_three(x, *args, **kwargs):
        ...     return x + 3
        >>> add_six = pipeline(add_one, add_two, add_three)
        >>> add_six(1)
        7

    NOTE: The result of a function is passed as the first argument to the next when it is not None.
    """  # noqa

    def _pipeline(*args, **kwargs):
        prev_result = None
        result = None
        for func in funcs:
            if prev_result is None and result is None:
                prev_result = func(*args, **kwargs)
            else:
                prev_result = func(result, *args, **kwargs)  # noqa
            if prev_result is not None:
                result = prev_result
        return result

    return _pipeline


def create_hotkey_str(
    use_ctrl: bool,
    use_alt: bool,
    use_shift: bool,
    use_super: bool,
    char: str,
) -> str:
    """Create hotkey string from keybind config

    Args:
        use_ctrl: whether to use ctrl
        use_alt: whether to use alt
        use_shift: whether to use shift
        use_super: whether to use super
        char: character to be used

    Returns:
        hotkey_str: hotkey string

    Examples:
        >>> create_hotkey_str(True, False, False, False, 'a')
        '<ctrl>+a'
        >>> create_hotkey_str(True, True, False, False, 'a')
        '<ctrl>+<alt>+a'
        >>> create_hotkey_str(True, True, True, False, 'a')
        '<ctrl>+<alt>+<shift>+a'
    """
    hotkey_str = ''
    if use_ctrl:
        hotkey_str += '<ctrl>+'
    if use_alt:
        hotkey_str += '<alt>+'
    if use_shift:
        hotkey_str += '<shift>+'
    if use_super:
        hotkey_str += '<cmd>+'
    hotkey_str += char
    return hotkey_str
