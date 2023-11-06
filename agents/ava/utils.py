def load_openai_api_key():
    with open("openai_api_key.secret", "r", encoding="utf-8") as f:
        return f.read()


def _str_megenta(str: str) -> str:
    return '\033[95m' + str + '\033[0m'


def _str_yellow(str: str) -> str:
    return '\033[93m' + str + '\033[0m'


def log_tool(tool_name: str, *args, end="\n"):
    args_str = _str_megenta(", ").join([_str_yellow(str(a)) for a in args])
    print(f"{_str_megenta(tool_name) + _str_megenta('(')}{args_str + _str_megenta(')')}", end=end)
