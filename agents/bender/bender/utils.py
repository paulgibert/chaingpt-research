import os


OPENAI_API_KEY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../openai_api_key.secret")


def load_openai_api_key():
    with open(OPENAI_API_KEY_PATH, "r", encoding="utf-8") as f:
        return f.read()