def load_openai_api_key():
    with open("openai_api_key.secret", "r", encoding="utf-8") as f:
        return f.read()