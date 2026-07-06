load_dotenv()

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}


def to_bool(value):
    return str(value).strip().lower() in ["true", "1", "yes", "on"]


@app.get("/effective-config")
def effective_config(set: List[str] = Query(default=[])):
    config = DEFAULTS.copy()

    # YAML Layer
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml", "r") as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                config.update(yaml_config)

    # .env Layer
    if os.getenv("APP_PORT"):
        config["port"] = int(os.getenv("APP_PORT"))

    if os.getenv("NUM_WORKERS"):
        config["workers"] = int(os.getenv("NUM_WORKERS"))

    if os.getenv("APP_API_KEY"):
        config["api_key"] = os.getenv("APP_API_KEY")

    # OS Environment Layer (highest before CLI)
    if os.environ.get("APP_PORT"):
        config["port"] = int(os.environ["APP_PORT"])

    if os.environ.get("APP_WORKERS"):
        config["workers"] = int(os.environ["APP_WORKERS"])

    if os.environ.get("APP_LOG_LEVEL"):
        config["log_level"] = os.environ["APP_LOG_LEVEL"]

    if os.environ.get("APP_API_KEY"):
        config["api_key"] = os.environ["APP_API_KEY"]

    # CLI Overrides
    for item in set:
        if "=" not in item:
            continue

        key, value = item.split("=", 1)

        if key in ["port", "workers"]:
            config[key] = int(value)

        elif key == "debug":
            config[key] = to_bool(value)

        else:
            config[key] = value

    # Secret Masking
    config["api_key"] = "****"

    return config