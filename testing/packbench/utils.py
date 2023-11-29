from typing import List


def arg_to_strings(arg_name: str, vals: str | List[str]) -> str:
    """
    Parses a `str` or `List[str]` into a strings argument.
    For example:

    arg="arg1" => "arg1"
    arg=["arg1", "arg2"] => "arg1 arg2"
    """
    if isinstance(vals, str):
        return f"{arg_name} {vals}"

    if isinstance(vals, list):
        return ' '.join([f"{arg_name} {v}" for v in vals])

    return arg_to_strings(arg_name, str(vals))


def append_arg(val: str, arg: str | List[str]=None) -> str | List[str]:
    """
    Appends a value to an argument and returns the result converted
    into a strings argument.
    """
    if arg is None:
        return val

    if isinstance(arg, str):
        return arg_to_strings([arg, val])

    if isinstance(arg, list):
        return arg_to_strings(arg.append(val))

    new_arg = append_arg(val, str(arg))
    return arg_to_strings(new_arg)
